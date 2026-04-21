import streamlit as st
import anthropic
import json
import re
import io

# ── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HAZOP AI Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

.main { background-color: #0a0f1e; }

.stApp {
    background: linear-gradient(135deg, #0a0f1e 0%, #0d1a2e 50%, #0a1628 100%);
    color: #e2e8f0;
}

h1 {
    font-family: 'IBM Plex Mono', monospace !important;
    color: #f97316 !important;
    letter-spacing: -1px;
    font-size: 2rem !important;
}

h2, h3 {
    font-family: 'IBM Plex Mono', monospace !important;
    color: #fb923c !important;
}

.hero-banner {
    background: linear-gradient(90deg, #1a0a00 0%, #2d1000 50%, #1a0a00 100%);
    border: 1px solid #f97316;
    border-radius: 4px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}

.hero-banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #f97316, #fbbf24, #f97316, transparent);
}

.hero-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.2rem;
    font-weight: 600;
    color: #f97316;
    margin: 0;
    letter-spacing: -1px;
}

.hero-sub {
    font-size: 0.9rem;
    color: #94a3b8;
    margin-top: 0.3rem;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 1px;
}

.metric-card {
    background: rgba(249,115,22,0.08);
    border: 1px solid rgba(249,115,22,0.3);
    border-radius: 4px;
    padding: 1rem;
    text-align: center;
}

.metric-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2rem;
    font-weight: 600;
    color: #f97316;
}

.metric-label {
    font-size: 0.75rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

.risk-CRITICAL {
    background: rgba(239,68,68,0.15);
    border-left: 3px solid #ef4444;
    border-radius: 0 4px 4px 0;
    padding: 0.4rem 0.8rem;
    color: #fca5a5;
    font-weight: 600;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
}

.risk-HIGH {
    background: rgba(249,115,22,0.15);
    border-left: 3px solid #f97316;
    border-radius: 0 4px 4px 0;
    padding: 0.4rem 0.8rem;
    color: #fdba74;
    font-weight: 600;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
}

.risk-MEDIUM {
    background: rgba(234,179,8,0.12);
    border-left: 3px solid #eab308;
    border-radius: 0 4px 4px 0;
    padding: 0.4rem 0.8rem;
    color: #fde047;
    font-weight: 600;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
}

.risk-LOW {
    background: rgba(34,197,94,0.1);
    border-left: 3px solid #22c55e;
    border-radius: 0 4px 4px 0;
    padding: 0.4rem 0.8rem;
    color: #86efac;
    font-weight: 600;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
}

.section-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 2px;
    color: #f97316;
    text-transform: uppercase;
    border-bottom: 1px solid rgba(249,115,22,0.3);
    padding-bottom: 0.4rem;
    margin-bottom: 1rem;
}

.stTextArea textarea {
    background: #0d1a2e !important;
    border: 1px solid rgba(249,115,22,0.4) !important;
    color: #e2e8f0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.85rem !important;
    border-radius: 4px !important;
}

.stTextArea textarea:focus {
    border-color: #f97316 !important;
    box-shadow: 0 0 0 2px rgba(249,115,22,0.2) !important;
}

