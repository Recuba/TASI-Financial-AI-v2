"""Example questions component for Venna AI.

Provides clickable example queries to help users get started.
"""

import streamlit as st
from typing import Optional


# Example questions organized by category
EXAMPLE_QUESTIONS = {
    "Popular": [
        {
            "label": "Top 10 companies by revenue",
            "query": "Show the top 10 companies by revenue",
            "icon": "chart_with_upwards_trend"
        },
        {
            "label": "Most profitable companies",
            "query": "Which companies are most profitable?",
            "icon": "moneybag"
        },
        {
            "label": "Sector performance comparison",
            "query": "Compare sector performance by average ROE",
            "icon": "bar_chart"
        },
    ],
    "Analysis": [
        {
            "label": "Companies with losses",
            "query": "Show companies with negative net profit",
            "icon": "warning"
        },
        {
            "label": "High debt companies",
            "query": "Which companies have high debt to equity ratio?",
            "icon": "credit_card"
        },
        {
            "label": "Strong liquidity companies",
            "query": "List companies with strong liquidity",
            "icon": "droplet"
        },
    ],
    "Exploration": [
        {
            "label": "Insurance sector analysis",
            "query": "Show insurance sector performance",
            "icon": "shield"
        },
        {
            "label": "Year over year summary",
            "query": "Show year over year financial summary",
            "icon": "calendar"
        },
        {
            "label": "All sectors overview",
            "query": "How many companies are in each sector?",
            "icon": "building"
        },
    ]
}


def get_examples_by_category(category: str) -> list:
    """Get examples for a specific category.

    Args:
        category: Category name (Popular, Analysis, Exploration)

    Returns:
        List of example dictionaries
    """
    return EXAMPLE_QUESTIONS.get(category, [])


def get_all_examples() -> list:
    """Get all examples flattened into a single list."""
    all_examples = []
    for questions in EXAMPLE_QUESTIONS.values():
        all_examples.extend(questions)
    return all_examples


def render_example_questions(max_visible: int = 3) -> Optional[str]:
    """Render example question buttons.

    Args:
        max_visible: Number of questions to show by default

    Returns:
        Selected query string or None
    """
    selected_query = None

    # Show a few examples prominently
    st.subheader("Try an Example")

    # Display first few examples as prominent buttons
    popular = EXAMPLE_QUESTIONS["Popular"][:max_visible]

    cols = st.columns(len(popular))
    for i, example in enumerate(popular):
        with cols[i]:
            btn_key = f"example_prominent_{i}"
            is_active = st.session_state.get("active_example") == btn_key

            btn_type = "primary" if is_active else "secondary"

            if st.button(
                f":{example['icon']}: {example['label']}",
                key=btn_key,
                use_container_width=True,
                help=example["query"],
                type=btn_type
            ):
                selected_query = example["query"]
                st.session_state.active_example = btn_key

    # More examples in expander
    with st.expander("More Examples", expanded=False):
        for category, questions in EXAMPLE_QUESTIONS.items():
            if category == "Popular":
                # Skip first 3 already shown
                remaining = questions[max_visible:]
                if not remaining:
                    continue
                questions_to_show = remaining
            else:
                questions_to_show = questions

            st.markdown(f"**{category}**")

            for j, example in enumerate(questions_to_show):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f":{example['icon']}: {example['label']}")
                with col2:
                    if st.button(
                        "Try",
                        key=f"example_{category}_{j}",
                        help=example["query"]
                    ):
                        selected_query = example["query"]

            st.markdown("")  # Spacing

    return selected_query


def render_example_questions_minimal() -> Optional[str]:
    """Render a minimal version of example questions (just buttons).

    Returns:
        Selected query string or None
    """
    st.markdown("**Quick Examples:**")

    popular = EXAMPLE_QUESTIONS["Popular"][:3]

    cols = st.columns(len(popular))
    for i, example in enumerate(popular):
        with cols[i]:
            if st.button(example["label"], key=f"quick_{i}", use_container_width=True):
                return example["query"]

    return None
