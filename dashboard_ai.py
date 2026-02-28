import streamlit as st
import pandas as pd
import json
import re
import traceback
from anthropic import Anthropic
import os
from dotenv import load_dotenv
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

load_dotenv()

st.set_page_config(page_title="DashAI - Ultimate", page_icon="📊", layout="wide")

# Session state
for key in ['dashboard_result', 'uploaded_df', 'query_history', 'filters', 'nl_results']:
    if key not in st.session_state:
        if key in ('query_history', 'nl_results'):
            st.session_state[key] = []
        elif key == 'filters':
            st.session_state[key] = {}
        else:
            st.session_state[key] = None

@st.cache_resource
def get_claude_client():
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        st.error("❌ ANTHROPIC_API_KEY not found in .env")
        return None
    return Anthropic(api_key=api_key)

# ─────────────────────────────────────────────────────────
# ROBUST JSON EXTRACTION
# ─────────────────────────────────────────────────────────
def extract_json(text):
    """Extract JSON from AI response - handles markdown, extra text, trailing commas."""
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*\n?', '', text)
    text = re.sub(r'\n?```\s*$', '', text)
    text = text.strip()

    # Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find outermost braces
    brace_start = text.find('{')
    if brace_start == -1:
        return None

    depth = 0
    brace_end = -1
    in_string = False
    escape_next = False
    for i in range(brace_start, len(text)):
        ch = text[i]
        if escape_next:
            escape_next = False
            continue
        if ch == '\\':
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                brace_end = i
                break

    if brace_end == -1:
        return None

    json_str = text[brace_start:brace_end + 1]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    # Fix trailing commas
    cleaned = re.sub(r',\s*([}\]])', r'\1', json_str)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


def safe_exec(code, df):
    """Execute code safely with all needed libraries available. Auto-fixes common issues."""
    state_codes = {'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA','Colorado':'CO','Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA','Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS','Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD','Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS','Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA','West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY'}
    exec_globals = {
        'df': df.copy(),
        'pd': pd,
        'px': px,
        'go': go,
        'np': np,
        'state_codes': state_codes,
        'result': None,
        'fig': None,
        'insight': '',
    }
    try:
        exec(code, exec_globals)
        return {
            'result': exec_globals.get('result') or exec_globals.get('fig'),
            'insight': exec_globals.get('insight', ''),
            'error': None
        }
    except Exception as e:
        error_msg = str(e)
        # Auto-fix: remove unsupported 'size' from choropleth
        if 'choropleth' in code and "unexpected keyword argument 'size'" in error_msg:
            fixed_code = re.sub(r",\s*size=['\"]?[\w_]+['\"]?", '', code)
            try:
                exec_globals2 = {'df': df.copy(), 'pd': pd, 'px': px, 'go': go, 'np': np, 'result': None, 'fig': None, 'insight': ''}
                exec(fixed_code, exec_globals2)
                return {'result': exec_globals2.get('result') or exec_globals2.get('fig'), 'insight': exec_globals2.get('insight', ''), 'error': None}
            except Exception:
                pass
        # Auto-fix: remove unsupported keyword arguments generically
        if 'unexpected keyword argument' in error_msg:
            bad_kwarg = re.search(r"'(\w+)'", error_msg)
            if bad_kwarg:
                fixed_code = re.sub(rf",\s*{bad_kwarg.group(1)}=[^,)]+", '', code)
                try:
                    exec_globals3 = {'df': df.copy(), 'pd': pd, 'px': px, 'go': go, 'np': np, 'result': None, 'fig': None, 'insight': ''}
                    exec(fixed_code, exec_globals3)
                    return {'result': exec_globals3.get('result') or exec_globals3.get('fig'), 'insight': exec_globals3.get('insight', ''), 'error': None}
                except Exception:
                    pass
        return {'result': None, 'insight': '', 'error': error_msg}


