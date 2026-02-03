"""
TASI Financial Database - Vanna 2.0 Agent
Uses Gemini Flash 2.5 via OpenRouter + PostgreSQL + ChromaDB
"""

import os
import sys
import io
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from typing import Type, List, Optional, Any, Dict
from pydantic import BaseModel, Field

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

load_dotenv()

import streamlit as st

# =============================================================================
# Configuration - Handle both Streamlit Cloud (st.secrets) and local (.env)
# =============================================================================

def get_config(key: str, default: str = None) -> str:
    """Get config from Streamlit secrets first, then environment variables."""
    # Try Streamlit secrets first (for Streamlit Cloud)
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    # Fall back to environment variables (for local development)
    return os.getenv(key, default)

DATABASE_URL = get_config("DATABASE_URL", "postgresql://tasi:tasi_dev_123@localhost:5433/tasi_financials")
OPENROUTER_API_KEY = get_config("OPENROUTER_API_KEY")
CHROMA_PERSIST_DIR = Path(__file__).parent / "chroma_db"


# =============================================================================
# OpenRouter LLM Service (Gemini Flash 2.5)
# =============================================================================

from openai import OpenAI

class OpenRouterLlmService:
    """LLM Service using OpenRouter API with Gemini Flash 2.5"""

    def __init__(
        self,
        api_key: str = None,
        model: str = "google/gemini-2.5-flash",  # Correct OpenRouter model ID
        base_url: str = "https://openrouter.ai/api/v1"
    ):
        self.api_key = api_key or OPENROUTER_API_KEY
        self.model = model
        self.client = OpenAI(
            base_url=base_url,
            api_key=self.api_key,
        )

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send a chat completion request."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content

    async def achat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Async chat completion."""
        # For simplicity, using sync in thread
        return self.chat(messages, **kwargs)


# =============================================================================
# PostgreSQL Connection
# =============================================================================

import psycopg2
from psycopg2.extras import RealDictCursor

class PostgresRunner:
    """SQL Runner for PostgreSQL"""

    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or DATABASE_URL
        self._conn = None

    def get_connection(self):
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(self.connection_string)
        return self._conn

    def run_sql(self, sql: str) -> List[Dict[str, Any]]:
        """Execute SQL and return results as list of dicts."""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql)
                if cursor.description:
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                conn.commit()
                return [{"status": "success", "rowcount": cursor.rowcount}]
        except Exception as e:
            conn.rollback()
            raise e

    def get_schema(self) -> str:
        """Get database schema information."""
        sql = """
        SELECT
            table_name,
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
        """
        results = self.run_sql(sql)

        schema_text = []
        current_table = None

        for row in results:
            if row['table_name'] != current_table:
                current_table = row['table_name']
                schema_text.append(f"\n{current_table}:")

            nullable = "NULL" if row['is_nullable'] == 'YES' else "NOT NULL"
            schema_text.append(f"  - {row['column_name']}: {row['data_type']} ({nullable})")

        return "\n".join(schema_text)


# =============================================================================
# Simple Vanna-style Agent
# =============================================================================

class TASIFinancialAgent:
    """
    Simple Vanna-style agent for TASI financial queries.
    Uses Gemini Flash 2.5 via OpenRouter to convert natural language to SQL.
    """

    def __init__(self):
        self.llm = OpenRouterLlmService()
        self.sql_runner = PostgresRunner()
        self.schema = self.sql_runner.get_schema()

        # Training examples for better SQL generation
        self.training_examples = self._load_training_examples()

    def _load_training_examples(self) -> str:
        """Load training examples for few-shot prompting."""
        return """
## Example Queries

### General Company Queries

Question: "Show all companies"
SQL: SELECT ticker, company_name, sector, company_type, size_category FROM company_financials WHERE is_latest = TRUE GROUP BY ticker, company_name, sector, company_type, size_category ORDER BY company_name;

Question: "Which companies are most profitable?"
SQL: SELECT ticker, company_name, sector, roe_percent, net_profit_millions, revenue_millions FROM company_financials WHERE is_latest = TRUE AND is_annual = TRUE AND profit_status = 'Profit' ORDER BY roe_percent DESC NULLS LAST LIMIT 20;

Question: "Top 10 companies by ROE in 2024"
SQL: SELECT ticker, company_name, sector, roe_percent, net_margin_percent FROM company_financials WHERE fiscal_year = 2024 AND is_annual = TRUE AND profit_status = 'Profit' ORDER BY roe_percent DESC NULLS LAST LIMIT 10;

