import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import random
from utils.data_generator import generate_sample_data
from utils.sentiment_analyzer import analyze_sentiment_batch
from utils.journey_mapper import map_customer_journeys
from agents.recommendation_agent import generate_recommendations
from agents.campaign_agent import generate_campaign

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CX Intelligence Platform",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #111118;
    --surface2: #16161f;
    --border: #1e1e2e;
    --accent: #6c63ff;
    --accent2: #ff6584;
    --accent3: #43e97b;
    --accent4: #f9a825;
    --text: #e8e8f0;
    --text-muted: #6b6b80;
    --positive: #43e97b;
    --negative: #ff6584;
    --neutral: #6c63ff;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

.stApp { background-color: var(--bg); }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .stMarkdown { color: var(--text); }

/* Hide default Streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 2rem; max-width: 1400px; }

/* Hero Header */
.hero-header {
    background: linear-gradient(135deg, #0a0a0f 0%, #111128 50%, #0a0a0f 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -10%;
    width: 40%;
    height: 200%;
    background: radial-gradient(ellipse, rgba(108,99,255,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-header::after {
    content: '';
    position: absolute;
    top: -50%;
    right: -5%;
    width: 30%;
    height: 200%;
    background: radial-gradient(ellipse, rgba(255,101,132,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.6rem;
    font-weight: 400;
    margin: 0 0 0.4rem;
    background: linear-gradient(135deg, #e8e8f0 30%, #6c63ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 0.95rem;
    color: var(--text-muted);
    font-weight: 300;
    letter-spacing: 0.02em;
    margin: 0;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(108,99,255,0.15);
    border: 1px solid rgba(108,99,255,0.3);
    border-radius: 100px;
    padding: 4px 12px;
    font-size: 0.75rem;
    color: #a09fff;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.05em;
    margin-bottom: 1rem;
}

/* Metric Cards */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: rgba(108,99,255,0.4); }
.metric-card .accent-line {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.metric-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    color: var(--text);
    line-height: 1.1;
    margin: 0.5rem 0 0.2rem;
}
.metric-label {
    font-size: 0.78rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 500;
}
.metric-delta {
    font-size: 0.82rem;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 0.3rem;
}
.delta-pos { color: var(--positive); }
.delta-neg { color: var(--negative); }

/* Section Headers */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 2rem 0 1rem;
}
.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: var(--text);
    margin: 0;
    font-weight: 400;
}
.section-line {
    flex: 1;
    height: 1px;
    background: var(--border);
}
.section-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-muted);
    letter-spacing: 0.1em;
}

/* Channel Cards */
.channel-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.75rem;
}
.channel-name {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    font-weight: 600;
    margin-bottom: 0.5rem;
}

/* Recommendation Cards */
.rec-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    border-left: 3px solid var(--accent);
    transition: all 0.2s;
}
.rec-card:hover {
    border-color: var(--accent);
    border-left-color: var(--accent2);
    background: var(--surface2);
}
.rec-card.high { border-left-color: var(--negative); }
.rec-card.medium { border-left-color: var(--accent4); }
.rec-card.low { border-left-color: var(--positive); }
.rec-priority {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 4px;
    display: inline-block;
    margin-bottom: 0.6rem;
}
.rec-priority.high { background: rgba(255,101,132,0.15); color: var(--negative); }
.rec-priority.medium { background: rgba(249,168,37,0.15); color: var(--accent4); }
.rec-priority.low { background: rgba(67,233,123,0.15); color: var(--positive); }
.rec-title { font-weight: 600; font-size: 0.95rem; margin-bottom: 0.4rem; color: var(--text); }
.rec-body { font-size: 0.85rem; color: var(--text-muted); line-height: 1.6; }
.rec-impact {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--accent);
    margin-top: 0.6rem;
}

/* Campaign Card */
.campaign-card {
    background: linear-gradient(135deg, rgba(108,99,255,0.08) 0%, rgba(255,101,132,0.05) 100%);
    border: 1px solid rgba(108,99,255,0.25);
    border-radius: 14px;
    padding: 1.8rem;
    margin-bottom: 1rem;
}
.campaign-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.2rem;
    color: var(--text);
    margin-bottom: 0.3rem;
}
.campaign-tag {
    display: inline-block;
    background: rgba(108,99,255,0.2);
    color: #a09fff;
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
    padding: 3px 10px;
    border-radius: 4px;
    margin-right: 6px;
    margin-bottom: 0.8rem;
    letter-spacing: 0.08em;
}
.campaign-body { font-size: 0.87rem; color: var(--text-muted); line-height: 1.7; }