# ─────────────────────────────────────────────────────────
# NATURAL LANGUAGE QUERY
# ─────────────────────────────────────────────────────────
def natural_language_query(df, question, client):
    """Ask a question about the data and get a real answer + visualization."""
    df_info = {
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "shape": list(df.shape),
        "sample_values": {col: df[col].dropna().unique()[:5].tolist() for col in df.columns[:15]},
    }

    prompt = f"""You are a senior data analyst. Answer this question about the dataset:

QUESTION: "{question}"

DATA INFO:
{json.dumps(df_info, indent=2, default=str)}

Respond with ONLY a JSON object:
{{
  "answer": "A clear 2-3 sentence answer with actual numbers/values from the data",
  "code": "Python code using df, px, go. Must assign a Plotly figure to 'result'. Use df directly - it's already loaded.",
  "insight": "One key business insight or recommendation"
}}

RULES:
- The 'answer' must contain REAL computed values, not placeholders
- Code must be executable Python using pandas (pd), plotly.express (px), plotly.graph_objects (go)
- Always assign the final figure to 'result'
- For metrics/numbers, compute them in code and include in 'answer'
- Return ONLY JSON, no other text"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        return extract_json(response.content[0].text)
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


# ─────────────────────────────────────────────────────────
# DASHBOARD GENERATOR - Gemini-style: real code per chart
# ─────────────────────────────────────────────────────────
def generate_dashboard(df, prompt, client):
    """Generate a complete dashboard with REAL executable code for each visualization."""
    df_info = {
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "shape": list(df.shape),
        "numeric_columns": list(df.select_dtypes(include=['number']).columns),
        "categorical_columns": list(df.select_dtypes(include=['object']).columns),
        "sample_values": {col: df[col].dropna().unique()[:5].tolist() for col in df.columns[:15]},
    }
    # Add dedup hint if customer_id exists
    if 'customer_id' in df.columns:
        n_unique = df['customer_id'].nunique()
        df_info['note'] = f"Dataset has {len(df)} rows but only {n_unique} unique customers. Multiple rows per customer (monthly records). Deduplicate on customer_id for customer-level metrics."

    dataset_str = json.dumps(df_info, indent=2, default=str)
    ai_prompt = ("You are an expert BI dashboard designer. Create a complete dashboard.\n\n"
        "USER REQUEST:\n" + prompt + "\n\n"
        "DATASET:\n" + dataset_str + "\n\n"
        'RESPOND WITH ONLY THIS JSON (no other text):\n'
        '{\n'
        '  "title": "Dashboard Title",\n'
        '  "description": "What this dashboard shows",\n'
        '  "kpis": [{"label": "KPI Name", "code": "result = df[\'column\'].sum()", "format": "${:,.0f}"}],\n'
        '  "insights": ["Key insight with specific numbers"],\n'
        '  "visualizations": [{"title": "Chart Title", "chart_type": "bar", "code": "agg = df.groupby(\'col\')[\'val\'].sum().reset_index()\\nresult = px.bar(agg, x=\'col\', y=\'val\')", "insight": "What this reveals"}]\n'
        '}\n\n'
        'CRITICAL RULES:\n'
        '1. Generate 4-6 visualizations with DIFFERENT chart types\n'
        '2. Each visualization code must be REAL executable Python creating a Plotly figure assigned to result\n'
        '3. Use ACTUAL column names from the dataset\n'
        '4. KPI code must compute a real value assigned to result\n'
        '5. KPI format uses Python format strings like ${:,.0f} or {:,} or {:.1f}/5 or {:.1%}\n'
        '6. Include 2-4 KPIs and 2-3 insights\n'
        '7. For map charts: use px.choropleth with locationmode=USA-states\n'
        '8. For donut: use px.pie with hole=0.4\n'
        '9. For gauge: use go.Figure(go.Indicator(...))\n'
        '10. Code has access to: df, pd, px, go, np, and state_codes (dict mapping full state name to 2-letter code)\n'
        '10b. IMPORTANT: If df has a customer_id column, the data may have MULTIPLE ROWS per customer (e.g. monthly records). For customer-level KPIs like churn rate, active count, etc. you MUST deduplicate first: customers = df.drop_duplicates(subset="customer_id", keep="last"). Then compute churn from that.\n'
        '11. For MAP/choropleth: Data has FULL state names. You MUST convert to 2-letter codes: agg["state_code"] = agg["state"].map(state_codes). Then px.choropleth(agg, locations="state_code", locationmode="USA-states", color="value_col", scope="usa", color_continuous_scale="Reds"). Do NOT pass size to choropleth.\n'
        '12. Return ONLY the JSON object')

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=6000,
            messages=[{"role": "user", "content": ai_prompt}]
        )
        text = response.content[0].text
        result = extract_json(text)

        if result is None:
            st.error("⚠️ Could not parse dashboard JSON from AI response.")
            with st.expander("🔍 Raw AI Response (debug)"):
                st.code(text[:1500])
            return None

        if 'visualizations' not in result:
            st.error("⚠️ AI response missing 'visualizations' key.")
            st.json(result)
            return None

        return result
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


# ─────────────────────────────────────────────────────────
# RENDER DASHBOARD
# ─────────────────────────────────────────────────────────
def render_dashboard(df, dashboard):
    """Render a dashboard by executing real code for each component."""

    # ── Sidebar Filters ──
    with st.sidebar:
        st.markdown("## 🎛️ Dashboard Filters")
        st.caption("Power BI-style slicers — filter all charts at once")
        
        # Only show filters for low-cardinality columns (useful slicers)
        all_cols = df.columns.tolist()
        slicer_cols = []
        for col in all_cols:
            nunique = df[col].nunique()
            # Skip high-cardinality (IDs, dates with many values) and numeric cols
            if nunique <= 20 and df[col].dtype == 'object' and 'id' not in col.lower() and 'date' not in col.lower():
                slicer_cols.append(col)
        
        if not slicer_cols:
            st.info("No suitable filter columns detected.")
        
        filters = {}
        for col in slicer_cols[:6]:
            options = sorted(df[col].dropna().unique().tolist())
            selected = st.multiselect(
                f"📌 {col.replace('_', ' ').title()}",
                options=options,
                key=f"slicer_{col}"
            )
            if selected:
                filters[col] = selected

        st.session_state['filters'] = filters
        if filters:
            st.success(f"✅ {len(filters)} filter(s) active")
        if st.button("🔄 Clear All Filters"):
            st.session_state['filters'] = {}
            st.rerun()

    # Apply filters
    filtered_df = df.copy()
    for col, vals in st.session_state['filters'].items():
        if vals and col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[col].isin(vals)]

    if st.session_state['filters']:
        st.info(f"🔍 Showing {len(filtered_df):,} / {len(df):,} rows after filtering")

    # ── Title & Description ──
    st.markdown(f"# 📊 {dashboard.get('title', 'Dashboard')}")
    st.markdown(f"*{dashboard.get('description', '')}*")
    st.divider()

    # ── KPIs ──
    kpis = dashboard.get('kpis', [])
    if kpis:
        st.markdown("### 🎯 Key Metrics")
        kpi_cols = st.columns(len(kpis))
        for i, kpi in enumerate(kpis):
            with kpi_cols[i]:
                code = kpi.get('code', 'result = 0')
                fmt = kpi.get('format', '{:,}')
                out = safe_exec(code, filtered_df)
                if out['error']:
                    st.metric(kpi.get('label', 'KPI'), "Error")
                    st.caption(f"⚠️ {out['error'][:60]}")
                else:
                    val = out['result']
                    try:
                        display_val = fmt.format(val)
                    except Exception:
                        display_val = str(val)
                    st.metric(kpi.get('label', 'KPI'), display_val)
        st.divider()

    # ── Insights ──
    insights = dashboard.get('insights', [])
    if insights:
        st.markdown("### 💡 Key Insights")
        for ins in insights:
            st.markdown(f"• {ins}")
        st.divider()

    # ── Visualizations ──
    st.markdown("### 📊 Visualizations")
    vizs = dashboard.get('visualizations', [])
    chart_cols = st.columns(2)

    for i, viz in enumerate(vizs):
        if not isinstance(viz, dict):
            continue

        with chart_cols[i % 2]:
            title = viz.get('title', f'Chart {i+1}')
            chart_type = viz.get('chart_type', 'bar')
            st.markdown(f"**{title}**")
            st.caption(f"*{chart_type.replace('_', ' ').title()}*")

            code = viz.get('code', '')
            out = safe_exec(code, filtered_df)

            if out['error']:
                st.warning(f"⚠️ Chart error: {out['error'][:100]}")
                with st.expander("View Code"):
                    st.code(code, language='python')
            elif out['result'] is not None:
                fig = out['result']
                if isinstance(fig, pd.DataFrame):
                    st.dataframe(fig, use_container_width=True)
                elif hasattr(fig, 'update_layout'):
                    fig.update_layout(
                        height=380,
                        margin=dict(l=20, r=20, t=40, b=20),
                        template='plotly_white'
                    )
                    st.plotly_chart(fig, use_container_width=True, key=f"dash_chart_{i}")
                else:
                    st.write(fig)

            # Insight below chart
            if viz.get('insight'):
                st.caption(f"💡 {viz['insight']}")

            st.markdown("---")


# ─────────────────────────────────────────────────────────
# PRESET DASHBOARDS
# ─────────────────────────────────────────────────────────
def generate_preset_dashboards(df, client):
    """Generate 5 role-based preset dashboard options."""
    df_info = {
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "numeric_columns": list(df.select_dtypes(include=['number']).columns),
        "categorical_columns": list(df.select_dtypes(include=['object']).columns),
        "shape": list(df.shape),
        "sample_values": {col: df[col].dropna().unique()[:5].tolist() for col in df.columns[:15]},
    }

    prompt = f"""Generate 5 different dashboard configurations for this dataset.