Question: "Show companies with excellent ROE"
SQL: SELECT ticker, company_name, sector, roe_percent, roe_status FROM company_financials WHERE is_latest = TRUE AND is_annual = TRUE AND roe_status = 'Excellent' ORDER BY roe_percent DESC;

Question: "Largest companies by revenue"
SQL: SELECT ticker, company_name, sector, revenue_millions, net_profit_millions FROM company_financials WHERE is_latest = TRUE AND is_annual = TRUE ORDER BY revenue_millions DESC NULLS LAST LIMIT 20;

Question: "Which companies are losing money?"
SQL: SELECT ticker, company_name, sector, net_profit_millions, net_margin_percent FROM company_financials WHERE is_latest = TRUE AND is_annual = TRUE AND profit_status = 'Loss' ORDER BY net_profit_millions ASC;

Question: "Companies with strong liquidity"
SQL: SELECT ticker, company_name, current_ratio, quick_ratio, liquidity_status FROM company_financials WHERE is_latest = TRUE AND is_annual = TRUE AND liquidity_status = 'Strong' ORDER BY current_ratio DESC;

Question: "Most leveraged companies"
SQL: SELECT ticker, company_name, sector, debt_to_equity_percent, leverage_status FROM company_financials WHERE is_latest = TRUE AND is_annual = TRUE ORDER BY debt_to_equity_percent DESC NULLS LAST LIMIT 20;

### Bank-Specific Queries

Question: "Show all banks with their latest Net Interest Income"
SQL: SELECT ticker, company_name, bank_type, net_interest_income_m, nim_percent, roe_percent FROM v_banks_latest WHERE is_latest = TRUE AND is_annual = TRUE ORDER BY net_interest_income_m DESC NULLS LAST;

Question: "Which banks have the highest Net Interest Margin?"
SQL: SELECT ticker, company_name, bank_type, nim_percent, net_interest_income_m, roe_percent FROM v_banks_latest WHERE is_latest = TRUE AND is_annual = TRUE ORDER BY nim_percent DESC NULLS LAST LIMIT 10;

Question: "Show Islamic banks performance"
SQL: SELECT ticker, company_name, net_interest_income_m, total_loans_m, total_deposits_m, nim_percent, roe_percent FROM v_banks_latest WHERE bank_type = 'Islamic Bank' AND is_latest = TRUE AND is_annual = TRUE ORDER BY total_assets_m DESC NULLS LAST;

Question: "Banks with the best loan to deposit ratio"
SQL: SELECT ticker, company_name, total_loans_m, total_deposits_m, loan_to_deposit_percent, nim_percent FROM v_banks_latest WHERE is_latest = TRUE AND is_annual = TRUE ORDER BY loan_to_deposit_percent DESC NULLS LAST;

Question: "Which banks have the lowest NPL ratio?"
SQL: SELECT ticker, company_name, npl_m, total_loans_m, npl_percent, capital_adequacy_percent FROM v_banks_latest WHERE is_latest = TRUE AND is_annual = TRUE AND npl_percent IS NOT NULL ORDER BY npl_percent ASC LIMIT 10;

Question: "Top banks by total assets in 2024"
SQL: SELECT ticker, company_name, bank_type, total_assets_m, total_equity_m, roe_percent FROM v_banks_latest WHERE fiscal_year = 2024 AND is_annual = TRUE ORDER BY total_assets_m DESC NULLS LAST;

Question: "Banks with highest ROE"
SQL: SELECT ticker, company_name, bank_type, roe_percent, roa_percent, net_interest_income_m, net_profit_m FROM v_banks_latest WHERE is_latest = TRUE AND is_annual = TRUE ORDER BY roe_percent DESC NULLS LAST LIMIT 10;

Question: "Compare commercial banks vs Islamic banks"
SQL: SELECT bank_type, COUNT(*) as bank_count, ROUND(AVG(nim_percent), 2) as avg_nim, ROUND(AVG(roe_percent), 2) as avg_roe, ROUND(AVG(loan_to_deposit_percent), 2) as avg_ltd_ratio FROM v_banks_latest WHERE is_latest = TRUE AND is_annual = TRUE GROUP BY bank_type ORDER BY avg_roe DESC;

### Insurance Company Queries

Question: "Show all insurance companies with Gross Written Premiums"
SQL: SELECT ticker, company_name, insurance_type, gross_written_premiums_m, net_profit_m, roe_percent FROM v_insurance_latest WHERE is_latest = TRUE AND is_annual = TRUE ORDER BY gross_written_premiums_m DESC NULLS LAST;

