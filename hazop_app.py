import streamlit as st
import json
import re
import pandas as pd
from groq import Groq

st.set_page_config(
    page_title="HAZOP AI Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    color: #f1f5f9 !important;
}

.stApp {
    background: #0f172a !important;
}

section[data-testid="stSidebar"] {
    background: #1e293b !important;
    border-right: 2px solid #f97316 !important;
}

section[data-testid="stSidebar"] * {
    color: #f1f5f9 !important;
}

section[data-testid="stSidebar"] label {
    color: #fbbf24 !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}

section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #0f172a !important;
    color: #f1f5f9 !important;
    border: 1px solid #f97316 !important;
}

h1, h2, h3, h4 {
    font-family: 'IBM Plex Mono', monospace !important;
    color: #f97316 !important;
}

p, li, span, div {
    color: #e2e8f0 !important;
}

.hero-banner {
    background: #1e293b;
    border: 2px solid #f97316;
    border-radius: 8px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
}

.hero-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #f97316 !important;
    margin: 0;
}

.hero-sub {
    font-size: 0.9rem;
    color: #94a3b8 !important;
    margin-top: 0.4rem;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 1px;
}

.metric-card {
    background: #1e293b;
    border: 2px solid #334155;
    border-radius: 8px;
    padding: 1.2rem;
    text-align: center;
}

.metric-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    color: #f97316 !important;
}

.metric-label {
    font-size: 0.75rem;
    color: #94a3b8 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

.section-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 2px;
    color: #f97316 !important;
    text-transform: uppercase;
    border-bottom: 1px solid #f97316;
    padding-bottom: 0.4rem;
    margin-bottom: 1rem;
    margin-top: 0.5rem;
}

.info-box {
    background: #1e293b;
    border: 1px solid #f97316;
    border-radius: 6px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
}

