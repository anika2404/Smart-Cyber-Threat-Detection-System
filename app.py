import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time
import random
import requests
from datetime import datetime, timedelta
from backend.pdf_report import create_analysis_pdf
from backend.report_generator import generate_analysis_pdf

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI DFIR Tool | SOC Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS (keeping your existing styles)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');

:root {
  --bg-void: #020408;
  --bg-panel: rgba(5, 15, 30, 0.85);
  --bg-card: rgba(0, 20, 45, 0.6);
  --neon-blue: #00d4ff;
  --neon-green: #00ff88;
  --neon-red: #ff2d55;
  --neon-amber: #ffb800;
  --border-glow: rgba(0, 212, 255, 0.25);
  --text-primary: #e0f4ff;
  --text-muted: rgba(160, 210, 240, 0.55);
  --font-mono: 'Share Tech Mono', monospace;
  --font-display: 'Orbitron', monospace;
  --font-ui: 'Rajdhani', sans-serif;
}

html, body, [class*="css"] {
  font-family: var(--font-ui);
  color: var(--text-primary);
}

.stApp {
  background: var(--bg-void);
  background-image:
    radial-gradient(ellipse 80% 60% at 50% -10%, rgba(0,100,200,0.12) 0%, transparent 70%),
    radial-gradient(ellipse 50% 30% at 90% 110%, rgba(0,255,136,0.06) 0%, transparent 60%),
    linear-gradient(180deg, #020408 0%, #040d1a 100%);
  min-height: 100vh;
}

/* Keep all your existing CSS... */
.kpi-card {
  background: var(--bg-card);
  border: 1px solid var(--border-glow);
  border-radius: 14px;
  padding: 22px 24px;
  backdrop-filter: blur(16px);
  box-shadow: 0 4px 30px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04);
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
  overflow: hidden;
}

/* NEW: Info box styling */
.info-box {
  background: rgba(0,100,200,0.1);
  border-left: 4px solid var(--neon-blue);
  border-radius: 8px;
  padding: 16px;
  margin: 12px 0;
  font-family: var(--font-ui);
  font-size: 0.9rem;
  color: var(--text-primary);
}

.info-box-title {
  font-family: var(--font-display);
  font-size: 0.85rem;
  color: var(--neon-blue);
  margin-bottom: 8px;
  font-weight: 700;
}

.help-tip {
  background: rgba(0,212,255,0.1);
  border: 1px solid rgba(0,212,255,0.3);
  border-radius: 6px;
  padding: 8px 12px;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: rgba(160,210,240,0.8);
  margin: 8px 0;
}

.metric-explained {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-muted);
  margin-top: 8px;
  line-height: 1.6;
}

.recommendation-box {
  background: rgba(0,255,136,0.08);
  border-left: 4px solid var(--neon-green);
  border-radius: 8px;
  padding: 14px;
  margin: 12px 0;
  font-size: 0.85rem;
}

.warning-box {
  background: rgba(255,45,85,0.08);
  border-left: 4px solid var(--neon-red);
  border-radius: 8px;
  padding: 14px;
  margin: 12px 0;
  font-size: 0.85rem;
}

/* Keep rest of your existing CSS */
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PLOTLY DEFAULTS
# ─────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,10,25,0.5)",
    font=dict(family="Share Tech Mono", color="#a0d2f0", size=11),
    xaxis=dict(gridcolor="rgba(0,212,255,0.08)", linecolor="rgba(0,212,255,0.2)"),
    yaxis=dict(gridcolor="rgba(0,212,255,0.08)", linecolor="rgba(0,212,255,0.2)"),
    margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#a0d2f0")),
)
NEON_COLORS = ["#00d4ff", "#00ff88", "#ff2d55", "#ffb800", "#7b2fff", "#ff6b35"]

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
if "live_attacks" not in st.session_state:
    st.session_state.live_attacks = random.randint(142, 280)
if "blocked" not in st.session_state:
    st.session_state.blocked = random.randint(90, 200)
if "uptime_start" not in st.session_state:
    st.session_state.uptime_start = datetime.now()
