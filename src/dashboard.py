"""Shared visual styles and formatting for the SalesIQ Streamlit app."""

import plotly.io as pio
import streamlit as st


def apply_theme() -> None:
    """Apply the shared dark SalesIQ theme across every Streamlit page."""
    colors = {
        "canvas": "#080d18",
        "surface": "#101827",
        "surface_alt": "#141f31",
        "ink": "#edf3ff",
        "muted": "#8998b3",
        "line": "#202d42",
        "grid": "#263248",
        "accent": "#80a5ff",
        "teal": "#53d6c2",
        "header": "rgba(8,13,24,.88)",
        "shadow": "rgba(0,0,0,.18)",
        "plot_template": "plotly_dark",
    }
    st.session_state["salesiq_is_dark"] = True

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
        :root {{ color-scheme:dark; --canvas:{colors['canvas']}; --surface:{colors['surface']}; --surface-alt:{colors['surface_alt']}; --ink:{colors['ink']}; --muted:{colors['muted']}; --line:{colors['line']}; --grid:{colors['grid']}; --blue:{colors['accent']}; --teal:{colors['teal']}; }}
        html, body, [class*="css"] {{ font-family:'DM Sans',sans-serif !important; color:var(--ink) !important; }}
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{ background:var(--canvas) !important; color:var(--ink) !important; }}
        [data-testid="stHeader"] {{ background:{colors['header']} !important; backdrop-filter:blur(14px); }}
        [data-testid="stSidebar"], [data-testid="stSidebar"] > div {{ background:var(--surface) !important; border-right:1px solid var(--line); }}
        [data-testid="stSidebar"] > div:first-child {{ padding:1.35rem 1rem 1rem; }}
        [data-testid="stMainBlockContainer"] {{ max-width:1580px; padding:2rem 3rem 4rem; }}
        .brand-mark {{ font:800 1.58rem Manrope,sans-serif; color:var(--ink); letter-spacing:-1.1px; }}
        .brand-mark:first-letter {{ color:var(--blue); }}
        .brand-mark span {{ margin-left:.28rem; }}
        .eyebrow {{ color:var(--teal); font-size:.68rem; font-weight:700; letter-spacing:2.15px; margin:.65rem 0 .35rem; }}
        h1 {{ font:800 clamp(2rem,3.1vw,2.65rem) Manrope,sans-serif !important; letter-spacing:-1.5px; color:var(--ink) !important; padding-bottom:.12rem; }}
        h2,h3,h4 {{ font-family:Manrope,sans-serif !important; letter-spacing:-.45px; color:var(--ink) !important; }}
        h4 {{ font-size:1.04rem !important; margin-bottom:.75rem !important; }}
        .subhead {{ color:var(--muted); font-size:.94rem; margin:0 0 1.45rem; }}
        [data-testid="stMetric"] {{ position:relative; overflow:hidden; background:linear-gradient(145deg,var(--surface),var(--surface-alt)); border:1px solid var(--line); border-radius:16px; padding:19px 20px; box-shadow:0 8px 24px {colors['shadow']}; transition:transform .18s ease,border-color .18s ease; }}
        [data-testid="stMetric"]:hover {{ transform:translateY(-2px); border-color:var(--blue); }}
        [data-testid="stMetric"]:before {{ content:''; position:absolute; top:0; left:18px; width:36px; height:2px; background:linear-gradient(90deg,var(--blue),var(--teal)); border-radius:2px; }}
        [data-testid="stMetricLabel"] {{ color:var(--muted) !important; font-size:.77rem; font-weight:600; }}
        [data-testid="stMetricValue"] {{ font:700 clamp(1.25rem,1.7vw,1.65rem) Manrope,sans-serif; color:var(--ink) !important; }}
        [data-testid="stMetricDelta"] {{ font-size:.75rem; }}
        [data-testid="stPlotlyChart"] {{ background:var(--surface); border:1px solid var(--line); border-radius:16px; padding:8px; box-shadow:0 8px 24px {colors['shadow']}; }}
        div[data-testid="stDataFrame"] {{ background:var(--surface); border:1px solid var(--line); border-radius:13px; overflow:hidden; }}
        [data-testid="stCaptionContainer"] p {{ color:var(--muted) !important; }}
        [data-testid="stMarkdownContainer"] p {{ color:var(--ink) !important; }}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{ color:var(--muted) !important; }}
        [data-testid="stWidgetLabel"] p {{ color:var(--ink) !important; font-weight:600; }}
        input, textarea, [data-baseweb="select"] > div, [data-baseweb="input"] > div {{ background-color:var(--surface-alt) !important; color:var(--ink) !important; border-color:var(--line) !important; }}
        [data-baseweb="tag"] {{ background:rgba(128,165,255,.18) !important; color:var(--ink) !important; }}
        [data-testid="stDateInput"] button {{ color:var(--ink); }}
        [data-testid="stAlert"] {{ border-radius:12px; }}
        .stButton > button,.stDownloadButton > button {{ border-radius:10px; font-weight:600; transition:all .18s ease; }}
        .stButton > button {{ border:1px solid var(--line); background:var(--surface-alt); color:var(--ink); }}
        .stButton > button:hover,.stDownloadButton > button:hover {{ border-color:var(--blue); color:var(--blue); transform:translateY(-1px); }}
        .stDownloadButton > button {{ border:1px solid var(--line); background:var(--surface-alt); color:var(--ink); }}
        [data-testid="stSidebar"] hr {{ border-color:var(--line); }}
        [data-testid="stSidebarNav"] {{ padding-top:.4rem; }}
        [data-testid="stSidebarNav"] a {{ border-radius:9px; margin:2px 0; }}
        [data-testid="stSidebarNav"] a[aria-current="page"] {{ background:rgba(128,165,255,.14); color:var(--blue); }}
        footer {{ visibility:hidden; }}
        @media(max-width:900px) {{ [data-testid="stMainBlockContainer"] {{ padding:1.5rem 1.1rem 3rem; }} }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    pio.templates.default = colors["plot_template"]


def chart_layout() -> dict:
    """Return shared Plotly layout options."""
    text_color = "#aab8ce"
    grid_color = "#263248"
    line_color = "#303e55"
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "DM Sans, sans-serif", "color": text_color, "size": 11},
        "margin": {"l": 8, "r": 12, "t": 18, "b": 8},
        "xaxis": {"showgrid": False, "zeroline": False, "linecolor": line_color, "tickfont": {"color": text_color}},
        "yaxis": {"showgrid": True, "gridcolor": grid_color, "zeroline": False, "tickfont": {"color": text_color}},
    }


def currency(value: float) -> str:
    """Format a monetary value for display."""
    return f"${value:,.2f}"