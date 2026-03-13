"""
AnalyticDashAI — Upload data. Ask anything. See everything.
AI-powered dashboard builder powered by Claude API.
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import re
import io
import base64
import traceback
import os
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AnalyticDashAI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Brand colors ──────────────────────────────────────────────────────────────
ORANGE   = "#FF5C00"
OBSIDIAN = "#0C0C0C"
CHARCOAL = "#1E1E1E"
WHITE    = "#FFFFFF"
GREY     = "#6B6B6B"

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

  html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: #0C0C0C;
    color: #FFFFFF;
  }

  /* Header */
  .brand-header {
    padding: 1.5rem 0 0.5rem 0;
    border-bottom: 1px solid #1E1E1E;
    margin-bottom: 1rem;
  }
  .brand-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0;
    letter-spacing: -0.5px;
  }
  .brand-title span { color: #FF5C00; }
  .brand-subtitle {
    font-size: 0.85rem;
    color: #6B6B6B;
    margin: 0.2rem 0 0 0;
    font-family: 'Space Grotesk', sans-serif;
  }

  /* Progress badges */
  .progress-bar {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin: 0.75rem 0;
  }
  .badge {
    padding: 0.3rem 0.75rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: 'Space Grotesk', sans-serif;
    letter-spacing: 0.3px;
    border: 1px solid #2E2E2E;
    background: #1E1E1E;
    color: #6B6B6B;
  }
  .badge.done {
    background: #0C2010;
    border-color: #1A5C2A;
    color: #4ADE80;
  }

  /* Step label */
  .step-label {
    display: inline-block;
    background: #1E1E1E;
    color: #FF5C00;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 0.3rem 0.8rem;
    border-radius: 4px;
    border-left: 3px solid #FF5C00;
    margin-bottom: 0.5rem;
  }

  /* Cards */
  .info-card {
    background: #1E1E1E;
    border: 1px solid #2E2E2E;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
  }
  .info-card h4 { margin: 0 0 0.25rem 0; color: #FFFFFF; font-size: 0.95rem; }
  .info-card p  { margin: 0; color: #8B8B8B; font-size: 0.82rem; }

  /* Narrative / So What box */
  .so-what-box {
    background: linear-gradient(135deg, #1A1200 0%, #1E1000 100%);
    border: 1px solid #FF5C00;
    border-left: 4px solid #FF5C00;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
  }
  .so-what-box h4 {
    color: #FF5C00;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin: 0 0 0.6rem 0;
  }
  .so-what-box p { color: #E0E0E0; font-size: 0.92rem; line-height: 1.6; margin: 0; }

  /* Anomaly alert */
  .anomaly-box {
    background: #1A0A00;
    border: 1px solid #FF3300;
    border-left: 4px solid #FF3300;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.85rem;
    color: #FFB3A0;
  }

  /* Question prompt buttons */
  .stButton > button {
    background: #1E1E1E !important;
    color: #FFFFFF !important;
    border: 1px solid #2E2E2E !important;
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.85rem !important;
    transition: all 0.2s !important;
    text-align: left !important;
  }
  .stButton > button:hover {
    border-color: #FF5C00 !important;
    color: #FF5C00 !important;
    background: #1A0E00 !important;
  }

  /* Primary CTA */
  .cta-btn > button {
    background: #FF5C00 !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
  }
  .cta-btn > button:hover {
    background: #FF7A2B !important;
  }

  /* Tab styling */
  .stTabs [data-baseweb="tab-list"] {
    background: #1E1E1E;
    border-radius: 10px;
    padding: 4px;
    gap: 2px;
  }
  .stTabs [data-baseweb="tab"] {
    color: #6B6B6B !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    border-radius: 8px !important;
    padding: 0.5rem 1rem !important;
  }
  .stTabs [aria-selected="true"] {
    background: #FF5C00 !important;
    color: #FFFFFF !important;
  }

  /* Metric cards */
  [data-testid="metric-container"] {
    background: #1E1E1E;
    border: 1px solid #2E2E2E;
    border-radius: 10px;
    padding: 1rem;
  }

  /* Dataframe */
  [data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

  /* Inputs */
  .stTextArea textarea, .stTextInput input {
    background: #1E1E1E !important;
    border: 1px solid #2E2E2E !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
  }
  .stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #FF5C00 !important;
  }

  /* Selectbox */
  .stSelectbox > div > div {
    background: #1E1E1E !important;
    border-color: #2E2E2E !important;
    color: #FFFFFF !important;
  }

  /* Expander */
  .streamlit-expanderHeader {
    background: #1E1E1E !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
  }

  /* File uploader */
  [data-testid="stFileUploader"] {
    background: #1E1E1E;
    border: 2px dashed #2E2E2E;
    border-radius: 10px;
  }

  /* Pro tip */
  .pro-tip {
    background: #111;
    border-left: 3px solid #FF5C00;
    padding: 0.5rem 0.9rem;
    border-radius: 0 6px 6px 0;
    font-size: 0.82rem;
    color: #8B8B8B;
    margin: 0.5rem 0;
  }
  .pro-tip span { color: #FF5C00; font-weight: 700; }

  /* Hide Streamlit branding */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1rem !important; max-width: 1200px; }
</style>
""", unsafe_allow_html=True)


