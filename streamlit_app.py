"""
Venna AI - Saudi TASI Financial Analytics Platform
===================================================
A Streamlit app for natural language querying of TASI financial data.
Powered by Gemini Flash 2.5 via OpenRouter + PostgreSQL.
"""

import streamlit as st

# --- PAGE CONFIG (must be first Streamlit command) ---
st.set_page_config(
    page_title="Venna AI | TASI Financial Analytics",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- IMPORTS ---
import os
import sys
import io
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- APPLY STYLES ---
from styles.css import get_base_css, get_error_css
st.markdown(get_base_css(), unsafe_allow_html=True)
st.markdown(get_error_css(), unsafe_allow_html=True)

# --- IMPORT COMPONENTS ---
from components.chat import (
    render_chat_input,
    render_chat_history,
    render_ai_response,
    add_to_chat_history,
    get_chat_history,
    clear_chat_history,
    initialize_chat_history,
)
from components.sidebar import render_sidebar
from components.example_questions import render_example_questions

# --- IMPORT AGENT ---
from vanna_app import TASIFinancialAgent, PostgresRunner


# =============================================================================
# Database Functions
# =============================================================================

@st.cache_resource
def get_agent() -> TASIFinancialAgent:
    """Get or create the TASI Financial Agent (cached)."""
    return TASIFinancialAgent()


@st.cache_data(ttl=300)
def get_database_stats(_agent: TASIFinancialAgent) -> Dict[str, Any]:
    """Get database statistics.

    Args:
        _agent: The TASIFinancialAgent instance (underscore prefix for caching)

    Returns:
        Dictionary with database stats
    """
    try:
        # Get company count
        companies_result = _agent.sql_runner.run_sql(
            "SELECT COUNT(DISTINCT ticker) as count FROM company_financials"
        )
        companies = companies_result[0]['count'] if companies_result else 0

        # Get total records
        records_result = _agent.sql_runner.run_sql(
            "SELECT COUNT(*) as count FROM company_financials"
        )
        records = records_result[0]['count'] if records_result else 0

        # Get sectors count
        sectors_result = _agent.sql_runner.run_sql(
            "SELECT COUNT(DISTINCT sector) as count FROM company_financials"
        )
        sectors = sectors_result[0]['count'] if sectors_result else 0

        # Get year range
        years_result = _agent.sql_runner.run_sql(
            "SELECT MIN(fiscal_year) as min_year, MAX(fiscal_year) as max_year FROM company_financials"
        )
        if years_result:
            years = f"{years_result[0]['min_year']} - {years_result[0]['max_year']}"
        else:
            years = "N/A"

        return {
            "companies": companies,
            "records": records,
            "sectors": sectors,
            "years": years,
        }
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {
            "companies": "Error",
            "records": "Error",
            "sectors": "Error",
            "years": "Error",
        }


def check_database_connection(agent: TASIFinancialAgent) -> tuple[bool, Optional[str]]:
    """Check if database is connected.

    Args:
        agent: The TASIFinancialAgent instance

    Returns:
        Tuple of (is_connected, error_message)
    """
    try:
        agent.sql_runner.run_sql("SELECT 1")
        return True, None
    except Exception as e:
        return False, str(e)


def process_query(agent: TASIFinancialAgent, question: str) -> Dict[str, Any]:
    """Process a natural language query.

    Args:
        agent: The TASIFinancialAgent instance
        question: The user's question

    Returns:
        Response dictionary with results
    """
    return agent.ask(question)


# =============================================================================
# Data Preview Component
# =============================================================================

def render_data_preview(agent: TASIFinancialAgent, expanded: bool = False, max_rows: int = 5) -> None:
    """Render a preview of the data.

    Args:
        agent: The TASIFinancialAgent instance
        expanded: Whether to expand the preview by default
        max_rows: Maximum rows to show in preview
    """
    with st.expander("Data Preview", expanded=expanded):
        try:
            # Get sample data
            preview_result = agent.sql_runner.run_sql(f"""
                SELECT ticker, company_name, sector, fiscal_year,
                       revenue_millions, net_profit_millions, roe_percent, profit_status
                FROM company_financials
                WHERE is_latest = TRUE AND is_annual = TRUE
                ORDER BY revenue_millions DESC NULLS LAST
                LIMIT {max_rows}
            """)

            if preview_result:
                import pandas as pd
                df = pd.DataFrame(preview_result)
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.caption(f"Showing top {max_rows} companies by revenue (latest annual data)")
            else:
                st.info("No preview data available")
        except Exception as e:
            st.error(f"Error loading preview: {e}")


# =============================================================================
# Initialize Session State
# =============================================================================

def initialize_session() -> None:
    """Initialize all session state variables."""
    initialize_chat_history()

    if "query" not in st.session_state:
        st.session_state.query = None

    if "last_query" not in st.session_state:
        st.session_state.last_query = None

    if "db_connected" not in st.session_state:
        st.session_state.db_connected = False

    if "connection_error" not in st.session_state:
        st.session_state.connection_error = None


# =============================================================================
# Main Application
# =============================================================================

def main():
    """Main application entry point."""

    # Initialize session
    initialize_session()

    # Initialize agent
    try:
        agent = get_agent()
        is_connected, connection_error = check_database_connection(agent)
        st.session_state.db_connected = is_connected
        st.session_state.connection_error = connection_error
    except Exception as e:
        logger.error(f"Error initializing agent: {e}")
        is_connected = False
        connection_error = str(e)
        agent = None

    # Get database stats if connected
    db_stats = None
    if is_connected and agent:
        db_stats = get_database_stats(agent)

    # --- SIDEBAR ---
    sidebar_state = render_sidebar(
        db_stats=db_stats,
        is_connected=is_connected,
        connection_error=connection_error
    )

    # Handle sidebar actions
    if sidebar_state["action"] == "clear_chat":
        clear_chat_history()
        st.rerun()

    # --- HEADER ---
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.markdown(
            '<h1 class="brand-title">Venna AI</h1>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<p class="brand-subtitle">TASI Financial Analytics | Saudi Stock Exchange</p>',
            unsafe_allow_html=True
        )

    st.divider()

    # --- MAIN CONTENT ---
    if not is_connected:
        st.error("Could not connect to database. Please check your connection settings.")
        if connection_error:
            with st.expander("Error Details"):
                st.code(connection_error)

        st.info("""
        **Connection Settings:**
        - Host: localhost
        - Port: 5433
        - Database: tasi_financials
        - User: tasi

        Make sure PostgreSQL is running and the database exists.
        """)
        return

    # Data preview
    render_data_preview(agent, expanded=True, max_rows=5)

    # Example questions
    example_query = render_example_questions(max_visible=3)
    if example_query:
        st.session_state.query = example_query

    # Render chat history
    show_sql = sidebar_state["settings"].get("show_sql", True)
    render_chat_history(show_sql=show_sql)

    # Clear history button if there's history
    if get_chat_history():
        col1, col2, col3 = st.columns([6, 1, 1])
        with col3:
            if st.button("Clear", key="clear_btn", type="secondary"):
                clear_chat_history()
                st.rerun()

    st.divider()

    # Chat input
    prompt = render_chat_input()

    # Check for button-triggered query (from example questions)
    if "query" in st.session_state and st.session_state.query:
        prompt = st.session_state.query
        st.session_state.query = None

    # Process query
    if prompt:
        st.session_state.last_query = prompt

        # Add user message to history
        add_to_chat_history("user", prompt)

        # Process with AI
        with st.chat_message("ai"):
            with st.spinner("Analyzing your question..."):
                response = process_query(agent, prompt)

            # Add response to history
            add_to_chat_history("assistant", "", response)

            # Render response
            if response["success"]:
                render_ai_response(response, show_sql=show_sql)
            else:
                render_ai_response(response, show_sql=show_sql)

                # Retry button
                if st.button("Retry Query", key="retry_query"):
                    st.session_state.query = prompt
                    st.rerun()

    # --- FOOTER ---
    st.divider()
    st.caption("Venna AI | Powered by Gemini Flash 2.5 + PostgreSQL | Saudi Exchange TASI Data")


if __name__ == "__main__":
    main()
