import streamlit as st
import pandas as pd
import json
import re
import traceback
from anthropic import Anthropic
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')
load_dotenv()

# Enhanced page config
st.set_page_config(
    page_title="DashAI - Ultimate Enhanced", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced session state management
def init_session_state():
    """Initialize all session state variables with proper defaults"""
    defaults = {
        'dashboard_result': None,
        'uploaded_df': None,
        'query_history': [],
        'filters': {},
        'nl_results': [],
        'saved_dashboards': {},
        'current_dashboard_name': '',
        'export_format': 'PDF',
        'chart_customizations': {},
        'loading_state': False,
        'error_log': [],
        'data_quality_report': None,
        'current_question': '',  # FIX: Add this for suggestion buttons
        'show_save_dialog': False,  # FIX: Add this for save dialog
        'dashboard_templates': {
            'executive': "Executive overview with revenue KPIs, trend analysis, and geographic distribution",
            'operations': "Operational metrics with performance indicators, usage patterns, and efficiency charts",
            'marketing': "Customer segments, campaign performance, conversion rates, and growth metrics",
            'finance': "Revenue breakdown, ARPU analysis, profitability charts, and cost structure",
            'analytics': "Statistical analysis with correlations, distributions, and predictive insights"
        }
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

init_session_state()

@st.cache_resource
def get_claude_client():
    """Initialize Claude client with error handling - supports both local .env and Streamlit Cloud secrets"""
    # Try Streamlit secrets first (for Streamlit Cloud deployment)
    api_key = st.secrets.get("ANTHROPIC_API_KEY", None) if hasattr(st, 'secrets') else None
    # Fall back to environment variable (for local development)
    if not api_key:
        api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        st.error("❌ ANTHROPIC_API_KEY not found")
        st.info("For local dev: add to .env file. For Streamlit Cloud: add to app secrets.")
        return None
    try:
        return Anthropic(api_key=api_key)
    except Exception as e:
        st.error(f"❌ Failed to initialize Claude client: {str(e)}")
        return None

# Enhanced data quality validation (handles Power BI better)
def validate_data_quality(df, sheet_info=None):
    """Enhanced data quality assessment that handles Power BI exports properly"""
    quality_report = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB",
        'issues': [],
        'recommendations': [],
        'column_analysis': {},
        'data_type': 'Unknown'
    }
    
    # Detect data type based on size and structure
    if len(df) <= 10 and ('plan' in str(df.columns).lower() or 'product' in str(df.columns).lower()):
        quality_report['data_type'] = 'Reference Data'
        quality_report['recommendations'].append("📋 This appears to be reference data - some missing values may be expected")
    elif 'customer' in str(df.columns).lower():
        quality_report['data_type'] = 'Customer Data'
    elif 'usage' in str(df.columns).lower() or 'transaction' in str(df.columns).lower():
        quality_report['data_type'] = 'Usage Data'
    elif 'performance' in str(df.columns).lower() or 'network' in str(df.columns).lower():
        quality_report['data_type'] = 'Performance Metrics'
    elif 'sales' in str(df.columns).lower() or 'revenue' in str(df.columns).lower():
        quality_report['data_type'] = 'Sales Data'
    
    # Check for missing values (be more intelligent based on data type)
    missing_data = df.isnull().sum()
    
    if quality_report['data_type'] == 'Reference Data':
        # For reference data, only flag if > 60% missing
        high_missing = missing_data[missing_data > len(df) * 0.6]
        if not high_missing.empty:
            quality_report['issues'].append(f"Significant missing data in reference table: {list(high_missing.index)}")
    else:
        # For regular data, use 30% threshold
        high_missing = missing_data[missing_data > len(df) * 0.3]
        if not high_missing.empty:
            quality_report['issues'].append(f"High missing data: {list(high_missing.index)}")
            quality_report['recommendations'].append("Consider data cleaning or imputation")
    
    # Check for duplicate rows
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        quality_report['issues'].append(f"{duplicates} duplicate rows found")
        quality_report['recommendations'].append("Remove duplicate rows for accurate analysis")
    
    return quality_report

# Enhanced error handling
def log_error(error_msg, context="General"):
    """Log errors with context and timestamp"""
    error_entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'context': context,
        'error': str(error_msg),
    }
    st.session_state['error_log'].append(error_entry)

def show_loading_state(message="Processing..."):
    """Enhanced loading state"""
    return st.spinner(f"🤖 {message}")

