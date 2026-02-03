"""CSS generator functions for Venna AI - Saudi Financial Theme."""

from .variables import (
    # Green colors
    GREEN_PRIMARY,
    GREEN_LIGHT,
    GREEN_DARK,
    GREEN_GRADIENT,
    # Gold colors
    GOLD_PRIMARY,
    GOLD_LIGHT,
    GOLD_DARK,
    GOLD_GRADIENT,
    # Background colors
    BG_DARK,
    BG_CARD,
    BG_CARD_HOVER,
    BG_INPUT,
    # Text colors
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    # Accent colors
    ACCENT_GREEN,
    ACCENT_RED,
    ACCENT_YELLOW,
    ACCENT_BLUE,
    # Status colors
    STATUS_SUCCESS,
    STATUS_WARNING,
    STATUS_ERROR,
    STATUS_INFO,
    # Typography
    FONT_SIZE_XS,
    FONT_SIZE_SM,
    FONT_SIZE_BASE,
    FONT_SIZE_LG,
    FONT_SIZE_XL,
    FONT_SIZE_2XL,
    # Spacing
    SPACING_XS,
    SPACING_SM,
    SPACING_MD,
    SPACING_LG,
    SPACING_XL,
    SPACING_2XL,
    # Border radius
    RADIUS_SM,
    RADIUS_MD,
    RADIUS_LG,
    # Shadows
    SHADOW_GREEN,
    SHADOW_GOLD,
    SHADOW_CARD,
    SHADOW_FOCUS,
    # Transitions
    TRANSITION_FAST,
    TRANSITION_DEFAULT,
)


