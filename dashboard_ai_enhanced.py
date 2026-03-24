"""
AnalyticDashAI — Upload data. Ask anything. See everything.
V7: Intelligent Model Routing + Enhanced So What? + Large Dataset Support + Bug Fixes
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import re
import io
import os
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go

load_dotenv()

st.set_page_config(page_title="AnalyticDashAI", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
  html,body,[class*="css"]{font-family:'Plus Jakarta Sans',sans-serif!important;background-color:#0C0C0C;color:#FFF}
  .brand-header{padding:1.5rem 0 0.5rem;border-bottom:1px solid #1E1E1E;margin-bottom:1rem}
  .brand-title{font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:800;color:#FFF;margin:0;letter-spacing:-.5px}
  .brand-title span{color:#FF5C00}
  .brand-subtitle{font-size:.85rem;color:#6B6B6B;margin:.2rem 0 0;font-family:'Space Grotesk',sans-serif}
  .progress-bar{display:flex;gap:.5rem;flex-wrap:wrap;margin:.75rem 0}
  .badge{padding:.3rem .75rem;border-radius:999px;font-size:.72rem;font-weight:600;font-family:'Space Grotesk',sans-serif;border:1px solid #2E2E2E;background:#1E1E1E;color:#6B6B6B}
  .badge.done{background:#0C2010;border-color:#1A5C2A;color:#4ADE80}
  .step-label{display:inline-block;background:#1E1E1E;color:#FF5C00;font-family:'Space Grotesk',sans-serif;font-size:.72rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;padding:.3rem .8rem;border-radius:4px;border-left:3px solid #FF5C00;margin-bottom:.5rem}
  .info-card{background:#1E1E1E;border:1px solid #2E2E2E;border-radius:10px;padding:1rem 1.25rem;margin-bottom:1rem}
  .info-card h4{margin:0 0 .25rem;color:#FFF;font-size:.95rem}
  .info-card p{margin:0;color:#8B8B8B;font-size:.82rem}
  .so-what-box{background:linear-gradient(135deg,#1A1200,#1E1000);border:1px solid #FF5C00;border-left:4px solid #FF5C00;border-radius:10px;padding:1.25rem 1.5rem;margin:1rem 0}
  .so-what-box h4{color:#FF5C00;font-family:'Space Grotesk',sans-serif;font-size:.8rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin:0 0 .6rem}
  .so-what-box p{color:#E0E0E0;font-size:.92rem;line-height:1.6;margin:0 0 .5rem}
  .so-what-label{color:#FF5C00;font-size:.75rem;font-weight:700;font-family:'Space Grotesk',sans-serif;text-transform:uppercase;letter-spacing:.5px;margin:.75rem 0 .25rem}
  .so-what-box ul{margin:0;padding-left:1.2rem;color:#D0D0D0;font-size:.88rem}
  .so-what-box li{margin-bottom:.2rem}
  .so-what-meta{display:flex;gap:1.5rem;margin-top:.75rem;font-size:.78rem;font-family:'Space Grotesk',sans-serif}
  .so-what-meta span{color:#6B6B6B}
  .so-what-meta .val{color:#FF5C00;font-weight:700}
  .anomaly-box{background:#1A0A00;border:1px solid #FF3300;border-left:4px solid #FF3300;border-radius:8px;padding:.75rem 1rem;margin:.5rem 0;font-size:.85rem;color:#FFB3A0}
  .warn-box{background:#1A1000;border:1px solid #FFBB33;border-left:4px solid #FFBB33;border-radius:8px;padding:.6rem 1rem;margin:.4rem 0;font-size:.82rem;color:#FFE0A0}
  .router-badge{display:inline-flex;align-items:center;gap:.3rem;background:#111;border:1px solid #2E2E2E;border-radius:6px;padding:.15rem .5rem;font-size:.7rem;font-family:'Space Grotesk',sans-serif;color:#6B6B6B}
  .haiku-color{color:#4ADE80}.sonnet-color{color:#FFBB33}.opus-color{color:#FF5C00}
  .cost-pill{background:#0C2010;border:1px solid #1A5C2A;border-radius:999px;padding:.15rem .6rem;font-size:.7rem;color:#4ADE80;font-family:'Space Grotesk',sans-serif;font-weight:700}
  .stButton>button{background:#1E1E1E!important;color:#FFF!important;border:1px solid #2E2E2E!important;border-radius:8px!important;font-size:.85rem!important;transition:all .2s!important}
  .stButton>button:hover{border-color:#FF5C00!important;color:#FF5C00!important;background:#1A0E00!important}
  .stTabs [data-baseweb="tab-list"]{background:#1E1E1E;border-radius:10px;padding:4px;gap:2px}
  .stTabs [data-baseweb="tab"]{color:#6B6B6B!important;font-family:'Space Grotesk',sans-serif!important;font-weight:600!important;font-size:.85rem!important;border-radius:8px!important;padding:.5rem 1rem!important}
  .stTabs [aria-selected="true"]{background:#FF5C00!important;color:#FFF!important}
  [data-testid="metric-container"]{background:#1E1E1E;border:1px solid #2E2E2E;border-radius:10px;padding:1rem}
  .stTextArea textarea,.stTextInput input{background:#1E1E1E!important;border:1px solid #2E2E2E!important;color:#FFF!important;border-radius:8px!important}
  .stTextArea textarea:focus,.stTextInput input:focus{border-color:#FF5C00!important}
  .stSelectbox>div>div{background:#1E1E1E!important;border-color:#2E2E2E!important;color:#FFF!important}
  .streamlit-expanderHeader{background:#1E1E1E!important;border-radius:8px!important;color:#FFF!important}
  [data-testid="stFileUploader"]{background:#1E1E1E;border:2px dashed #2E2E2E;border-radius:10px}
  .pro-tip{background:#111;border-left:3px solid #FF5C00;padding:.5rem .9rem;border-radius:0 6px 6px 0;font-size:.82rem;color:#8B8B8B;margin:.5rem 0}
  .pro-tip span{color:#FF5C00;font-weight:700}
  #MainMenu,footer,header{visibility:hidden}
  .block-container{padding-top:1rem!important;max-width:1200px}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
MAX_ROWS_FULL    = 50_000
MAX_SAMPLE_ROWS  = 500
MAX_COLS_DESC    = 20

MODEL_PRICING = {
    "claude-haiku-4-5":  {"input": 0.80,  "output": 4.00},
    "claude-sonnet-4-5": {"input": 3.00,  "output": 15.0},
    "claude-opus-4-5":   {"input": 15.0,  "output": 75.0},
}
_SP = [r'\b(count|sum|average|mean|min|max|list|show|display|get|how many|total)\b']
_CP = [r'\b(why|explain|analyze|analyse|interpret|recommend|predict|strategy|correlation|forecast|trend|insight|impact|cause|reason)\b']
_KP = [r'\b(executive summary|final report|decision|board|stakeholder|investor|ceo|cfo)\b']

# ── Model Router ──────────────────────────────────────────────────────────────
def _complexity(task, rows=0):
    t = task.lower()
    for p in _KP:
        if re.search(p, t): return "critical"
    cs = sum(1 for p in _CP if re.search(p, t))
    ss = sum(1 for p in _SP if re.search(p, t))
    if rows > 100_000: cs += 1
    if cs >= 2: return "complex"
    if cs >= 1 or ss == 0: return "moderate"
    return "simple"

def route_model(task, rows=0, quality="auto"):
    if quality == "premium": return "claude-opus-4-5"
    if quality == "fast":    return "claude-haiku-4-5"
    m = {"simple":"claude-haiku-4-5","moderate":"claude-sonnet-4-5","complex":"claude-opus-4-5","critical":"claude-opus-4-5"}
    return m.get(_complexity(task, rows), "claude-sonnet-4-5")

def calc_cost(model, i, o):
    p = MODEL_PRICING.get(model, MODEL_PRICING["claude-sonnet-4-5"])
    return (i/1_000_000)*p["input"] + (o/1_000_000)*p["output"]

def mbadge(model):
    if "haiku"  in model: return '<span class="router-badge"><span class="haiku-color">&#9889; Haiku</span></span>'
    if "sonnet" in model: return '<span class="router-badge"><span class="sonnet-color">&#127919; Sonnet</span></span>'
    if "opus"   in model: return '<span class="router-badge"><span class="opus-color">&#128293; Opus</span></span>'
    return ""

# ── Client ────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    key = os.environ.get("ANTHROPIC_API_KEY","")
    if not key:
        try: key = st.secrets.get("ANTHROPIC_API_KEY","")
        except Exception: key = ""
    if not key:
        st.error("ANTHROPIC_API_KEY not found. Add it to .env or Streamlit secrets.")
        st.stop()
    return Anthropic(api_key=key)

def init_state():
    D = {"business_question":"","df":None,"df_clean":None,"filename":"",
         "analysis_result":None,"recommendations":None,"so_what":None,
         "anomalies":[],"charts":[],"dashboard_charts":[],"nl_history":[],
         "kpis":{},"snapshots":[],
         "question_set":False,"data_loaded":False,"analysed":False,"data_cleaned":False,
         "session_cost":0.0,"session_tokens":0,"model_calls":{"haiku":0,"sonnet":0,"opus":0},
         "large_dataset":False}
    for k,v in D.items():
        if k not in st.session_state: st.session_state[k]=v

init_state()
client = get_client()

# ── Helpers ───────────────────────────────────────────────────────────────────
def is_large(df): return len(df) > MAX_ROWS_FULL
def sdf(df, n=MAX_SAMPLE_ROWS): return df if len(df)<=n else df.sample(n=n, random_state=42)

def df_summary(df, max_rows=5):
    ds = sdf(df, max(max_rows*10,100)) if is_large(df) else df
    b = io.StringIO()
    b.write(f"Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
    b.write(f" (sample of {len(ds):,})\n" if is_large(df) else "\n")
    b.write(f"Columns: {list(df.columns)}\n")
    b.write(f"Dtypes:\n{df.dtypes.to_string()}\n")
    b.write(f"Sample:\n{ds.head(max_rows).to_string()}\n")
    nc = ds.select_dtypes(include=[np.number]).columns[:MAX_COLS_DESC]
    if len(nc): b.write(f"Stats:\n{ds[nc].describe().to_string()}\n")
    nl = df.isnull().sum(); ni = nl[nl>0]
    b.write(f"Nulls:\n{ni.to_string()}\n" if len(ni) else "Nulls: None\n")
    return b.getvalue()

def ask_claude(prompt, hint="", rows=0, quality="auto", max_tokens=2000, system=""):
    model = route_model(hint or prompt[:200], rows=rows, quality=quality)
    try:
        r = client.messages.create(model=model, max_tokens=max_tokens,
            system=system or "You are a senior data analyst. Be concise and precise.",
            messages=[{"role":"user","content":prompt}])
        t = r.content[0].text
        i,o = r.usage.input_tokens, r.usage.output_tokens
        st.session_state.session_cost   += calc_cost(model,i,o)
        st.session_state.session_tokens += i+o
        if   "haiku"  in model: st.session_state.model_calls["haiku"]  += 1
        elif "sonnet" in model: st.session_state.model_calls["sonnet"] += 1
        elif "opus"   in model: st.session_state.model_calls["opus"]   += 1
        return t, model
    except Exception as e: raise RuntimeError(f"Claude API error ({model}): {e}")

def pjson(text):
    text = re.sub(r"```(?:json)?","",text).strip().strip("`").strip()
    text = re.sub(r",\s*([}\]])",r"\1",text)
    return json.loads(text)

def snum(s): return pd.to_numeric(s, errors="coerce")

def auto_clean(df):
    df = df.copy()
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].astype(str).str.strip().replace({"nan":np.nan,"None":np.nan,"":np.nan})
    for c in df.select_dtypes(include="object").columns:
        cv = snum(df[c])
        if cv.notna().sum()/max(len(df),1) > 0.7: df[c] = cv
    df.dropna(axis=1,how="all",inplace=True)
    return df

def detect_anomalies(df):
    ds = sdf(df,10_000) if is_large(df) else df
    alerts = []
    for c in ds.select_dtypes(include=[np.number]).columns[:8]:
        q1,q3 = ds[c].quantile(.25), ds[c].quantile(.75)
        iqr = q3-q1
        if iqr==0: continue
        out = ds[(ds[c]<q1-2.5*iqr)|(ds[c]>q3+2.5*iqr)]
        if len(out): alerts.append(f"**{c}**: {len(out)} outliers ({round(len(out)/len(ds)*100,1)}%) outside 2.5x IQR [{round(q1-2.5*iqr,2)}, {round(q3+2.5*iqr,2)}]")
    return alerts

def build_chart(df, ctype, x, y, color=None, title=""):
    try:
        dp = sdf(df,5_000) if is_large(df) else df.copy()
        if y and y in dp.columns: dp[y]=snum(dp[y]); dp=dp.dropna(subset=[y])
        if x and x in dp.columns: dp=dp.dropna(subset=[x])
        if len(dp)==0: st.warning(f"No data to plot: {title}"); return None
        vc = color if color and color in dp.columns else None
        kw = dict(x=x,y=y,title=title,color=vc,color_discrete_sequence=px.colors.sequential.Oranges)
        ct = ctype.lower()
        if ct=="bar":
            if len(dp)>500: da=dp.groupby(x,as_index=False)[y].mean(); fig=px.bar(da,x=x,y=y,title=title,color_discrete_sequence=["#FF5C00"])
            else: fig=px.bar(dp,**kw)
        elif ct=="line":     fig=px.line(dp,**kw)
        elif ct=="scatter":  fig=px.scatter(dp,**kw)
        elif ct=="area":     fig=px.area(dp,**kw)
        elif ct=="histogram":fig=px.histogram(dp,x=x,title=title,color_discrete_sequence=["#FF5C00"])
        elif ct=="box":      fig=px.box(dp,x=x,y=y,title=title,color_discrete_sequence=["#FF5C00"])
        elif ct=="violin":   fig=px.violin(dp,x=x,y=y,title=title,color_discrete_sequence=["#FF5C00"])
        elif ct=="pie":
            da=dp.groupby(x,as_index=False)[y].sum().nlargest(15,y)
            fig=px.pie(da,names=x,values=y,title=title,color_discrete_sequence=px.colors.sequential.Oranges)
        elif ct=="donut":
            da=dp.groupby(x,as_index=False)[y].sum().nlargest(15,y)
            fig=px.pie(da,names=x,values=y,title=title,hole=.45,color_discrete_sequence=px.colors.sequential.Oranges)
        elif ct=="heatmap":
            piv = dp.pivot_table(values=y,index=x,columns=vc,aggfunc="mean") if (vc and dp[x].nunique()<=50 and dp[vc].nunique()<=20) else dp.select_dtypes(include=[np.number]).corr()
            fig=px.imshow(piv,title=title,color_continuous_scale="Oranges")
        elif ct=="funnel":   fig=px.funnel(dp,x=y,y=x,title=title,color_discrete_sequence=["#FF5C00"])
        elif ct=="treemap":
            da=dp.groupby(x,as_index=False)[y].sum(); da=da[da[y]>0]
            fig=px.treemap(da,path=[x],values=y,title=title,color_discrete_sequence=px.colors.sequential.Oranges)
        elif ct=="sunburst":
            da=dp.groupby(x,as_index=False)[y].sum(); da=da[da[y]>0]
            fig=px.sunburst(da,path=[x],values=y,title=title,color_discrete_sequence=px.colors.sequential.Oranges)
        elif ct=="bubble":
            sc=dp[y].copy(); sc=sc-sc.min()+1 if sc.min()<=0 else sc
            fig=px.scatter(dp,x=x,y=y,size=sc,title=title,color_discrete_sequence=["#FF5C00"])
        elif ct=="waterfall":
            dw=dp.groupby(x,as_index=False)[y].sum()
            fig=go.Figure(go.Waterfall(x=dw[x].astype(str).tolist(),y=dw[y].tolist(),connector={"line":{"color":"#FF5C00"}})); fig.update_layout(title=title)
        else: fig=px.bar(dp,**kw)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="#111111",
            font=dict(family="Plus Jakarta Sans",color="#FFF",size=12),
            title_font=dict(family="Space Grotesk",size=14,color="#FFF"),
            legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#AAA")),
            margin=dict(l=40,r=20,t=45,b=40),
            xaxis=dict(gridcolor="#1E1E1E",linecolor="#2E2E2E",tickfont=dict(color="#888")),
            yaxis=dict(gridcolor="#1E1E1E",linecolor="#2E2E2E",tickfont=dict(color="#888")))
        return fig
    except Exception as e: st.warning(f"Chart error ({ctype} — {x} vs {y}): {e}"); return None

def get_sample_data():
    np.random.seed(42); n=300
    months=pd.date_range("2024-01-01",periods=12,freq="MS")
    df=pd.DataFrame({
        "Date":np.random.choice(months,n),"Region":np.random.choice(["North","South","East","West","Central"],n),
        "Product":np.random.choice(["Pro Plan","Starter","Enterprise","Basic","Add-on"],n),
        "Channel":np.random.choice(["Organic","Paid Search","Email","Referral","Social"],n),
        "Revenue":np.round(np.random.lognormal(7.5,.8,n),2),"Units":np.random.randint(1,50,n),
        "Cost":np.round(np.random.lognormal(6.5,.6,n),2),"Customers":np.random.randint(10,500,n),
        "Churn_Rate":np.round(np.random.beta(2,18,n)*100,2),
        "Satisfaction":np.round(np.random.normal(7.5,1.5,n).clip(1,10),1)})
    df["Profit"]=(df["Revenue"]-df["Cost"]).round(2); df["Month"]=df["Date"].dt.strftime("%b %Y")
    return df

def render_so_what(sw):
    if not sw or not isinstance(sw,dict): return
    uc={"immediate":"#FF3300","short-term":"#FFBB33","long-term":"#4ADE80"}.get(sw.get("urgency","short-term"),"#FFBB33")
    c=sw.get("confidence",0); cp=f"{int(float(c)*100)}%" if float(c)<=1 else f"{int(float(c))}%"
    ah="".join(f"<li>{a}</li>" for a in sw.get("action_items",[]))
    sh=", ".join(sw.get("stakeholders",[])); fi=sw.get("financial_impact") or ""
    st.markdown(f"""<div class="so-what-box">
      <h4>&#127919; SO WHAT? — AI EXECUTIVE SUMMARY</h4>
      <p><strong>{sw.get("insight_summary","")}</strong></p>
      <div class="so-what-label">Business Impact</div><p>{sw.get("business_impact","")}</p>
      {"<div class='so-what-label'>Financial Impact</div><p>"+fi+"</p>" if fi else ""}
      <div class="so-what-label">Action Items</div><ul>{ah}</ul>
      {"<div class='so-what-label'>Stakeholders</div><p>"+sh+"</p>" if sh else ""}
      <div class="so-what-meta">
        <span>URGENCY: <span class="val" style="color:{uc}">{sw.get("urgency","short-term").upper()}</span></span>
        <span>CONFIDENCE: <span class="val">{cp}</span></span>
      </div></div>""", unsafe_allow_html=True)

def render_header():
    st.markdown("""<div class="brand-header">
      <p class="brand-title">Analytic<span>Dash</span><span style="color:#FF5C00">AI</span></p>
      <p class="brand-subtitle">AI Dashboard Builder &nbsp;&middot;&nbsp; Natural Language Queries &nbsp;&middot;&nbsp; Auto Data Cleaning &nbsp;&middot;&nbsp; Intelligent Model Routing</p>
    </div>""", unsafe_allow_html=True)
    b=st.session_state
    def badge(l,d): return f'<span class="{"badge done" if d else "badge"}">{"&#10003;" if d else "&#9675;"} {l}</span>'
    cost=f'<span class="cost-pill">&#36;{b.session_cost:.4f}</span>' if b.session_cost>0 else ""
    big=f'<span class="warn-box" style="display:inline;padding:.15rem .5rem;border-radius:4px;font-size:.7rem">&#9888; Large dataset</span>' if b.large_dataset else ""
    st.markdown(f"""<div class="progress-bar">{badge("Question Set",b.question_set)}{badge("Data Loaded",b.data_loaded)}{badge("Analysed",b.analysed)}{badge("Data Cleaned",b.data_cleaned)} {cost} {big}</div>""", unsafe_allow_html=True)

QUESTION_PROMPTS=["Why is customer churn increasing?","Which products are most profitable by region?",
    "What's driving revenue growth this quarter?","Which customer segments have the highest lifetime value?",
    "Where are we losing customers in the funnel?","Which states/regions have the best performance?"]

def tab_setup():
    st.markdown('<div class="step-label">STEP 1 — DEFINE YOUR QUESTION</div>', unsafe_allow_html=True)
    st.markdown("## What are you trying to figure out?")
    st.markdown("Start with a business question — AnalyticDashAI will tailor every analysis and dashboard to answer it.")
    cols=st.columns(3)
    for i,q in enumerate(QUESTION_PROMPTS):
        with cols[i%3]:
            if st.button(q, key=f"q_{i}", use_container_width=True):
                st.session_state.business_question=q; st.session_state.question_set=True; st.rerun()

    # FIX 1: Show green confirmation card so user knows their click registered
    if st.session_state.business_question:
        st.markdown(f"""<div style="background:#0C2010;border:1px solid #1A5C2A;border-left:4px solid #4ADE80;
            border-radius:8px;padding:.6rem 1rem;margin:.75rem 0;">
          <span style="font-size:.75rem;color:#4ADE80;font-weight:700;font-family:'Space Grotesk',sans-serif;
              text-transform:uppercase;letter-spacing:.5px;">&#10003; Question Set</span>
          <p style="margin:.2rem 0 0;color:#FFF;font-size:.92rem;">{st.session_state.business_question}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="step-label" style="margin-top:1.5rem">STEP 2 — UPLOAD YOUR DATA</div>', unsafe_allow_html=True)
    new_q=st.text_input("Or type your own question:", value=st.session_state.business_question,
                        placeholder="e.g., Why are high-value customers churning after month 3?", key="q_input")
    c1,_=st.columns([2,1])
    with c1:
        if st.button("Set Business Question", use_container_width=True, key="set_q"):
            if new_q.strip(): st.session_state.business_question=new_q.strip(); st.session_state.question_set=True; st.rerun()
    st.markdown('<div class="pro-tip"><span>Pro tip:</span> The more specific your question, the better the analysis.</div>', unsafe_allow_html=True)

    uploaded=st.file_uploader("Upload your data file (CSV or Excel, up to 200MB):", type=["csv","xlsx","xls"], key="file_upload")
    if uploaded:
        try:
            with st.spinner("Loading and cleaning data..."):
                if uploaded.name.endswith(".csv"):
                    try: df=pd.read_csv(uploaded)
                    except Exception: uploaded.seek(0); df=pd.read_csv(uploaded,encoding="latin-1")
                else:
                    xl=pd.ExcelFile(uploaded)
                    sheet=st.selectbox("Select sheet:",xl.sheet_names,key="sheet_sel") if len(xl.sheet_names)>1 else xl.sheet_names[0]
                    df=pd.read_excel(uploaded,sheet_name=sheet)
                df=auto_clean(df)
                st.session_state.df=df; st.session_state.df_clean=df.copy()
                st.session_state.filename=uploaded.name; st.session_state.data_loaded=True
                st.session_state.data_cleaned=True; st.session_state.analysed=False
                st.session_state.large_dataset=is_large(df)
            mb=uploaded.size/(1024*1024)
            st.success(f"Loaded **{uploaded.name}** — {df.shape[0]:,} rows x {df.shape[1]} columns ({mb:.1f} MB)")
            if is_large(df): st.markdown(f'<div class="warn-box">&#9888; Large dataset ({df.shape[0]:,} rows). Sampling used for AI analysis.</div>', unsafe_allow_html=True)
        except Exception as e: st.error(f"Error reading file: {e}")

    st.markdown("---")
    st.markdown('<div class="info-card"><h4>No data handy?</h4><p>Try AnalyticDashAI instantly with a built-in sample sales dataset.</p></div>', unsafe_allow_html=True)
    if st.button("Try with Sample Data", key="sample_btn"):
        df=get_sample_data(); st.session_state.df=df; st.session_state.df_clean=df.copy()
        st.session_state.filename="sample_sales_data.csv"; st.session_state.data_loaded=True
        st.session_state.data_cleaned=True; st.session_state.large_dataset=False
        if not st.session_state.business_question:
            st.session_state.business_question="What's driving revenue growth this quarter?"; st.session_state.question_set=True
        st.success("Sample data loaded — 300 rows."); st.rerun()

    if st.session_state.df is not None:
        df=st.session_state.df; st.markdown("---"); st.markdown("**Data Preview (first 10 rows):**")
        st.dataframe(df.head(10),use_container_width=True)
        m1,m2,m3,m4=st.columns(4)
        m1.metric("Rows",f"{df.shape[0]:,}"); m2.metric("Columns",str(df.shape[1]))
        m3.metric("Numeric cols",str(len(df.select_dtypes(include=[np.number]).columns)))
        m4.metric("Missing values",f"{df.isnull().sum().sum():,}")

