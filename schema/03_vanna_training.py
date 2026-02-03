"""
Vanna AI Training Script for TASI Financial Database
Teaches Vanna to understand the schema and generate accurate SQL queries
"""

import vanna
from vanna.remote import VannaDefault
import os

# Configuration
VANNA_MODEL = os.getenv("VANNA_MODEL", "tasi-financials")
VANNA_API_KEY = os.getenv("VANNA_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/tasi_financials")


def get_vanna_instance():
    """Initialize Vanna AI with your configuration."""
    # Option 1: Use Vanna's hosted service
    vn = VannaDefault(model=VANNA_MODEL, api_key=VANNA_API_KEY)

    # Connect to database
    vn.connect_to_postgres(url=DATABASE_URL)

    return vn


def train_ddl(vn):
    """Train Vanna on the database schema (DDL)."""
    print("Training on DDL (schema definitions)...")

    # Core tables DDL
    vn.train(ddl="""
    -- Companies table: Master list of TASI-listed Saudi companies
    CREATE TABLE companies (
        company_id SERIAL PRIMARY KEY,
        ticker VARCHAR(10) UNIQUE NOT NULL,  -- Saudi exchange ticker symbol
        company_name VARCHAR(200) NOT NULL,  -- Full company name in English
        sector_id INTEGER REFERENCES sectors(sector_id),
        company_type VARCHAR(50),  -- 'Industrial', 'Service', etc.
        size_category VARCHAR(20)  -- 'Small Cap', 'Mid Cap', 'Large Cap'
    );
    """)

    vn.train(ddl="""
    -- Sectors table: Industry sector classifications
    CREATE TABLE sectors (
        sector_id SERIAL PRIMARY KEY,
        sector_name VARCHAR(100) NOT NULL  -- e.g., 'Real Estate', 'Industrial', 'Banking'
    );
    """)

    vn.train(ddl="""
    -- Fiscal periods: Quarterly and annual reporting periods
    CREATE TABLE fiscal_periods (
        period_id SERIAL PRIMARY KEY,
        fiscal_year SMALLINT NOT NULL,  -- e.g., 2024
        fiscal_quarter VARCHAR(5) NOT NULL,  -- 'Q1', 'Q2', 'Q3', 'Q4', 'FY'
        period_type VARCHAR(10) NOT NULL,  -- 'Quarterly' or 'Annual'
        period_end DATE NOT NULL
    );
    """)

    vn.train(ddl="""
    -- Financial statements: Core financial data
    CREATE TABLE financial_statements (
        statement_id SERIAL PRIMARY KEY,
        company_id INTEGER REFERENCES companies(company_id),
        period_id INTEGER REFERENCES fiscal_periods(period_id),

        -- Income Statement (values in Saudi Riyals - SAR)
        revenue NUMERIC(20,2),  -- Total revenue
        cost_of_sales NUMERIC(20,2),  -- Cost of goods sold
        gross_profit NUMERIC(20,2),
        operating_profit NUMERIC(20,2),
        net_profit NUMERIC(20,2),  -- Net income after tax

        -- Balance Sheet (values in SAR)
        total_assets NUMERIC(20,2),
        total_equity NUMERIC(20,2),  -- Shareholders equity
        total_liabilities NUMERIC(20,2),
        current_assets NUMERIC(20,2),
        current_liabilities NUMERIC(20,2),

        -- Cash Flow (values in SAR)
        operating_cash_flow NUMERIC(20,2),
        free_cash_flow NUMERIC(20,2),

        is_latest BOOLEAN  -- TRUE for most recent filing
    );
    """)

    vn.train(ddl="""
    -- Financial metrics: Calculated ratios and performance indicators
    CREATE TABLE financial_metrics (
        metric_id SERIAL PRIMARY KEY,
        statement_id INTEGER REFERENCES financial_statements(statement_id),

        -- Profitability ratios (as decimals: 0.15 = 15%)
        return_on_equity NUMERIC(10,6),  -- ROE
        return_on_assets NUMERIC(10,6),  -- ROA
        gross_margin NUMERIC(10,6),
        operating_margin NUMERIC(10,6),
        net_margin NUMERIC(10,6),

        -- Liquidity ratios
        current_ratio NUMERIC(10,4),
        quick_ratio NUMERIC(10,4),

        -- Leverage ratios
        debt_to_equity NUMERIC(10,6),

        -- Performance classifications
        profit_status VARCHAR(10),  -- 'Profit', 'Loss', 'N/A'
        roe_status VARCHAR(15)  -- 'Excellent', 'Good', 'Average', 'Weak', 'Negative'
    );
    """)

    vn.train(ddl="""
    -- company_financials: Pre-joined view for easy querying
    -- All monetary values are in MILLIONS of Saudi Riyals
    -- All ratios are expressed as PERCENTAGES (15 = 15%)
    CREATE MATERIALIZED VIEW company_financials AS
    SELECT
        ticker,  -- Company ticker symbol
        company_name,
        company_type,
        size_category,
        sector,  -- Industry sector

        fiscal_year,
        fiscal_quarter,  -- 'Q1', 'Q2', 'Q3', 'Q4', or 'FY' for annual
        period_type,  -- 'Quarterly' or 'Annual'
        period_end,

        -- Financials in millions SAR
        revenue_millions,
        gross_profit_millions,
        operating_profit_millions,
        net_profit_millions,
        total_assets_millions,
        total_equity_millions,

        -- Ratios as percentages
        roe_percent,  -- Return on equity
        roa_percent,  -- Return on assets
        gross_margin_percent,
        operating_margin_percent,
        net_margin_percent,
        debt_to_equity_percent,

        current_ratio,
        quick_ratio,

        -- Status classifications
        profit_status,  -- 'Profit' or 'Loss'
        liquidity_status,  -- 'Strong', 'Moderate', 'Weak'
        leverage_status,  -- 'Low', 'Moderate', 'High'
        roe_status,  -- 'Excellent', 'Good', 'Average', 'Weak', 'Negative'

        is_latest,  -- TRUE for most recent data
        is_annual  -- TRUE for annual (FY) data
    FROM financial_statements fs
    JOIN companies c ON fs.company_id = c.company_id
    JOIN fiscal_periods fp ON fs.period_id = fp.period_id
    LEFT JOIN sectors s ON c.sector_id = s.sector_id
    LEFT JOIN financial_metrics fm ON fs.statement_id = fm.statement_id;
    """)