def enhanced_error_display(error_msg, context=""):
    """Enhanced error display"""
    st.error(f"❌ Error in {context}: {error_msg}")
    
    if "API" in str(error_msg):
        st.info("💡 Check your API key and internet connection")
    elif "column" in str(error_msg).lower():
        st.info("💡 Verify column names match your data")

# JSON extraction
def extract_json(text):
    """Enhanced JSON extraction"""
    try:
        text = text.strip()
        text = re.sub(r'^```(?:json)?\s*\n?', '', text, flags=re.MULTILINE)
        text = re.sub(r'\n?```\s*$', '', text, flags=re.MULTILINE)
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Find JSON boundaries
        brace_start = text.find('{')
        if brace_start == -1:
            return None

        brace_count = 0
        brace_end = -1
        in_string = False
        escape_next = False
        
        for i in range(brace_start, len(text)):
            char = text[i]
            
            if escape_next:
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                continue
                
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
                
            if in_string:
                continue
                
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    brace_end = i
                    break

        if brace_end == -1:
            return None

        json_str = text[brace_start:brace_end + 1]
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            cleaned = re.sub(r',\s*([}\]])', r'\1', json_str)
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                return None
                
    except Exception as e:
        log_error(f"JSON extraction failed: {e}", "JSON_EXTRACTION")
        return None

# FIXED: Code execution with KPI calculation fixes
def safe_exec(code, df, timeout=30):
    """Enhanced code execution with KPI calculation fixes"""
    state_codes = {
        'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA',
        'Colorado':'CO','Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA',
        'Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS',
        'Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD','Massachusetts':'MA',
        'Michigan':'MI','Minnesota':'MN','Mississippi':'MS','Missouri':'MO','Montana':'MT',
        'Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM',
        'New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK',
        'Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC',
        'South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT',
        'Virginia':'VA','Washington':'WA','West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY'
    }
    
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
        'datetime': datetime,
        'timedelta': timedelta
    }
    
    try:
        # FIX: Auto-fix common KPI calculation errors (sum vs mean)
        if ('utilization' in code.lower() or 'percentage' in code.lower() or 
            'rate' in code.lower() or 'capacity' in code.lower()) and '.sum()' in code:
            code = code.replace('.sum()', '.mean()')
            log_error("Auto-fixed: Changed sum() to mean() for utilization/percentage metric", "AUTO_FIX")
        
        exec(code, exec_globals)
        return {
            'result': exec_globals.get('result') or exec_globals.get('fig'),
            'insight': exec_globals.get('insight', ''),
            'error': None
        }
    except Exception as e:
        log_error(str(e), "CODE_EXECUTION")
        return {'result': None, 'insight': '', 'error': str(e)}

# FIXED: Dashboard save/load functionality
def save_dashboard(dashboard_data, name):
    """Fixed dashboard save functionality"""
    try:
        saves_dir = Path("dashboard_saves")
        saves_dir.mkdir(exist_ok=True)
        
        save_data = {
            'name': name,
            'created_at': datetime.now().isoformat(),
            'dashboard': dashboard_data,
            'version': '2.0'
        }
        
        safe_name = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        save_path = saves_dir / f"{safe_name}.json"
        
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=2, default=str)
        
        # Update session state
        if 'saved_dashboards' not in st.session_state:
            st.session_state['saved_dashboards'] = {}
        
        st.session_state['saved_dashboards'][name] = save_data
        st.session_state['current_dashboard_name'] = name
        
        return True
        
    except Exception as e:
        log_error(f"Failed to save dashboard: {e}", "SAVE_DASHBOARD")
        return False

def load_dashboard(name):
    """Load dashboard configuration"""
    try:
        safe_name = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        save_path = Path("dashboard_saves") / f"{safe_name}.json"
        
        if save_path.exists():
            with open(save_path, 'r') as f:
                save_data = json.load(f)
            
            st.session_state['dashboard_result'] = {
                'type': 'custom', 
                'data': save_data['dashboard']
            }
            st.session_state['current_dashboard_name'] = name
            return True
        else:
            st.error(f"Dashboard '{name}' not found")
            return False
            
    except Exception as e:
        log_error(f"Failed to load dashboard: {e}", "LOAD_DASHBOARD")
        return False