DATASET: {json.dumps(df_info, indent=2, default=str)}

Each dashboard targets a different business role. Respond with ONLY this JSON:
{{
  "dashboards": [
    {{
      "name": "Executive Overview",
      "icon": "👔",
      "audience": "C-Suite, Board Members",
      "description": "High-level business health metrics",
      "kpis": [
        {{"label": "KPI Name", "code": "result = df['col'].sum()", "format": "${{:,.0f}}"}}
      ],
      "insights": ["insight1", "insight2"],
      "visualizations": [
        {{
          "title": "Chart Title",
          "chart_type": "line",
          "code": "agg = df.groupby('x')['y'].sum().reset_index()\\nresult = px.line(agg, x='x', y='y', title='Title')",
          "insight": "What this shows"
        }}
      ]
    }}
  ]
}}

Create these 5 dashboards:
1. Executive Overview (C-Suite) - revenue trends, KPIs, geographic view
2. Operations (Managers) - operational metrics, usage patterns
3. Analytics Deep-Dive (Data Analysts) - correlations, distributions, statistical views
4. Marketing & Growth (Marketing Team) - customer segments, plan performance
5. Financial (CFO/Finance) - revenue breakdown, ARPU, profitability

RULES:
- Each dashboard: 3-4 KPIs, 4-6 visualizations, 2-3 insights
- KPI code must compute a value assigned to 'result'
- Visualization code must create a Plotly figure assigned to 'result'
- Use ACTUAL column names from the dataset
- Mix chart types: bar, line, donut, scatter, box, heatmap, treemap, funnel, gauge, waterfall, histogram, map
- Return ONLY JSON"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}]
        )
        result = extract_json(response.content[0].text)
        if result and 'dashboards' in result:
            return result
        st.error("⚠️ Could not parse preset dashboards.")
        with st.expander("Debug"):
            st.code(response.content[0].text[:1500])
        return None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