def train_documentation(vn):
    """Train Vanna on domain-specific documentation."""
    print("Training on documentation...")

    # General overview
    vn.train(documentation="""
    This database contains financial data for companies listed on TASI (Tadawul All Share Index),
    the main stock market index of the Saudi Exchange. Data includes:

    - Quarterly and annual financial statements from 2020 to 2025
    - Income statement, balance sheet, and cash flow data
    - Calculated financial ratios and performance metrics
    - Company information including sector and size classification

    Key facts:
    - All monetary values in the raw tables are in Saudi Riyals (SAR)
    - The company_financials view shows values in MILLIONS of SAR
    - Ratios in the metrics table are decimals (0.15 = 15%)
    - Ratios in company_financials are percentages (15 = 15%)
    - Use is_annual = TRUE to filter for annual (full-year) data
    - Use is_latest = TRUE to get the most recent data for each company
    """)

    # Terminology
    vn.train(documentation="""
    Common terminology translations:

    Saudi/Arabic terms:
    - TASI = Tadawul All Share Index (Saudi main stock index)
    - SAR = Saudi Riyal (currency)
    - Tadawul = Saudi Stock Exchange

    Financial terms:
    - ROE = Return on Equity = Net Profit / Shareholders Equity
    - ROA = Return on Assets = Net Profit / Total Assets
    - Gross Margin = Gross Profit / Revenue
    - Net Margin = Net Profit / Revenue
    - Current Ratio = Current Assets / Current Liabilities
    - Quick Ratio = (Current Assets - Inventory) / Current Liabilities
    - D/E = Debt to Equity Ratio = Total Liabilities / Total Equity
    """)

    # Status classifications
    vn.train(documentation="""
    Performance status classifications:

    ROE Status:
    - Excellent: ROE > 20%
    - Good: ROE 15-20%
    - Average: ROE 10-15%
    - Weak: ROE 0-10%
    - Negative: ROE < 0%

    Liquidity Status (based on current ratio):
    - Strong: Current ratio >= 2
    - Moderate: Current ratio 1-2
    - Weak: Current ratio 0.5-1
    - Critical: Current ratio < 0.5

    Leverage Status (based on debt-to-equity):
    - Low: D/E < 0.5
    - Moderate: D/E 0.5-1.5
    - High: D/E > 1.5

    Size Categories:
    - Small Cap: Small market capitalization companies
    - Mid Cap: Medium market capitalization
    - Large Cap: Large market capitalization
    """)


