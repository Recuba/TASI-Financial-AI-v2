"""Sidebar component for Venna AI.

Provides database info, settings, column reference, and filters.
"""

import streamlit as st
from typing import Dict, Any, Optional


# Column categories for reference
COLUMN_CATEGORIES = {
    "Identifiers": [
        "ticker",
        "company_name",
        "fiscal_year",
        "fiscal_quarter",
        "period_type",
    ],
    "Financial Metrics (Millions SAR)": [
        "revenue_millions",
        "net_profit_millions",
        "total_assets_millions",
        "total_equity_millions",
    ],
    "Ratios (%)": [
        "roe_percent",
        "net_margin_percent",
        "current_ratio",
        "quick_ratio",
        "debt_to_equity_percent",
    ],
    "Categories": [
        "sector",
        "company_type",
        "size_category",
        "profit_status",
        "liquidity_status",
        "leverage_status",
        "roe_status",
    ],
    "Flags": [
        "is_latest",
        "is_annual",
    ],
}


def render_database_info(db_stats: Optional[Dict[str, Any]] = None) -> None:
    """Render the database information section in collapsible expander."""
    with st.expander("Database Info", expanded=True):
        if db_stats:
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label="Companies",
                    value=f"{db_stats.get('companies', 'N/A'):,}" if isinstance(db_stats.get('companies'), int) else db_stats.get('companies', 'N/A'),
                    help="Unique companies in the database"
                )
            with col2:
                st.metric(
                    label="Records",
                    value=f"{db_stats.get('records', 'N/A'):,}" if isinstance(db_stats.get('records'), int) else db_stats.get('records', 'N/A'),
                    help="Total financial records"
                )

            if db_stats.get('sectors'):
                st.caption(f"Sectors: {db_stats['sectors']}")
            if db_stats.get('years'):
                st.caption(f"Years: {db_stats['years']}")
        else:
            st.info("Connect to database to see stats")


def render_column_reference() -> None:
    """Render available columns grouped by category."""
    with st.expander("Column Reference", expanded=False):
        for category, columns in COLUMN_CATEGORIES.items():
            st.markdown(f"**{category}:**")
            st.code("\n".join(columns), language=None)


def render_settings() -> Dict[str, Any]:
    """Render settings section and return current settings."""
    settings = {}

    with st.expander("Settings", expanded=False):
        # Max results setting
        settings["max_results"] = st.slider(
            "Max Results",
            min_value=10,
            max_value=100,
            value=20,
            step=10,
            help="Maximum number of rows to return"
        )

        # Show SQL toggle
        settings["show_sql"] = st.checkbox(
            "Show Generated SQL",
            value=True,
            help="Display the generated SQL query"
        )

        # Auto-format numbers
        settings["format_numbers"] = st.checkbox(
            "Format Numbers",
            value=True,
            help="Format large numbers with commas"
        )

    return settings


def render_filters() -> Dict[str, Any]:
    """Render filter section and return current filters."""
    filters = {}

    with st.expander("Filters (Optional)", expanded=False):
        st.caption("Apply these filters to your queries")

        # Year filter
        current_year = 2024
        years = list(range(current_year, 2018, -1))
        filters["year"] = st.selectbox(
            "Fiscal Year",
            options=["All"] + years,
            index=0,
            help="Filter by fiscal year"
        )

        # Period type filter
        filters["period_type"] = st.selectbox(
            "Period Type",
            options=["All", "Annual", "Quarterly"],
            index=0,
            help="Filter by annual or quarterly data"
        )

        # Sector filter (common sectors)
        common_sectors = [
            "All",
            "Financials",
            "Insurance",
            "Real Estate",
            "Materials",
            "Consumer Staples",
            "Healthcare",
            "Energy",
            "Utilities",
        ]
        filters["sector"] = st.selectbox(
            "Sector",
            options=common_sectors,
            index=0,
            help="Filter by industry sector"
        )

    return filters


def render_quick_actions() -> Optional[str]:
    """Render quick action buttons and return selected action."""
    with st.expander("Quick Actions", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Clear Chat", use_container_width=True, type="secondary"):
                return "clear_chat"

        with col2:
            if st.button("Reset Filters", use_container_width=True, type="secondary"):
                return "reset_filters"

    return None


def render_connection_status(is_connected: bool = False, error: str = None) -> None:
    """Render database connection status."""
    if is_connected:
        st.success("Database Connected", icon=":material/check_circle:")
    else:
        st.error("Database Disconnected", icon=":material/error:")
        if error:
            st.caption(f"Error: {error}")


def render_sidebar(
    db_stats: Optional[Dict[str, Any]] = None,
    is_connected: bool = False,
    connection_error: str = None
) -> Dict[str, Any]:
    """Render the complete sidebar.

    Args:
        db_stats: Database statistics dictionary
        is_connected: Whether database is connected
        connection_error: Connection error message if any

    Returns:
        Dictionary containing all sidebar state (settings, filters, actions)
    """
    sidebar_state = {
        "settings": {},
        "filters": {},
        "action": None,
    }

    with st.sidebar:
        # Logo/Brand
        st.markdown(
            '<h2 style="text-align: center; color: #00A651;">Venna AI</h2>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<p style="text-align: center; color: #D4A84B; font-size: 14px;">TASI Financial Analytics</p>',
            unsafe_allow_html=True
        )

        st.divider()

        # Connection status
        render_connection_status(is_connected, connection_error)

        st.divider()

        # Database info
        render_database_info(db_stats)

        # Settings
        sidebar_state["settings"] = render_settings()

        # Filters
        sidebar_state["filters"] = render_filters()

        # Column reference
        render_column_reference()

        # Quick actions
        sidebar_state["action"] = render_quick_actions()

        # Footer
        st.divider()
        st.caption("Powered by Gemini Flash 2.5")
        st.caption("PostgreSQL + OpenRouter")

    return sidebar_state
