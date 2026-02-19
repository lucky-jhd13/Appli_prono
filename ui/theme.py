# ─────────────────────────────────────────────
# ui/theme.py — Thème, couleurs & injection CSS
# ─────────────────────────────────────────────

import streamlit as st


def get_couleurs(theme_clair: bool) -> dict:
    if theme_clair:
        return dict(
            bg="#F0F4F8", card="#FFFFFF", card2="#EFF6FF",
            txt="#0F172A", brd="#CBD5E1", grid="#94A3B8", acc="#3b82f6"
        )
    return dict(
        bg="#0A0E17", card="#131920", card2="#0D1B2A",
        txt="#E8EDF5", brd="#1E2936", grid="#2A3545", acc="#3b82f6"
    )


def injecter_css(c: dict):
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Inter:wght@300;400;500&display=swap');

header[data-testid="stHeader"] {{ background: transparent !important; border: none !important; }}
.stApp {{ background-color: {c['bg']}; color: {c['txt']}; font-family: 'Inter', sans-serif; }}
.stApp, .stMarkdown, p, h1, h2, h3, h4, span, label, li {{ color: {c['txt']} !important; }}

div[data-baseweb="select"] > div {{ background-color: {c['card']} !important; color: {c['txt']} !important; border-color: {c['brd']} !important; }}
div[data-baseweb="popover"] ul {{ background-color: {c['card']} !important; }}
div[data-baseweb="popover"] li {{ color: {c['txt']} !important; }}
[data-testid="stSidebar"] {{ background-color: {c['card']} !important; min-width: 260px !important; }}
.stTabs [data-baseweb="tab-list"] {{ background-color: {c['card']}; border-radius: 12px; padding: 4px; }}
.stTabs [data-baseweb="tab"] {{ color: {c['txt']}; border-radius: 8px; }}
.stTabs [aria-selected="true"] {{ background-color: {c['acc']} !important; color: white !important; }}

/* MATCH HEADER */
.match-header {{
    background: linear-gradient(135deg, {c['card']} 0%, {c['card2']} 100%);
    border: 1px solid {c['brd']}; border-radius: 20px;
    padding: 28px 32px; margin-bottom: 20px;
    display: flex; align-items: center; justify-content: space-between; gap: 20px;
}}
.team-block {{ text-align: center; flex: 1; }}
.team-logo {{ width: 70px; height: 70px; object-fit: contain; margin-bottom: 8px; }}
.team-name {{ font-family: 'Rajdhani', sans-serif; font-size: 1.3rem; font-weight: 700; color: {c['txt']}; margin: 0; }}
.vs-block {{ font-family: 'Rajdhani', sans-serif; font-size: 2rem; font-weight: 700; color: {c['acc']}; padding: 0 20px; }}
.prob-big {{ font-family: 'Rajdhani', sans-serif; font-size: 2.4rem; font-weight: 700; line-height: 1; }}
.prob-label {{ font-size: 0.75rem; opacity: 0.6; text-transform: uppercase; letter-spacing: 1px; }}

/* STAT CARDS */
.stat-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 16px 0; }}
.stat-card {{ background: {c['card']}; border: 1px solid {c['brd']}; border-radius: 14px; padding: 16px; text-align: center; }}
.stat-value {{ font-family: 'Rajdhani', sans-serif; font-size: 1.6rem; font-weight: 700; color: {c['acc']}; display: block; }}
.stat-label {{ font-size: 0.72rem; opacity: 0.55; text-transform: uppercase; letter-spacing: 0.8px; }}

/* VERDICT CARDS */
.verdict-card {{ background: {c['card']}; border: 1px solid {c['brd']}; border-radius: 16px; padding: 22px 20px; text-align: center; height: 100%; }}
.verdict-title {{ font-family: 'Rajdhani', sans-serif; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.6; margin-bottom: 10px; }}
.verdict-main {{ font-family: 'Rajdhani', sans-serif; font-size: 1.8rem; font-weight: 700; color: {c['txt']}; }}
.verdict-prob {{ font-size: 0.9rem; opacity: 0.7; margin-top: 4px; }}

/* BADGES */
.badge-green {{ background:#16a34a22; color:#4ade80; border:1px solid #16a34a44; border-radius:8px; padding:4px 12px; font-size:0.8rem; font-weight:600; display:inline-block; margin-top:8px; }}
.badge-red   {{ background:#dc262622; color:#f87171; border:1px solid #dc262644; border-radius:8px; padding:4px 12px; font-size:0.8rem; font-weight:600; display:inline-block; margin-top:8px; }}
.badge-blue  {{ background:#3b82f622; color:#60a5fa; border:1px solid #3b82f644; border-radius:8px; padding:4px 12px; font-size:0.8rem; font-weight:600; display:inline-block; margin-top:8px; }}

/* FORME */
.forme-container {{ display:flex; gap:5px; justify-content:center; margin-top:8px; }}
.forme-w {{ background:#16a34a; color:white; border-radius:6px; padding:3px 8px; font-size:0.78rem; font-weight:700; }}
.forme-d {{ background:#ca8a04; color:white; border-radius:6px; padding:3px 8px; font-size:0.78rem; font-weight:700; }}
.forme-l {{ background:#dc2626; color:white; border-radius:6px; padding:3px 8px; font-size:0.78rem; font-weight:700; }}

/* KELLY */
.kelly-box     {{ background: linear-gradient(135deg, #16a34a22, #16a34a11); border: 1px solid #16a34a55; border-radius: 12px; padding: 12px 16px; margin-top: 12px; }}
.kelly-box-neg {{ background: {c['card']}; border: 1px solid {c['brd']}; border-radius: 12px; padding: 12px 16px; margin-top: 12px; opacity: 0.5; }}

/* SECTION TITLES */
.section-title {{ font-family: 'Rajdhani', sans-serif; font-size: 1.15rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; color: {c['acc']}; border-left: 3px solid {c['acc']}; padding-left: 12px; margin: 24px 0 14px 0; }}

.heatmap-note {{ font-size: 0.75rem; opacity: 0.5; text-align: center; margin-top: 6px; }}
</style>
""", unsafe_allow_html=True)