Question: "Which insurance companies have the best combined ratio?"
SQL: SELECT ticker, company_name, insurance_type, combined_ratio_percent, loss_ratio_percent, expense_ratio_percent FROM v_insurance_latest WHERE is_latest = TRUE AND is_annual = TRUE AND combined_ratio_percent IS NOT NULL ORDER BY combined_ratio_percent ASC LIMIT 10;

Question: "Insurance companies with the highest claims"
SQL: SELECT ticker, company_name, insurance_type, claims_incurred_m, net_earned_premiums_m, loss_ratio_percent FROM v_insurance_latest WHERE is_latest = TRUE AND is_annual = TRUE ORDER BY claims_incurred_m DESC NULLS LAST LIMIT 10;

Question: "Show Takaful insurance performance"
SQL: SELECT ticker, company_name, gross_written_premiums_m, claims_incurred_m, net_profit_m, combined_ratio_percent, roe_percent FROM v_insurance_latest WHERE insurance_type = 'Takaful (Islamic Insurance)' AND is_latest = TRUE AND is_annual = TRUE ORDER BY gross_written_premiums_m DESC NULLS LAST;

Question: "Insurance companies with best ROE in 2024"
SQL: SELECT ticker, company_name, insurance_type, roe_percent, roa_percent, gross_written_premiums_m, net_profit_m FROM v_insurance_latest WHERE fiscal_year = 2024 AND is_annual = TRUE ORDER BY roe_percent DESC NULLS LAST;

Question: "Compare insurance types by profitability"
SQL: SELECT insurance_type, COUNT(*) as company_count, ROUND(AVG(combined_ratio_percent), 2) as avg_combined_ratio, ROUND(AVG(roe_percent), 2) as avg_roe, ROUND(AVG(loss_ratio_percent), 2) as avg_loss_ratio FROM v_insurance_latest WHERE is_latest = TRUE AND is_annual = TRUE GROUP BY insurance_type ORDER BY avg_roe DESC NULLS LAST;

### 2024-Specific Queries

Question: "All companies with 2024 annual data"
SQL: SELECT ticker, company_name, company_type, sector, primary_income_m, net_profit_m, roe_percent FROM v_all_companies_2024 WHERE is_annual = TRUE ORDER BY primary_income_m DESC NULLS LAST;

Question: "Top 20 companies by revenue equivalent in 2024"
SQL: SELECT ticker, company_name, company_type, income_metric_name, primary_income_m, net_profit_m, roe_percent FROM v_all_companies_2024 WHERE is_annual = TRUE ORDER BY primary_income_m DESC NULLS LAST LIMIT 20;

Question: "Compare 2024 performance across institution types"
SQL: SELECT company_type, COUNT(*) as company_count, ROUND(AVG(primary_income_m), 2) as avg_income_m, ROUND(AVG(net_profit_m), 2) as avg_profit_m, ROUND(AVG(roe_percent), 2) as avg_roe FROM v_all_companies_2024 WHERE is_annual = TRUE GROUP BY company_type ORDER BY avg_roe DESC NULLS LAST;

Question: "2024 banks vs insurance companies performance"
SQL: SELECT company_type, COUNT(*) as companies, ROUND(SUM(primary_income_m), 2) as total_income, ROUND(SUM(net_profit_m), 2) as total_profit, ROUND(AVG(roe_percent), 2) as avg_roe FROM v_all_companies_2024 WHERE company_type IN ('Commercial Bank', 'Insurance Company') AND is_annual = TRUE GROUP BY company_type;

### Sector Analysis Queries

Question: "What is the total revenue by sector?"
SQL: SELECT sector, COUNT(DISTINCT ticker) as companies, SUM(revenue_millions) as total_revenue_millions, AVG(roe_percent) as avg_roe_percent FROM company_financials WHERE is_latest = TRUE AND is_annual = TRUE GROUP BY sector ORDER BY total_revenue_millions DESC NULLS LAST;

Question: "Insurance sector performance"
SQL: SELECT ticker, company_name, revenue_millions, net_profit_millions, roe_percent, net_margin_percent, profit_status FROM company_financials WHERE sector = 'Insurance' AND is_latest = TRUE AND is_annual = TRUE ORDER BY revenue_millions DESC NULLS LAST;

Question: "Compare sectors by profitability"
SQL: SELECT sector, COUNT(DISTINCT ticker) as company_count, AVG(roe_percent) as avg_roe, AVG(net_margin_percent) as avg_net_margin, SUM(CASE WHEN profit_status = 'Profit' THEN 1 ELSE 0 END) as profitable_companies FROM company_financials WHERE is_latest = TRUE AND is_annual = TRUE GROUP BY sector ORDER BY avg_roe DESC NULLS LAST;