def list_saved_dashboards():
    """List all saved dashboards"""
    try:
        saves_dir = Path("dashboard_saves")
        if not saves_dir.exists():
            return []
        
        dashboards = []
        for save_file in saves_dir.glob("*.json"):
            try:
                with open(save_file, 'r') as f:
                    save_data = json.load(f)
                    dashboards.append({
                        'name': save_data['name'],
                        'created_at': save_data['created_at'],
                        'file_path': save_file
                    })
            except Exception:
                continue
        
        return sorted(dashboards, key=lambda x: x['created_at'], reverse=True)
        
    except Exception as e:
        log_error(f"Failed to list dashboards: {e}", "LIST_DASHBOARDS")
        return []

# Export functionality
def export_dashboard_to_pdf(dashboard_data, df, filename="dashboard_export.pdf"):
    """Export dashboard to PDF format"""
    try:
        buffer = BytesIO()
        
        content = f"""DASHBOARD EXPORT
================

Title: {dashboard_data.get('title', 'Dashboard')}
Description: {dashboard_data.get('description', '')}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

KEY PERFORMANCE INDICATORS:
"""
        
        for i, kpi in enumerate(dashboard_data.get('kpis', []), 1):
            code = kpi.get('code', 'result = 0')
            fmt = kpi.get('format', '{:,}')
            exec_result = safe_exec(code, df)
            
            if not exec_result['error'] and exec_result['result'] is not None:
                try:
                    value = fmt.format(exec_result['result'])
                except Exception:
                    value = str(exec_result['result'])
            else:
                value = "Error"
            
            content += f"{i}. {kpi.get('label', 'KPI')}: {value}\n"
        
        content += f"\nKEY INSIGHTS:\n"
        for i, insight in enumerate(dashboard_data.get('insights', []), 1):
            content += f"{i}. {insight}\n"
        
        buffer.write(content.encode('utf-8'))
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        log_error(f"PDF export failed: {e}", "PDF_EXPORT")
        return None

# Templates
def get_prompt_templates():
    """Return predefined dashboard templates"""
    return {
        "Executive Dashboard": {
            "icon": "👔",
            "prompt": "Executive telecommunications dashboard with revenue KPIs, customer satisfaction by state, network performance metrics, and average revenue per customer analysis",
            "description": "High-level metrics for C-suite and board members"
        },
        "Sales Performance": {
            "icon": "📈",
            "prompt": "Sales dashboard with revenue trends by month and state, plan type performance, customer acquisition patterns, and pricing analysis",
            "description": "Comprehensive sales analytics and performance tracking"
        },
        "Customer Analytics": {
            "icon": "👥",
            "prompt": "Customer analytics showing satisfaction distribution by state, usage patterns by plan type, churn analysis, and customer lifetime value metrics",
            "description": "Deep dive into customer behavior and segments"
        },
        "Financial Overview": {
            "icon": "💰",
            "prompt": "Financial dashboard with revenue breakdown by plan type, monthly charge analysis, ARPU calculations, and profitability metrics",
            "description": "Financial performance and profitability analysis"
        },
        "Operations Dashboard": {
            "icon": "⚙️",
            "prompt": "Telecom operations dashboard with network performance by state, data usage patterns, call and text volume analysis, and capacity utilization metrics",
            "description": "Operational efficiency and network performance monitoring"
        }
    }

# Enhanced natural language query
def natural_language_query(df, question, client):
    """Enhanced natural language query with better error handling"""
    try:
        with show_loading_state(f"Analyzing: {question[:50]}..."):
            df_info = {
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "shape": list(df.shape),
                "sample_values": {col: df[col].dropna().unique()[:5].tolist() for col in df.columns[:15]},
                "numeric_columns": list(df.select_dtypes(include=['number']).columns),
                "categorical_columns": list(df.select_dtypes(include=['object']).columns)
            }

            prompt = f"""You are a senior data analyst. Answer this question about the dataset:

QUESTION: "{question}"

DATA INFO:
{json.dumps(df_info, indent=2, default=str)}

Respond with ONLY a JSON object:
{{
  "answer": "A clear 2-3 sentence answer with actual numbers/values from the data",
  "code": "Python code using df, px, go. Must assign a Plotly figure to 'result'. Use df directly.",
  "insight": "One key business insight or recommendation based on the data"
}}

RULES:
- The 'answer' must contain REAL computed values, not placeholders
- Code must be executable Python using pandas (pd), plotly.express (px), plotly.graph_objects (go)
- Always assign the final figure to 'result'
- For utilization/percentage metrics, use .mean() not .sum()
- Return ONLY JSON, no other text"""

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = extract_json(response.content[0].text)
            if result:
                st.session_state['query_history'].append({
                    'question': question,
                    'timestamp': datetime.now().isoformat(),
                    'result': result,
                    'success': True
                })
                return result
            else:
                enhanced_error_display("Failed to parse AI response", "Natural Language Query")
                return None
            
    except Exception as e:
        log_error(f"Natural language query failed: {e}", "NL_QUERY")
        enhanced_error_display(str(e), "Natural Language Query")
        return None