def tab_analyse():
    if st.session_state.df is None: st.info("Upload data in the **Setup** tab first."); return
    df=st.session_state.df_clean; question=st.session_state.business_question or "General analysis"; rows=len(df)
    st.markdown('<div class="step-label">STEP 2 — AI DATA ANALYST</div>', unsafe_allow_html=True)
    st.markdown("## AI Data Analyst")
    st.markdown("Data Profiling &nbsp;&middot;&nbsp; Issue Detection &nbsp;&middot;&nbsp; Intelligent Model Routing &nbsp;&middot;&nbsp; Business Insights")
    if is_large(df): st.markdown(f'<div class="warn-box">&#9888; Large dataset ({rows:,} rows) — using {MAX_SAMPLE_ROWS}-row sample for AI prompts.</div>', unsafe_allow_html=True)

    if st.button("Run AI Analyst", key="run_analyst"):
        with st.spinner("Running analysis with intelligent model routing..."):
            summary=df_summary(df,max_rows=5)
            qp=f"""Analyse data quality for: "{question}"\nDataset: {summary}\nReturn ONLY valid JSON:\n{{"score":<0-100>,"issues":["<issue>"],"recommendations":["<fix>"]}}"""
            try: rq,mq=ask_claude(qp,hint="count list show data quality",rows=rows,max_tokens=500); dq=pjson(rq)
            except Exception as e: dq={"score":75,"issues":[str(e)],"recommendations":[]}; mq="claude-haiku-4-5"

            ip=f"""You are a senior data analyst. Analyse for: "{question}"\n\nDataset:\n{summary}\n\nReturn ONLY valid JSON:\n{{\n  "key_insights":[{{"title":"<title>","insight":"<2 sentences>","metric":"<value>"}}],\n  "suggested_charts":[{{"type":"<bar|line|scatter|pie|donut|area|histogram|box>","x":"<col>","y":"<col>","title":"<title>"}}],\n  "so_what":{{"insight_summary":"<headline>","business_impact":"<2 sentences>","financial_impact":"<or null>","action_items":["<a1>","<a2>","<a3>"],"stakeholders":["<d1>","<d2>"],"urgency":"<immediate|short-term|long-term>","confidence":<0.0-1.0>}}\n}}\nOnly use columns that exist: {list(df.columns)}\nReturn at least 4 key_insights and 5 suggested_charts."""
            try:
                ri,mi=ask_claude(ip,hint=f"analyze explain why insight {question}",rows=rows,max_tokens=2500)
                result=pjson(ri); result["data_quality"]=dq
                st.session_state.analysis_result=result; st.session_state.so_what=result.get("so_what",{})
                st.session_state.charts=result.get("suggested_charts",[]); st.session_state.anomalies=detect_anomalies(df)
                st.session_state.analysed=True
                st.success(f"Analysis complete! Profiling: {mbadge(mq)} &nbsp; Insights: {mbadge(mi)}")
                st.rerun()
            except json.JSONDecodeError as e: st.error(f"JSON parse error — try again. Detail: {e}")
            except Exception as e: st.error(f"Analysis error: {e}")

    if not st.session_state.analysis_result: return
    result=st.session_state.analysis_result
    if st.session_state.so_what: render_so_what(st.session_state.so_what)
    if st.session_state.anomalies:
        st.markdown("### &#9888;&#65039; Anomaly Alerts")
        for a in st.session_state.anomalies[:5]: st.markdown(f'<div class="anomaly-box">{a}</div>', unsafe_allow_html=True)

    dq=result.get("data_quality",{}); score=dq.get("score",0)
    c1,c2=st.columns([1,2])
    with c1:
        col=("#4ADE80" if score>=80 else "#FFBB33" if score>=60 else "#FF5C00")
        st.markdown(f'<div class="info-card" style="text-align:center"><h4 style="font-size:2.5rem;color:{col};margin:0">{score}</h4><p style="margin:0;font-size:.8rem">Data Quality Score / 100</p></div>', unsafe_allow_html=True)
    with c2:
        issues=dq.get("issues",[])
        if issues: st.markdown("**Issues found:**");  [st.markdown(f"- {i}") for i in issues]

    # FIX 2: Show how to fix data quality issues
    recs=dq.get("recommendations",[])
    if recs:
        with st.expander("&#128295; How to fix these issues", expanded=(score<70)):
            for r in recs: st.markdown(f"- {r}")
    if score<60: st.markdown('<div class="warn-box">&#9888; <strong>Low data quality.</strong> Common fixes: remove duplicates, standardize text casing, fill/drop nulls, ensure numeric cols have no text.</div>', unsafe_allow_html=True)

    insights=result.get("key_insights",[])
    if insights:
        st.markdown("### &#128161; Key Insights")
        ic=st.columns(min(len(insights),4))
        for i,ins in enumerate(insights[:4]):
            with ic[i]: st.metric(ins.get("title",""),ins.get("metric","—")); st.caption(ins.get("insight",""))

    # FIX 3+4: validate columns + unique keys on every plotly_chart
    charts=st.session_state.charts
    if charts:
        st.markdown("### &#128200; AI-Generated Charts")
        cc=st.columns(2); ci=0; nc_list=list(df.select_dtypes(include=[np.number]).columns)
        for i,spec in enumerate(charts[:6]):
            xc=spec.get("x",""); yc=spec.get("y","")
            if xc not in df.columns: continue
            if yc not in df.columns: yc=nc_list[0] if nc_list else ""; 
            if not yc: continue
            fig=build_chart(df,spec.get("type","bar"),xc,yc,title=spec.get("title",""))
            if fig:
                with cc[ci%2]: st.plotly_chart(fig,use_container_width=True,key=f"ac_{i}")
                ci+=1

    st.markdown("---")
    st.markdown('<div class="step-label">STEP 3 — AI RECOMMENDATIONS</div>', unsafe_allow_html=True)
    st.markdown("## AI Recommendations")
    if st.button("Generate Recommendations", key="gen_recs", use_container_width=True):
        with st.spinner("Generating recommendations..."):
            p=f"""Based on analysis of "{question}", provide 5 actionable recommendations.\nInsights: {json.dumps(result.get("key_insights",[]))}\nReturn ONLY JSON array:\n[{{"action":"<title>","detail":"<2 sentences>","impact":"<High|Medium|Low>","timeline":"<1 week|1 month|1 quarter>"}}]"""
            try:
                raw,_=ask_claude(p,hint=f"recommend strategy {question}",rows=rows,max_tokens=1200)
                rs=pjson(raw)
                if isinstance(rs,list): st.session_state.recommendations=rs; st.rerun()
            except Exception as e: st.error(f"Error: {e}")
    if st.session_state.recommendations:
        for rec in st.session_state.recommendations:
            impact=rec.get("impact","Medium"); col={"High":"#FF5C00","Medium":"#FFBB33","Low":"#4ADE80"}.get(impact,"#888")
            st.markdown(f'<div class="info-card"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.4rem"><h4 style="margin:0">{rec.get("action","")}</h4><span style="font-size:.75rem;color:{col};font-weight:700">{impact} IMPACT &middot; {rec.get("timeline","")}</span></div><p>{rec.get("detail","")}</p></div>', unsafe_allow_html=True)