Question: "Year over year summary"
SQL: SELECT fiscal_year, COUNT(DISTINCT ticker) as companies_reporting, ROUND(SUM(revenue_millions)::numeric, 2) as total_revenue_m, ROUND(SUM(net_profit_millions)::numeric, 2) as total_profit_m, ROUND(AVG(roe_percent)::numeric, 2) as avg_roe_pct FROM company_financials WHERE is_annual = TRUE GROUP BY fiscal_year ORDER BY fiscal_year;

### Industrial/Standard Company Queries

Question: "Show industrial companies with highest gross margin"
SQL: SELECT ticker, company_name, sector, gross_margin_percent, operating_margin_percent, net_margin_percent, roe_percent FROM v_industrial_latest WHERE is_latest = TRUE AND is_annual = TRUE AND gross_margin_percent IS NOT NULL ORDER BY gross_margin_percent DESC LIMIT 20;

Question: "Industrial companies with best operating efficiency"
SQL: SELECT ticker, company_name, sector, revenue_m, operating_profit_m, operating_margin_percent, roe_percent FROM v_industrial_latest WHERE is_latest = TRUE AND is_annual = TRUE ORDER BY operating_margin_percent DESC NULLS LAST LIMIT 10;
"""

    def _build_system_prompt(self) -> str:
        """Build the system prompt for SQL generation."""
        return f"""You are a SQL expert for the TASI (Saudi Stock Exchange) financial database.
Your task is to convert natural language questions into PostgreSQL queries.

## Database Schema
{self.schema}

## Available Views
1. **company_financials** (Main view): All companies with unified metrics
2. **v_banks_latest**: Bank-specific view with Net Interest Income, NIM, loan/deposit ratios
3. **v_insurance_latest**: Insurance-specific view with GWP, claims, combined ratio
4. **v_industrial_latest**: Standard companies with revenue, gross profit, operating profit
5. **v_all_companies_2024**: All companies with 2024 data using appropriate revenue metrics

## Key Information
- All monetary values are in MILLIONS of Saudi Riyals (SAR)
- All ratios (roe_percent, net_margin_percent, etc.) are expressed as percentages (e.g., 15 means 15%)
- Use `is_latest = TRUE` to get the most recent data for each company
- Use `is_annual = TRUE` to filter for annual (full-year) data only

## Company Types & Their Metrics
- **BANKS**: Use Net Interest Income (not revenue), NIM, loan/deposit ratios, NPL ratio
  - Views: v_banks_latest or company_financials (filter by institution_type = 'Commercial Bank')
  - Key columns: net_interest_income_millions, nim_percent, loan_to_deposit_percent, npl_percent

- **INSURANCE**: Use Gross Written Premiums (not revenue), loss ratio, combined ratio
  - Views: v_insurance_latest or company_financials (filter by institution_type = 'Insurance Company')
  - Key columns: gross_written_premiums_millions, loss_ratio_percent, combined_ratio_percent

- **STANDARD/INDUSTRIAL**: Use revenue, gross profit, operating profit
  - Views: v_industrial_latest or company_financials
  - Key columns: revenue_millions, gross_margin_percent, operating_margin_percent

## Status Classifications
- profit_status: 'Profit', 'Loss', 'N/A'
- liquidity_status: 'Strong', 'Moderate', 'Weak', 'Critical'
- leverage_status: 'Low', 'Moderate', 'High', 'Critical'
- roe_status: 'Excellent', 'Good', 'Average', 'Weak', 'Negative', 'N/A'

{self.training_examples}

## Instructions
1. Generate ONLY the SQL query, no explanations
2. Choose the appropriate view based on the question:
   - For bank-specific queries (NII, NIM, loans, deposits): use v_banks_latest
   - For insurance-specific queries (GWP, claims, combined ratio): use v_insurance_latest
   - For industrial/standard companies: use v_industrial_latest
   - For mixed queries or general comparisons: use company_financials or v_all_companies_2024