/* Sentiment Badge */
.sentiment-pos { color: var(--positive); font-weight: 600; }
.sentiment-neg { color: var(--negative); font-weight: 600; }
.sentiment-neu { color: var(--neutral); font-weight: 600; }

/* Styledivider */
.styled-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
}

/* Sidebar Styles */
.sidebar-section {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-muted);
    font-weight: 600;
    margin: 1.5rem 0 0.5rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
}

/* Plotly dark override */
.js-plotly-plot .plotly { background: transparent !important; }

/* Spinner */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), #8b83ff);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    letter-spacing: 0.02em;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }

/* Selectbox, Multiselect */
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: var(--surface) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid var(--border);
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: var(--text-muted);
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    padding: 0.6rem 1.2rem;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: var(--text) !important;
    border-bottom: 2px solid var(--accent) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ── Plotly Theme ──────────────────────────────────────────────────────────────
PLOTLY_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans', color='#6b6b80', size=11),
    xaxis=dict(gridcolor='#1e1e2e', linecolor='#1e1e2e', tickfont=dict(size=10)),
    yaxis=dict(gridcolor='#1e1e2e', linecolor='#1e1e2e', tickfont=dict(size=10)),
    margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#6b6b80', size=10)),
    colorway=['#6c63ff','#ff6584','#43e97b','#f9a825','#38bdf8','#e879f9']
)

