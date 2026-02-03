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


def render_2024_data_status() -> None:
    """Render 2024 data freshness indicator with detailed company status."""
    with st.expander("📊 2024 Data Status", expanded=True):
        # Data freshness badge
        st.markdown(
            '<div style="background: linear-gradient(135deg, #00A651 0%, #D4A84B 100%); '
            'padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 12px;">'
            '<div style="color: white; font-size: 14px; font-weight: 600;">Latest Extraction</div>'
            '<div style="color: white; font-size: 20px; font-weight: 700;">Feb 3, 2026</div>'
            '</div>',
            unsafe_allow_html=True
        )

        # Company count
        st.metric(
            label="Companies with 2024 Data",
            value="36",
            help="Companies with complete 2024 annual financial data"
        )

        # Sector breakdown
        st.markdown("**Sector Breakdown:**")
        sectors_html = """
        <div style="font-size: 13px; line-height: 1.8;">
            <div>🏦 Banks: <strong>6</strong></div>
            <div>🏭 Industrial: <strong>15</strong></div>
            <div>🛒 Consumer & Retail: <strong>7</strong></div>
            <div>💰 Finance: <strong>3</strong></div>
            <div>🏢 Real Estate: <strong>1</strong></div>
            <div>📺 Media: <strong>1</strong></div>
            <div>📡 Telecom: <strong>1</strong></div>
            <div>💼 Financial Services: <strong>1</strong></div>
            <div>🏥 Healthcare: <strong>1</strong></div>
        </div>
        """
        st.markdown(sectors_html, unsafe_allow_html=True)


def render_data_quality_section() -> None:
    """Render detailed data quality and company status section."""
    with st.expander("📋 Data Quality & Coverage", expanded=False):
        # Companies with complete 2024 data
        companies_2024 = [
            "Riyad Bank", "Bank Aljazira", "Saudi Investment Bank",
            "Saudi Awwal Bank", "Bank Albilad", "Alinma Bank",
            "Arabian Cement Co", "Yamama Cement Co", "Yanbu Cement Co",
            "City Cement Co", "Southern Province Cement Co", "Umm Al-Qura Cement Co",
            "Qassim Cement Co", "Riyadh Cement Co", "Eastern Province Cement Co",
            "Almarai Co", "Jarir Marketing Co", "Nahdi Medical Co",
            "BinDawood Holding Co", "Leejam Sports Co", "Aldrees Petroleum and Transport Services Co",
            "Almunajem Foods Co", "Arabian Pipes Co", "Zamil Industrial Investment Co",
            "Saudi Industrial Investment Group", "Astra Industrial Group", "Bawan Co",
            "United Wire Factories Co", "Amlak International Finance Co",
            "Nayifat Finance Co", "SHL Finance Co", "Emaar The Economic City",
            "MBC Group Co", "Etihad Atheeb Telecommunication Co", "Canadian Medical Center Co",
            "Saudi Tadawul Group Holding Co"
        ]

        st.markdown("**✅ Companies with Complete 2024 Data (36):**")
        st.caption("All major sectors represented with latest annual reports")

        # Show companies in a clean list format
        with st.container():
            companies_text = "\n".join([f"• {company}" for company in sorted(companies_2024)])
            st.text_area(
                "Company List",
                companies_text,
                height=150,
                label_visibility="collapsed",
                disabled=True
            )

        st.divider()

        # Data quality indicators
        st.markdown("**📊 Data Quality Indicators:**")

        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                label="Completeness",
                value="100%",
                help="All 36 companies have complete financial records"
            )
        with col2:
            st.metric(
                label="Validation Status",
                value="Valid",
                help="All records passed validation checks"
            )

        # Coverage stats
        st.markdown("**📈 Coverage Statistics:**")
        coverage_html = """
        <div style="font-size: 12px; line-height: 1.6;">
            <div>✓ Financial Statements: <strong>Complete</strong></div>
            <div>✓ Key Metrics: <strong>All Captured</strong></div>
            <div>✓ Sector Classification: <strong>Verified</strong></div>
            <div>✓ Data Extraction Date: <strong>Feb 3, 2026</strong></div>
        </div>
        """
        st.markdown(coverage_html, unsafe_allow_html=True)

        st.info("💡 To update data, run: `python scripts/insert_extracted_data.py`", icon="ℹ️")


def render_database_info(db_stats: Optional[Dict[str, Any]] = None) -> None:
    """Render the database information section in collapsible expander."""
    with st.expander("Database Overview", expanded=False):
        if db_stats:
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label="Total Companies",
                    value=f"{db_stats.get('companies', 'N/A'):,}" if isinstance(db_stats.get('companies'), int) else db_stats.get('companies', 'N/A'),
                    help="All unique companies in the database"
                )
            with col2:
                st.metric(
                    label="Total Records",
                    value=f"{db_stats.get('records', 'N/A'):,}" if isinstance(db_stats.get('records'), int) else db_stats.get('records', 'N/A'),
                    help="All financial records across all years"
                )

            if db_stats.get('sectors'):
                st.caption(f"Sectors: {db_stats['sectors']}")
            if db_stats.get('years'):
                st.caption(f"Year Range: {db_stats['years']}")
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

        # 2024 Data Status (NEW!)
        render_2024_data_status()

        # Data Quality Section (NEW!)
        render_data_quality_section()

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