.stButton > button {
    background: linear-gradient(135deg, #f97316, #ea580c) !important;
    color: white !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    padding: 0.6rem 2rem !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #fb923c, #f97316) !important;
    box-shadow: 0 0 20px rgba(249,115,22,0.4) !important;
    transform: translateY(-1px) !important;
}

.stSelectbox > div > div {
    background: #0d1a2e !important;
    border: 1px solid rgba(249,115,22,0.4) !important;
    color: #e2e8f0 !important;
    border-radius: 4px !important;
}

.stDataFrame {
    border: 1px solid rgba(249,115,22,0.2) !important;
    border-radius: 4px !important;
}

div[data-testid="stDataFrame"] table {
    background: #0d1a2e !important;
    color: #e2e8f0 !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(249,115,22,0.2) !important;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace !important;
    color: #64748b !important;
    font-size: 0.8rem !important;
    letter-spacing: 1px !important;
}

.stTabs [aria-selected="true"] {
    color: #f97316 !important;
    border-bottom: 2px solid #f97316 !important;
}

.stSidebar {
    background: #060c18 !important;
    border-right: 1px solid rgba(249,115,22,0.2) !important;
}

.stSidebar .stMarkdown {
    color: #94a3b8 !important;
}

.hazop-row {
    background: rgba(13, 26, 46, 0.8);
    border: 1px solid rgba(249,115,22,0.1);
    border-radius: 4px;
    padding: 1rem;
    margin-bottom: 0.5rem;
}

.guide-word-badge {
    display: inline-block;
    background: rgba(249,115,22,0.15);
    border: 1px solid rgba(249,115,22,0.4);
    color: #f97316;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 2px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.info-box {
    background: rgba(249,115,22,0.06);
    border: 1px solid rgba(249,115,22,0.2);
    border-radius: 4px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
}

footer { display: none; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── HERO BANNER ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🛡️ HAZOP AI ASSISTANT</div>
    <div class="hero-sub">// HAZARD & OPERABILITY STUDY — POWERED BY CLAUDE AI //</div>
</div>
""", unsafe_allow_html=True)

# ── API CLIENT ───────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not key:
        st.error("❌ API key missing. Add ANTHROPIC_API_KEY in Streamlit secrets.")
        st.stop()
    return anthropic.Anthropic(api_key=key)

# ── HAZOP PROMPT ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a senior Process Safety Engineer with 20+ years of HAZOP experience.
Perform a rigorous HAZOP study on the given process node.

Return ONLY valid JSON — no markdown, no explanation, nothing else.

JSON format:
{
  "node_name": "string",
  "process_intent": "string (what this node is supposed to do)",
  "design_conditions": {"temperature": "...", "pressure": "...", "flow": "...", "composition": "..."},
  "deviations": [
    {
      "guide_word": "NO/MORE/LESS/REVERSE/OTHER THAN/AS WELL AS/PART OF",
      "parameter": "Flow/Temperature/Pressure/Level/Composition/...",
      "deviation": "full deviation phrase e.g. No Flow",
      "possible_causes": ["cause 1", "cause 2", "cause 3"],
      "consequences": ["consequence 1", "consequence 2"],
      "safeguards": ["existing safeguard 1", "safeguard 2"],
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

Be thorough. Generate 8-14 meaningful deviations covering all major guide words.
Focus on realistic industrial scenarios."""

def run_hazop(client, node_description: str, process_type: str) -> dict:
    prompt = f"""Process Type: {process_type}
Node Description: {node_description}

Perform complete HAZOP study. Return JSON only."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)

# ── RISK COLOR HELPER ────────────────────────────────────────────────────────
RISK_EMOJI = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
RISK_COLOR = {"CRITICAL": "#ef4444", "HIGH": "#f97316", "MEDIUM": "#eab308", "LOW": "#22c55e"}

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-header">// Configuration</div>', unsafe_allow_html=True)
    
    process_type = st.selectbox(
        "Process Industry",
        ["Oil & Gas", "Petrochemical", "Pharmaceutical", "Chemical Plant",
         "Power Generation", "Water Treatment", "Food & Beverage", "General"]
    )

    st.markdown('<div class="section-header">// Example Nodes</div>', unsafe_allow_html=True)
    
    examples = {
        "Heat Exchanger (Shell & Tube)": 
            "Shell and tube heat exchanger E-101. Hot process fluid (crude oil at 180°C, 8 bar) flows through shell side. Cooling water at 30°C, 4 bar flows through tube side. Design duty: 5 MW. Outlet process temperature: 120°C. Connected to upstream crude pump P-101 and downstream atmospheric distillation column T-101.",
        
        "Centrifugal Pump":
            "Centrifugal pump P-201 transferring flammable liquid (hexane) from storage tank TK-101 to reactor R-201. Flow rate: 50 m3/hr, discharge pressure: 6 bar, suction pressure: 1.5 bar. Motor driven. Equipped with mechanical seal. Ambient temperature operation. Liquid is flammable (flash point -22°C).",
        
        "High Pressure Reactor":
            "Continuous stirred tank reactor R-301. Exothermic reaction between ethylene oxide and water to produce ethylene glycol. Operating at 150°C, 3 bar. Jacket cooling with cooling water. Feed flow: 2000 kg/hr EO, 5000 kg/hr water. Relief valve set at 5 bar. Agitator driven by 75kW motor.",
        
        "Distillation Column":
            "Atmospheric distillation column T-101 separating benzene/toluene mixture. Feed at 50% benzene, 120°C. Column pressure: 1.1 bar. 30 trays. Condenser E-201 at top, reboiler E-202 at bottom. Reflux ratio: 2.5. Overhead product: 99% benzene. Bottom product: 99% toluene.",
        
        "Pressure Vessel / Storage":
            "Horizontal pressure vessel V-401 storing liquid ammonia. Capacity: 100 m3. Operating at -33°C, 1 bar (refrigerated storage). Relief valve set at 2.5 bar. Insulated. Located in open area with dyke wall. Connected to loading/unloading lines and refrigeration system."
    }
    
    selected = st.selectbox("Load Example", ["-- Select --"] + list(examples.keys()))

    st.markdown('<div class="section-header">// Filters</div>', unsafe_allow_html=True)
    show_risk = st.multiselect(
        "Show Risk Levels",
        ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        default=["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    )
    
    st.markdown("---")
    st.markdown("""
    <div style="font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; color: #475569; line-height: 1.8;">
    GUIDE WORDS:<br>
    NO · MORE · LESS<br>
    REVERSE · OTHER THAN<br>
    AS WELL AS · PART OF<br><br>
    IEC 61882 Compliant
    </div>
    """, unsafe_allow_html=True)

# ── MAIN INPUT ───────────────────────────────────────────────────────────────
col_in, col_btn = st.columns([5, 1])

with col_in:
    default_val = examples.get(selected, "") if selected != "-- Select --" else ""
    node_input = st.text_area(
        "Process Node Description",
        value=default_val,
        height=150,
        placeholder="Describe the process node in detail:\n- Equipment type and tag number\n- Operating conditions (T, P, flow rate)\n- Feed/product streams\n- Connected equipment\n- Any existing safety systems..."
    )

with col_btn:
    st.markdown("<br><br>", unsafe_allow_html=True)
    run_btn = st.button("▶ RUN HAZOP", use_container_width=True)

# ── RUN ──────────────────────────────────────────────────────────────────────
if run_btn:
    if not node_input.strip():
        st.warning("⚠️ Please describe the process node first.")
    else:
        client = get_client()
        
        with st.spinner("🤖 AI is conducting HAZOP study... (~15 seconds)"):
            try:
                data = run_hazop(client, node_input, process_type)
            except json.JSONDecodeError as e:
                st.error(f"❌ JSON parse error: {e}. Try again.")
                st.stop()
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.stop()
        
        st.session_state["hazop_data"] = data
        st.session_state["node_input"] = node_input
        st.session_state["process_type"] = process_type

# ── DISPLAY RESULTS ──────────────────────────────────────────────────────────
if "hazop_data" in st.session_state:
    data = st.session_state["hazop_data"]
    summary = data.get("summary", {})
    deviations = data.get("deviations", [])
    
    # Filter by selected risk levels
    deviations = [d for d in deviations if d.get("risk_level","LOW") in show_risk]

    # ── METRICS ROW ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(f"### 📍 Node: `{data.get('node_name', 'Process Node')}`")
    
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-num">{len(deviations)}</div><div class="metric-label">Total Deviations</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card" style="border-color:rgba(239,68,68,0.5)"><div class="metric-num" style="color:#ef4444">{summary.get("critical_count",0)}</div><div class="metric-label">Critical</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card" style="border-color:rgba(249,115,22,0.5)"><div class="metric-num" style="color:#f97316">{summary.get("high_count",0)}</div><div class="metric-label">High</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card" style="border-color:rgba(234,179,8,0.4)"><div class="metric-num" style="color:#eab308">{summary.get("medium_count",0)}</div><div class="metric-label">Medium</div></div>', unsafe_allow_html=True)
    with m5:
        st.markdown(f'<div class="metric-card" style="border-color:rgba(34,197,94,0.4)"><div class="metric-num" style="color:#22c55e">{summary.get("low_count",0)}</div><div class="metric-label">Low</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # ── PROCESS INTENT ────────────────────────────────────────────────────────
    st.markdown(f'<div class="info-box"><b style="color:#f97316;font-family:IBM Plex Mono,monospace;font-size:0.75rem;letter-spacing:1px;">DESIGN INTENT</b><br><span style="color:#cbd5e1;font-size:0.9rem;">{data.get("process_intent","")}</span></div>', unsafe_allow_html=True)

    # ── TOP RECOMMENDATION ────────────────────────────────────────────────────
    if summary.get("top_recommendation"):
        st.markdown(f'<div class="info-box" style="border-color:rgba(239,68,68,0.4);background:rgba(239,68,68,0.06)"><b style="color:#ef4444;font-family:IBM Plex Mono,monospace;font-size:0.75rem;letter-spacing:1px;">⚠ TOP PRIORITY ACTION</b><br><span style="color:#fca5a5;font-size:0.9rem;">{summary.get("top_recommendation","")}</span></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📋  HAZOP WORKSHEET", "📊  RISK MATRIX VIEW", "💾  EXPORT"])

    with tab1:
        st.markdown('<div class="section-header">// Deviation Analysis</div>', unsafe_allow_html=True)
        
        for i, dev in enumerate(deviations):
            risk = dev.get("risk_level", "LOW")
            emoji = RISK_EMOJI.get(risk, "⚪")
            color = RISK_COLOR.get(risk, "#64748b")
            
            with st.expander(f"{emoji} [{risk}]  {dev.get('guide_word','')} — {dev.get('deviation','')}  |  Severity: {dev.get('severity','')}"):
                c1, c2 = st.columns(2)
                
                with c1:
                    st.markdown(f'<div class="section-header">// Possible Causes</div>', unsafe_allow_html=True)
                    for cause in dev.get("possible_causes", []):
                        st.markdown(f"• {cause}")
                    
                    st.markdown(f'<div class="section-header" style="margin-top:1rem">// Consequences</div>', unsafe_allow_html=True)
                    for cons in dev.get("consequences", []):
                        st.markdown(f"⚡ {cons}")
                
                with c2:
                    st.markdown(f'<div class="section-header">// Existing Safeguards</div>', unsafe_allow_html=True)
                    for sg in dev.get("safeguards", []):
                        st.markdown(f"✅ {sg}")
                    
                    st.markdown(f'<div class="section-header" style="margin-top:1rem">// Recommendations</div>', unsafe_allow_html=True)
                    for rec in dev.get("recommendations", []):
                        st.markdown(f"🔧 **{rec}**")
                
                st.markdown(f"""
                <div style="display:flex;gap:1rem;margin-top:0.5rem;font-family:'IBM Plex Mono',monospace;font-size:0.75rem;">
                    <span style="color:#64748b">PARAMETER: <span style="color:#94a3b8">{dev.get('parameter','')}</span></span>
                    <span style="color:#64748b">LIKELIHOOD: <span style="color:#94a3b8">{dev.get('likelihood','')}</span></span>
                    <span style="color:#64748b">SEVERITY: <span style="color:{color}">{dev.get('severity','')}</span></span>
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="section-header">// Risk Distribution</div>', unsafe_allow_html=True)
        
        # Simple bar chart using st.bar_chart
        import pandas as pd
        
        risk_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for d in data.get("deviations", []):
            r = d.get("risk_level", "LOW")
            if r in risk_counts:
                risk_counts[r] += 1
        
        df_risk = pd.DataFrame({
            "Risk Level": list(risk_counts.keys()),
            "Count": list(risk_counts.values())
        }).set_index("Risk Level")
        
        st.bar_chart(df_risk, color="#f97316")
        
        # Summary table
        st.markdown('<div class="section-header" style="margin-top:1.5rem">// All Deviations Summary</div>', unsafe_allow_html=True)
        
        table_rows = []
        for d in data.get("deviations", []):
            table_rows.append({
                "Guide Word": d.get("guide_word",""),
                "Parameter": d.get("parameter",""),
                "Deviation": d.get("deviation",""),
                "Risk": d.get("risk_level",""),
                "Likelihood": d.get("likelihood",""),
                "Severity": d.get("severity","")
            })
        
        if table_rows:
            df_all = pd.DataFrame(table_rows)
            st.dataframe(
                df_all,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Risk": st.column_config.TextColumn("Risk Level", width="small"),
                }
            )

    with tab3:
        st.markdown('<div class="section-header">// Export Options</div>', unsafe_allow_html=True)
        
        ec1, ec2 = st.columns(2)
        
        with ec1:
            # JSON Export
            json_str = json.dumps(data, indent=2)
            st.download_button(
                "⬇️ Download Full Report (JSON)",
                data=json_str,
                file_name=f"HAZOP_{data.get('node_name','node').replace(' ','_')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with ec2:
            # CSV Export
            import pandas as pd
            rows = []
            for d in data.get("deviations", []):
                rows.append({
                    "Node": data.get("node_name",""),
                    "Guide Word": d.get("guide_word",""),
                    "Parameter": d.get("parameter",""),
                    "Deviation": d.get("deviation",""),
                    "Causes": " | ".join(d.get("possible_causes",[])),
                    "Consequences": " | ".join(d.get("consequences",[])),
                    "Safeguards": " | ".join(d.get("safeguards",[])),
                    "Recommendations": " | ".join(d.get("recommendations",[])),
                    "Risk Level": d.get("risk_level",""),
                    "Likelihood": d.get("likelihood",""),
                    "Severity": d.get("severity","")
                })
            df_export = pd.DataFrame(rows)
            csv_data = df_export.to_csv(index=False)
            st.download_button(
                "⬇️ Download HAZOP Worksheet (CSV)",
                data=csv_data,
                file_name=f"HAZOP_{data.get('node_name','node').replace(' ','_')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">// Full Text Report</div>', unsafe_allow_html=True)
        
        # Generate text report
        report_lines = [
            f"HAZOP STUDY REPORT",
            f"=" * 60,
            f"Node: {data.get('node_name','')}",
            f"Process Type: {st.session_state.get('process_type','')}",
            f"Design Intent: {data.get('process_intent','')}",
            f"",
            f"RISK SUMMARY:",
            f"  Critical: {summary.get('critical_count',0)}",
            f"  High:     {summary.get('high_count',0)}",
            f"  Medium:   {summary.get('medium_count',0)}",
            f"  Low:      {summary.get('low_count',0)}",
            f"",
            f"TOP PRIORITY: {summary.get('top_recommendation','')}",
            f"",
            f"=" * 60,
            f"DETAILED DEVIATIONS:",
            f"",
        ]
        
        for i, d in enumerate(data.get("deviations", []), 1):
            report_lines += [
                f"{i}. [{d.get('risk_level','')}] {d.get('deviation','')}",
                f"   Guide Word: {d.get('guide_word','')} | Parameter: {d.get('parameter','')}",
                f"   Causes: {'; '.join(d.get('possible_causes',[]))}",
                f"   Consequences: {'; '.join(d.get('consequences',[]))}",
                f"   Safeguards: {'; '.join(d.get('safeguards',[]))}",
                f"   Recommendations: {'; '.join(d.get('recommendations',[]))}",
                f"   Likelihood: {d.get('likelihood','')} | Severity: {d.get('severity','')}",
                f"",
            ]
        
        report_text = "\n".join(report_lines)
        st.text_area("Report Preview", value=report_text, height=300)
        st.download_button(
            "⬇️ Download Text Report (.txt)",
            data=report_text,
            file_name=f"HAZOP_Report_{data.get('node_name','node').replace(' ','_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

else:
    # ── EMPTY STATE ───────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding: 3rem 1rem; color: #334155;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🛡️</div>
        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 1rem; color: #475569; letter-spacing: 1px;">
            ENTER PROCESS NODE DESCRIPTION AND CLICK RUN HAZOP
        </div>
        <div style="font-size: 0.8rem; color: #334155; margin-top: 0.5rem;">
            Use the example nodes from the sidebar to get started quickly
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 2rem 0 1rem; font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; color: #1e293b; letter-spacing: 2px;">
IEC 61882 · AI-ASSISTED · NOT A SUBSTITUTE FOR CERTIFIED HAZOP STUDY
</div>
""", unsafe_allow_html=True)