def get_base_css() -> str:
    """Return the main CSS stylesheet with all styling for the app."""
    return f"""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');

/* CSS Custom Properties (Variables) */
:root {{
    /* Green Palette (Saudi) */
    --green-primary: {GREEN_PRIMARY};
    --green-light: {GREEN_LIGHT};
    --green-dark: {GREEN_DARK};
    --green-gradient: {GREEN_GRADIENT};

    /* Gold Palette */
    --gold-primary: {GOLD_PRIMARY};
    --gold-light: {GOLD_LIGHT};
    --gold-dark: {GOLD_DARK};
    --gold-gradient: {GOLD_GRADIENT};

    /* Background Colors */
    --bg-dark: {BG_DARK};
    --bg-card: {BG_CARD};
    --bg-card-hover: {BG_CARD_HOVER};
    --bg-input: {BG_INPUT};

    /* Text Colors */
    --text-primary: {TEXT_PRIMARY};
    --text-secondary: {TEXT_SECONDARY};
    --text-muted: {TEXT_MUTED};

    /* Accent Colors */
    --accent-green: {ACCENT_GREEN};
    --accent-red: {ACCENT_RED};
    --accent-yellow: {ACCENT_YELLOW};
    --accent-blue: {ACCENT_BLUE};

    /* Status Colors */
    --status-success: {STATUS_SUCCESS};
    --status-warning: {STATUS_WARNING};
    --status-error: {STATUS_ERROR};
    --status-info: {STATUS_INFO};

    /* Typography Scale */
    --font-size-xs: {FONT_SIZE_XS};
    --font-size-sm: {FONT_SIZE_SM};
    --font-size-base: {FONT_SIZE_BASE};
    --font-size-lg: {FONT_SIZE_LG};
    --font-size-xl: {FONT_SIZE_XL};
    --font-size-2xl: {FONT_SIZE_2XL};

    /* Spacing Scale */
    --spacing-xs: {SPACING_XS};
    --spacing-sm: {SPACING_SM};
    --spacing-md: {SPACING_MD};
    --spacing-lg: {SPACING_LG};
    --spacing-xl: {SPACING_XL};
    --spacing-2xl: {SPACING_2XL};

    /* Border Radius */
    --radius-sm: {RADIUS_SM};
    --radius-md: {RADIUS_MD};
    --radius-lg: {RADIUS_LG};

    /* Shadows */
    --shadow-green: {SHADOW_GREEN};
    --shadow-gold: {SHADOW_GOLD};
    --shadow-card: {SHADOW_CARD};
    --shadow-focus: {SHADOW_FOCUS};

    /* Transitions */
    --transition-fast: {TRANSITION_FAST};
    --transition-default: {TRANSITION_DEFAULT};
}}

/* Global Background */
.stApp {{
    background: radial-gradient(ellipse at top, #1a1a1a 0%, var(--bg-dark) 50%) !important;
}}

/* Main Container */
[data-testid="stAppViewContainer"] {{
    background: transparent !important;
}}

[data-testid="stMain"] {{
    background: transparent !important;
}}

/* Sidebar Styling */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, var(--bg-card) 0%, var(--bg-dark) 100%) !important;
    border-right: 1px solid rgba(0, 108, 53, 0.3) !important;
}}

[data-testid="stSidebar"] [data-testid="stMarkdown"] {{
    color: var(--text-primary) !important;
}}

/* Headers / Typography */
h1, h2, h3 {{
    color: var(--text-primary) !important;
    font-family: 'Tajawal', sans-serif !important;
}}

/* Brand Title with Green Gradient */
.brand-title {{
    background: var(--green-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.5rem;
    font-weight: 700;
    text-align: center;
    filter: drop-shadow(0 2px 4px rgba(0, 108, 53, 0.4));
}}

.brand-subtitle {{
    color: var(--gold-light);
    text-align: center;
    font-size: 1.1rem;
    margin-bottom: 1rem;
}}

/* Metric Cards */
[data-testid="stMetric"] {{
    background: var(--bg-card) !important;
    border: 1px solid rgba(0, 108, 53, 0.3) !important;
    border-radius: var(--radius-md) !important;
    padding: 1rem !important;
    transition: all var(--transition-default) !important;
}}

[data-testid="stMetric"]:hover {{
    border-color: var(--green-primary) !important;
    box-shadow: var(--shadow-green) !important;
    transform: translateY(-2px);
}}

[data-testid="stMetric"] [data-testid="stMetricLabel"] {{
    color: var(--gold-light) !important;
}}

[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: var(--text-primary) !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
}}

/* Primary Buttons (Green) */
.stButton > button[kind="primary"], .stButton > button {{
    background: linear-gradient(135deg, var(--green-dark) 0%, var(--green-primary) 100%) !important;
    color: var(--text-primary) !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: all var(--transition-default) !important;
}}

.stButton > button:hover {{
    background: linear-gradient(135deg, var(--green-primary) 0%, var(--green-light) 100%) !important;
    box-shadow: var(--shadow-green) !important;
    transform: translateY(-2px) !important;
}}

/* Secondary Buttons (Gold) */
.stButton > button[kind="secondary"] {{
    background: transparent !important;
    border: 1px solid var(--gold-primary) !important;
    color: var(--gold-light) !important;
}}

.stButton > button[kind="secondary"]:hover {{
    background: rgba(212, 168, 75, 0.1) !important;
    box-shadow: var(--shadow-gold) !important;
}}

/* Example Button Styles */
.example-btn {{
    background: var(--bg-card) !important;
    border: 1px solid rgba(0, 108, 53, 0.3) !important;
    color: var(--text-primary) !important;
    transition: all var(--transition-default) !important;
}}

.example-btn:hover {{
    background: var(--bg-card-hover) !important;
    border-color: var(--green-primary) !important;
    box-shadow: var(--shadow-green) !important;
}}

/* Chat Input Container */
[data-testid="stChatInput"] {{
    background: var(--bg-card) !important;
    border: 2px solid var(--green-primary) !important;
    border-radius: var(--radius-lg) !important;
    padding: var(--spacing-sm) !important;
    box-shadow: 0 0 15px rgba(0, 108, 53, 0.2) !important;
}}

[data-testid="stChatInput"] textarea {{
    background: var(--bg-input) !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-size: var(--font-size-base) !important;
    padding: var(--spacing-md) !important;
}}

[data-testid="stChatInput"] textarea::placeholder {{
    color: var(--text-muted) !important;
}}

[data-testid="stChatInput"] textarea:focus {{
    border-color: transparent !important;
    box-shadow: none !important;
    outline: none !important;
}}

[data-testid="stChatInput"] button {{
    background: var(--green-gradient) !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
}}

[data-testid="stChatInput"] button:hover {{
    box-shadow: var(--shadow-green) !important;
    transform: scale(1.05) !important;
}}

/* Chat Messages */
[data-testid="stChatMessage"] {{
    background: var(--bg-card) !important;
    border-radius: var(--radius-md) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}}

/* User message styling */
[data-testid="stChatMessage"][data-testid*="user"] {{
    border-left: 3px solid var(--green-primary) !important;
}}

/* AI message styling */
[data-testid="stChatMessage"][data-testid*="assistant"] {{
    border-left: 3px solid var(--gold-primary) !important;
}}

/* Dataframes */
[data-testid="stDataFrame"] {{
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
}}

[data-testid="stDataFrame"] table {{
    background: var(--bg-card) !important;
}}

[data-testid="stDataFrame"] th {{
    background: var(--green-dark) !important;
    color: var(--text-primary) !important;
}}

/* Expander */
[data-testid="stExpander"] {{
    background: var(--bg-card) !important;
    border: 1px solid rgba(0, 108, 53, 0.2) !important;
    border-radius: var(--radius-md) !important;
}}

[data-testid="stExpander"] summary {{
    color: var(--gold-light) !important;
}}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {{
    background: var(--bg-input) !important;
    border: 1px solid rgba(0, 108, 53, 0.3) !important;
    border-radius: var(--radius-sm) !important;
}}

/* Divider */
hr {{
    border-color: rgba(0, 108, 53, 0.2) !important;
}}

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {{
    background: var(--bg-card) !important;
    border-radius: var(--radius-sm) !important;
}}

[data-testid="stTabs"] button[aria-selected="true"] {{
    background: var(--green-primary) !important;
    color: var(--text-primary) !important;
}}

/* Code Blocks */
[data-testid="stCode"] {{
    background: var(--bg-input) !important;
    border: 1px solid rgba(0, 108, 53, 0.2) !important;
    border-radius: var(--radius-sm) !important;
}}

/* Scrollbar */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

::-webkit-scrollbar-track {{
    background: var(--bg-dark);
}}

::-webkit-scrollbar-thumb {{
    background: var(--green-dark);
    border-radius: 4px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: var(--green-primary);
}}

/* Caption/Footer */
.stCaption, [data-testid="stCaption"] {{
    color: var(--text-muted) !important;
}}

/* Spinner */
[data-testid="stSpinner"] {{
    color: var(--green-primary) !important;
}}

/* Loading Indicator Animation */
@keyframes pulse-green {{
    0% {{
        box-shadow: 0 0 0 0 rgba(0, 108, 53, 0.4);
    }}
    70% {{
        box-shadow: 0 0 0 10px rgba(0, 108, 53, 0);
    }}
    100% {{
        box-shadow: 0 0 0 0 rgba(0, 108, 53, 0);
    }}
}}

@keyframes spin {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
}}

.loading-indicator {{
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 2px solid var(--green-light);
    border-top-color: var(--green-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}}

.loading-pulse {{
    animation: pulse-green 2s infinite;
}}

/* Loading Dot Animation */
@keyframes bounce {{
    0%, 80%, 100% {{
        transform: translateY(0);
    }}
    40% {{
        transform: translateY(-8px);
    }}
}}

.loading-dot {{
    display: inline-block;
    width: 8px;
    height: 8px;
    margin: 0 4px;
    background: var(--green-primary);
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out both;
}}

.loading-dot:nth-child(1) {{
    animation-delay: -0.32s;
}}

.loading-dot:nth-child(2) {{
    animation-delay: -0.16s;
}}

.loading-dot:nth-child(3) {{
    animation-delay: 0s;
}}

/* Keyboard Hint Styling */
.kbd-hint {{
    display: inline-block;
    background: var(--bg-input);
    border: 1px solid rgba(0, 108, 53, 0.3);
    border-radius: 4px;
    padding: 2px 6px;
    font-size: var(--font-size-xs);
    font-family: monospace;
    color: var(--text-secondary);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}}

.kbd-hint:hover {{
    border-color: var(--green-primary);
    color: var(--green-light);
}}

/* Data Preview Section */
.data-preview {{
    background: var(--bg-card);
    border: 1px solid rgba(0, 108, 53, 0.2);
    border-radius: var(--radius-md);
    padding: var(--spacing-md);
    margin: var(--spacing-md) 0;
}}

/* Export Buttons */
.export-btn {{
    background: transparent !important;
    border: 1px solid var(--gold-primary) !important;
    color: var(--gold-light) !important;
    padding: 0.25rem 0.75rem !important;
    font-size: var(--font-size-sm) !important;
}}

.export-btn:hover {{
    background: rgba(212, 168, 75, 0.1) !important;
}}

/* Status Badge */
.status-badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: var(--font-size-xs);
    font-weight: 600;
}}

.status-badge.success {{
    background: rgba(0, 166, 81, 0.2);
    color: var(--status-success);
}}

.status-badge.error {{
    background: rgba(255, 107, 107, 0.2);
    color: var(--status-error);
}}

.status-badge.warning {{
    background: rgba(255, 167, 38, 0.2);
    color: var(--status-warning);
}}

/* Toast notifications */
[data-testid="stToast"] {{
    background: var(--bg-card) !important;
    border: 1px solid rgba(0, 108, 53, 0.3) !important;
    border-radius: var(--radius-md) !important;
}}

/* SQL Code Display */
.sql-display {{
    background: var(--bg-input);
    border: 1px solid rgba(212, 168, 75, 0.2);
    border-radius: var(--radius-sm);
    padding: var(--spacing-md);
    font-family: 'Fira Code', 'Consolas', monospace;
    font-size: var(--font-size-sm);
    overflow-x: auto;
}}

/* Results Count Badge */
.results-count {{
    background: var(--green-dark);
    color: var(--text-primary);
    padding: 4px 12px;
    border-radius: 16px;
    font-size: var(--font-size-sm);
    font-weight: 600;
}}

/* Download Button styling */
[data-testid="stDownloadButton"] button {{
    background: transparent !important;
    border: 1px solid var(--gold-primary) !important;
    color: var(--gold-light) !important;
}}

[data-testid="stDownloadButton"] button:hover {{
    background: rgba(212, 168, 75, 0.1) !important;
    box-shadow: var(--shadow-gold) !important;
}}

/* Sidebar Metric Labels - Prevent Truncation */
[data-testid="stSidebar"] [data-testid="stMetric"] {{
    min-width: 80px !important;
}}

[data-testid="stSidebar"] [data-testid="stMetricLabel"] {{
    white-space: nowrap !important;
    overflow: visible !important;
    text-overflow: clip !important;
    font-size: var(--font-size-sm) !important;
}}

[data-testid="stSidebar"] [data-testid="stMetricValue"] {{
    font-size: var(--font-size-lg) !important;
}}

/* Radio buttons (mode selector) */
[data-testid="stRadio"] > div {{
    background: var(--bg-card) !important;
    border-radius: var(--radius-sm) !important;
    padding: var(--spacing-xs) !important;
}}

[data-testid="stRadio"] label {{
    color: var(--text-primary) !important;
}}
</style>
"""