3. Use proper PostgreSQL syntax
4. Handle NULL values with NULLS LAST in ORDER BY
5. Limit results to reasonable numbers (20-50) unless asked for all
6. For "latest" or "current" data, use `is_latest = TRUE`
7. For annual comparisons, use `is_annual = TRUE`
8. For 2024-specific queries, use v_all_companies_2024 or filter by fiscal_year = 2024
"""

    def generate_sql(self, question: str) -> str:
        """Generate SQL from a natural language question."""
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": f"Generate a SQL query for: {question}"}
        ]

        response = self.llm.chat(messages, temperature=0.1, max_tokens=1000)

        # Clean the response - extract just the SQL
        sql = response.strip()

        # Remove markdown code blocks if present
        if sql.startswith("```sql"):
            sql = sql[6:]
        elif sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]

        return sql.strip()

    def ask(self, question: str) -> Dict[str, Any]:
        """
        Ask a question in natural language and get results.
        Returns both the generated SQL and the query results.
        """
        try:
            # Generate SQL
            sql = self.generate_sql(question)
            print(f"\nGenerated SQL:\n{sql}\n")

            # Execute SQL
            results = self.sql_runner.run_sql(sql)

            return {
                "question": question,
                "sql": sql,
                "results": results,
                "success": True,
                "error": None
            }
        except Exception as e:
            return {
                "question": question,
                "sql": sql if 'sql' in dir() else None,
                "results": None,
                "success": False,
                "error": str(e)
            }

    def format_results(self, results: List[Dict[str, Any]], max_rows: int = 20) -> str:
        """Format query results as a nice table."""
        if not results:
            return "No results found."

        # Get column names
        columns = list(results[0].keys())

        # Calculate column widths
        widths = {col: len(col) for col in columns}
        for row in results[:max_rows]:
            for col in columns:
                val = str(row.get(col, ''))[:50]  # Truncate long values
                widths[col] = max(widths[col], len(val))

        # Build header
        header = " | ".join(col.ljust(widths[col]) for col in columns)
        separator = "-+-".join("-" * widths[col] for col in columns)

        # Build rows
        rows = []
        for row in results[:max_rows]:
            row_str = " | ".join(
                str(row.get(col, ''))[:50].ljust(widths[col])
                for col in columns
            )
            rows.append(row_str)

        # Combine
        table = f"{header}\n{separator}\n" + "\n".join(rows)

        if len(results) > max_rows:
            table += f"\n\n... and {len(results) - max_rows} more rows"

        return table


# =============================================================================
# Streamlit App
# =============================================================================

from components.sidebar import render_sidebar, render_2024_data_status
from components.chat import (
    initialize_chat_history,
    add_to_chat_history,
    render_chat_history,
    render_chat_input,
    render_user_message,
    render_ai_response,
)
from components.example_questions import render_example_questions


def main():
    """Streamlit web app for TASI Financial Agent."""
    # Page config
    st.set_page_config(
        page_title="Venna AI - TASI Financial Analytics",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Custom CSS for Saudi theme
    st.markdown("""
        <style>
        .stApp {
            background-color: #fafafa;
        }
        .main-header {
            background: linear-gradient(135deg, #006C35 0%, #00A651 100%);
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        .main-header h1 {
            color: white;
            margin: 0;
            font-size: 1.8rem;
        }
        .main-header p {
            color: rgba(255,255,255,0.9);
            margin: 0.5rem 0 0 0;
        }
        .results-count {
            background: #D4A84B;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }
        .error-banner {
            background: #fee2e2;
            border-left: 4px solid #dc2626;
            padding: 1rem;
            border-radius: 4px;
            margin: 1rem 0;
        }
        .error-banner-title {
            color: #dc2626;
            font-weight: 600;
        }
        .error-banner-message {
            color: #7f1d1d;
        }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/Saudi_Arabia_Flag.svg/125px-Saudi_Arabia_Flag.svg.png", width=60)
        st.title("Venna AI")
        st.caption("TASI Financial Analytics")
        st.divider()
        render_2024_data_status()
        st.divider()
        st.markdown("**Settings**")
        show_sql = st.checkbox("Show SQL queries", value=True)

    # Main header
    st.markdown("""
        <div class="main-header">
            <h1>📊 TASI Financial Analytics</h1>
            <p>Ask questions about Saudi stock market companies in natural language</p>
        </div>
    """, unsafe_allow_html=True)

    # Initialize
    initialize_chat_history()

    # Initialize agent (cached)
    @st.cache_resource
    def get_agent():
        return TASIFinancialAgent()

    try:
        agent = get_agent()
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        st.stop()

    # Example questions
    selected_example = render_example_questions()

    # Chat history
    render_chat_history(show_sql=show_sql)

    # Chat input
    user_query = render_chat_input()

    # Handle example question click or chat input
    query = selected_example or user_query

    if query:
        # Add user message
        add_to_chat_history("user", query)
        render_user_message(query)

        # Get response
        with st.chat_message("ai"):
            with st.spinner("Analyzing..."):
                result = agent.ask(query)

            render_ai_response(result, show_sql=show_sql)
            add_to_chat_history("assistant", "", result)


if __name__ == "__main__":
    main()