def train_example_queries(vn):
    """Train Vanna on example question-SQL pairs."""
    print("Training on example queries...")

    # Basic queries
    vn.train(question="Show all companies", sql="""
    SELECT ticker, company_name, sector, company_type, size_category
    FROM company_financials
    WHERE is_latest = TRUE
    GROUP BY ticker, company_name, sector, company_type, size_category
    ORDER BY company_name;
    """)

    vn.train(question="List all sectors", sql="""
    SELECT DISTINCT sector
    FROM company_financials
    WHERE sector IS NOT NULL
    ORDER BY sector;
    """)

    # Profitability queries
    vn.train(question="Which companies are most profitable?", sql="""
    SELECT ticker, company_name, sector, roe_percent, net_profit_millions, revenue_millions
    FROM company_financials
    WHERE is_latest = TRUE AND is_annual = TRUE AND profit_status = 'Profit'
    ORDER BY roe_percent DESC NULLS LAST
    LIMIT 20;
    """)

    vn.train(question="Top 10 companies by ROE in 2024", sql="""
    SELECT ticker, company_name, sector, roe_percent, net_margin_percent
    FROM company_financials
    WHERE fiscal_year = 2024 AND is_annual = TRUE AND profit_status = 'Profit'
    ORDER BY roe_percent DESC NULLS LAST
    LIMIT 10;
    """)

    vn.train(question="Show companies with excellent ROE", sql="""
    SELECT ticker, company_name, sector, roe_percent, roe_status
    FROM company_financials
    WHERE is_latest = TRUE AND is_annual = TRUE AND roe_status = 'Excellent'
    ORDER BY roe_percent DESC;
    """)

    # Revenue and size queries
    vn.train(question="Largest companies by revenue", sql="""
    SELECT ticker, company_name, sector, revenue_millions, net_profit_millions
    FROM company_financials
    WHERE is_latest = TRUE AND is_annual = TRUE
    ORDER BY revenue_millions DESC NULLS LAST
    LIMIT 20;
    """)

    vn.train(question="What is the total revenue by sector?", sql="""
    SELECT sector, COUNT(DISTINCT ticker) as companies,
           SUM(revenue_millions) as total_revenue_millions,
           AVG(roe_percent) as avg_roe_percent
    FROM company_financials
    WHERE is_latest = TRUE AND is_annual = TRUE
    GROUP BY sector
    ORDER BY total_revenue_millions DESC NULLS LAST;
    """)

    # Loss-making companies
    vn.train(question="Which companies are losing money?", sql="""
    SELECT ticker, company_name, sector, net_profit_millions, net_margin_percent
    FROM company_financials
    WHERE is_latest = TRUE AND is_annual = TRUE AND profit_status = 'Loss'
    ORDER BY net_profit_millions ASC;
    """)

    # Liquidity queries
    vn.train(question="Companies with strong liquidity", sql="""
    SELECT ticker, company_name, current_ratio, quick_ratio, liquidity_status
    FROM company_financials
    WHERE is_latest = TRUE AND is_annual = TRUE AND liquidity_status = 'Strong'
    ORDER BY current_ratio DESC;
    """)

    vn.train(question="Show companies with weak liquidity", sql="""
    SELECT ticker, company_name, sector, current_ratio, quick_ratio, liquidity_status
    FROM company_financials
    WHERE is_latest = TRUE AND is_annual = TRUE
      AND (liquidity_status = 'Weak' OR liquidity_status = 'Critical')
    ORDER BY current_ratio ASC;
    """)

    # Leverage queries
    vn.train(question="Most leveraged companies", sql="""
    SELECT ticker, company_name, sector, debt_to_equity_percent, leverage_status
    FROM company_financials
    WHERE is_latest = TRUE AND is_annual = TRUE
    ORDER BY debt_to_equity_percent DESC NULLS LAST
    LIMIT 20;
    """)

    vn.train(question="Low debt companies", sql="""
    SELECT ticker, company_name, sector, debt_to_equity_percent, leverage_status
    FROM company_financials
    WHERE is_latest = TRUE AND is_annual = TRUE AND leverage_status = 'Low'
    ORDER BY debt_to_equity_percent ASC NULLS LAST;
    """)

    # Specific company queries
    vn.train(question="Show financial data for company 9541", sql="""
    SELECT ticker, company_name, fiscal_year, fiscal_quarter,
           revenue_millions, net_profit_millions, roe_percent, net_margin_percent
    FROM company_financials
    WHERE ticker = '9541'
    ORDER BY fiscal_year DESC, fiscal_quarter DESC;
    """)

    vn.train(question="Academy of Learning financials", sql="""
    SELECT fiscal_year, fiscal_quarter, period_type,
           revenue_millions, net_profit_millions, roe_percent, profit_status
    FROM company_financials
    WHERE company_name ILIKE '%Academy of Learning%'
    ORDER BY fiscal_year DESC, fiscal_quarter DESC;
    """)

    # Sector analysis
    vn.train(question="Real estate sector performance", sql="""
    SELECT ticker, company_name, revenue_millions, net_profit_millions,
           roe_percent, net_margin_percent, profit_status
    FROM company_financials
    WHERE sector = 'Real Estate' AND is_latest = TRUE AND is_annual = TRUE
    ORDER BY revenue_millions DESC NULLS LAST;
    """)

    vn.train(question="Compare sectors by profitability", sql="""
    SELECT sector,
           COUNT(DISTINCT ticker) as company_count,
           AVG(roe_percent) as avg_roe,
           AVG(net_margin_percent) as avg_net_margin,
           SUM(CASE WHEN profit_status = 'Profit' THEN 1 ELSE 0 END) as profitable_companies,
           SUM(CASE WHEN profit_status = 'Loss' THEN 1 ELSE 0 END) as loss_making_companies
    FROM company_financials
    WHERE is_latest = TRUE AND is_annual = TRUE
    GROUP BY sector
    ORDER BY avg_roe DESC NULLS LAST;
    """)

    # Time series queries
    vn.train(question="Revenue trend for company 4191", sql="""
    SELECT fiscal_year, fiscal_quarter, period_type,
           revenue_millions, net_profit_millions
    FROM company_financials
    WHERE ticker = '4191' AND is_annual = TRUE
    ORDER BY fiscal_year;
    """)

    vn.train(question="How has the banking sector performed over time?", sql="""
    SELECT fiscal_year,
           COUNT(DISTINCT ticker) as companies,
           SUM(revenue_millions) as total_revenue,
           SUM(net_profit_millions) as total_profit,
           AVG(roe_percent) as avg_roe
    FROM company_financials
    WHERE sector = 'Banking' AND is_annual = TRUE
    GROUP BY fiscal_year
    ORDER BY fiscal_year;
    """)

    # Comparison queries
    vn.train(question="Compare small cap vs large cap companies", sql="""
    SELECT size_category,
           COUNT(DISTINCT ticker) as companies,
           AVG(revenue_millions) as avg_revenue,
           AVG(roe_percent) as avg_roe,
           AVG(net_margin_percent) as avg_net_margin
    FROM company_financials
    WHERE is_latest = TRUE AND is_annual = TRUE
    GROUP BY size_category
    ORDER BY avg_revenue DESC;
    """)

    # Growth queries
    vn.train(question="Companies with revenue growth", sql="""
    WITH yearly AS (
        SELECT ticker, company_name, fiscal_year, revenue_millions
        FROM company_financials
        WHERE is_annual = TRUE AND revenue_millions > 0
    ),
    growth AS (
        SELECT
            y2.ticker, y2.company_name,
            y1.revenue_millions as prev_revenue,
            y2.revenue_millions as curr_revenue,
            ((y2.revenue_millions - y1.revenue_millions) / y1.revenue_millions * 100) as growth_pct
        FROM yearly y2
        JOIN yearly y1 ON y2.ticker = y1.ticker AND y2.fiscal_year = y1.fiscal_year + 1
        WHERE y2.fiscal_year = 2024
    )
    SELECT * FROM growth
    WHERE growth_pct > 0
    ORDER BY growth_pct DESC
    LIMIT 20;
    """)


def main():
    """Run the full training pipeline."""
    print("=" * 60)
    print("Vanna AI Training for TASI Financial Database")
    print("=" * 60)

    vn = get_vanna_instance()

    # Train on schema
    train_ddl(vn)

    # Train on documentation
    train_documentation(vn)

    # Train on example queries
    train_example_queries(vn)

    print("\nTraining complete!")
    print("\nTest the model with:")
    print('  vn.ask("Show me the top 10 most profitable companies")')


if __name__ == "__main__":
    main()