def get_error_css() -> str:
    """Return CSS for error states and alerts."""
    return f"""
<style>
/* Error Banner */
.error-banner {{
    background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 107, 107, 0.05) 100%);
    border: 1px solid {STATUS_ERROR};
    border-left: 4px solid {STATUS_ERROR};
    border-radius: {RADIUS_MD};
    padding: {SPACING_MD} {SPACING_LG};
    margin: {SPACING_MD} 0;
    color: {TEXT_PRIMARY};
}}

.error-banner-title {{
    color: {STATUS_ERROR};
    font-weight: 600;
    font-size: {FONT_SIZE_LG};
    margin-bottom: {SPACING_SM};
    display: flex;
    align-items: center;
    gap: {SPACING_SM};
}}

.error-banner-message {{
    color: {TEXT_SECONDARY};
    font-size: {FONT_SIZE_BASE};
    line-height: 1.5;
}}

/* Warning Banner */
.warning-banner {{
    background: linear-gradient(135deg, rgba(255, 167, 38, 0.1) 0%, rgba(255, 167, 38, 0.05) 100%);
    border: 1px solid {STATUS_WARNING};
    border-left: 4px solid {STATUS_WARNING};
    border-radius: {RADIUS_MD};
    padding: {SPACING_MD} {SPACING_LG};
    margin: {SPACING_MD} 0;
    color: {TEXT_PRIMARY};
}}

/* Success Banner */
.success-banner {{
    background: linear-gradient(135deg, rgba(0, 166, 81, 0.1) 0%, rgba(0, 166, 81, 0.05) 100%);
    border: 1px solid {STATUS_SUCCESS};
    border-left: 4px solid {STATUS_SUCCESS};
    border-radius: {RADIUS_MD};
    padding: {SPACING_MD} {SPACING_LG};
    margin: {SPACING_MD} 0;
    color: {TEXT_PRIMARY};
}}

/* Retry Button */
.retry-btn {{
    background: transparent !important;
    border: 1px solid {STATUS_ERROR} !important;
    color: {STATUS_ERROR} !important;
    border-radius: {RADIUS_SM} !important;
    padding: {SPACING_SM} {SPACING_MD} !important;
    font-weight: 500 !important;
    transition: all {TRANSITION_DEFAULT} !important;
    cursor: pointer;
}}

.retry-btn:hover {{
    background: rgba(255, 107, 107, 0.1) !important;
    box-shadow: 0 0 10px rgba(255, 107, 107, 0.3) !important;
}}

@keyframes slideIn {{
    from {{
        opacity: 0;
        transform: translateY(-10px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

@keyframes fadeOut {{
    from {{
        opacity: 1;
        transform: translateY(0);
    }}
    to {{
        opacity: 0;
        transform: translateY(-10px);
    }}
}}
</style>
"""