CHANNEL_COLORS = {
    'Phone': '#6c63ff',
    'Chat': '#43e97b',
    'Web': '#ff6584'
}

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0 1rem;">
        <div style="font-family:'DM Serif Display',serif; font-size:1.3rem; color:#e8e8f0;">◈ CX Intelligence</div>
        <div style="font-size:0.72rem; color:#6b6b80; margin-top:2px; font-family:'JetBrains Mono',monospace;">v2.1.0 · PLATFORM</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Data Configuration</div>', unsafe_allow_html=True)

    date_range = st.selectbox("Time Range", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last 6 Months"], index=1)
    channels = st.multiselect("Channels", ["Phone", "Chat", "Web"], default=["Phone", "Chat", "Web"])
    segments = st.multiselect("Customer Segments", ["Enterprise", "SMB", "Consumer", "Trial"], default=["Enterprise", "SMB", "Consumer", "Trial"])

    st.markdown('<div class="sidebar-section">AI Configuration</div>', unsafe_allow_html=True)

    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
    rec_focus = st.selectbox("Recommendation Focus", ["Balanced", "Revenue Growth", "Retention", "Acquisition", "NPS Improvement"])
    campaign_budget = st.selectbox("Campaign Budget Tier", ["Starter ($1k–$5k)", "Growth ($5k–$20k)", "Scale ($20k–$100k)", "Enterprise ($100k+)"])

    st.markdown('<div class="sidebar-section">Actions</div>', unsafe_allow_html=True)
    run_analysis = st.button("◈  Run Full Analysis", use_container_width=True)
    st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)
    export_btn = st.button("↓  Export Report", use_container_width=True)

    st.markdown("""
    <div style="margin-top:2rem; padding:1rem; background:#111118; border:1px solid #1e1e2e; border-radius:10px;">
        <div style="font-size:0.72rem; color:#6b6b80; font-family:'JetBrains Mono',monospace; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.5rem;">Data Source</div>
        <div style="font-size:0.8rem; color:#e8e8f0;">📊 Synthetic Demo Data</div>
        <div style="font-size:0.75rem; color:#6b6b80; margin-top:0.3rem; line-height:1.5;">Connect GA4, Salesforce, or Zendesk via the integrations panel to use live data.</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# LOAD / GENERATE DATA
# ─────────────────────────────────────────────────────────────────────────────
days_map = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90, "Last 6 Months": 180}
n_days = days_map[date_range]

@st.cache_data(ttl=300)
def load_data(n_days, channels, segments):
    return generate_sample_data(n_days, channels, segments)

data = load_data(n_days, tuple(channels), tuple(segments))
df_interactions = data['interactions']
df_journey = data['journey']
df_web = data['web']

# ─────────────────────────────────────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-header">
    <div class="hero-badge">◈ AI-POWERED · REAL-TIME ANALYSIS</div>
    <div class="hero-title">Customer Experience Intelligence</div>
    <p class="hero-sub">Sentiment analysis · Journey mapping · Predictive recommendations · Campaign generation</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# KPI METRICS ROW
# ─────────────────────────────────────────────────────────────────────────────
total_interactions = len(df_interactions)
avg_sentiment = df_interactions['sentiment_score'].mean()
positive_pct = (df_interactions['sentiment'] == 'Positive').mean() * 100
conversion_rate = df_web['converted'].mean() * 100
csat = df_interactions['csat'].mean()
nps = df_interactions['nps'].mean()

col1, col2, col3, col4, col5, col6 = st.columns(6)

metrics = [
    (col1, f"{total_interactions:,}", "Total Interactions", "+12.4%", True, "#6c63ff"),
    (col2, f"{avg_sentiment:.2f}", "Avg Sentiment Score", "+0.08", True, "#43e97b"),
    (col3, f"{positive_pct:.1f}%", "Positive Sentiment", "+3.2pp", True, "#43e97b"),
    (col4, f"{conversion_rate:.1f}%", "Web Conversion Rate", "-0.4pp", False, "#ff6584"),
    (col5, f"{csat:.1f}/5", "CSAT Score", "+0.2", True, "#f9a825"),
    (col6, f"{nps:.0f}", "Net Promoter Score", "+5", True, "#38bdf8"),
]

for col, val, label, delta, is_pos, color in metrics:
    delta_class = "delta-pos" if is_pos else "delta-neg"
    delta_arrow = "▲" if is_pos else "▼"
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="accent-line" style="background:{color};"></div>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-delta {delta_class}">{delta_arrow} {delta} vs prior period</div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["  Sentiment Analysis  ", "  Customer Journeys  ", "  Web Analytics  ", "  AI Recommendations & Campaigns  "])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SENTIMENT ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header"><div class="section-title">Sentiment Overview</div><div class="section-line"></div><div class="section-tag">MULTI-CHANNEL</div></div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1.8, 1])

    with col_left:
        # Sentiment over time by channel
        df_time = df_interactions.copy()
        df_time['date'] = pd.to_datetime(df_time['date'])
        df_time_agg = df_time.groupby(['date','channel'])['sentiment_score'].mean().reset_index()

        fig = go.Figure()
        for ch in channels:
            sub = df_time_agg[df_time_agg['channel'] == ch]
            fig.add_trace(go.Scatter(
                x=sub['date'], y=sub['sentiment_score'],
                name=ch, mode='lines',
                line=dict(color=CHANNEL_COLORS.get(ch, '#6c63ff'), width=2),
                fill='tozeroy',
                fillcolor={'Phone': 'rgba(108,99,255,0.05)', 'Chat': 'rgba(67,233,123,0.05)', 'Web': 'rgba(255,101,132,0.05)'}.get(ch, 'rgba(108,99,255,0.05)'),
            ))
        fig.update_layout(title="Sentiment Score Trend by Channel", **PLOTLY_THEME)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        # Donut: sentiment distribution
        sent_counts = df_interactions['sentiment'].value_counts()
        fig2 = go.Figure(go.Pie(
            labels=sent_counts.index,
            values=sent_counts.values,
            hole=0.65,
            marker=dict(colors=['#43e97b','#ff6584','#6c63ff']),
            textinfo='percent',
            textfont=dict(size=11, color='#e8e8f0'),
        ))
        fig2.update_layout(
            title="Sentiment Distribution",
            annotations=[dict(text=f"{positive_pct:.0f}%<br><span style='font-size:10px'>Positive</span>", x=0.5, y=0.5, font_size=18, showarrow=False, font_color='#e8e8f0')],
            **PLOTLY_THEME
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Sentiment by channel breakdown
    st.markdown('<div class="section-header"><div class="section-title">Channel Breakdown</div><div class="section-line"></div></div>', unsafe_allow_html=True)

    cols = st.columns(len(channels))
    for i, ch in enumerate(channels):
        ch_df = df_interactions[df_interactions['channel'] == ch]
        pos = (ch_df['sentiment'] == 'Positive').mean() * 100
        neg = (ch_df['sentiment'] == 'Negative').mean() * 100
        neu = (ch_df['sentiment'] == 'Neutral').mean() * 100
        avg = ch_df['sentiment_score'].mean()

        with cols[i]:
            color = CHANNEL_COLORS.get(ch, '#6c63ff')
            st.markdown(f"""
            <div class="channel-card" style="border-top: 2px solid {color};">
                <div class="channel-name">{ch} Channel</div>
                <div style="font-family:'DM Serif Display',serif; font-size:1.8rem; color:#e8e8f0; margin-bottom:0.8rem;">{avg:.2f}</div>
                <div style="display:flex; gap:1rem; font-size:0.82rem;">
                    <span class="sentiment-pos">▲ {pos:.0f}%</span>
                    <span class="sentiment-neg">▼ {neg:.0f}%</span>
                    <span class="sentiment-neu">— {neu:.0f}%</span>
                </div>
                <div style="margin-top:0.8rem; background:#1e1e2e; border-radius:4px; height:4px; overflow:hidden;">
                    <div style="width:{pos}%; background:{color}; height:100%;"></div>
                </div>
                <div style="font-size:0.75rem; color:#6b6b80; margin-top:0.4rem;">{len(ch_df):,} interactions</div>
            </div>
            """, unsafe_allow_html=True)

    # Heatmap: sentiment by day of week and hour
    st.markdown('<div class="section-header"><div class="section-title">Sentiment Heatmap</div><div class="section-line"></div><div class="section-tag">HOUR × DAY</div></div>', unsafe_allow_html=True)

    df_interactions['hour'] = pd.to_datetime(df_interactions['date']).dt.hour
    df_interactions['dow'] = pd.to_datetime(df_interactions['date']).dt.day_name()
    heat = df_interactions.groupby(['dow','hour'])['sentiment_score'].mean().reset_index()
    heat_pivot = heat.pivot(index='dow', columns='hour', values='sentiment_score')
    day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    heat_pivot = heat_pivot.reindex([d for d in day_order if d in heat_pivot.index])

    fig3 = go.Figure(go.Heatmap(
        z=heat_pivot.values,
        x=[f"{h:02d}:00" for h in heat_pivot.columns],
        y=heat_pivot.index,
        colorscale=[[0,'#ff6584'],[0.5,'#1e1e2e'],[1,'#43e97b']],
        showscale=True,
        colorbar=dict(tickfont=dict(color='#6b6b80', size=10)),
    ))
    fig3.update_layout(title="Average Sentiment by Day & Hour", **PLOTLY_THEME)
    st.plotly_chart(fig3, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CUSTOMER JOURNEYS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header"><div class="section-title">Journey Funnel Analysis</div><div class="section-line"></div><div class="section-tag">CONVERSION PATHS</div></div>', unsafe_allow_html=True)

    col_f, col_s = st.columns([1, 1])

    with col_f:
        stages = ['Awareness','Consideration','Intent','Purchase','Retention']
        values = [10000, 6800, 3900, 2100, 1650]
        colors = ['#6c63ff','#8b83ff','#a09fff','#c4bfff','#43e97b']

        fig_funnel = go.Figure(go.Funnel(
            y=stages, x=values,
            textinfo="value+percent initial",
            marker=dict(color=colors),
            textfont=dict(color='#e8e8f0', size=11),
            connector=dict(line=dict(color='#1e1e2e', width=1)),
        ))
        fig_funnel.update_layout(title="Customer Acquisition Funnel", **PLOTLY_THEME)
        st.plotly_chart(fig_funnel, use_container_width=True)

    with col_s:
        # Sankey: channel → stage → outcome
        fig_sankey = go.Figure(go.Sankey(
            arrangement="snap",
            node=dict(
                pad=15, thickness=15,
                line=dict(color='#1e1e2e', width=0.5),
                label=["Phone","Chat","Web","Resolved","Escalated","Churned","Retained","Converted"],
                color=["#6c63ff","#43e97b","#ff6584","#6c63ff","#f9a825","#ff6584","#43e97b","#38bdf8"],
                hovertemplate='%{label}: %{value}<extra></extra>',
            ),
            link=dict(
                source=[0,0,1,1,2,2,3,3,4,5,6],
                target=[3,4,3,4,3,5,6,7,7,7,7],
                value=[420,180,380,120,510,290,510,310,300,140,380],
                color=["rgba(108,99,255,0.2)"]*11,
            ),
        ))
        fig_sankey.update_layout(title="Channel → Resolution → Outcome Flow", **PLOTLY_THEME)
        st.plotly_chart(fig_sankey, use_container_width=True)

    # Journey stage metrics
    st.markdown('<div class="section-header"><div class="section-title">Stage Performance</div><div class="section-line"></div></div>', unsafe_allow_html=True)

    stage_data = [
        ("Awareness", "10,000", "Visitors", "—", True, "#6c63ff", "Organic search (42%), Paid (31%), Social (27%)"),
        ("Consideration", "6,800", "Engaged Users", "68.0%", True, "#8b83ff", "Avg. 3.2 pages/session · 4:20 time on site"),
        ("Intent", "3,900", "High-Intent", "57.4%", False, "#a09fff", "Cart abandonment: 38% · Wishlist adds: 22%"),
        ("Purchase", "2,100", "Converted", "53.8%", True, "#43e97b", "Avg order value: $142 · Repeat rate: 34%"),
        ("Retention", "1,650", "Retained (90d)", "78.6%", True, "#43e97b", "LTV: $890 · NPS contribution: +42"),
    ]

    for stage, val, label, rate, is_pos, color, detail in stage_data:
        delta_str = f" · <span style='color:{'#43e97b' if is_pos else '#ff6584'}'>{rate} pass-through</span>" if rate != "—" else ""
        st.markdown(f"""
        <div class="channel-card" style="border-left:3px solid {color}; display:flex; align-items:center; gap:1.5rem;">
            <div style="min-width:120px;">
                <div class="channel-name">{stage}</div>
                <div style="font-family:'DM Serif Display',serif; font-size:1.6rem; color:#e8e8f0;">{val}</div>
                <div style="font-size:0.78rem; color:#6b6b80;">{label}{delta_str}</div>
            </div>
            <div style="flex:1; font-size:0.82rem; color:#6b6b80; border-left:1px solid #1e1e2e; padding-left:1.5rem;">{detail}</div>
        </div>
        """, unsafe_allow_html=True)

    # Drop-off analysis
    st.markdown('<div class="section-header"><div class="section-title">Drop-off Analysis</div><div class="section-line"></div><div class="section-tag">WHERE CUSTOMERS LEAVE</div></div>', unsafe_allow_html=True)

    dropoff_reasons = {
        'Price concerns': 28,
        'Complexity/UX friction': 22,
        'Competitor switched': 18,
        'Support experience': 15,
        'Feature gap': 12,
        'Other': 5
    }
    fig_bar = go.Figure(go.Bar(
        x=list(dropoff_reasons.values()),
        y=list(dropoff_reasons.keys()),
        orientation='h',
        marker=dict(
            color=list(dropoff_reasons.values()),
            colorscale=[[0,'#1e1e2e'],[1,'#ff6584']],
            showscale=False,
        ),
        text=[f"{v}%" for v in dropoff_reasons.values()],
        textposition='outside',
        textfont=dict(color='#6b6b80', size=10),
    ))
    fig_bar.update_layout(title="Top Drop-off Reasons", **PLOTLY_THEME, height=280)
    st.plotly_chart(fig_bar, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — WEB ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header"><div class="section-title">Web Behavior Analytics</div><div class="section-line"></div><div class="section-tag">TRAFFIC & ENGAGEMENT</div></div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        # Sessions over time
        df_web_daily = df_web.groupby('date').agg(
            sessions=('session_id','count'),
            conversions=('converted','sum'),
            bounce=('bounced','mean')
        ).reset_index()

        fig_sess = make_subplots(specs=[[{"secondary_y": True}]])
        fig_sess.add_trace(go.Bar(
            x=df_web_daily['date'], y=df_web_daily['sessions'],
            name='Sessions', marker_color='rgba(108,99,255,0.6)',
        ), secondary_y=False)
        fig_sess.add_trace(go.Scatter(
            x=df_web_daily['date'], y=df_web_daily['conversions'],
            name='Conversions', line=dict(color='#43e97b', width=2), mode='lines+markers',
            marker=dict(size=4),
        ), secondary_y=True)
        fig_sess.update_layout(title="Daily Sessions & Conversions", **PLOTLY_THEME)
        st.plotly_chart(fig_sess, use_container_width=True)

    with col_b:
        # Traffic sources
        sources = {'Organic Search': 38, 'Paid Search': 24, 'Social Media': 18, 'Direct': 12, 'Email': 5, 'Referral': 3}
        fig_src = go.Figure(go.Pie(
            labels=list(sources.keys()),
            values=list(sources.values()),
            hole=0.55,
            marker=dict(colors=['#6c63ff','#ff6584','#43e97b','#f9a825','#38bdf8','#e879f9']),
            textinfo='label+percent',
            textfont=dict(size=10, color='#e8e8f0'),
            insidetextorientation='radial',
        ))
        fig_src.update_layout(title="Traffic Source Breakdown", **PLOTLY_THEME, showlegend=False)
        st.plotly_chart(fig_src, use_container_width=True)

    # Page performance
    st.markdown('<div class="section-header"><div class="section-title">Page Performance</div><div class="section-line"></div></div>', unsafe_allow_html=True)

    pages = {
        '/home': (12400, 42, 2.1, 3.8),
        '/pricing': (8200, 58, 1.4, 2.2),
        '/features': (6100, 35, 3.2, 4.1),
        '/demo': (4800, 22, 4.8, 6.2),
        '/blog': (9300, 71, 1.1, 1.8),
        '/contact': (3200, 31, 2.9, 3.4),
    }

    page_df = pd.DataFrame([
        {'Page': p, 'Sessions': v[0], 'Bounce Rate': f"{v[1]}%", 'Avg Pages/Session': v[2], 'Avg Duration (min)': v[3]}
        for p, v in pages.items()
    ])

    st.dataframe(
        page_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Sessions': st.column_config.ProgressColumn('Sessions', min_value=0, max_value=15000, format="%d"),
            'Bounce Rate': st.column_config.TextColumn('Bounce Rate'),
        }
    )

    # Behavior scatter
    st.markdown('<div class="section-header"><div class="section-title">Engagement vs Conversion</div><div class="section-line"></div></div>', unsafe_allow_html=True)

    fig_scatter = go.Figure()
    for seg in segments:
        seg_df = df_web[df_web['segment'] == seg]
        fig_scatter.add_trace(go.Scatter(
            x=seg_df['pages_viewed'],
            y=seg_df['time_on_site'],
            mode='markers',
            name=seg,
            marker=dict(
                size=6,
                opacity=0.6,
                color='#43e97b' if seg_df['converted'].mean() > 0.15 else '#6c63ff',
            ),
        ))
    fig_scatter.update_layout(
        title="Pages Viewed vs Time on Site by Segment",
        xaxis_title="Pages Viewed",
        yaxis_title="Time on Site (min)",
        **PLOTLY_THEME
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — AI RECOMMENDATIONS & CAMPAIGNS
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header"><div class="section-title">AI-Powered Recommendations</div><div class="section-line"></div><div class="section-tag">ANTHROPIC CLAUDE</div></div>', unsafe_allow_html=True)

    if not api_key:
        st.markdown("""
        <div style="background:rgba(108,99,255,0.08); border:1px solid rgba(108,99,255,0.2); border-radius:12px; padding:2rem; text-align:center;">
            <div style="font-size:1.5rem; margin-bottom:0.5rem;">◈</div>
            <div style="font-family:'DM Serif Display',serif; font-size:1.1rem; color:#e8e8f0; margin-bottom:0.4rem;">Enter your API Key to activate AI analysis</div>
            <div style="font-size:0.83rem; color:#6b6b80;">Add your Anthropic API key in the sidebar to generate personalized recommendations and campaigns.</div>
        </div>
        """, unsafe_allow_html=True)
    elif run_analysis:
        # Build context summary for the AI
        context = {
            "total_interactions": total_interactions,
            "avg_sentiment": round(float(avg_sentiment), 3),
            "positive_pct": round(float(positive_pct), 1),
            "negative_pct": round(float((df_interactions['sentiment'] == 'Negative').mean() * 100), 1),
            "conversion_rate": round(float(conversion_rate), 2),
            "csat": round(float(csat), 2),
            "nps": round(float(nps), 1),
            "channels": channels,
            "segments": segments,
            "top_dropoff": "Price concerns (28%), UX friction (22%), Competitor (18%)",
            "top_traffic": "Organic Search (38%), Paid (24%), Social (18%)",
            "time_range": date_range,
            "focus": rec_focus,
            "budget_tier": campaign_budget,
        }

        with st.spinner("Claude is analyzing your customer data..."):
            recs = generate_recommendations(api_key, context)

        st.markdown("### Recommendations")
        for rec in recs:
            priority_class = rec.get('priority','medium').lower()
            st.markdown(f"""
            <div class="rec-card {priority_class}">
                <div class="rec-priority {priority_class}">{rec.get('priority','MEDIUM').upper()} PRIORITY</div>
                <div class="rec-title">{rec.get('title','')}</div>
                <div class="rec-body">{rec.get('description','')}</div>
                <div class="rec-impact">→ Expected impact: {rec.get('impact','')}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-header"><div class="section-title">Campaign Strategy</div><div class="section-line"></div><div class="section-tag">AI-GENERATED</div></div>', unsafe_allow_html=True)

        with st.spinner("Generating targeted campaigns..."):
            campaigns = generate_campaign(api_key, context)

        for camp in campaigns:
            tags_html = ''.join([f'<span class="campaign-tag">{t}</span>' for t in camp.get('tags', [])])
            st.markdown(f"""
            <div class="campaign-card">
                <div class="campaign-title">{camp.get('name','')}</div>
                <div style="margin:0.5rem 0;">{tags_html}</div>
                <div class="campaign-body">{camp.get('description','')}</div>
                <div style="margin-top:1rem; display:flex; gap:2rem; font-size:0.82rem;">
                    <span><span style="color:#6b6b80;">Target:</span> <span style="color:#e8e8f0;">{camp.get('target','')}</span></span>
                    <span><span style="color:#6b6b80;">Channel:</span> <span style="color:#e8e8f0;">{camp.get('channel','')}</span></span>
                    <span><span style="color:#6b6b80;">Est. ROI:</span> <span style="color:#43e97b;">{camp.get('roi','')}</span></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="background:rgba(67,233,123,0.05); border:1px dashed rgba(67,233,123,0.2); border-radius:12px; padding:2rem; text-align:center;">
            <div style="font-size:0.85rem; color:#6b6b80;">Configure your settings in the sidebar, then click <strong style="color:#43e97b;">◈ Run Full Analysis</strong> to generate AI recommendations and campaigns.</div>
        </div>
        """, unsafe_allow_html=True)

    # Always show static example preview
    st.markdown('<div class="section-header"><div class="section-title">Example Output Preview</div><div class="section-line"></div><div class="section-tag">STATIC DEMO</div></div>', unsafe_allow_html=True)

    example_recs = [
        ("High", "Reduce Cart Abandonment on Pricing Page", "The pricing page has the highest bounce rate (58%) and is a primary drop-off point. Implement exit-intent popups with a limited-time offer and simplify the pricing tier comparison.", "↓ Cart abandonment by ~15% · ↑ Conversion rate to 4.2%"),
        ("High", "Launch Proactive Chat for High-Intent Users", "Users spending 3+ minutes on /demo or /pricing show strong intent but don't convert. Trigger a proactive chat offer with a demo scheduling CTA to capture these leads.", "↑ Demo bookings by 30% · ↑ Pipeline $180k/quarter"),
        ("Medium", "Resolve Phone Channel Sentiment Decline", "Phone sentiment dropped 0.12 points over the last 14 days. Root cause analysis points to hold times exceeding 8 minutes. Implement callback scheduling to reduce frustration.", "↑ CSAT by 0.4 points · ↓ Churn risk by 8%"),
        ("Low", "Personalize Email Re-engagement for Trial Segment", "Trial users who haven't logged in within 7 days have a 72% churn probability. A personalized 3-email sequence with feature highlights and a 1-on-1 onboarding call offer can re-activate this cohort.", "↑ Trial-to-paid conversion by 12%"),
    ]

    for priority, title, desc, impact in example_recs:
        p = priority.lower()
        st.markdown(f"""
        <div class="rec-card {p}">
            <div class="rec-priority {p}">{priority.upper()} PRIORITY · EXAMPLE</div>
            <div class="rec-title">{title}</div>
            <div class="rec-body">{desc}</div>
            <div class="rec-impact">→ {impact}</div>
        </div>
        """, unsafe_allow_html=True)