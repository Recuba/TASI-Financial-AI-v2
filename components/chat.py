"""Chat interface component for Venna AI.

Provides chat input, message display, and response handling with export functionality.
"""

import hashlib
import io
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st
import pandas as pd


def _get_response_key(response_data: Dict[str, Any]) -> str:
    """Generate a stable key from response data.

    Uses a hash of the content to ensure consistent keys across Streamlit reruns.

    Args:
        response_data: Response dictionary

    Returns:
        8-character hex string suitable for widget keys
    """
    content = str(response_data.get("sql", "")) + str(len(response_data.get("results", [])))
    return hashlib.md5(content.encode()).hexdigest()[:8]


def initialize_chat_history() -> None:
    """Initialize the chat history in session state."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def add_to_chat_history(role: str, content: Any, response_data: Optional[Dict[str, Any]] = None) -> None:
    """Add a message to the chat history.

    Args:
        role: The role ("user" or "assistant")
        content: The message content
        response_data: Optional response data for assistant messages
    """
    initialize_chat_history()

    entry = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
    }

    if response_data is not None:
        entry["response_data"] = response_data

    st.session_state.chat_history.append(entry)


def get_chat_history() -> list:
    """Get the current chat history.

    Returns:
        List of chat history entries
    """
    initialize_chat_history()
    return st.session_state.chat_history


def clear_chat_history() -> None:
    """Clear the chat history."""
    st.session_state.chat_history = []


def render_chat_input(placeholder: str = "Ask a question about TASI financial data...") -> Optional[str]:
    """Render the chat input with keyboard hints.

    Args:
        placeholder: Placeholder text for the input

    Returns:
        User's query or None
    """
    st.markdown(
        '<p style="text-align: right; color: var(--text-muted); font-size: 12px; margin-bottom: 4px;">'
        '<span class="kbd-hint">Enter</span> to send'
        '</p>',
        unsafe_allow_html=True
    )

    return st.chat_input(placeholder)


def render_user_message(query: str) -> None:
    """Render a user's message in the chat.

    Args:
        query: The user's query string
    """
    with st.chat_message("human"):
        st.write(query)


def export_to_csv(df: pd.DataFrame) -> str:
    """Export DataFrame to CSV string.

    Args:
        df: DataFrame to export

    Returns:
        CSV string
    """
    return df.to_csv(index=False)


def export_to_excel(df: pd.DataFrame) -> bytes:
    """Export DataFrame to Excel bytes.

    Args:
        df: DataFrame to export

    Returns:
        Excel file bytes
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Results')
    return output.getvalue()


def generate_export_filename(prefix: str, extension: str) -> str:
    """Generate a filename for exports.

    Args:
        prefix: Filename prefix
        extension: File extension

    Returns:
        Generated filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def render_export_buttons(df: pd.DataFrame, response_key: str) -> None:
    """Render export buttons for a DataFrame.

    Args:
        df: DataFrame to export
        response_key: Unique key for the response
    """
    col1, col2, col3 = st.columns([2, 1, 1])

    with col2:
        csv_data = export_to_csv(df)
        st.download_button(
            label=":material/download: CSV",
            data=csv_data,
            file_name=generate_export_filename("tasi_data", "csv"),
            mime="text/csv",
            key=f"export_csv_{response_key}",
            help="Download as CSV"
        )

    with col3:
        try:
            excel_data = export_to_excel(df)
            st.download_button(
                label=":material/table_chart: Excel",
                data=excel_data,
                file_name=generate_export_filename("tasi_data", "xlsx"),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"export_xlsx_{response_key}",
                help="Download as Excel"
            )
        except Exception:
            # openpyxl might not be installed
            pass


def render_ai_response(response_data: Dict[str, Any], show_sql: bool = True) -> None:
    """Render an AI response in the chat.

    Args:
        response_data: Response dictionary with keys: success, sql, results, error
        show_sql: Whether to show the generated SQL
    """
    if not response_data.get("success"):
        # Error response
        error_msg = response_data.get("error", "An unknown error occurred")
        st.markdown(
            f'''
            <div class="error-banner">
                <div class="error-banner-title">:material/error: Query Error</div>
                <div class="error-banner-message">{error_msg}</div>
            </div>
            ''',
            unsafe_allow_html=True
        )

        # Show attempted SQL if available
        if response_data.get("sql") and show_sql:
            with st.expander("Attempted SQL", expanded=False):
                st.code(response_data["sql"], language="sql")
        return

    # Success response
    results = response_data.get("results", [])
    sql = response_data.get("sql", "")
    response_key = _get_response_key(response_data)

    # Results count badge
    st.markdown(
        f'<span class="results-count">{len(results)} results</span>',
        unsafe_allow_html=True
    )

    # Create tabs for Result and SQL
    if show_sql:
        tab_result, tab_sql = st.tabs(["Result", "SQL"])
    else:
        tab_result = st.container()

    with tab_result:
        if results:
            # Convert to DataFrame
            df = pd.DataFrame(results)

            # Export buttons
            render_export_buttons(df, response_key)

            # Display dataframe
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No results found for this query.")

    if show_sql:
        with tab_sql:
            if sql:
                st.code(sql, language="sql")
            else:
                st.info("No SQL was generated for this response.")


def render_chat_history(show_sql: bool = True) -> None:
    """Render the full chat history.

    Args:
        show_sql: Whether to show SQL in responses
    """
    history = get_chat_history()

    for entry in history:
        role = entry["role"]
        content = entry["content"]

        if role == "user":
            with st.chat_message("human"):
                st.write(content)
        else:
            with st.chat_message("ai"):
                if "response_data" in entry:
                    render_ai_response(entry["response_data"], show_sql=show_sql)
                else:
                    st.write(content)


def render_clear_history_button() -> bool:
    """Render a clear history button with confirmation.

    Returns:
        True if history was cleared, False otherwise
    """
    col1, col2 = st.columns([3, 1])

    with col2:
        if "confirm_clear" not in st.session_state:
            st.session_state.confirm_clear = False

        if st.session_state.confirm_clear:
            subcol1, subcol2 = st.columns(2)
            with subcol1:
                if st.button("Yes", key="confirm_yes", type="primary"):
                    clear_chat_history()
                    st.session_state.confirm_clear = False
                    return True
            with subcol2:
                if st.button("No", key="confirm_no"):
                    st.session_state.confirm_clear = False
        else:
            if st.button("Clear Chat", key="clear_history"):
                st.session_state.confirm_clear = True

    return False


def render_loading_animation() -> None:
    """Render a loading animation."""
    st.markdown(
        '''
        <div style="text-align: center; padding: 20px;">
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <p style="color: var(--text-muted); margin-top: 10px;">Analyzing your question...</p>
        </div>
        ''',
        unsafe_allow_html=True
    )