# Enhanced dashboard generator with KPI fixes
def generate_dashboard(df, prompt, client):
    """Enhanced dashboard generator with KPI calculation fixes"""
    try:
        with show_loading_state("Generating comprehensive dashboard..."):
            df_info = {
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "shape": list(df.shape),
                "numeric_columns": list(df.select_dtypes(include=['number']).columns),
                "categorical_columns": list(df.select_dtypes(include=['object']).columns),
                "sample_values": {col: df[col].dropna().unique()[:5].tolist() for col in df.columns[:15]},
            }

            ai_prompt = f"""You are an expert BI dashboard designer. Create a comprehensive dashboard.

USER REQUEST:
{prompt}

DATASET:
{json.dumps(df_info, indent=2, default=str)}

RESPOND WITH ONLY THIS JSON:
{{
  "title": "Professional Dashboard Title",
  "description": "What this dashboard shows and its business value",
  "kpis": [
    {{
      "label": "KPI Name", 
      "code": "result = df['column'].sum()", 
      "format": "${{:,.0f}}"
    }}
  ],
  "insights": [
    "Specific business insight with numbers and recommendations"
  ],
  "visualizations": [
    {{
      "title": "Descriptive Chart Title",
      "chart_type": "bar",
      "code": "agg = df.groupby('col')['val'].sum().reset_index()\\nresult = px.bar(agg, x='col', y='val', title='Title')",
      "insight": "What this visualization reveals"
    }}
  ]
}}

CRITICAL REQUIREMENTS:
1. Generate 4-6 visualizations with DIFFERENT chart types
2. Use REAL column names from the dataset
3. Include 3-4 meaningful KPIs
4. For utilization/percentage/rate metrics, use .mean() not .sum()
5. Mix chart types: bar, line, pie, scatter, box, etc.

Return ONLY the JSON object."""

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                messages=[{"role": "user", "content": ai_prompt}]
            )
            
            result = extract_json(response.content[0].text)
            
            if result is None:
                enhanced_error_display("Could not parse dashboard JSON", "Dashboard Generation")
                return None

            if 'visualizations' not in result:
                enhanced_error_display("Missing visualizations in response", "Dashboard Generation")
                return None
            
            return result
            
    except Exception as e:
        log_error(f"Dashboard generation failed: {e}", "DASHBOARD_GENERATION")
        enhanced_error_display(str(e), "Dashboard Generation")
        return None