def tab_explore():
    if st.session_state.df is None: st.info("Upload data in the **Setup** tab first."); return
    df=st.session_state.df_clean; rows=len(df)
    st.markdown('<div class="step-label">STEP 4 — NATURAL LANGUAGE QUERY</div>', unsafe_allow_html=True)
    st.markdown("## Ask Questions")
    st.markdown("Ask anything in plain English. Simple &#9889; Haiku, complex &#128293; Opus")
    query=st.text_input("",placeholder="e.g., Which region has the highest revenue?",key="nl_query",label_visibility="collapsed")
    _,c2=st.columns([4,1])
    with c2: ask_btn=st.button("Ask",key="ask_btn",use_container_width=True)
    if ask_btn and query.strip():
        with st.spinner("Thinking..."):
            p=f"""User asks: "{query}"\nDataset: {df_summary(df,max_rows=3)}\nReturn ONLY JSON:\n{{"answer":"<2-3 sentence answer>","chart":{{"type":"<bar|line|pie|scatter|histogram>","x":"<col>","y":"<col>","title":"<title>"}} or null,"table":<true or false>}}\nOnly use columns: {list(df.columns)}"""
            try:
                raw,mu=ask_claude(p,hint=query,rows=rows,max_tokens=800)
                parsed=pjson(raw); parsed["_model"]=mu
                st.session_state.nl_history.append({"query":query,"result":parsed}); st.rerun()
            except Exception as e: st.error(f"Error: {e}")

    for idx,item in enumerate(reversed(st.session_state.nl_history[-5:])):
        res=item["result"]; b=mbadge(res.get("_model",""))
        st.markdown(f'<div class="info-card" style="border-left:3px solid #FF5C00"><p style="font-size:.8rem;color:#FF5C00;font-weight:700;margin-bottom:.3rem">{item["query"]} {b}</p><p style="margin:0">{res.get("answer","")}</p></div>', unsafe_allow_html=True)
        cs=res.get("chart")
        if cs and cs.get("x") in df.columns and cs.get("y","") in df.columns:
            fig=build_chart(df,cs.get("type","bar"),cs["x"],cs["y"],title=cs.get("title",""))
            if fig: st.plotly_chart(fig,use_container_width=True,key=f"nlc_{idx}")  # FIX 5: unique key
        if res.get("table"):
            mc=[c for c in df.columns if c.lower() in item["query"].lower()]
            st.dataframe(df[mc[:4] if mc else list(df.columns[:4])].head(10),use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="step-label">STEP 5 — CHART BUILDER</div>', unsafe_allow_html=True)
    st.markdown("## Build Your Own Chart")
    chart_types=["bar","line","scatter","area","histogram","box","violin","pie","donut","heatmap","funnel","treemap","sunburst","bubble","waterfall"]
    nc=list(df.select_dtypes(include=[np.number]).columns); ac=list(df.columns)
    c1,c2,c3,c4=st.columns(4)
    with c1: ct=st.selectbox("Chart type",chart_types,key="cb_type")
    with c2: cx=st.selectbox("X axis",ac,key="cb_x")
    with c3: cy=st.selectbox("Y axis",nc if nc else ac,key="cb_y")
    with c4: ctt=st.text_input("Title",value="",key="cb_title")
    if st.button("Generate Chart",key="gen_chart"):
        fig=build_chart(df,ct,cx,cy,title=ctt or f"{ct.title()}: {cy} by {cx}")
        if fig: st.plotly_chart(fig,use_container_width=True,key="cbo")  # FIX 5: unique key

ROLE_TEMPLATES={"Executive":"Revenue overview, profit margin trend, regional performance, top product mix, YoY growth KPIs",
    "Sales":"Sales by rep/region, pipeline funnel, win rate trend, revenue by product, quota attainment",
    "Marketing":"Channel performance, CAC trend, campaign ROI, lead funnel, customer acquisition by region",
    "Operations":"Cost breakdown, efficiency metrics, SLA adherence, volume trends, capacity utilization",
    "Finance":"P&L summary, revenue vs cost, margin analysis, cash flow trend, budget vs actual",
    "Customer":"Satisfaction scores, churn rate, LTV segments, support tickets, NPS trend"}

def tab_dashboard():
    if st.session_state.df is None: st.info("Upload data in the **Setup** tab first."); return
    df=st.session_state.df_clean; question=st.session_state.business_question or "General analysis"; rows=len(df)
    nc=list(df.select_dtypes(include=[np.number]).columns); cc=list(df.select_dtypes(include="object").columns)
    st.markdown('<div class="step-label">STEP 6 — CUSTOM DASHBOARD</div>', unsafe_allow_html=True)
    st.markdown("## Generate Custom Dashboard")
    rc=st.columns(len(ROLE_TEMPLATES))
    for i,(role,desc) in enumerate(ROLE_TEMPLATES.items()):
        with rc[i]:
            if st.button(role,key=f"role_{role}",use_container_width=True):
                st.session_state["dashboard_desc"]=desc; st.rerun()

    desc=st.text_area("Dashboard Description:",value=st.session_state.get("dashboard_desc",""),
                      placeholder="e.g., Executive overview with revenue KPIs",height=80,key="dash_desc_input")
    c1,c2=st.columns([3,1])
    with c1: gen=st.button("Generate Dashboard",key="gen_dash",use_container_width=True)
    with c2:
        if st.button("Clear",key="clear_dash"): st.session_state.dashboard_charts=[]; st.rerun()

    if gen:
        with st.spinner("Building dashboard..."):
            p=f"""Create dashboard for: "{question}"\nFocus: {desc or "general overview"}\nDataset: {df_summary(df,max_rows=3)}\nReturn ONLY JSON array of 6 chart specs:\n[{{"type":"<bar|line|scatter|pie|donut|area|histogram|box>","x":"<col>","y":"<col>","color":null,"title":"<title>"}}]\nOnly use columns: {list(df.columns)}"""
            try:
                raw,_=ask_claude(p,hint="generate dashboard chart visualization",rows=rows,max_tokens=1200)
                specs=pjson(raw)
                if isinstance(specs,list):
                    valid=[s for s in specs if s.get("x") in df.columns and s.get("y","") in df.columns]
                    st.session_state.dashboard_charts=valid; st.rerun()
            except Exception as e: st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown('<div class="step-label">STEP 7 — PRESET ROLE DASHBOARDS</div>', unsafe_allow_html=True)
    st.markdown("## Or Choose a Preset Dashboard")

    # FIX 6: Use actual df columns — always works regardless of data
    if st.button("Generate 5 Role-Based Dashboards",key="role_dash",use_container_width=True):
        x=cc[0] if cc else df.columns[0]
        y=nc[0] if nc else (df.columns[1] if len(df.columns)>1 else df.columns[0])
        y2=nc[1] if len(nc)>1 else y
        st.session_state.dashboard_charts=[
            {"type":"bar","x":x,"y":y,"title":f"Revenue by {x}"},
            {"type":"line","x":x,"y":y,"title":f"{y} Trend"},
            {"type":"donut","x":x,"y":y,"title":f"{y} Mix"},
            {"type":"scatter","x":y,"y":y2,"title":f"{y} vs {y2}"},
            {"type":"histogram","x":y,"y":y,"title":f"{y} Distribution"},
            {"type":"box","x":x,"y":y,"title":f"{y} by {x}"},]
        st.rerun()

    if st.session_state.dashboard_charts:
        st.markdown("---"); st.markdown("### Your Dashboard")
        specs=st.session_state.dashboard_charts
        for i in range(0,len(specs),2):
            row=specs[i:i+2]; cols=st.columns(len(row))
            for j,spec in enumerate(row):
                sx=spec.get("x",df.columns[0]); sy=spec.get("y",df.columns[1] if len(df.columns)>1 else df.columns[0])
                if sx not in df.columns: sx=df.columns[0]
                if sy not in df.columns: sy=nc[0] if nc else df.columns[0]
                fig=build_chart(df,spec.get("type","bar"),sx,sy,color=spec.get("color"),title=spec.get("title",""))
                if fig:
                    with cols[j]: st.plotly_chart(fig,use_container_width=True,key=f"dc_{i}_{j}")  # FIX 4+5

        st.markdown("---"); st.markdown("### Export")
        e1,e2,e3=st.columns(3)
        with e1: st.download_button("Download CSV",df.to_csv(index=False),"analyticdashai_data.csv","text/csv",use_container_width=True)
        with e2:
            try:
                buf=io.BytesIO()
                with pd.ExcelWriter(buf,engine="xlsxwriter") as w:
                    df.head(100_000).to_excel(w,sheet_name="Data",index=False)
                    ins=(st.session_state.analysis_result or {}).get("key_insights",[])
                    if ins: pd.DataFrame(ins).to_excel(w,sheet_name="Insights",index=False)
                buf.seek(0)
                st.download_button("Download Excel",buf.read(),"analyticdashai_report.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
            except Exception as e: st.warning(f"Excel export error: {e}")
        with e3:
            ed={"generated":datetime.now().isoformat(),"business_question":question,"so_what":st.session_state.so_what or {},"anomalies":st.session_state.anomalies,"recommendations":st.session_state.recommendations or [],"session_cost_usd":round(st.session_state.session_cost,4)}
            st.download_button("Download AI Summary",json.dumps(ed,indent=2),"analyticdashai_summary.json","application/json",use_container_width=True)

def tab_monitor():
    if st.session_state.df is None: st.info("Upload data in the **Setup** tab first."); return
    df=st.session_state.df_clean
    st.markdown('<div class="step-label">STEP 8 — MONITOR & ITERATE</div>', unsafe_allow_html=True)
    st.markdown("## Monitor & Iterate")
    st.markdown("### &#128176; Session Cost Tracker")
    mc=st.session_state.model_calls; tot=mc["haiku"]+mc["sonnet"]+mc["opus"]
    if tot>0:
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Session Cost",f"${st.session_state.session_cost:.4f}"); c2.metric("Total Tokens",f"{st.session_state.session_tokens:,}")
        c3.metric("Fast calls &#9889;",mc["haiku"],help="Haiku"); c4.metric("Deep calls &#128293;",mc["sonnet"]+mc["opus"],help="Sonnet/Opus")
        saved=(mc["haiku"]*(0.015-0.001))+(mc["sonnet"]*(0.015-0.004))
        if saved>0.001: st.success(f"&#9889; Smart routing saved ~**${saved:.3f}** vs always using Opus.")
    else: st.markdown('<div class="info-card"><h4>No API calls yet</h4><p>Run an analysis to start tracking costs.</p></div>', unsafe_allow_html=True)

    st.markdown("---"); st.markdown("### &#9881;&#65039; Configure KPIs")
    with st.expander("Add / Edit Monitored KPIs"):
        ncols=list(df.select_dtypes(include=[np.number]).columns)
        if st.button("Auto-detect KPIs",key="auto_kpi"):
            st.session_state.kpis={c:{"value":float(df[c].mean()),"label":f"Avg {c}"} for c in ncols[:5]}
            st.success(f"Auto-detected {len(st.session_state.kpis)} KPIs."); st.rerun()
        m1,m2,m3=st.columns([2,3,1])
        with m1: kl=st.text_input("KPI Label",placeholder="e.g., Avg Revenue",key="kpi_label")
        with m2: kc=st.text_input("Python code",placeholder="result = df['Revenue'].mean()",key="kpi_code")
        with m3:
            st.markdown("<br>",unsafe_allow_html=True)
            if st.button("Add KPI",key="add_kpi"):
                if kl and kc:
                    try:
                        lv={"df":df,"pd":pd,"np":np}; exec(kc,{},lv); val=lv.get("result")
                        if val is not None: st.session_state.kpis[kl]={"value":float(val),"label":kl}; st.success(f"KPI '{kl}' = {val:.2f}"); st.rerun()
                    except Exception as e: st.error(f"KPI error: {e}")
    if st.session_state.kpis:
        st.markdown("### Current KPIs"); items=list(st.session_state.kpis.items()); kc=st.columns(min(len(items),4))
        for i,(n,d) in enumerate(items[:4]):
            with kc[i]: st.metric(n,f"{d.get('value',0):,.2f}")

    st.markdown("---"); st.markdown("### &#128248; Snapshots")
    s1,s2=st.columns([3,2])
    with s1: sl=st.text_input("Snapshot label:",placeholder="e.g., After Q2 cleaning",key="snap_label")
    with s2:
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("Take Snapshot",key="snap_btn"):
            st.session_state.snapshots.append({"label":sl or f"Snapshot {len(st.session_state.snapshots)+1}","timestamp":datetime.now().strftime("%Y-%m-%d %H:%M"),"rows":len(df),"kpis":dict(st.session_state.kpis),"anomalies":list(st.session_state.anomalies)})
            st.success("Snapshot saved."); st.rerun()
    if st.session_state.snapshots:
        for snap in reversed(st.session_state.snapshots):
            st.markdown(f'<div class="info-card"><div style="display:flex;justify-content:space-between"><h4 style="margin:0">{snap["label"]}</h4><span style="font-size:.78rem;color:#6B6B6B">{snap["timestamp"]}</span></div><p style="margin:.3rem 0 0">{snap["rows"]:,} rows &middot; {len(snap["kpis"])} KPIs &middot; {len(snap["anomalies"])} anomalies</p></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:center;padding:2.5rem;color:#6B6B6B;background:#1E1E1E;border-radius:10px;border:1px dashed #2E2E2E"><p style="font-size:2rem;margin:0">&#128248;</p><p style="margin:.5rem 0 0;font-size:.9rem">No snapshots yet</p></div>', unsafe_allow_html=True)
    if st.session_state.anomalies:
        st.markdown("---"); st.markdown("### &#9888;&#65039; Active Anomaly Alerts")
        for a in st.session_state.anomalies: st.markdown(f'<div class="anomaly-box">{a}</div>', unsafe_allow_html=True)
    elif st.session_state.analysed:
        st.markdown('<div class="info-card" style="border-color:#1A5C2A"><h4 style="color:#4ADE80">&#10003; No anomalies detected</h4><p>Your data looks clean.</p></div>', unsafe_allow_html=True)

def main():
    render_header()
    t1,t2,t3,t4,t5=st.tabs(["&#128203; 1 &middot; Setup","&#128300; 2 &middot; Analyse","&#128269; 3 &middot; Explore","&#128202; 4 &middot; Dashboard","&#128225; 5 &middot; Monitor"])
    with t1: tab_setup()
    with t2: tab_analyse()
    with t3: tab_explore()
    with t4: tab_dashboard()
    with t5: tab_monitor()

if __name__ == "__main__":
    main()