# ─────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────
def main():
    st.title("📊 DashAI — AI Dashboard Builder")
    st.markdown("*Real charts from real data • Natural language queries • Custom & preset dashboards*")
    st.divider()

    client = get_claude_client()
    if not client:
        st.stop()

    # ═══════════════════════════════════════
    # STEP 1: UPLOAD DATA
    # ═══════════════════════════════════════
    st.header("📁 Step 1: Upload Data")
    st.caption("Upload one or more CSV/Excel files — they'll be auto-merged")
    uploaded_files = st.file_uploader(
        "Drop your files here",
        type=['csv', 'xlsx', 'xls'],
        accept_multiple_files=True
    )

    if not uploaded_files:
        st.info("👆 Upload one or more CSV/Excel files to start!")
        st.markdown("### ✨ What's New in V5")
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown("**📊 Real Charts**"); c1.caption("AI writes actual Plotly code")
        c2.markdown("**💡 AI Insights**"); c2.caption("Data-driven observations")
        c3.markdown("**🔗 Multi-File**"); c3.caption("Upload multiple CSVs, auto-merged")
        c4.markdown("**🎛️ Live Filters**"); c4.caption("Slicers update all charts")
        return

    # Load and merge files
    dfs = []
    for f in uploaded_files:
        try:
            if f.name.endswith('.csv'):
                d = pd.read_csv(f)
                dfs.append(d)
                st.caption(f"✓ {f.name}: {len(d)} rows, {len(d.columns)} cols")
            else:
                # Excel: read ALL sheets and merge them
                xls = pd.ExcelFile(f)
                sheet_names = xls.sheet_names
                for sheet in sheet_names:
                    d = pd.read_excel(xls, sheet_name=sheet)
                    if len(d) > 0:
                        dfs.append(d)
                        st.caption(f"✓ {f.name} → {sheet}: {len(d)} rows, {len(d.columns)} cols")
        except Exception as e:
            st.warning(f"⚠️ Could not load {f.name}: {e}")

    if not dfs:
        st.error("No files loaded successfully.")
        return

    # Merge on shared columns if multiple files
    if len(dfs) == 1:
        df = dfs[0]
    else:
        df = dfs[0]
        for other in dfs[1:]:
            shared = list(set(df.columns) & set(other.columns))
            if shared:
                df = df.merge(other, on=shared, how='outer')
            else:
                df = pd.concat([df, other], axis=1)

    st.session_state['uploaded_df'] = df
    st.success(f"✅ Combined: {len(df):,} rows × {len(df.columns)} columns")

    with st.expander("📋 Data Preview"):
        st.dataframe(df.head(10), use_container_width=True)
        col_info = pd.DataFrame({
            'Type': df.dtypes.astype(str),
            'Non-Null': df.notna().sum(),
            'Unique': df.nunique(),
            'Sample': [str(df[c].dropna().iloc[0]) if len(df[c].dropna()) > 0 else 'N/A' for c in df.columns]
        })
        st.dataframe(col_info, use_container_width=True)

    st.divider()

    # ═══════════════════════════════════════
    # STEP 2: ASK QUESTIONS (Natural Language)
    # ═══════════════════════════════════════
    st.header("💬 Step 2: Ask Questions")
    st.caption("Ask anything about your data in plain English — get real answers + charts")

    col1, col2 = st.columns([4, 1])
    with col1:
        question = st.text_input("Your question", placeholder="e.g., Which state has the highest churn rate?")
    with col2:
        ask_btn = st.button("🔍 Ask", type="primary", use_container_width=True)

    if ask_btn and question:
        with st.spinner("🤖 Analyzing your data..."):
            result = natural_language_query(df, question, client)
            if result:
                # Answer
                st.markdown(f"### 📝 Answer")
                st.markdown(result.get('answer', ''))

                # Insight
                if result.get('insight'):
                    st.info(f"💡 **Insight:** {result['insight']}")

                # Chart
                code = result.get('code', '')
                if code:
                    out = safe_exec(code, df)
                    if out['result'] is not None and hasattr(out['result'], 'update_layout'):
                        out['result'].update_layout(template='plotly_white')
                        st.plotly_chart(out['result'], use_container_width=True)
                    elif out['error']:
                        st.warning(f"Chart error: {out['error'][:100]}")

                    with st.expander("🔧 View Code"):
                        st.code(code, language='python')

                st.session_state['query_history'].append({
                    'q': question, 'time': datetime.now().strftime('%H:%M:%S')
                })

    if st.session_state['query_history']:
        with st.expander("📜 Query History"):
            for q in reversed(st.session_state['query_history'][-5:]):
                st.markdown(f"`{q['time']}` — {q['q']}")

    st.divider()

    # ═══════════════════════════════════════
    # STEP 3: CUSTOM DASHBOARD
    # ═══════════════════════════════════════
    st.header("🎨 Step 3: Generate Custom Dashboard")
    st.caption("Describe what you want — simple or detailed, both work!")

    custom_prompt = st.text_area(
        "Dashboard Description",
        placeholder="e.g., 'Executive overview with revenue KPIs, plan mix donut chart, and geographic map'\n\nOr paste detailed specs with bullet points — DashAI handles it!",
        height=120
    )

    if st.button("🚀 Generate Custom Dashboard", type="primary", use_container_width=True):
        if custom_prompt:
            with st.spinner("🤖 Generating dashboard with real data visualizations..."):
                result = generate_dashboard(df, custom_prompt, client)
                if result:
                    st.session_state['dashboard_result'] = {'type': 'custom', 'data': result}
                    st.rerun()
        else:
            st.warning("Enter a description first!")

    st.divider()

    # ═══════════════════════════════════════
    # STEP 4: PRESET DASHBOARDS
    # ═══════════════════════════════════════
    st.header("🤖 Step 4: Or Choose a Preset Dashboard")

    if st.button("📊 Generate 5 Role-Based Dashboards", use_container_width=True):
        with st.spinner("🤖 Generating 5 dashboards with real charts..."):
            result = generate_preset_dashboards(df, client)
            if result:
                st.session_state['dashboard_result'] = {'type': 'presets', 'data': result}
                st.rerun()

    # ═══════════════════════════════════════
    # RENDER RESULTS
    # ═══════════════════════════════════════
    dash_result = st.session_state.get('dashboard_result')
    if dash_result:
        if dash_result['type'] == 'custom':
            st.divider()
            render_dashboard(df, dash_result['data'])

            if st.button("🔄 Generate New Dashboard", use_container_width=True):
                st.session_state['dashboard_result'] = None
                st.rerun()

        elif dash_result['type'] == 'presets':
            presets = dash_result['data']
            dashboards = presets.get('dashboards', [])
            st.success(f"✅ {len(dashboards)} dashboards generated!")

            st.markdown("### Select a Dashboard")
            cols = st.columns(min(len(dashboards), 5))
            for i, d in enumerate(dashboards):
                with cols[i % 5]:
                    icon = d.get('icon', '📊')
                    st.markdown(f"### {icon} {d.get('name', f'Dashboard {i+1}')}")
                    st.caption(d.get('audience', ''))
                    st.markdown(f"*{d.get('description', '')}*")
                    if st.button("Select", key=f"preset_{i}", use_container_width=True):
                        st.session_state['dashboard_result'] = {'type': 'custom', 'data': d}
                        st.rerun()

            if st.button("🔄 Regenerate All", use_container_width=True):
                st.session_state['dashboard_result'] = None
                st.rerun()


if __name__ == "__main__":
    main()