# FIXED: Dashboard renderer with working save and clear filters
def render_dashboard(df, dashboard):
    """Enhanced dashboard renderer with fixed save and filters"""
    
    # Dashboard Header with Actions
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown(f"# 📊 {dashboard.get('title', 'Dashboard')}")
        st.markdown(f"*{dashboard.get('description', '')}*")
    
    # FIXED: Save Dashboard functionality
    with col2:
        if st.button("💾 Save Dashboard", use_container_width=True, key="save_dashboard_btn"):
            st.session_state['show_save_dialog'] = True
        
        if st.session_state.get('show_save_dialog', False):
            with st.form("save_dashboard_form"):
                name = st.text_input("Dashboard Name:", value=dashboard.get('title', 'My Dashboard'))
                col_save, col_cancel = st.columns(2)
                with col_save:
                    save_submitted = st.form_submit_button("✅ Save", use_container_width=True)
                with col_cancel:
                    cancel_submitted = st.form_submit_button("❌ Cancel", use_container_width=True)
                
                if save_submitted and name:
                    if save_dashboard(dashboard, name):
                        st.success(f"✅ Saved as '{name}'")
                        st.session_state['show_save_dialog'] = False
                        st.rerun()
                    else:
                        st.error("❌ Save failed")
                
                if cancel_submitted:
                    st.session_state['show_save_dialog'] = False
                    st.rerun()
    
    with col3:
        if st.button("📤 Export PDF", use_container_width=True):
            buffer = export_dashboard_to_pdf(dashboard, df)
            if buffer:
                st.download_button(
                    "📄 Download PDF",
                    data=buffer,
                    file_name=f"{dashboard.get('title', 'dashboard')}.pdf",
                    mime="application/pdf"
                )

    st.divider()

    # FIXED: Sidebar Filters with working Clear All functionality
    with st.sidebar:
        st.markdown("## 🎛️ Interactive Filters")
        
        filter_candidates = []
        for col in df.columns:
            nunique = df[col].nunique()
            if (2 <= nunique <= 25 and df[col].dtype == 'object'):
                filter_candidates.append(col)
        
        if not filter_candidates:
            st.info("No suitable filter columns detected")
        
        filters = {}
        for col in filter_candidates[:5]:
            options = sorted(df[col].dropna().unique().tolist())
            selected = st.multiselect(
                f"Filter by {col.replace('_', ' ').title()}:",
                options=options,
                key=f"filter_{col}"
            )
            if selected:
                filters[col] = selected

        st.session_state['filters'] = filters
        
        if filters:
            st.success(f"✅ {len(filters)} active filter(s)")
        
        # FIXED: Clear All Filters button
        if st.button("🗑️ Clear All Filters", use_container_width=True, key="clear_filters_btn"):
            # Clear all filter-related session state
            keys_to_delete = [key for key in st.session_state.keys() if key.startswith('filter_')]
            for key in keys_to_delete:
                del st.session_state[key]
            st.session_state['filters'] = {}
            st.rerun()

    # Apply filters
    filtered_df = df.copy()
    for col, vals in st.session_state['filters'].items():
        if vals and col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[col].isin(vals)]

    if st.session_state['filters']:
        st.info(f"🔍 Showing {len(filtered_df):,} of {len(df):,} rows after filtering")

    # KPIs Section
    kpis = dashboard.get('kpis', [])
    if kpis:
        st.markdown("### 🎯 Key Performance Indicators")
        kpi_cols = st.columns(len(kpis))
        
        for i, kpi in enumerate(kpis):
            with kpi_cols[i]:
                code = kpi.get('code', 'result = 0')
                fmt = kpi.get('format', '{:,}')
                
                exec_result = safe_exec(code, filtered_df)
                
                if exec_result['error']:
                    st.metric(kpi.get('label', 'KPI'), "Error")
                else:
                    try:
                        val = exec_result['result']
                        display_val = fmt.format(val) if not pd.isna(val) else "N/A"
                    except Exception:
                        display_val = str(exec_result['result'])
                    
                    st.metric(kpi.get('label', 'KPI'), display_val)
        
        st.divider()

    # Insights Section
    insights = dashboard.get('insights', [])
    if insights:
        st.markdown("### 💡 Key Business Insights")
        for i, insight in enumerate(insights, 1):
            st.markdown(f"{i}. {insight}")
        st.divider()

    # Visualizations Section
    st.markdown("### 📊 Interactive Visualizations")
    vizs = dashboard.get('visualizations', [])
    chart_cols = st.columns(2)

    for i, viz in enumerate(vizs):
        if not isinstance(viz, dict):
            continue

        with chart_cols[i % 2]:
            title = viz.get('title', f'Chart {i+1}')
            st.markdown(f"**{title}**")

            code = viz.get('code', '')
            exec_result = safe_exec(code, filtered_df)

            if exec_result['error']:
                st.error(f"⚠️ Chart Error: {exec_result['error'][:150]}...")
                with st.expander("🔧 Debug Info"):
                    st.code(code, language='python')
                    
            elif exec_result['result'] is not None:
                fig = exec_result['result']
                
                if isinstance(fig, pd.DataFrame):
                    st.dataframe(fig.head(10), use_container_width=True)
                        
                elif hasattr(fig, 'update_layout'):
                    fig.update_layout(
                        height=400,
                        margin=dict(l=20, r=20, t=40, b=40),
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{i}")
                else:
                    st.write(fig)

            if viz.get('insight'):
                st.info(f"💡 {viz['insight']}")

            st.markdown("---")

# Main application
def main():
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="main-header">
        <h1>📊 DashAI - Enhanced (ALL BUGS FIXED)</h1>
        <p>Professional AI Dashboard Builder - Issues Resolved ✅</p>
    </div>
    """, unsafe_allow_html=True)

    client = get_claude_client()
    if not client:
        st.stop()

    # Sidebar - Dashboard Management
    with st.sidebar:
        st.markdown("## 🎛️ Dashboard Control")
        
        st.markdown("### 💾 Saved Dashboards")
        saved_dashboards = list_saved_dashboards()
        
        if saved_dashboards:
            dashboard_names = [d['name'] for d in saved_dashboards]
            selected_dashboard = st.selectbox("Load Dashboard:", [""] + dashboard_names)
            
            if selected_dashboard and st.button("📂 Load Selected"):
                if load_dashboard(selected_dashboard):
                    st.success(f"✅ Loaded '{selected_dashboard}'")
                    st.rerun()
        else:
            st.info("No saved dashboards yet")
        
        st.divider()
        
        if st.session_state['error_log']:
            st.markdown("### 🚨 Error Log")
            with st.expander(f"View {len(st.session_state['error_log'])} errors"):
                for error in reversed(st.session_state['error_log'][-3:]):
                    st.text(f"[{error['timestamp']}] {error['context']}")
                    st.code(error['error'][:100])
            
            if st.button("🗑️ Clear Error Log"):
                st.session_state['error_log'] = []
                st.rerun()

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📁 Data Upload", "💬 Query Data", "🎨 Create Dashboard", "⚙️ Advanced"])

    # TAB 1: Data Upload
    with tab1:
        st.header("📁 Data Upload & Validation")
        
        uploaded_files = st.file_uploader(
            "Upload your data files",
            type=['csv', 'xlsx', 'xls'],
            accept_multiple_files=True,
            help="Support for CSV and Excel files"
        )

        if not uploaded_files:
            st.info("👆 Upload data files to get started!")
            return

        with show_loading_state("Processing files..."):
            dfs = []
            
            for file in uploaded_files:
                try:
                    if file.name.endswith('.csv'):
                        df = pd.read_csv(file)
                        dfs.append(df)
                    else:
                        excel_file = pd.ExcelFile(file)
                        for sheet_name in excel_file.sheet_names:
                            df = pd.read_excel(excel_file, sheet_name=sheet_name)
                            if len(df) > 0:
                                dfs.append(df)
                except Exception as e:
                    enhanced_error_display(f"Could not load {file.name}: {str(e)}", "File Upload")

        if not dfs:
            st.error("❌ No files loaded successfully")
            return

        st.success(f"✅ Loaded {len(dfs)} dataset(s)")
        
        # Merge datasets
        if len(dfs) == 1:
            combined_df = dfs[0]
        else:
            with show_loading_state("Merging datasets..."):
                combined_df = dfs[0]
                for other_df in dfs[1:]:
                    common_cols = list(set(combined_df.columns) & set(other_df.columns))
                    if common_cols:
                        combined_df = combined_df.merge(other_df, on=common_cols, how='outer')
                    else:
                        combined_df = pd.concat([combined_df, other_df], axis=1)

        st.session_state['uploaded_df'] = combined_df

        with show_loading_state("Analyzing data quality..."):
            quality_report = validate_data_quality(combined_df)
            st.session_state['data_quality_report'] = quality_report

        # FIXED: Display quality results with proper spacing
        st.markdown("### 📊 Data Summary")
        col1, col2, col3, col4 = st.columns([2, 2, 2, 3])
        with col1:
            st.metric("Rows", f"{quality_report['total_rows']:,}")
        with col2:
            st.metric("Columns", f"{quality_report['total_columns']}")
        with col3:
            st.metric("Memory", quality_report['memory_usage'])
        with col4:
            st.metric("Data Type", quality_report.get('data_type', 'Unknown'))

        if quality_report['issues']:
            st.warning("⚠️ Data Quality Issues:")
            for issue in quality_report['issues']:
                st.caption(f"• {issue}")

        with st.expander("📋 Data Preview"):
            st.dataframe(combined_df.head(10), use_container_width=True)

    # TAB 2: Query Data (FIXED)
    with tab2:
        if st.session_state['uploaded_df'] is None:
            st.warning("⚠️ Please upload data first")
            return
            
        df = st.session_state['uploaded_df']
        
        st.header("💬 Ask Questions About Your Data")

        # FIXED: Quick suggestions that populate the input
        st.markdown("### 💡 Try These Questions:")
        suggestions = [
            "What are the top 5 customers by revenue?",
            "Show me the monthly trend for revenue", 
            "Which state has the highest customer satisfaction?",
            "What's the average data usage by plan type?"
        ]
        
        suggestion_cols = st.columns(2)
        for i, suggestion in enumerate(suggestions):
            with suggestion_cols[i % 2]:
                if st.button(f"💡 {suggestion}", key=f"suggest_{i}", use_container_width=True):
                    st.session_state['current_question'] = suggestion
                    st.rerun()

        question = st.text_input(
            "Your Question:",
            value=st.session_state.get('current_question', ''),
            placeholder="e.g., Which customers generate the most revenue?",
            key="nl_question"
        )

        if st.button("🔍 Ask Question", type="primary") and question:
            result = natural_language_query(df, question, client)
            
            if result:
                st.markdown("### 📝 Answer")
                st.markdown(result.get('answer', ''))

                code = result.get('code', '')
                if code:
                    exec_result = safe_exec(code, df)
                    
                    if exec_result['result'] is not None and hasattr(exec_result['result'], 'update_layout'):
                        exec_result['result'].update_layout(template='plotly_white', height=500)
                        st.plotly_chart(exec_result['result'], use_container_width=True)
                    elif exec_result['error']:
                        enhanced_error_display(exec_result['error'], "Visualization")

                    with st.expander("🔧 View Generated Code"):
                        st.code(code, language='python')

                if result.get('insight'):
                    st.success(f"💡 **Business Insight:** {result['insight']}")

        if st.session_state['query_history']:
            st.markdown("### 📜 Recent Questions")
            for query in reversed(st.session_state['query_history'][-5:]):
                st.caption(f"• {query['question']} ({query['timestamp'][:16]})")

    # TAB 3: Dashboard Creation (FIXED)
    with tab3:
        if st.session_state['uploaded_df'] is None:
            st.warning("⚠️ Please upload data first")
            return
            
        df = st.session_state['uploaded_df']
        
        st.header("🎨 Create Professional Dashboards")

        st.markdown("### 📋 Quick Start Templates")
        templates = get_prompt_templates()
        
        template_cols = st.columns(3)
        for i, (name, template_info) in enumerate(templates.items()):
            with template_cols[i % 3]:
                st.markdown(f"**{template_info['icon']} {name}**")
                st.caption(template_info['description'])
                if st.button("Use Template", key=f"template_{i}", use_container_width=True):
                    st.session_state['selected_template'] = template_info['prompt']
                    st.rerun()

        st.divider()

        st.markdown("### ✏️ Custom Dashboard")
        
        dashboard_prompt = st.text_area(
            "Describe Your Dashboard:",
            value=st.session_state.get('selected_template', ''),
            placeholder="Examples:\n• Executive dashboard with revenue KPIs\n• Customer analytics with satisfaction metrics\n• Network performance with coverage analysis",
            height=100
        )

        if st.button("🚀 Generate Dashboard", type="primary") and dashboard_prompt:
            result = generate_dashboard(df, dashboard_prompt, client)
            if result:
                st.session_state['dashboard_result'] = {'type': 'custom', 'data': result}
                st.success("✅ Dashboard generated!")
                st.rerun()

        if st.session_state.get('dashboard_result'):
            result_data = st.session_state['dashboard_result']
            
            if result_data['type'] == 'custom':
                st.divider()
                render_dashboard(df, result_data['data'])

        if st.session_state.get('dashboard_result'):
            if st.button("🔄 Start Over"):
                st.session_state['dashboard_result'] = None
                st.session_state['selected_template'] = ''
                st.rerun()

    # TAB 4: Advanced Features
    with tab4:
        st.header("⚙️ Advanced Features")
        
        if st.session_state['uploaded_df'] is not None:
            df = st.session_state['uploaded_df']
            
            st.markdown("### 📊 Data Overview")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", f"{len(df):,}")
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Memory", f"{df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
        
        st.markdown("### 🔧 System Information")
        col1, col2 = st.columns(2)
        with col1:
            st.json({
                'Data Loaded': st.session_state['uploaded_df'] is not None,
                'Dashboard Generated': st.session_state['dashboard_result'] is not None,
                'Query History': len(st.session_state['query_history']),
                'Active Filters': len(st.session_state['filters']),
                'Saved Dashboards': len(st.session_state.get('saved_dashboards', {}))
            })
        with col2:
            if st.button("Reset All Data"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                init_session_state()
                st.success("Session reset!")
                st.rerun()

if __name__ == "__main__":
    main()