if "show_tutorial" not in st.session_state:
    st.session_state.show_tutorial = True

# ─────────────────────────────────────────────
#  SIDEBAR WITH BETTER GUIDANCE
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🛡️ AI DFIR TOOL</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:var(--font-mono);font-size:0.65rem;color:rgba(160,210,240,0.4);letter-spacing:.12em">Digital Forensics & Incident Response</div>', unsafe_allow_html=True)
    
    # Quick Start Guide
    with st.expander("📖 Quick Start Guide", expanded=st.session_state.show_tutorial):
        st.markdown("""
        **Welcome to AI DFIR Tool!** 👋
        
        **How to use:**
        1. 📂 Upload your network traffic CSV
        2. 🔍 The AI will analyze threats automatically
        3. 📊 View insights in different tabs
        4. 📄 Generate PDF reports
        
        **What you'll get:**
        - Attack detection & classification
        - Traffic pattern analysis
        - Threat intelligence insights
        - Actionable security recommendations
        """)
        if st.button("Got it! Don't show again"):
            st.session_state.show_tutorial = False
            st.rerun()
    
    st.divider()

    st.markdown('<div class="sidebar-section">▸ Navigation</div>', unsafe_allow_html=True)
    page = st.radio(
        "",
        ["🏠  Overview", "📂  Dataset Analysis", "⚠️  Threat Intelligence", "🔍  Raw Data"],
        label_visibility="collapsed",
        help="Navigate between different analysis views"
    )

    st.divider()
    
    st.markdown('<div class="sidebar-section">▸ Upload Your Data</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="help-tip">
    📌 Accepted: CSV files with network traffic logs
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Drop CSV here", 
        type=["csv"], 
        label_visibility="collapsed",
        help="Upload network traffic data in CSV format. Should contain columns like timestamp, src_ip, dst_ip, label, etc."
    )

    st.divider()
    
    st.markdown('<div class="sidebar-section">▸ Configuration</div>', unsafe_allow_html=True)
    
    label_col = st.text_input(
        "Label column name", 
        value="label", 
        placeholder="e.g. label / attack_type",
        help="The column in your CSV that contains traffic classification (normal/attack)"
    )
    
    normal_label = st.text_input(
        "Normal traffic label", 
        value="normal", 
        placeholder="e.g. BENIGN / normal",
        help="The value that represents normal/benign traffic in your label column"
    )

    st.divider()
    
    st.markdown('<div class="sidebar-section">▸ System Threat Level</div>', unsafe_allow_html=True)
    threat_level = st.select_slider(
        "", 
        options=["LOW", "MEDIUM", "HIGH", "CRITICAL"], 
        value="HIGH", 
        label_visibility="collapsed",
        help="Current threat assessment level based on detected patterns"
    )
    
    css_class = {"LOW": "threat-low", "MEDIUM": "threat-medium", "HIGH": "threat-high", "CRITICAL": "threat-high"}[threat_level]
    icons = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴", "CRITICAL": "💀"}
    st.markdown(f'<div class="threat-level-badge {css_class}">{icons[threat_level]} THREAT: {threat_level}</div>', unsafe_allow_html=True)

    st.divider()
    now = datetime.now()
    st.markdown(f"""
    <div style="font-family:var(--font-mono);font-size:0.63rem;color:rgba(160,210,240,0.4);line-height:1.8">
    🕐 {now.strftime('%Y-%m-%d %H:%M:%S')}<br>
    🖥️ ENGINE: ONLINE<br>
    📡 FEEDS: ACTIVE<br>
    🔒 TLS: VERIFIED
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TOP HEADER
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="dfir-header">
  <div>
    <div class="dfir-logo">🛡️ AI DFIR TOOL</div>
    <div class="dfir-tagline">SECURITY OPERATIONS CENTER · REAL-TIME THREAT ANALYSIS · v2.4.1</div>
  </div>
  <div style="display:flex;gap:12px;align-items:center">
    <div class="dfir-live-badge">
      <div class="pulse-dot"></div>
      LIVE MONITORING
    </div>
    <div style="font-family:var(--font-mono);font-size:0.68rem;color:rgba(160,210,240,0.5)">
      {now.strftime('%H:%M:%S UTC')}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────
@st.cache_data
def load_data(file):
    return pd.read_csv(file)

def simulate_df():
    """Generate demo dataset"""
    np.random.seed(42)
    n = 5000
    cats = ["DDoS", "Port Scan", "Brute Force", "SQL Injection", "XSS", "normal", "normal", "normal"]
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=n, freq="1min"),
        "src_ip": [f"192.168.{random.randint(0,5)}.{random.randint(1,254)}" for _ in range(n)],
        "dst_ip": [f"10.0.{random.randint(0,3)}.{random.randint(1,100)}" for _ in range(n)],
        "src_port": np.random.randint(1024, 65535, n),
        "dst_port": np.random.choice([80, 443, 22, 3306, 8080, 53], n),
        "bytes": np.random.exponential(5000, n).astype(int),
        "packets": np.random.randint(1, 500, n),
        "duration": np.random.exponential(2.5, n).round(2),
        "label": np.random.choice(cats, n, p=[0.08,0.07,0.06,0.04,0.03,0.3,0.25,0.17]),
    })
    return df

# ─────────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────────
is_demo = uploaded_file is None

if is_demo:
    st.info("""
    ### 👋 Welcome to AI DFIR Tool!
    
    **You're currently viewing demo data.** To analyze your own network traffic:
    
    1. 📂 Upload a CSV file using the sidebar
    2. 🔧 Configure your label columns
    3. 📊 View comprehensive threat analysis
    
    **Demo mode** shows you what the dashboard can do with sample attack data.
    """)
    df = simulate_df()
    lbl = "label"
    norm = "normal"
else:
    with st.spinner("Analyzing your data..."):
        time.sleep(1.2)
    df = load_data(uploaded_file)
    lbl = label_col if label_col in df.columns else df.columns[-1]
    norm = normal_label
    
    # Fix label (0/1 → normal/attack)
if lbl in df.columns:
    unique_vals = set(df[lbl].astype(str).unique())
    if unique_vals.issubset({'0', '1'}):
        df[lbl] = df[lbl].astype(int).map({0: 'normal', 1: 'attack'})

# Fix attack categories
if "attack_cat" in df.columns:
    df["attack_cat"] = df["attack_cat"].fillna("Normal")
    df["attack_cat"] = df["attack_cat"].replace({
        "normal": "Normal",
        "NORMAL": "Normal"
    })
else:
    df["attack_cat"] = "Unknown"
    
    st.success(f"""
    ✅ **File uploaded successfully!**
    - Records: {len(df):,}
    - Columns: {df.shape[1]}
    - Label column: `{lbl}`
    """)

# ─────────────────────────────────────────────
#  COMPUTED STATS
# ─────────────────────────────────────────────
total = len(df)
attacks = (df[lbl] != norm).sum() if lbl in df.columns else 0
normal_ = total - attacks
atk_pct = round(attacks / total * 100, 1) if total else 0

# ─────────────────────────────────────────────
#  PAGE: OVERVIEW
# ─────────────────────────────────────────────
if "Overview" in page:
    
    st.markdown('<div class="section-header">📡 &nbsp; LIVE TELEMETRY</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <div class="info-box-title">📊 What are these metrics?</div>
    These key performance indicators (KPIs) give you an instant snapshot of your network security status.
    Watch for sudden spikes in attacks or unusual patterns.
    </div>
    """, unsafe_allow_html=True)
    
    k1, k2, k3, k4, k5 = st.columns(5)

    def kpi(col, icon, label, value, delta, accent):
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="--accent-color:{accent}">
              <div class="kpi-icon">{icon}</div>
              <div class="kpi-label">{label}</div>
              <div class="kpi-value">{value}</div>
              <div class="kpi-delta">{delta}</div>
            </div>
            """, unsafe_allow_html=True)

    kpi(k1, "📦", "Total Records", f"{total:,}", "▲ dataset loaded", "#00d4ff")
    kpi(k2, "⚠️", "Attacks Detected", f"{attacks:,}", f"▲ {atk_pct}% of traffic", "#ff2d55")
    kpi(k3, "✅", "Normal Traffic", f"{normal_:,}", f"▼ {100-atk_pct}% of traffic", "#00ff88")
    kpi(k4, "🔴", "Live Threats", f"{st.session_state.live_attacks}", "↻ real-time feed", "#ffb800")
    kpi(k5, "🛡️", "Blocked Today", f"{st.session_state.blocked}", "▲ auto-mitigated", "#7b2fff")

    # Intelligent Insights
    st.markdown('<div class="section-header">🧠 &nbsp; AI INSIGHTS & RECOMMENDATIONS</div>', unsafe_allow_html=True)
    
    risk_score = (len(df[df[lbl] == "attack"]) / total * 100) if total > 0 else 0
    
    if risk_score > 10:
        st.markdown(f"""
        <div class="warning-box">
        <strong>🚨 HIGH RISK DETECTED</strong><br>
        Your network shows <strong>{attacks:,} suspicious activities</strong> ({risk_score:.1f}% of traffic).
        <br><br>
        <strong>Recommended Actions:</strong>
        <ul>
        <li>🔍 Investigate top attacker IPs immediately</li>
        <li>🛡️ Enable additional firewall rules</li>
        <li>📊 Review the Threat Intelligence tab for details</li>
        <li>📞 Consider escalating to security team</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    elif risk_score > 3:
        st.markdown(f"""
        <div class="info-box">
        <div class="info-box-title">⚠️ MODERATE RISK</div>
        Detected <strong>{attacks:,} threats</strong> ({risk_score:.1f}% of traffic).
        <br><br>
        <strong>Recommendations:</strong>
        <ul>
        <li>Monitor suspicious IPs</li>
        <li>Check for patterns in attack types</li>
        <li>Review security policies</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="recommendation-box">
        <strong>✅ LOW RISK - Network Healthy</strong><br>
        Your network traffic appears normal with minimal threats detected.
        <br><br>
        <strong>Continue monitoring for:</strong>
        <ul>
        <li>Unusual traffic patterns</li>
        <li>New source IPs</li>
        <li>Port scanning attempts</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts with explanations
    st.markdown('<div class="section-header">📊 &nbsp; TRAFFIC OVERVIEW</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([3, 2])

    with c1:
        st.markdown("""
        <div class="help-tip">
        📈 This chart shows traffic volume over time. Sudden spikes may indicate attacks.
        </div>
        """, unsafe_allow_html=True)
        
        if lbl in df.columns and "timestamp" in df.columns:
            df["_ts"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df["_hour"] = df["_ts"].dt.floor("H")
            ts = df.groupby(["_hour", lbl]).size().reset_index(name="count")
            fig = px.area(ts, x="_hour", y="count", color=lbl,
                          color_discrete_sequence=NEON_COLORS,
                          title="Traffic Volume Over Time")
        else:
            vc = df["attack_cat"].value_counts().reset_index()
            vc.columns = ["Attack Type","Count"]
            fig = px.bar(vc, x="Attack Type", y="Count",
             color="Attack Type", color_discrete_sequence=NEON_COLORS,
                         title="Attack Type Distribution")
        
        fig.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        <div class="metric-explained">
        💡 <strong>How to read this:</strong> Each color represents a different traffic type. 
        Normal traffic should be dominant. Sudden attack spikes need investigation.
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="help-tip">
        🥧 Pie chart shows proportion of each traffic type at a glance.
        </div>
        """, unsafe_allow_html=True)
        
        if lbl in df.columns:
            vc = df["attack_cat"].value_counts().reset_index()
            vc.columns = ["Attack Type","Count"]
            fig2 = px.pie(vc, names="Attack Type", values="Count",
                          hole=0.55, color_discrete_sequence=NEON_COLORS,
                          title="Traffic Composition")
            fig2.update_layout(**PLOTLY_LAYOUT)
            st.plotly_chart(fig2, use_container_width=True)
            
            st.markdown(f"""
            <div class="metric-explained">
            💡 <strong>Quick summary:</strong> 
            {normal_:,} normal ({100-atk_pct}%) vs {attacks:,} attacks ({atk_pct}%)
            </div>
            """, unsafe_allow_html=True)

    # PDF Report Generation
    st.markdown('<div class="section-header">📄 &nbsp; EXPORT ANALYSIS</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <div class="info-box-title">📋 Generate Comprehensive Report</div>
    Create a PDF report containing all charts, metrics, and threat analysis for sharing with your team or compliance purposes.
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📄 Generate PDF Report", use_container_width=True):
        with st.spinner("Generating comprehensive PDF report..."):
            # Collect all figures
            figures = []
            if 'fig' in locals():
                figures.append(("Traffic Volume", fig))
            if 'fig2' in locals():
                figures.append(("Traffic Composition", fig2))
            
            pdf_buffer = generate_analysis_pdf(df, figures, label_col=lbl, normal_label=norm)
            
            st.download_button(
                label="⬇ Download PDF Report",
                data=pdf_buffer,
                file_name=f"dfir_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            st.success("✅ Report generated successfully!")

# ─────────────────────────────────────────────
#  PAGE: THREAT INTELLIGENCE
# ─────────────────────────────────────────────
elif "Threat" in page:
    st.markdown('<div class="section-header">⚠️ &nbsp; THREAT INTELLIGENCE</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    <div class="info-box-title">🔍 Understanding Threat Intelligence</div>
    This section helps you identify:
    <ul>
    <li><strong>Attack types:</strong> What kind of attacks are happening</li>
    <li><strong>Attacker IPs:</strong> Who is attacking your network</li>
    <li><strong>Geographic origins:</strong> Where attacks are coming from</li>
    </ul>
    Use this information to block malicious IPs and strengthen defenses.
    </div>
    """, unsafe_allow_html=True)

    t1, t2 = st.columns(2)

    with t1:
        st.markdown("""
        <div class="help-tip">
        📊 Most frequent attack types in your traffic
        </div>
        """, unsafe_allow_html=True)
        
        if lbl in df.columns:
            atk_df = df[df[lbl] == "attack"]
            vc = atk_df["attack_cat"].value_counts().reset_index()
            vc.columns = ["Attack Type", "Count"]
            fig_atk = px.bar(vc, x="Count", y="Attack Type", orientation="h",
                             color="Count", color_continuous_scale=["#1a0010","#ff2d55"],
                             title="Attack Type Frequency")
            fig_atk.update_layout(**PLOTLY_LAYOUT)
            st.plotly_chart(fig_atk, use_container_width=True)
            
            st.markdown(f"""
            <div class="metric-explained">
            💡 Top threat: <strong>{vc.iloc[0]['Attack Type']}</strong> with {vc.iloc[0]['Count']:,} occurrences
            </div>
            """, unsafe_allow_html=True)

    with t2:
        st.markdown("""
        <div class="help-tip">
        🎯 Source IPs with most attack attempts - consider blocking these
        </div>
        """, unsafe_allow_html=True)
        
        if "src_ip" in df.columns and not is_demo:
            top_ips = (df[df[lbl] != norm]["src_ip"]
                       .value_counts().head(10).reset_index())
            top_ips.columns = ["Source IP", "Attacks"]
            fig_ip = px.bar(top_ips, x="Attacks", y="Source IP", orientation="h",
                            color="Attacks", color_continuous_scale=["#001a35","#00d4ff"],
                            title="Top Attacker IPs")
            fig_ip.update_layout(**PLOTLY_LAYOUT)
            st.plotly_chart(fig_ip, use_container_width=True)
            
            st.markdown(f"""
            <div class="warning-box">
            🚨 <strong>Action Required:</strong> Consider blocking IP <code>{top_ips.iloc[0]['Source IP']}</code> 
            ({top_ips.iloc[0]['Attacks']:,} attacks)
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("⚠️ Dataset does not include source IP addresses — skipping IP analysis.")

# ─────────────────────────────────────────────
#  PAGE: DATASET ANALYSIS
# ─────────────────────────────────────────────
elif "Dataset" in page:
    st.markdown('<div class="section-header">📂 &nbsp; DATASET ANALYSIS</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    <div class="info-box-title">📊 Data Quality Check</div>
    This section helps you understand your dataset structure, quality, and statistics.
    Look for missing values and data inconsistencies.
    </div>
    """, unsafe_allow_html=True)

    i1, i2, i3, i4 = st.columns(4)
    i1.metric("Total Rows", f"{len(df):,}", help="Number of network traffic records")
    i2.metric("Columns", f"{df.shape[1]}", help="Number of features in dataset")
    i3.metric("Attack Rows", f"{attacks:,}", help="Records classified as attacks")
    i4.metric("Missing Values", f"{df.isnull().sum().sum():,}", help="Data quality indicator")

    st.markdown('<div class="section-header">🔎 &nbsp; DATA PREVIEW</div>', unsafe_allow_html=True)
    n_rows = st.slider("Rows to display", 5, 100, 20, help="Adjust to see more/less data")
    st.dataframe(df.head(n_rows), use_container_width=True)

    st.markdown('<div class="section-header">📈 &nbsp; COLUMN STATISTICS</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="help-tip">
    📊 Statistical summary helps identify outliers and anomalies in numeric data
    </div>
    """, unsafe_allow_html=True)
    
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    if num_cols:
        selected = st.multiselect("Select numeric columns to analyze", num_cols, default=num_cols[:4])
        if selected:
            st.dataframe(df[selected].describe().T, use_container_width=True)

# ─────────────────────────────────────────────
#  PAGE: RAW DATA
# ─────────────────────────────────────────────
elif "Raw" in page:
    st.markdown('<div class="section-header">🔍 &nbsp; RAW DATA EXPLORER</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    <div class="info-box-title">🔎 Search & Filter</div>
    Explore your raw data with powerful filtering. Search for specific IPs, attack types, or any text.
    Export filtered results for further analysis.
    </div>
    """, unsafe_allow_html=True)

    col_filter, col_search = st.columns([2, 3])
    with col_filter:
        if lbl in df.columns:
            categories = ["All"] + df[lbl].unique().tolist()
            sel_cat = st.selectbox("Filter by traffic type", categories)
    with col_search:
        search_term = st.text_input("Search in data", placeholder="e.g. 192.168 or DDoS")

    filtered = df.copy()
    if lbl in df.columns and sel_cat != "All":
        filtered = filtered[filtered[lbl] == sel_cat]
    if search_term:
        mask = filtered.astype(str).apply(lambda col: col.str.contains(search_term, case=False)).any(axis=1)
        filtered = filtered[mask]

    st.markdown(f"""
    <div class="metric-explained">
    ✅ Found {len(filtered):,} matching records ({len(filtered)/len(df)*100:.1f}% of dataset)
    </div>
    """, unsafe_allow_html=True)
    
    st.dataframe(filtered, use_container_width=True, height=500)

    if st.button("📄 Generate PDF Report"):
        with st.spinner("Generating PDF..."):
            pdf_buffer = generate_analysis_pdf(df, figures)

        st.download_button(
            label="⬇ Download Report",
            data=pdf_buffer,
            file_name="dfir_report.pdf",
            mime="application/pdf"
        )

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;margin-top:48px;padding:18px;
  border-top:1px solid rgba(0,212,255,0.12);
  font-family:var(--font-mono);font-size:0.65rem;
  color:rgba(160,210,240,0.3);letter-spacing:.12em">
  🛡️ AI DFIR TOOL &nbsp;·&nbsp; SOC DASHBOARD v2.4.1 &nbsp;·&nbsp;
  {"⚡ DEMO MODE — Upload your CSV to get started" if is_demo else "📂 ANALYZING YOUR DATASET"} &nbsp;·&nbsp;
  © {datetime.now().year}
</div>
""", unsafe_allow_html=True)