.info-box * { color: #e2e8f0 !important; }
.info-box b { color: #f97316 !important; }

.stTextArea label {
    color: #fbbf24 !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}

.stTextArea textarea {
    background: #1e293b !important;
    border: 2px solid #475569 !important;
    color: #f1f5f9 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.85rem !important;
    border-radius: 6px !important;
}

.stTextArea textarea:focus {
    border-color: #f97316 !important;
    box-shadow: 0 0 0 2px rgba(249,115,22,0.3) !important;
}

.stTextArea textarea::placeholder {
    color: #64748b !important;
}

.stButton > button {
    background: #f97316 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    padding: 0.7rem 1.5rem !important;
    font-size: 0.9rem !important;
    width: 100% !important;
}

.stButton > button:hover {
    background: #ea580c !important;
    box-shadow: 0 4px 15px rgba(249,115,22,0.4) !important;
}

.stSelectbox label {
    color: #fbbf24 !important;
    font-weight: 600 !important;
}

.stSelectbox > div > div {
    background: #1e293b !important;
    color: #f1f5f9 !important;
    border: 1px solid #475569 !important;
    border-radius: 6px !important;
}

.stMultiSelect label {
    color: #fbbf24 !important;
    font-weight: 600 !important;
}

.stMultiSelect > div {
    background: #1e293b !important;
    border: 1px solid #475569 !important;
    border-radius: 6px !important;
}

.stMultiSelect span {
    color: #f1f5f9 !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: #1e293b !important;
    border-radius: 8px !important;
    padding: 4px !important;
    gap: 4px !important;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace !important;
    color: #94a3b8 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.5px !important;
    background: transparent !important;
    border-radius: 6px !important;
    padding: 8px 16px !important;
}

.stTabs [aria-selected="true"] {
    color: #ffffff !important;
    background: #f97316 !important;
}

.stExpander {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 6px !important;
    margin-bottom: 0.5rem !important;
}

.stExpander summary {
    color: #f1f5f9 !important;
    font-weight: 600 !important;
}

.stExpander > div > div {
    background: #0f172a !important;
    padding: 1rem !important;
}

.stDataFrame {
    border: 1px solid #334155 !important;
    border-radius: 6px !important;
}

[data-testid="stDataFrameResizable"] {
    background: #1e293b !important;
}

.stMarkdown p { color: #e2e8f0 !important; }
.stMarkdown li { color: #e2e8f0 !important; }
.stMarkdown strong { color: #fbbf24 !important; }

.stSpinner > div { color: #f97316 !important; }

div[data-testid="stAlert"] {
    background: #1e293b !important;
    border: 1px solid #f97316 !important;
    color: #f1f5f9 !important;
    border-radius: 6px !important;
}

footer { display: none !important; }
#MainMenu { visibility: hidden !important; }

.empty-state {
    text-align: center;
    padding: 4rem 1rem;
    background: #1e293b;
    border-radius: 12px;
    border: 2px dashed #334155;
    margin-top: 1rem;
}

.empty-state-icon { font-size: 4rem; margin-bottom: 1rem; }

.empty-state-text {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1rem;
    color: #64748b !important;
    letter-spacing: 1px;
}

.empty-state-sub {
    font-size: 0.85rem;
    color: #475569 !important;
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🛡️ HAZOP AI ASSISTANT</div>
    <div class="hero-sub">// HAZARD & OPERABILITY STUDY — POWERED BY GROQ AI (LLAMA 3.3) //</div>
</div>
""", unsafe_allow_html=True)

# ── CLIENT ───────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    key = st.secrets.get("GROQ_API_KEY", "")
    if not key:
        st.error("❌ GROQ_API_KEY missing. Streamlit secrets mein add karein.")
        st.stop()
    return Groq(api_key=key)

# ── PROMPT ───────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a senior Process Safety Engineer with 20+ years of HAZOP experience.
Perform a rigorous HAZOP study on the given process node.

Return ONLY valid JSON — no markdown, no explanation, nothing else.

JSON format:
{
  "node_name": "string",
  "process_intent": "string",
  "deviations": [
    {
      "guide_word": "NO/MORE/LESS/REVERSE/OTHER THAN/AS WELL AS/PART OF",
      "parameter": "Flow/Temperature/Pressure/Level/Composition",
      "deviation": "full deviation phrase e.g. No Flow",
      "possible_causes": ["cause 1", "cause 2"],
      "consequences": ["consequence 1", "consequence 2"],
      "safeguards": ["safeguard 1", "safeguard 2"],
      "recommendations": ["action 1", "action 2"],
      "risk_level": "CRITICAL/HIGH/MEDIUM/LOW",
      "likelihood": "Frequent/Probable/Occasional/Remote/Improbable",
      "severity": "Catastrophic/Critical/Marginal/Negligible"
    }
  ],
  "summary": {
    "critical_count": 0,
    "high_count": 0,
    "medium_count": 0,
    "low_count": 0,
    "top_recommendation": "string"
  }
}
Generate 8-12 meaningful deviations. Return ONLY the JSON object."""

def run_hazop(client, node_description, process_type):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Process Type: {process_type}\nNode: {node_description}\nReturn JSON only."}
        ],
        temperature=0.3,
        max_tokens=4000
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)

RISK_EMOJI = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
RISK_COLOR = {"CRITICAL": "#ef4444", "HIGH": "#f97316", "MEDIUM": "#eab308", "LOW": "#22c55e"}

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-header">// Configuration</div>', unsafe_allow_html=True)
    process_type = st.selectbox("Process Industry", [
        "Oil & Gas", "Petrochemical", "Pharmaceutical",
        "Chemical Plant", "Power Generation", "Water Treatment",
        "Food & Beverage", "General"
    ])

    st.markdown('<div class="section-header">// Example Nodes</div>', unsafe_allow_html=True)
    examples = {
        "Heat Exchanger (E-101)":
            "Shell and tube heat exchanger E-101. Hot crude oil at 180°C, 8 bar on shell side. Cooling water at 30°C, 4 bar on tube side. Design duty 5 MW. Outlet process temperature 120°C. Connected to upstream pump P-101 and downstream distillation column T-101.",
        "Centrifugal Pump (P-201)":
            "Centrifugal pump P-201 transferring flammable hexane from tank TK-101 to reactor R-201. Flow 50 m3/hr, discharge 6 bar, suction 1.5 bar. Motor driven, mechanical seal. Flash point -22°C.",
        "CSTR Reactor (R-301)":
            "CSTR reactor R-301. Exothermic reaction ethylene oxide + water → ethylene glycol. 150°C, 3 bar. Jacket cooling. Feed 2000 kg/hr EO + 5000 kg/hr water. Relief valve at 5 bar. Agitator 75kW.",
        "Distillation Column (T-101)":
            "Atmospheric distillation column T-101, benzene/toluene separation. Feed 50% benzene at 120°C, 1.1 bar. 30 trays. Condenser E-201 top, reboiler E-202 bottom. Reflux ratio 2.5.",
        "Ammonia Storage (V-401)":
            "Horizontal vessel V-401 storing liquid ammonia. 100 m3, -33°C, 1 bar refrigerated. Relief valve 2.5 bar. Insulated. Dyke wall around. Loading/unloading lines connected."
    }
    selected = st.selectbox("Load Example", ["-- Select --"] + list(examples.keys()))

    st.markdown('<div class="section-header">// Risk Filter</div>', unsafe_allow_html=True)
    show_risk = st.multiselect("Show Risk Levels",
        ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        default=["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    )
    st.markdown("---")
    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#94a3b8;line-height:2;">
    <span style="color:#f97316;font-weight:700;">GUIDE WORDS:</span><br>
    NO &nbsp;·&nbsp; MORE &nbsp;·&nbsp; LESS<br>
    REVERSE &nbsp;·&nbsp; OTHER THAN<br>
    AS WELL AS &nbsp;·&nbsp; PART OF<br><br>
    <span style="color:#64748b;">IEC 61882 Compliant</span>
    </div>
    """, unsafe_allow_html=True)

# ── INPUT ─────────────────────────────────────────────────────────────────────
col_in, col_btn = st.columns([5, 1])
with col_in:
    default_val = examples.get(selected, "") if selected != "-- Select --" else ""
    node_input = st.text_area(
        "Process Node Description", value=default_val, height=150,
        placeholder="Describe the process node:\n- Equipment type and tag number (e.g. E-101)\n- Operating conditions (Temperature, Pressure, Flow rate)\n- Connected upstream/downstream equipment\n- Existing safety systems and instruments"
    )
with col_btn:
    st.markdown("<br><br>", unsafe_allow_html=True)
    run_btn = st.button("▶ RUN HAZOP", use_container_width=True)

# ── RUN ──────────────────────────────────────────────────────────────────────
if run_btn:
    if not node_input.strip():
        st.warning("⚠️ Please enter a process node description first.")
    else:
        client = get_client()
        with st.spinner("🤖 AI conducting HAZOP study... please wait ~15 seconds"):
            try:
                data = run_hazop(client, node_input, process_type)
                st.session_state["hazop_data"] = data
                st.session_state["process_type"] = process_type
                st.success(f"✅ HAZOP complete! Found {len(data.get('deviations',[]))} deviations.")
            except json.JSONDecodeError as e:
                st.error(f"❌ Parse error: {e}. Please try again.")
                st.stop()
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.stop()

# ── RESULTS ───────────────────────────────────────────────────────────────────
if "hazop_data" in st.session_state:
    data = st.session_state["hazop_data"]
    summary = data.get("summary", {})
    deviations = [d for d in data.get("deviations", []) if d.get("risk_level", "LOW") in show_risk]

    st.markdown("---")
    st.markdown(f"### 📍 Node: `{data.get('node_name', 'Process Node')}`")

    # Metrics
    m1, m2, m3, m4, m5 = st.columns(5)
    cols_metrics = [
        (m1, len(deviations), "Deviations", "#f97316", "#334155"),
        (m2, summary.get("critical_count",0), "Critical", "#ef4444", "rgba(239,68,68,0.2)"),
        (m3, summary.get("high_count",0), "High", "#f97316", "rgba(249,115,22,0.2)"),
        (m4, summary.get("medium_count",0), "Medium", "#eab308", "rgba(234,179,8,0.2)"),
        (m5, summary.get("low_count",0), "Low", "#22c55e", "rgba(34,197,94,0.2)"),
    ]
    for col, num, label, color, bg in cols_metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-color:{color};background:{bg}">
                <div class="metric-num" style="color:{color}!important">{num}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="info-box">
        <div class="section-header">DESIGN INTENT</div>
        <p style="color:#e2e8f0!important;font-size:0.95rem;margin:0;">{data.get("process_intent","")}</p>
    </div>""", unsafe_allow_html=True)

    if summary.get("top_recommendation"):
        st.markdown(f"""
        <div class="info-box" style="border-color:#ef4444;background:rgba(239,68,68,0.1)">
            <div class="section-header" style="color:#ef4444!important;border-color:#ef4444!important">⚠ TOP PRIORITY ACTION</div>
            <p style="color:#fca5a5!important;font-size:0.95rem;margin:0;">{summary.get("top_recommendation","")}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋  HAZOP WORKSHEET", "📊  RISK MATRIX VIEW", "💾  EXPORT"])

    with tab1:
        st.markdown('<div class="section-header">// HAZOP Deviation Table</div>', unsafe_allow_html=True)

        # Table header
        st.markdown("""
        <div style="overflow-x:auto;">
        <table style="width:100%;border-collapse:collapse;font-family:'IBM Plex Sans',sans-serif;font-size:0.82rem;">
            <thead>
                <tr style="background:#1e3a5f;border-bottom:2px solid #f97316;">
                    <th style="padding:10px 8px;color:#fbbf24;text-align:center;font-weight:700;white-space:nowrap;">#</th>
                    <th style="padding:10px 8px;color:#fbbf24;text-align:center;font-weight:700;white-space:nowrap;">Guide Word</th>
                    <th style="padding:10px 8px;color:#fbbf24;text-align:center;font-weight:700;white-space:nowrap;">Parameter</th>
                    <th style="padding:10px 8px;color:#fbbf24;text-align:left;font-weight:700;">Deviation</th>
                    <th style="padding:10px 8px;color:#fbbf24;text-align:left;font-weight:700;">Possible Causes</th>
                    <th style="padding:10px 8px;color:#fbbf24;text-align:left;font-weight:700;">Consequences</th>
                    <th style="padding:10px 8px;color:#fbbf24;text-align:left;font-weight:700;">Safeguards</th>
                    <th style="padding:10px 8px;color:#fbbf24;text-align:left;font-weight:700;">Recommendations</th>
                    <th style="padding:10px 8px;color:#fbbf24;text-align:center;font-weight:700;white-space:nowrap;">Likelihood</th>
                    <th style="padding:10px 8px;color:#fbbf24;text-align:center;font-weight:700;white-space:nowrap;">Severity</th>
                    <th style="padding:10px 8px;color:#fbbf24;text-align:center;font-weight:700;white-space:nowrap;">Risk</th>
                </tr>
            </thead>
            <tbody>
        """, unsafe_allow_html=True)

        RISK_BG   = {"CRITICAL": "rgba(239,68,68,0.15)",  "HIGH": "rgba(249,115,22,0.12)", "MEDIUM": "rgba(234,179,8,0.1)",  "LOW": "rgba(34,197,94,0.08)"}
        RISK_BADGE= {"CRITICAL": "#ef4444", "HIGH": "#f97316", "MEDIUM": "#eab308", "LOW": "#22c55e"}
        GW_COLOR  = {"NO":"#ef4444","MORE":"#f97316","LESS":"#3b82f6","REVERSE":"#a855f7","OTHER THAN":"#ec4899","AS WELL AS":"#06b6d4","PART OF":"#84cc16"}

        for i, dev in enumerate(deviations):
            risk    = dev.get("risk_level", "LOW")
            gw      = dev.get("guide_word", "")
            row_bg  = "#1e293b" if i % 2 == 0 else "#162032"
            rbg     = RISK_BG.get(risk, "transparent")
            rcol    = RISK_BADGE.get(risk, "#64748b")
            gwcol   = GW_COLOR.get(gw, "#94a3b8")

            causes  = "<br>".join([f"• {c}" for c in dev.get("possible_causes", [])])
            conseqs = "<br>".join([f"⚡ {c}" for c in dev.get("consequences", [])])
            safeg   = "<br>".join([f"✅ {s}" for s in dev.get("safeguards", [])])
            recs    = "<br>".join([f"🔧 {r}" for r in dev.get("recommendations", [])])

            st.markdown(f"""
            <tr style="background:{row_bg};border-bottom:1px solid #1e3a5f;vertical-align:top;">
                <td style="padding:10px 8px;text-align:center;color:#64748b;font-weight:700;">{i+1}</td>
                <td style="padding:10px 8px;text-align:center;">
                    <span style="background:{gwcol}22;color:{gwcol};border:1px solid {gwcol};border-radius:4px;padding:3px 8px;font-weight:700;font-size:0.75rem;white-space:nowrap;font-family:'IBM Plex Mono',monospace;">{gw}</span>
                </td>
                <td style="padding:10px 8px;text-align:center;color:#94a3b8;font-weight:600;white-space:nowrap;">{dev.get('parameter','')}</td>
                <td style="padding:10px 8px;color:#f1f5f9;font-weight:600;min-width:140px;">{dev.get('deviation','')}</td>
                <td style="padding:10px 8px;color:#cbd5e1;min-width:180px;line-height:1.7;">{causes}</td>
                <td style="padding:10px 8px;color:#fca5a5;min-width:180px;line-height:1.7;">{conseqs}</td>
                <td style="padding:10px 8px;color:#86efac;min-width:170px;line-height:1.7;">{safeg}</td>
                <td style="padding:10px 8px;color:#fde68a;min-width:180px;line-height:1.7;">{recs}</td>
                <td style="padding:10px 8px;text-align:center;color:#94a3b8;white-space:nowrap;">{dev.get('likelihood','')}</td>
                <td style="padding:10px 8px;text-align:center;color:#e2e8f0;white-space:nowrap;">{dev.get('severity','')}</td>
                <td style="padding:10px 8px;text-align:center;background:{rbg};">
                    <span style="color:{rcol};font-weight:700;font-family:'IBM Plex Mono',monospace;font-size:0.78rem;">{RISK_EMOJI.get(risk,'')} {risk}</span>
                </td>
            </tr>
            """, unsafe_allow_html=True)

        st.markdown("</tbody></table></div>", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="section-header">// Risk Distribution</div>', unsafe_allow_html=True)
        risk_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for d in data.get("deviations", []):
            r = d.get("risk_level", "LOW")
            if r in risk_counts: risk_counts[r] += 1
        df_risk = pd.DataFrame({"Count": risk_counts}).rename_axis("Risk Level")
        st.bar_chart(df_risk, color="#f97316")

        st.markdown('<div class="section-header">// All Deviations Summary</div>', unsafe_allow_html=True)
        rows = [{"Guide Word": d.get("guide_word",""), "Parameter": d.get("parameter",""),
                 "Deviation": d.get("deviation",""), "Risk": d.get("risk_level",""),
                 "Likelihood": d.get("likelihood",""), "Severity": d.get("severity","")}
                for d in data.get("deviations", [])]
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with tab3:
        st.markdown('<div class="section-header">// Export Options</div>', unsafe_allow_html=True)
        ec1, ec2 = st.columns(2)
        with ec1:
            st.download_button("⬇️ Download JSON Report",
                data=json.dumps(data, indent=2),
                file_name=f"HAZOP_{data.get('node_name','node').replace(' ','_')}.json",
                mime="application/json", use_container_width=True)
        with ec2:
            rows_csv = [{"Node": data.get("node_name",""), "Guide Word": d.get("guide_word",""),
                "Parameter": d.get("parameter",""), "Deviation": d.get("deviation",""),
                "Causes": " | ".join(d.get("possible_causes",[])),
                "Consequences": " | ".join(d.get("consequences",[])),
                "Safeguards": " | ".join(d.get("safeguards",[])),
                "Recommendations": " | ".join(d.get("recommendations",[])),
                "Risk Level": d.get("risk_level",""), "Likelihood": d.get("likelihood",""),
                "Severity": d.get("severity","")} for d in data.get("deviations",[])]
            st.download_button("⬇️ Download CSV Worksheet",
                data=pd.DataFrame(rows_csv).to_csv(index=False),
                file_name=f"HAZOP_{data.get('node_name','node').replace(' ','_')}.csv",
                mime="text/csv", use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        report_lines = ["HAZOP STUDY REPORT", "="*60,
            f"Node: {data.get('node_name','')}", f"Process: {st.session_state.get('process_type','')}",
            f"Intent: {data.get('process_intent','')}", "",
            "RISK SUMMARY:",
            f"  Critical : {summary.get('critical_count',0)}",
            f"  High     : {summary.get('high_count',0)}",
            f"  Medium   : {summary.get('medium_count',0)}",
            f"  Low      : {summary.get('low_count',0)}", "",
            f"TOP ACTION : {summary.get('top_recommendation','')}", "", "="*60, "DEVIATIONS:", ""]
        for i, d in enumerate(data.get("deviations",[]), 1):
            report_lines += [
                f"{i}. [{d.get('risk_level','')}] {d.get('deviation','')}",
                f"   Guide Word   : {d.get('guide_word','')}",
                f"   Parameter    : {d.get('parameter','')}",
                f"   Causes       : {'; '.join(d.get('possible_causes',[]))}",
                f"   Consequences : {'; '.join(d.get('consequences',[]))}",
                f"   Safeguards   : {'; '.join(d.get('safeguards',[]))}",
                f"   Recommend    : {'; '.join(d.get('recommendations',[]))}",
                f"   Likelihood   : {d.get('likelihood','')} | Severity: {d.get('severity','')}", ""]
        report_text = "\n".join(report_lines)
        st.text_area("Report Preview", value=report_text, height=250)
        st.download_button("⬇️ Download Text Report",
            data=report_text,
            file_name=f"HAZOP_Report.txt",
            mime="text/plain", use_container_width=True)

else:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">🛡️</div>
        <div class="empty-state-text">ENTER PROCESS NODE DESCRIPTION AND CLICK RUN HAZOP</div>
        <div class="empty-state-sub">Use the sidebar examples to get started quickly</div>
    </div>""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;border-top:1px solid #1e293b;margin-top:2rem;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#334155;letter-spacing:2px;margin-bottom:0.6rem;">
        IEC 61882 · GROQ LLAMA 3.3 · NOT A SUBSTITUTE FOR CERTIFIED HAZOP STUDY
    </div>
    <div style="font-family:'IBM Plex Sans',sans-serif;font-size:0.85rem;letter-spacing:0.5px;">
        <span style="color:#22c55e;font-weight:600;">Developed by</span>
        <span style="color:#ffffff;font-weight:700;"> Zunair Shahzad</span>
        <span style="color:#fbbf24;font-weight:500;"> · UET Lahore</span>
        <span style="color:#ffffff;font-weight:400;"> (New Campus)</span>
    </div>
</div>""", unsafe_allow_html=True)