# ── Anthropic client ──────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY", st.secrets.get("ANTHROPIC_API_KEY", ""))
    if not api_key:
        st.error("⚠️ ANTHROPIC_API_KEY not found. Add it to .env or Streamlit secrets.")
        st.stop()
    return Anthropic(api_key=api_key)


# ── Session state defaults ─────────────────────────────────────────────────────
def init_state():
    defaults = {
        "business_question": "",
        "df": None,
        "df_clean": None,
        "filename": "",
        "analysis_result": None,
        "recommendations": None,
        "so_what": "",
        "anomalies": [],
        "charts": [],
        "dashboard_charts": [],
        "nl_history": [],
        "kpis": {},
        "snapshots": [],
        "question_set": False,
        "data_loaded": False,
        "analysed": False,
        "data_cleaned": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
client = get_client()


# ── Helpers ───────────────────────────────────────────────────────────────────
def df_summary(df: pd.DataFrame, max_rows: int = 5) -> str:
    """Return a compact text summary of a DataFrame for Claude."""
    buf = io.StringIO()
    buf.write(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n")
    buf.write(f"Columns: {list(df.columns)}\n")
    buf.write(f"Dtypes:\n{df.dtypes.to_string()}\n")
    buf.write(f"Sample (first {max_rows} rows):\n{df.head(max_rows).to_string()}\n")
    buf.write(f"Numeric stats:\n{df.describe().to_string()}\n")
    nulls = df.isnull().sum()
    buf.write(f"Null counts:\n{nulls[nulls > 0].to_string() if nulls.any() else 'None'}\n")
    return buf.getvalue()


def ask_claude(prompt: str, system: str = "", max_tokens: int = 2000) -> str:
    """Single-turn Claude call — returns text."""
    msgs = [{"role": "user", "content": prompt}]
    resp = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=max_tokens,
        system=system or "You are a senior data analyst. Be concise and precise.",
        messages=msgs,
    )
    return resp.content[0].text


def parse_json_response(text: str) -> dict:
    """Strip markdown fences and parse JSON."""
    text = re.sub(r"```(?:json)?", "", text).strip().strip("`").strip()
    return json.loads(text)


def safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def auto_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Basic auto-cleaning: strip whitespace, fix dtypes, drop all-null cols."""
    df = df.copy()
    # Strip string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({"nan": np.nan, "None": np.nan, "": np.nan})
    # Try numeric coercion on object cols that look numeric
    for col in df.select_dtypes(include="object").columns:
        converted = safe_numeric(df[col])
        if converted.notna().sum() / max(len(df), 1) > 0.7:
            df[col] = converted
    # Drop fully-null columns
    df.dropna(axis=1, how="all", inplace=True)
    return df


def detect_anomalies(df: pd.DataFrame) -> list[str]:
    """Simple IQR-based anomaly detection on numeric columns."""
    alerts = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols[:8]:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        outliers = df[(df[col] < q1 - 2.5 * iqr) | (df[col] > q3 + 2.5 * iqr)]
        if len(outliers) > 0:
            pct = round(len(outliers) / len(df) * 100, 1)
            alerts.append(f"**{col}**: {len(outliers)} outliers ({pct}%) detected outside 2.5×IQR range [{round(q1-2.5*iqr,2)}, {round(q3+2.5*iqr,2)}]")
    return alerts


def build_chart(df: pd.DataFrame, chart_type: str, x: str, y: str, color: str = None, title: str = "") -> go.Figure | None:
    """Build a Plotly chart from spec."""
    try:
        df = df.copy()
        if y and y in df.columns:
            df[y] = safe_numeric(df[y])
        kwargs = dict(x=x, y=y, title=title, color=color if color and color in df.columns else None,
                      color_discrete_sequence=px.colors.sequential.Oranges)
        ct = chart_type.lower()
        if ct == "bar":           fig = px.bar(df, **kwargs)
        elif ct == "line":        fig = px.line(df, **kwargs)
        elif ct == "scatter":     fig = px.scatter(df, **kwargs)
        elif ct == "area":        fig = px.area(df, **kwargs)
        elif ct == "histogram":   fig = px.histogram(df, x=x, title=title, color_discrete_sequence=["#FF5C00"])
        elif ct == "box":         fig = px.box(df, x=x, y=y, title=title, color_discrete_sequence=["#FF5C00"])
        elif ct == "violin":      fig = px.violin(df, x=x, y=y, title=title, color_discrete_sequence=["#FF5C00"])
        elif ct == "pie":         fig = px.pie(df, names=x, values=y, title=title, color_discrete_sequence=px.colors.sequential.Oranges)
        elif ct == "donut":       fig = px.pie(df, names=x, values=y, title=title, hole=0.45, color_discrete_sequence=px.colors.sequential.Oranges)
        elif ct == "heatmap":
            pivot = df.pivot_table(values=y, index=x, columns=color, aggfunc="mean") if color and color in df.columns else df.select_dtypes(include=[np.number]).corr()
            fig = px.imshow(pivot, title=title, color_continuous_scale="Oranges")
        elif ct == "funnel":      fig = px.funnel(df, x=y, y=x, title=title, color_discrete_sequence=["#FF5C00"])
        elif ct == "treemap":     fig = px.treemap(df, path=[x], values=y, title=title, color_discrete_sequence=px.colors.sequential.Oranges)
        elif ct == "sunburst":    fig = px.sunburst(df, path=[x], values=y, title=title, color_discrete_sequence=px.colors.sequential.Oranges)
        elif ct == "bubble":      fig = px.scatter(df, x=x, y=y, size=y, title=title, color_discrete_sequence=["#FF5C00"])
        elif ct == "waterfall":
            fig = go.Figure(go.Waterfall(x=df[x].astype(str).tolist(), y=df[y].tolist(), name=title,
                                         connector={"line": {"color": "#FF5C00"}}))
            fig.update_layout(title=title)
        else:                     fig = px.bar(df, **kwargs)

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#111111",
            font=dict(family="Plus Jakarta Sans", color="#FFFFFF", size=12),
            title_font=dict(family="Space Grotesk", size=14, color="#FFFFFF"),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#AAAAAA")),
            margin=dict(l=40, r=20, t=45, b=40),
            xaxis=dict(gridcolor="#1E1E1E", linecolor="#2E2E2E", tickfont=dict(color="#888888")),
            yaxis=dict(gridcolor="#1E1E1E", linecolor="#2E2E2E", tickfont=dict(color="#888888")),
        )
        return fig
    except Exception as e:
        st.warning(f"Chart error ({chart_type}): {e}")
        return None


# ── SAMPLE DATA ────────────────────────────────────────────────────────────────
def get_sample_data() -> pd.DataFrame:
    np.random.seed(42)
    n = 300
    regions   = ["North", "South", "East", "West", "Central"]
    products  = ["Pro Plan", "Starter", "Enterprise", "Basic", "Add-on"]
    channels  = ["Organic", "Paid Search", "Email", "Referral", "Social"]
    months    = pd.date_range("2024-01-01", periods=12, freq="MS")

    df = pd.DataFrame({
        "Date":        np.random.choice(months, n),
        "Region":      np.random.choice(regions, n, p=[0.25, 0.20, 0.22, 0.18, 0.15]),
        "Product":     np.random.choice(products, n, p=[0.30, 0.25, 0.15, 0.20, 0.10]),
        "Channel":     np.random.choice(channels, n),
        "Revenue":     np.round(np.random.lognormal(7.5, 0.8, n), 2),
        "Units":       np.random.randint(1, 50, n),
        "Cost":        np.round(np.random.lognormal(6.5, 0.6, n), 2),
        "Customers":   np.random.randint(10, 500, n),
        "Churn_Rate":  np.round(np.random.beta(2, 18, n) * 100, 2),
        "Satisfaction":np.round(np.random.normal(7.5, 1.5, n).clip(1, 10), 1),
    })
    df["Profit"] = (df["Revenue"] - df["Cost"]).round(2)
    df["Month"]  = df["Date"].dt.strftime("%b %Y")
    return df


# ═══════════════════════════════════════════════════════════════════════════════
#  RENDER HEADER
# ═══════════════════════════════════════════════════════════════════════════════
def render_header():
    st.markdown("""
    <div class="brand-header">
      <p class="brand-title">Analytic<span>Dash</span><span style="color:#FF5C00">AI</span></p>
      <p class="brand-subtitle">AI Dashboard Builder &nbsp;·&nbsp; Natural Language Queries &nbsp;·&nbsp; Auto Data Cleaning &nbsp;·&nbsp; PDF &amp; PowerPoint Export</p>
    </div>
    """, unsafe_allow_html=True)

    # Progress badges
    b = st.session_state
    def badge(label, done): cls = "badge done" if done else "badge"; return f'<span class="{cls}">{"✓" if done else "○"} {label}</span>'
    st.markdown(f"""
    <div class="progress-bar">
      {badge("Question Set", b.question_set)}
      {badge("Data Loaded", b.data_loaded)}
      {badge("Analysed", b.analysed)}
      {badge("Data Cleaned", b.data_cleaned)}
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — SETUP
# ═══════════════════════════════════════════════════════════════════════════════
QUESTION_PROMPTS = [
    "Why is customer churn increasing?",
    "Which products are most profitable by region?",
    "What's driving revenue growth this quarter?",
    "Which customer segments have the highest lifetime value?",
    "Where are we losing customers in the funnel?",
    "Which states/regions have the best performance?",
]

def tab_setup():
    st.markdown('<div class="step-label">STEP 1 — DEFINE YOUR QUESTION</div>', unsafe_allow_html=True)
    st.markdown("## What are you trying to figure out?")
    st.markdown("Start with a business question — AnalyticDashAI will tailor every analysis and dashboard to answer it.")

    cols = st.columns(3)
    for i, q in enumerate(QUESTION_PROMPTS):
        with cols[i % 3]:
            if st.button(q, key=f"q_{i}", use_container_width=True):
                st.session_state.business_question = q
                st.session_state.question_set = True
                st.rerun()

    st.markdown('<div class="step-label" style="margin-top:1.5rem">STEP 2 — UPLOAD YOUR DATA</div>', unsafe_allow_html=True)

    q_val = st.text_area(
        "Or type your own question:",
        value=st.session_state.business_question,
        placeholder="e.g., Why are high-value customers churning after month 3?",
        height=80,
        key="q_input",
    )

    c1, c2 = st.columns([2, 1])
    with c1:
        if st.button("✓ Set Business Question", use_container_width=True, key="set_q"):
            if q_val.strip():
                st.session_state.business_question = q_val.strip()
                st.session_state.question_set = True
                st.success(f"Question set: *{st.session_state.business_question}*")
            else:
                st.warning("Please enter a question first.")

    st.markdown('<div class="pro-tip"><span>💡 Pro tip:</span> The more specific your question, the better AnalyticDashAI\'s analysis.</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload your data file:",
        type=["csv", "xlsx", "xls"],
        help="CSV or Excel files supported. Up to 200MB.",
        key="file_upload",
    )

    if uploaded:
        try:
            if uploaded.name.endswith(".csv"):
                df = pd.read_csv(uploaded)
            else:
                xl = pd.ExcelFile(uploaded)
                if len(xl.sheet_names) > 1:
                    sheet = st.selectbox("Select sheet:", xl.sheet_names, key="sheet_sel")
                else:
                    sheet = xl.sheet_names[0]
                df = pd.read_excel(uploaded, sheet_name=sheet)

            df = auto_clean(df)
            st.session_state.df = df
            st.session_state.df_clean = df.copy()
            st.session_state.filename = uploaded.name
            st.session_state.data_loaded = True
            st.session_state.data_cleaned = True
            st.session_state.analysed = False  # reset on new upload
            st.success(f"✓ Loaded **{uploaded.name}** — {df.shape[0]:,} rows × {df.shape[1]} columns")
        except Exception as e:
            st.error(f"Error reading file: {e}")

    # Sample data shortcut
    st.markdown("---")
    st.markdown('<div class="info-card"><h4>🚀 No data handy?</h4><p>Try AnalyticDashAI instantly with a built-in sample sales dataset.</p></div>', unsafe_allow_html=True)
    if st.button("▶ Try with Sample Data", key="sample_btn"):
        df = get_sample_data()
        st.session_state.df = df
        st.session_state.df_clean = df.copy()
        st.session_state.filename = "sample_sales_data.csv"
        st.session_state.data_loaded = True
        st.session_state.data_cleaned = True
        if not st.session_state.business_question:
            st.session_state.business_question = "What's driving revenue growth this quarter?"
            st.session_state.question_set = True
        st.success("✓ Sample sales data loaded (300 rows).")
        st.rerun()

    # Data preview
    if st.session_state.df is not None:
        st.markdown("---")
        st.markdown("**Data Preview:**")
        st.dataframe(st.session_state.df.head(10), use_container_width=True)
        m1, m2, m3, m4 = st.columns(4)
        df = st.session_state.df
        m1.metric("Rows", f"{df.shape[0]:,}")
        m2.metric("Columns", str(df.shape[1]))
        m3.metric("Numeric cols", str(len(df.select_dtypes(include=[np.number]).columns)))
        m4.metric("Missing values", f"{df.isnull().sum().sum():,}")


# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — ANALYSE
# ═══════════════════════════════════════════════════════════════════════════════
def tab_analyse():
    if st.session_state.df is None:
        st.info("Upload data in the **Setup** tab first.")
        return

    df = st.session_state.df_clean
    question = st.session_state.business_question or "General analysis"

    # ── AI Data Analyst ──
    st.markdown('<div class="step-label">STEP 2 — AI DATA ANALYST</div>', unsafe_allow_html=True)
    st.markdown("## AI Data Analyst")
    st.markdown("📊 Data Profiling · 🔍 Issue Detection · 🧹 Auto-Cleaning · ⚡ Feature Engineering · 💡 Business Insights")

    if st.button("⚙ Run AI Analyst", key="run_analyst", use_container_width=False):
        with st.spinner("Running full AI analysis…"):
            summary = df_summary(df)
            prompt = f"""
You are a senior data analyst. Analyse the following dataset in the context of this business question:
**Business Question:** {question}

**Dataset Summary:**
{summary}

Return ONLY valid JSON (no markdown) with this structure:
{{
  "data_quality": {{
    "score": <0-100 integer>,
    "issues": [<string>, ...],
    "recommendations": [<string>, ...]
  }},
  "key_insights": [
    {{"title": "<short>", "insight": "<2 sentences>", "metric": "<number or %>"}},
    ...
  ],
  "top_columns": [<column names relevant to the question>],
  "suggested_charts": [
    {{"type": "<chart_type>", "x": "<col>", "y": "<col>", "title": "<title>"}},
    ...
  ],
  "so_what": "<3 sentence plain English executive summary answering the business question>"
}}
Return at least 4 key_insights and 5 suggested_charts.
"""
            try:
                raw = ask_claude(prompt, max_tokens=3000)
                result = parse_json_response(raw)
                st.session_state.analysis_result = result
                st.session_state.so_what = result.get("so_what", "")
                st.session_state.charts = result.get("suggested_charts", [])
                st.session_state.anomalies = detect_anomalies(df)
                st.session_state.analysed = True
                st.success("✓ Analysis complete!")
                st.rerun()
            except Exception as e:
                st.error(f"Analysis error: {e}\n{traceback.format_exc()}")

    # ── Display analysis results ──
    if st.session_state.analysis_result:
        result = st.session_state.analysis_result

        # So What narrative
        if st.session_state.so_what:
            st.markdown(f"""
            <div class="so-what-box">
              <h4>🎯 SO WHAT? — AI EXECUTIVE SUMMARY</h4>
              <p>{st.session_state.so_what}</p>
            </div>
            """, unsafe_allow_html=True)

        # Anomaly alerts
        if st.session_state.anomalies:
            st.markdown("### ⚠️ Anomaly Alerts")
            for a in st.session_state.anomalies[:5]:
                st.markdown(f'<div class="anomaly-box">🔴 {a}</div>', unsafe_allow_html=True)

        # Data quality
        dq = result.get("data_quality", {})
        score = dq.get("score", 0)
        col1, col2 = st.columns([1, 2])
        with col1:
            color = "#4ADE80" if score >= 80 else "#FFBB33" if score >= 60 else "#FF5C00"
            st.markdown(f"""
            <div class="info-card" style="text-align:center">
              <h4 style="font-size:2.5rem;color:{color};margin:0">{score}</h4>
              <p style="margin:0;font-size:0.8rem">Data Quality Score / 100</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            issues = dq.get("issues", [])
            if issues:
                st.markdown("**Issues found:**")
                for i in issues:
                    st.markdown(f"• {i}")

        # Key insights
        insights = result.get("key_insights", [])
        if insights:
            st.markdown("### 💡 Key Insights")
            cols = st.columns(min(len(insights), 4))
            for i, ins in enumerate(insights[:4]):
                with cols[i]:
                    st.metric(ins.get("title", "Insight"), ins.get("metric", "—"))
                    st.caption(ins.get("insight", ""))

        # Suggested charts
        charts = st.session_state.charts
        if charts:
            st.markdown("### 📈 AI-Generated Charts")
            chart_cols = st.columns(2)
            for i, spec in enumerate(charts[:6]):
                fig = build_chart(
                    df,
                    spec.get("type", "bar"),
                    spec.get("x", df.columns[0]),
                    spec.get("y", df.columns[1] if len(df.columns) > 1 else df.columns[0]),
                    title=spec.get("title", ""),
                )
                if fig:
                    with chart_cols[i % 2]:
                        st.plotly_chart(fig, use_container_width=True)

    # ── AI Recommendations ──
    st.markdown("---")
    st.markdown('<div class="step-label">STEP 3 — AI RECOMMENDATIONS</div>', unsafe_allow_html=True)
    st.markdown("## AI Recommendations")

    if st.button("🎯 Generate Recommendations", key="gen_recs", use_container_width=True):
        if st.session_state.analysis_result is None:
            st.warning("Run the AI Analyst first.")
        else:
            with st.spinner("Generating recommendations…"):
                insights_text = json.dumps(st.session_state.analysis_result.get("key_insights", []))
                prompt = f"""
Based on this analysis of the question "{question}", provide 5 specific, actionable business recommendations.
Insights: {insights_text}

Return ONLY JSON array:
[
  {{"action": "<short action title>", "detail": "<2 sentence explanation>", "impact": "<High/Medium/Low>", "timeline": "<1 week/1 month/1 quarter>"}},
  ...
]
"""
                try:
                    raw = ask_claude(prompt, max_tokens=1500)
                    recs = parse_json_response(raw)
                    if isinstance(recs, list):
                        st.session_state.recommendations = recs
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.recommendations:
        for rec in st.session_state.recommendations:
            impact = rec.get("impact", "Medium")
            color  = {"High": "#FF5C00", "Medium": "#FFBB33", "Low": "#4ADE80"}.get(impact, "#888")
            st.markdown(f"""
            <div class="info-card">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem">
                <h4 style="margin:0">{rec.get('action','')}</h4>
                <span style="font-size:0.75rem;color:{color};font-weight:700;font-family:'Space Grotesk',sans-serif">{impact} IMPACT · {rec.get('timeline','')}</span>
              </div>
              <p>{rec.get('detail','')}</p>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — EXPLORE
# ═══════════════════════════════════════════════════════════════════════════════
def tab_explore():
    if st.session_state.df is None:
        st.info("Upload data in the **Setup** tab first.")
        return

    df = st.session_state.df_clean

    st.markdown('<div class="step-label">STEP 4 — NATURAL LANGUAGE QUERY</div>', unsafe_allow_html=True)
    st.markdown("## Ask Questions")
    st.markdown("Ask anything about your data in plain English — get real answers + charts.")

    query = st.text_input(
        "",
        placeholder="e.g., Which region has the highest revenue this month?",
        key="nl_query",
        label_visibility="collapsed",
    )

    c1, c2 = st.columns([4, 1])
    with c2:
        ask_btn = st.button("Ask →", key="ask_btn", use_container_width=True)

    if ask_btn and query.strip():
        with st.spinner("Thinking…"):
            summary = df_summary(df, max_rows=3)
            prompt = f"""
You are a data analyst. The user asks: "{query}"

Dataset summary:
{summary}

Return ONLY valid JSON:
{{
  "answer": "<clear 2-3 sentence answer>",
  "chart": {{"type": "<bar/line/pie/scatter/etc>", "x": "<col>", "y": "<col>", "title": "<title>"}} or null,
  "table": <true if showing top rows would help, else false>
}}
"""
            try:
                raw = ask_claude(prompt, max_tokens=1000)
                parsed = parse_json_response(raw)
                st.session_state.nl_history.append({"query": query, "result": parsed})
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # History
    if st.session_state.nl_history:
        for item in reversed(st.session_state.nl_history[-5:]):
            res = item["result"]
            st.markdown(f"""
            <div class="info-card" style="border-left:3px solid #FF5C00">
              <p style="font-size:0.8rem;color:#FF5C00;font-weight:700;margin-bottom:0.3rem">❓ {item['query']}</p>
              <p style="margin:0">{res.get('answer','')}</p>
            </div>
            """, unsafe_allow_html=True)

            chart_spec = res.get("chart")
            if chart_spec:
                fig = build_chart(df, chart_spec.get("type","bar"), chart_spec.get("x",""), chart_spec.get("y",""), title=chart_spec.get("title",""))
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

            if res.get("table"):
                cols_mentioned = [c for c in df.columns if c.lower() in item["query"].lower()]
                show_cols = cols_mentioned[:4] if cols_mentioned else list(df.columns[:4])
                st.dataframe(df[show_cols].head(10), use_container_width=True)

    # ── Manual Chart Builder ──
    st.markdown("---")
    st.markdown('<div class="step-label">STEP 5 — CHART BUILDER</div>', unsafe_allow_html=True)
    st.markdown("## Build Your Own Chart")

    chart_types = ["bar", "line", "scatter", "area", "histogram", "box", "violin", "pie", "donut",
                   "heatmap", "funnel", "treemap", "sunburst", "bubble", "waterfall"]
    num_cols = list(df.select_dtypes(include=[np.number]).columns)
    all_cols = list(df.columns)

    c1, c2, c3, c4 = st.columns(4)
    with c1: ctype = st.selectbox("Chart type", chart_types, key="cb_type")
    with c2: cx    = st.selectbox("X axis", all_cols, key="cb_x")
    with c3: cy    = st.selectbox("Y axis", num_cols if num_cols else all_cols, key="cb_y")
    with c4: ctitle= st.text_input("Title", value="", key="cb_title")

    if st.button("Generate Chart", key="gen_chart"):
        fig = build_chart(df, ctype, cx, cy, title=ctitle or f"{ctype.title()}: {cy} by {cx}")
        if fig:
            st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 4 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
ROLE_TEMPLATES = {
    "Executive": "Revenue overview, profit margin trend, regional performance, top product mix, YoY growth KPIs",
    "Sales":     "Sales by rep/region, pipeline funnel, win rate trend, revenue by product, quota attainment",
    "Marketing": "Channel performance, CAC trend, campaign ROI, lead funnel, customer acquisition by region",
    "Operations":"Cost breakdown, efficiency metrics, SLA adherence, volume trends, capacity utilization",
    "Finance":   "P&L summary, revenue vs cost, margin analysis, cash flow trend, budget vs actual",
    "Customer":  "Satisfaction scores, churn rate, LTV segments, support tickets, NPS trend",
}

def tab_dashboard():
    if st.session_state.df is None:
        st.info("Upload data in the **Setup** tab first.")
        return

    df = st.session_state.df_clean
    question = st.session_state.business_question or "General analysis"

    st.markdown('<div class="step-label">STEP 6 — CUSTOM DASHBOARD</div>', unsafe_allow_html=True)
    st.markdown("## Generate Custom Dashboard")
    st.markdown("Use a template or describe exactly what you want.")

    role_cols = st.columns(len(ROLE_TEMPLATES))
    for i, (role, desc) in enumerate(ROLE_TEMPLATES.items()):
        with role_cols[i]:
            if st.button(role, key=f"role_{role}", use_container_width=True):
                st.session_state["dashboard_desc"] = desc
                st.rerun()

    desc = st.text_area(
        "Dashboard Description:",
        value=st.session_state.get("dashboard_desc", ""),
        placeholder="e.g., 'Executive overview with revenue KPIs, product mix donut chart, and regional bar chart'",
        height=80,
        key="dash_desc_input",
    )

    c1, c2 = st.columns([3, 1])
    with c1:
        gen_btn = st.button("🚀 Generate Dashboard", key="gen_dash", use_container_width=True)
    with c2:
        if st.button("Clear", key="clear_dash"):
            st.session_state.dashboard_charts = []
            st.rerun()

    if gen_btn:
        with st.spinner("Building your dashboard…"):
            summary = df_summary(df, max_rows=3)
            prompt = f"""
Create a dashboard for the business question: "{question}"
Dashboard focus: {desc or 'general overview'}

Dataset: {summary}

Return ONLY JSON array of 6 chart specs:
[
  {{"type": "<chart_type>", "x": "<col>", "y": "<col>", "color": "<col or null>", "title": "<title>", "size": "<full or half>"}},
  ...
]
Valid chart types: bar, line, scatter, pie, donut, area, heatmap, funnel, treemap, histogram, box
Use only columns that exist: {list(df.columns)}
"""
            try:
                raw = ask_claude(prompt, max_tokens=1500)
                specs = parse_json_response(raw)
                if isinstance(specs, list):
                    st.session_state.dashboard_charts = specs
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # Preset role dashboards
    st.markdown("---")
    st.markdown('<div class="step-label">STEP 7 — PRESET ROLE DASHBOARDS</div>', unsafe_allow_html=True)
    st.markdown("## Or Choose a Preset Dashboard")
    if st.button("📊 Generate 5 Role-Based Dashboards", key="role_dash", use_container_width=True):
        with st.spinner("Generating all role dashboards…"):
            num_cols = list(df.select_dtypes(include=[np.number]).columns)
            cat_cols = list(df.select_dtypes(include="object").columns)
            x = cat_cols[0] if cat_cols else df.columns[0]
            y = num_cols[0] if num_cols else df.columns[1]
            y2 = num_cols[1] if len(num_cols) > 1 else y
            specs = [
                {"type": "bar",  "x": x,  "y": y,  "title": f"Revenue by {x}"},
                {"type": "line", "x": x,  "y": y,  "title": f"{y} Trend"},
                {"type": "donut","x": x,  "y": y,  "title": f"{y} Mix"},
                {"type": "scatter","x": y, "y": y2, "title": f"{y} vs {y2}"},
                {"type": "histogram","x": y, "y": y, "title": f"{y} Distribution"},
                {"type": "box",  "x": x,  "y": y,  "title": f"{y} Range by {x}"},
            ]
            st.session_state.dashboard_charts = specs
            st.rerun()

    # Render dashboard
    if st.session_state.dashboard_charts:
        st.markdown("---")
        st.markdown("### 📊 Your Dashboard")
        charts_per_row = 2
        specs = st.session_state.dashboard_charts
        for i in range(0, len(specs), charts_per_row):
            row_specs = specs[i:i+charts_per_row]
            cols = st.columns(len(row_specs))
            for j, spec in enumerate(row_specs):
                fig = build_chart(
                    df,
                    spec.get("type", "bar"),
                    spec.get("x", df.columns[0]),
                    spec.get("y", df.columns[1] if len(df.columns) > 1 else df.columns[0]),
                    color=spec.get("color"),
                    title=spec.get("title", ""),
                )
                if fig:
                    with cols[j]:
                        st.plotly_chart(fig, use_container_width=True)

        # Export buttons
        st.markdown("---")
        st.markdown("### 📤 Export Dashboard")
        ec1, ec2, ec3 = st.columns(3)

        with ec1:
            # CSV export
            csv = df.to_csv(index=False)
            st.download_button("⬇ Download Data (CSV)", csv, "analyticdashai_data.csv", "text/csv", use_container_width=True)

        with ec2:
            # Excel export
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="Data", index=False)
                if st.session_state.analysis_result:
                    insights = st.session_state.analysis_result.get("key_insights", [])
                    if insights:
                        pd.DataFrame(insights).to_excel(writer, sheet_name="Insights", index=False)
            buf.seek(0)
            st.download_button("⬇ Download Excel Report", buf.read(), "analyticdashai_report.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

        with ec3:
            # JSON summary export
            export_data = {
                "generated": datetime.now().isoformat(),
                "business_question": question,
                "so_what": st.session_state.so_what,
                "anomalies": st.session_state.anomalies,
                "recommendations": st.session_state.recommendations or [],
            }
            st.download_button("⬇ Download AI Summary (JSON)", json.dumps(export_data, indent=2),
                               "analyticdashai_summary.json", "application/json", use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 5 — MONITOR
# ═══════════════════════════════════════════════════════════════════════════════
def tab_monitor():
    if st.session_state.df is None:
        st.info("Upload data in the **Setup** tab first.")
        return

    df = st.session_state.df_clean

    st.markdown('<div class="step-label">STEP 8 — MONITOR & ITERATE</div>', unsafe_allow_html=True)
    st.markdown("## Monitor & Iterate")
    st.markdown("Track KPI changes over time, detect anomalies, and get AI-driven iteration recommendations.")

    # ── KPI Configuration ──
    st.markdown("### ⚙ Configure KPIs to Monitor")

    with st.expander("Add / Edit Monitored KPIs"):
        num_cols = list(df.select_dtypes(include=[np.number]).columns)

        if st.button("⚡ Auto-detect KPIs from data", key="auto_kpi"):
            auto_kpis = {}
            for col in num_cols[:5]:
                auto_kpis[col] = {"value": float(df[col].mean()), "label": f"Avg {col}"}
            st.session_state.kpis = auto_kpis
            st.success(f"✓ Auto-detected {len(auto_kpis)} KPIs.")
            st.rerun()

        st.markdown("**Manual KPI Setup:**")
        mc1, mc2, mc3 = st.columns([2, 3, 1])
        with mc1: kpi_label = st.text_input("KPI Label", placeholder="e.g., Avg Revenue", key="kpi_label")
        with mc2: kpi_code  = st.text_input("Python code (assign to result)", placeholder="result = df['revenue'].mean()", key="kpi_code")
        with mc3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("+ Add KPI", key="add_kpi"):
                if kpi_label and kpi_code:
                    try:
                        local_vars = {"df": df, "pd": pd, "np": np}
                        exec(kpi_code, {}, local_vars)
                        val = local_vars.get("result", None)
                        if val is not None:
                            st.session_state.kpis[kpi_label] = {"value": float(val), "label": kpi_label}
                            st.success(f"✓ KPI '{kpi_label}' = {val:.2f}")
                            st.rerun()
                    except Exception as e:
                        st.error(f"KPI error: {e}")

    # Display KPIs
    if st.session_state.kpis:
        st.markdown("### 📊 Current KPIs")
        kpi_items = list(st.session_state.kpis.items())
        kcols = st.columns(min(len(kpi_items), 4))
        for i, (name, data) in enumerate(kpi_items[:4]):
            with kcols[i]:
                val = data.get("value", 0)
                st.metric(name, f"{val:,.2f}")

    # ── Snapshots ──
    st.markdown("---")
    st.markdown("### 📸 Snapshots")

    sc1, sc2 = st.columns([3, 2])
    with sc1: snap_label = st.text_input("Snapshot label:", placeholder="e.g., After Q2 cleaning", key="snap_label")
    with sc2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📸 Take Snapshot Now", key="snap_btn"):
            snap = {
                "label": snap_label or f"Snapshot {len(st.session_state.snapshots)+1}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "rows": len(df),
                "kpis": dict(st.session_state.kpis),
                "anomalies": list(st.session_state.anomalies),
            }
            st.session_state.snapshots.append(snap)
            st.success("✓ Snapshot saved.")
            st.rerun()

    if st.session_state.snapshots:
        for i, snap in enumerate(reversed(st.session_state.snapshots)):
            st.markdown(f"""
            <div class="info-card">
              <div style="display:flex;justify-content:space-between">
                <h4 style="margin:0">{snap['label']}</h4>
                <span style="font-size:0.78rem;color:#6B6B6B;font-family:'Space Grotesk',sans-serif">{snap['timestamp']}</span>
              </div>
              <p style="margin:0.3rem 0 0 0">{snap['rows']:,} rows · {len(snap['kpis'])} KPIs tracked · {len(snap['anomalies'])} anomalies</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:2.5rem;color:#6B6B6B;background:#1E1E1E;border-radius:10px;border:1px dashed #2E2E2E">
          <p style="font-size:2rem;margin:0">📸</p>
          <p style="margin:0.5rem 0 0 0;font-size:0.9rem">No snapshots yet<br><span style="font-size:0.8rem">Configure KPIs above, then take a snapshot to start monitoring.</span></p>
        </div>
        """, unsafe_allow_html=True)

    # ── Anomaly Monitor ──
    if st.session_state.anomalies:
        st.markdown("---")
        st.markdown("### ⚠️ Active Anomaly Alerts")
        for a in st.session_state.anomalies:
            st.markdown(f'<div class="anomaly-box">🔴 {a}</div>', unsafe_allow_html=True)
    else:
        if st.session_state.analysed:
            st.markdown("""
            <div class="info-card" style="border-color:#1A5C2A">
              <h4 style="color:#4ADE80">✓ No anomalies detected</h4>
              <p>Your data looks clean with no major statistical outliers.</p>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    render_header()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 1 · Setup",
        "🔬 2 · Analyse",
        "🔍 3 · Explore",
        "📊 4 · Dashboard",
        "📡 5 · Monitor",
    ])

    with tab1: tab_setup()
    with tab2: tab_analyse()
    with tab3: tab_explore()
    with tab4: tab_dashboard()
    with tab5: tab_monitor()


if __name__ == "__main__":
    main()
