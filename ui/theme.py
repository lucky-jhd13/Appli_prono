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
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Inter:wght@300;400;500;600&display=swap');

/* ── RESET STREAMLIT ───────────────────────── */
header[data-testid="stHeader"] {{ display: none !important; }}
[data-testid="stSidebar"] {{ display: none !important; }}
.stApp {{ margin-top: 0 !important; }}
div.block-container {{
    padding-top: 0 !important;
    padding-bottom: 2rem !important;
    max-width: 1400px !important;
}}
footer {{ display: none !important; }}

/* ── MAIN THEME ─────────────────────────────── */
.stApp {{ background-color: {c['bg']}; color: {c['txt']}; font-family: 'Inter', sans-serif; }}
.stApp, .stMarkdown, p, h1, h2, h3, h4, span, label, li {{ color: {c['txt']} !important; }}

/* ── HEADER HERO ────────────────────────────── */
.pronofoot-header {{
    background: linear-gradient(135deg, {c['card']} 0%, {c['card2']} 60%, {c['card']} 100%);
    border-bottom: 1px solid {c['brd']};
    padding: 0;
    position: relative;
    overflow: hidden;
    margin-bottom: 24px;
}}
.pronofoot-header::before {{
    content: '';
    position: absolute;
    top: -50%;
    left: -10%;
    width: 50%;
    height: 200%;
    background: radial-gradient(ellipse, {c['acc']}18 0%, transparent 70%);
    pointer-events: none;
}}
.pronofoot-header::after {{
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 40%;
    height: 200%;
    background: radial-gradient(ellipse, #8b5cf618 0%, transparent 70%);
    pointer-events: none;
}}
.header-inner {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 32px;
    position: relative;
    z-index: 2;
    gap: 24px;
}}
.header-brand {{
    display: flex;
    align-items: center;
    gap: 14px;
    flex-shrink: 0;
}}
.header-logo {{
    width: 52px;
    height: 52px;
    border-radius: 14px;
    object-fit: cover;
    box-shadow: 0 4px 20px {c['acc']}44;
    border: 2px solid {c['acc']}55;
}}
.header-title {{
    font-family: 'Rajdhani', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, {c['acc']} 0%, #8b5cf6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 2px;
    text-transform: uppercase;
    line-height: 1;
}}
.header-subtitle {{
    font-size: 0.7rem;
    opacity: 0.5;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 2px;
    color: {c['txt']} !important;
}}

/* ── LEAGUE PILLS ───────────────────────────── */
.league-selector {{
    display: flex;
    align-items: center;
    gap: 8px;
    flex: 1;
    justify-content: center;
    flex-wrap: wrap;
}}
.league-pill {{
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 14px;
    border-radius: 50px;
    border: 1.5px solid {c['brd']};
    background: {c['card']};
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    text-decoration: none;
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    color: {c['txt']};
    white-space: nowrap;
}}
.league-pill:hover {{
    border-color: {c['acc']}66;
    background: {c['card2']};
    transform: translateY(-2px);
    box-shadow: 0 4px 12px {c['acc']}22;
    color: {c['txt']};
}}
.league-pill.active {{
    background: linear-gradient(135deg, {c['acc']}22, #8b5cf622);
    border-color: {c['acc']};
    color: {c['acc']};
    box-shadow: 0 4px 20px {c['acc']}33;
}}
.league-flag {{
    font-size: 1.3rem;
    line-height: 1;
}}
.league-name {{
    font-weight: 600;
}}

/* ── WIDGETS ─────────────────────────────────── */
div[data-baseweb="select"] > div {{
    background-color: {c['card2']} !important;
    color: {c['txt']} !important;
    border: 1.5px solid {c['brd']} !important;
    border-radius: 12px !important;
}}
div[data-baseweb="select"]:hover > div {{
    border-color: {c['acc']} !important;
}}
div[data-baseweb="popover"] ul {{
    background-color: {c['card']} !important;
    border: 1px solid {c['brd']};
    border-radius: 12px;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.2);
}}
div[data-baseweb="popover"] li {{ color: {c['txt']} !important; padding: 8px 16px !important; }}
div[data-baseweb="popover"] li[aria-selected="true"] {{
    background-color: {c['acc']}22 !important;
    color: {c['acc']} !important;
}}

/* ── TABS ────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background-color: {c['card2']} !important;
    border-radius: 16px !important;
    padding: 6px !important;
    gap: 8px !important;
    border: 1px solid {c['brd']} !important;
    margin-bottom: 2rem !important;
}}
.stTabs [data-baseweb="tab"] {{
    background-color: transparent !important;
    border: none !important;
    color: {c['txt']} !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 10px 20px !important;
    border-radius: 12px !important;
    transition: all 0.3s ease !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
    background-color: {c['acc']}15 !important;
    color: {c['acc']} !important;
}}
.stTabs [aria-selected="true"] {{
    background-color: {c['acc']} !important;
    color: white !important;
    box-shadow: 0 4px 15px {c['acc']}44 !important;
}}
[data-baseweb="tab-highlight"] {{ display: none !important; }}

/* ── MATCH HEADER ────────────────────────────── */
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

/* ── STAT CARDS ──────────────────────────────── */
.stat-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 16px 0; }}
.stat-card {{ background: {c['card']}; border: 1px solid {c['brd']}; border-radius: 14px; padding: 16px; text-align: center; }}
.stat-value {{ font-family: 'Rajdhani', sans-serif; font-size: 1.6rem; font-weight: 700; color: {c['acc']}; display: block; }}
.stat-label {{ font-size: 0.72rem; opacity: 0.55; text-transform: uppercase; letter-spacing: 0.8px; }}

/* ── VERDICT CARDS ───────────────────────────── */
.verdict-card {{
    background: {c['card']}; border: 1px solid {c['brd']}; border-radius: 16px;
    padding: 22px 20px; text-align: center;
    min-height: 170px; display: flex; flex-direction: column; justify-content: center;
}}
.verdict-title {{ font-family: 'Rajdhani', sans-serif; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.6; margin-bottom: 10px; }}
.verdict-main {{ font-family: 'Rajdhani', sans-serif; font-size: 1.8rem; font-weight: 700; color: {c['txt']}; }}
.verdict-prob {{ font-size: 0.9rem; opacity: 0.7; margin-top: 4px; }}

/* ── BADGES ──────────────────────────────────── */
.badge-green {{ background:#16a34a22; color:#4ade80; border:1px solid #16a34a44; border-radius:8px; padding:4px 12px; font-size:0.8rem; font-weight:600; display:inline-block; margin-top:8px; }}
.badge-red   {{ background:#dc262622; color:#f87171; border:1px solid #dc262644; border-radius:8px; padding:4px 12px; font-size:0.8rem; font-weight:600; display:inline-block; margin-top:8px; }}
.badge-blue  {{ background:#3b82f622; color:#60a5fa; border:1px solid #3b82f644; border-radius:8px; padding:4px 12px; font-size:0.8rem; font-weight:600; display:inline-block; margin-top:8px; }}

/* ── FORME ───────────────────────────────────── */
.forme-container {{ display:flex; gap:5px; justify-content:center; margin-top:8px; }}
.forme-w {{ background:#16a34a; color:white; border-radius:6px; padding:3px 8px; font-size:0.78rem; font-weight:700; }}
.forme-d {{ background:#ca8a04; color:white; border-radius:6px; padding:3px 8px; font-size:0.78rem; font-weight:700; }}
.forme-l {{ background:#dc2626; color:white; border-radius:6px; padding:3px 8px; font-size:0.78rem; font-weight:700; }}

/* ── KELLY ───────────────────────────────────── */
.kelly-box     {{ background: linear-gradient(135deg, #16a34a22, #16a34a11); border: 1px solid #16a34a55; border-radius: 12px; padding: 12px 16px; margin-top: 12px; font-size: 0.88rem; }}
.kelly-box-neg {{ background: {c['card']}; border: 1px solid {c['brd']}; border-radius: 12px; padding: 12px 16px; margin-top: 12px; opacity: 0.5; font-size: 0.88rem; }}

/* ── COLUMNS ALIGNMENT ───────────────────────── */
[data-testid="stHorizontalBlock"] {{ align-items: flex-start !important; flex-wrap: nowrap !important; }}
[data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {{ min-width: 0 !important; overflow: hidden; }}

/* ── SECTION TITLES ──────────────────────────── */
.section-title {{
    font-family: 'Rajdhani', sans-serif; font-size: 1.15rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 2px; color: {c['acc']};
    border-left: 3px solid {c['acc']}; padding-left: 12px; margin: 24px 0 14px 0;
}}
.heatmap-note {{ font-size: 0.75rem; opacity: 0.5; text-align: center; margin-top: 6px; }}

/* ── OPPORTUNITY CARDS ───────────────────────── */
.opp-card {{
    background: {c['card']}; border: 1px solid {c['brd']}; border-radius: 16px;
    padding: 18px 20px; margin-bottom: 12px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}
.opp-card:hover {{
    border-color: {c['acc']}66;
    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.1);
    transform: translateY(-2px);
}}
.opp-header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }}
.opp-teams {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
.opp-logo {{ width: 28px; height: 28px; object-fit: contain; }}
.opp-team-name {{ font-family: 'Rajdhani', sans-serif; font-size: 1.05rem; font-weight: 700; color: {c['txt']}; }}
.opp-vs {{ font-family: 'Rajdhani', sans-serif; font-size: 0.85rem; font-weight: 600; color: {c['acc']}; opacity: 0.7; padding: 0 4px; }}
.opp-confiance {{
    font-family: 'Rajdhani', sans-serif; font-size: 1.4rem; font-weight: 800;
    border: 2px solid; border-radius: 12px; padding: 4px 14px;
    min-width: 60px; text-align: center;
}}
.opp-body {{ display: flex; align-items: center; margin-bottom: 6px; }}
.opp-footer {{ opacity: 0.75; }}

/* ── BANKROLL ─────────────────────────────────── */
.bankroll-box {{
    background: linear-gradient(135deg, {c['card']} 0%, {c['card2']} 100%);
    border: 1px solid {c['brd']}; border-radius: 16px;
    padding: 18px 20px; text-align: center; margin-bottom: 16px;
}}
.bankroll-value {{ font-family: 'Rajdhani', sans-serif; font-size: 2rem; font-weight: 800; color: {c['acc']}; }}

/* ── PERFORMANCE DASHBOARD ───────────────────── */
.perf-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 16px 0; }}
.perf-stat {{ background: {c['card']}; border: 1px solid {c['brd']}; border-radius: 14px; padding: 18px 14px; text-align: center; }}
.perf-stat-value {{ font-family: 'Rajdhani', sans-serif; font-size: 2rem; font-weight: 800; display: block; }}
.perf-stat-label {{ font-size: 0.72rem; opacity: 0.55; text-transform: uppercase; letter-spacing: 0.8px; }}

/* ── THEME TOGGLE STYLE ──────────────────────── */
.theme-control {{
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
}}
.stToggle > label {{ color: {c['txt']} !important; font-size: 0.8rem !important; }}

/* ── STREAMLIT BUTTONS (LEAGUE SELECTOR) ─────── */
/* Forcer toutes les colonnes de boutons à la même taille */
[data-testid="stHorizontalBlock"]:has([data-testid="stButton"]) > [data-testid="stVerticalBlockBorderWrapper"] {{
    flex: 1 1 0 !important;
    min-width: 0 !important;
}}
/* Secondary buttons : texte lisible sur tous les thèmes */
[data-testid="stBaseButton-secondary"] {{
    background-color: {c['card']} !important;
    color: {c['txt']} !important;
    border: 1.5px solid {c['brd']} !important;
    border-radius: 50px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    transition: all 0.25s ease !important;
    height: 44px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}
[data-testid="stBaseButton-secondary"]:hover {{
    border-color: {c['acc']}88 !important;
    background-color: {c['card2']} !important;
    color: {c['acc']} !important;
}}
/* Primary button (active league) */
[data-testid="stBaseButton-primary"] {{
    background: linear-gradient(135deg, {c['acc']}, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    box-shadow: 0 4px 15px {c['acc']}44 !important;
    height: 44px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}

/* ── TOGGLE STYLE ────────────────────────────── */
[data-testid="stToggle"] label span {{
    color: {c['txt']} !important;
    font-family: 'Inter', sans-serif !important;
}}

/* ── TABS SCROLLABLE ────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    flex-wrap: nowrap !important;
}}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {{ display: none; }}
.stTabs [data-baseweb="tab"] {{ white-space: nowrap !important; flex-shrink: 0 !important; }}

/* ════════════════════════════════════════════════
   RESPONSIVE — TABLETTE (≤ 1024px)
   ════════════════════════════════════════════════ */
@media (max-width: 1024px) {{
    div.block-container {{
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
    }}

    /* Header : empile brand verticalement */
    .header-inner {{
        flex-direction: column;
        align-items: flex-start;
        padding: 14px 20px;
        gap: 14px;
    }}
    .header-brand {{ width: 100%; }}
    .header-title {{ font-size: 1.6rem; }}

    /* Match header : réduit padding */
    .match-header {{
        padding: 20px 16px;
        gap: 12px;
    }}
    .team-logo {{ width: 54px; height: 54px; }}
    .team-name {{ font-size: 1.1rem; }}
    .prob-big  {{ font-size: 1.9rem; }}
    .vs-block  {{ font-size: 1.5rem; padding: 0 10px; }}

    /* Stat grid : 2 colonnes */
    .stat-grid {{ grid-template-columns: repeat(2, 1fr); }}

    /* Perf grid : 2 colonnes */
    .perf-grid {{ grid-template-columns: repeat(2, 1fr); }}

    /* Tabs : texte réduit */
    .stTabs [data-baseweb="tab"] {{
        font-size: 0.82rem !important;
        padding: 8px 12px !important;
    }}

    /* Verdict cards : min-height réduit */
    .verdict-card {{ min-height: 140px; padding: 16px 14px; }}
    .verdict-main {{ font-size: 1.5rem; }}
}}

/* ════════════════════════════════════════════════
   RESPONSIVE — MOBILE / IPHONE (≤ 640px)
   ════════════════════════════════════════════════ */
@media (max-width: 640px) {{
    /* Padding global minimal */
    div.block-container {{
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
    }}

    /* Header compact mobile */
    .header-inner {{
        padding: 10px 12px;
        gap: 8px;
    }}
    .header-logo {{ width: 36px; height: 36px; border-radius: 10px; }}
    .header-title {{ font-size: 1.2rem; letter-spacing: 1px; }}
    .header-subtitle {{ font-size: 0.55rem; }}

    /* League buttons : grille 3x2 compacte */
    [data-testid="stHorizontalBlock"]:has([data-testid="stButton"]) {{
        display: grid !important;
        grid-template-columns: repeat(3, 1fr) !important;
        gap: 6px !important;
    }}
    [data-testid="stBaseButton-secondary"],
    [data-testid="stBaseButton-primary"] {{
        font-size: 0.7rem !important;
        padding: 8px 4px !important;
        border-radius: 12px !important;
        min-height: auto !important;
    }}

    /* Match header : colonne sur mobile */
    .match-header {{
        flex-direction: column;
        padding: 16px 12px;
        gap: 14px;
        text-align: center;
    }}
    .team-block {{ width: 100%; }}
    .team-logo  {{ width: 50px; height: 50px; }}
    .team-name  {{ font-size: 1.05rem; }}
    .prob-big   {{ font-size: 1.8rem; }}
    .vs-block   {{
        font-size: 1.1rem;
        padding: 2px 0;
        opacity: 0.5;
        width: 100%;
        text-align: center;
    }}

    /* Stat grid : 2 colonnes serrées */
    .stat-grid {{
        grid-template-columns: repeat(2, 1fr);
        gap: 6px;
    }}
    .stat-card {{ padding: 10px 6px; }}
    .stat-value {{ font-size: 1.2rem; }}
    .stat-label {{ font-size: 0.62rem; }}

    /* Perf grid : 2 colonnes */
    .perf-grid {{
        grid-template-columns: repeat(2, 1fr);
        gap: 6px;
    }}
    .perf-stat {{ padding: 12px 8px; }}
    .perf-stat-value {{ font-size: 1.5rem; }}

    /* Verdict cards : empilées */
    .verdict-card {{
        min-height: 110px;
        padding: 12px 10px;
    }}
    .verdict-main  {{ font-size: 1.3rem; }}
    .verdict-title {{ font-size: 0.7rem; letter-spacing: 1px; }}
    .verdict-prob  {{ font-size: 0.75rem; }}

    /* Tabs : scroll horizontal, fond transparent pour éviter artefacts noirs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 3px !important;
        padding: 3px !important;
        border-radius: 12px !important;
        background-color: {c['card']} !important;
        border: 1px solid {c['brd']} !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-size: 0.68rem !important;
        padding: 6px 6px !important;
        border-radius: 8px !important;
        background-color: transparent !important;
        color: {c['txt']} !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {c['acc']} !important;
        color: white !important;
    }}

    /* Colonnes Streamlit : forcer 1 colonne sur mobile (sauf league row) */
    [data-testid="stHorizontalBlock"]:not(:has([data-testid="stButton"])) {{
        flex-wrap: wrap !important;
    }}
    [data-testid="stHorizontalBlock"]:not(:has([data-testid="stButton"])) > [data-testid="stVerticalBlockBorderWrapper"] {{
        min-width: 100% !important;
        width: 100% !important;
    }}

    /* Opp cards */
    .opp-header {{ flex-direction: column; align-items: flex-start; gap: 6px; }}
    .opp-confiance {{ font-size: 1rem; padding: 3px 8px; }}
    .opp-team-name {{ font-size: 0.9rem; }}
    .opp-card {{ padding: 14px 12px; }}

    /* Bankroll box */
    .bankroll-value {{ font-size: 1.4rem; }}

    /* Kelly */
    .kelly-box, .kelly-box-neg {{ font-size: 0.78rem; padding: 8px 10px; }}

    /* Section title */
    .section-title {{ font-size: 0.9rem; letter-spacing: 1px; margin: 18px 0 10px 0; }}

    /* Badges */
    .badge-green, .badge-red, .badge-blue {{
        font-size: 0.68rem;
        padding: 2px 6px;
    }}

    /* Forme badges */
    .forme-w, .forme-d, .forme-l {{
        padding: 2px 5px;
        font-size: 0.68rem;
    }}

    /* Inputs */
    div[data-baseweb="select"] > div {{ border-radius: 10px !important; font-size: 0.85rem !important; }}
}}

/* ════════════════════════════════════════════════
   RESPONSIVE — TRÈS PETIT (≤ 390px — iPhone SE)
   ════════════════════════════════════════════════ */
@media (max-width: 390px) {{
    .header-title {{ font-size: 1.05rem; }}
    .header-logo {{ width: 32px; height: 32px; }}
    .prob-big     {{ font-size: 1.5rem; }}
    .team-name    {{ font-size: 0.9rem; }}
    .stat-value   {{ font-size: 1.1rem; }}
    .perf-stat-value {{ font-size: 1.3rem; }}

    [data-testid="stBaseButton-secondary"],
    [data-testid="stBaseButton-primary"] {{
        font-size: 0.62rem !important;
        padding: 6px 3px !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        font-size: 0.6rem !important;
        padding: 5px 4px !important;
    }}

    [data-testid="stHorizontalBlock"]:has([data-testid="stButton"]) {{
        grid-template-columns: repeat(2, 1fr) !important;
    }}
}}
</style>
""", unsafe_allow_html=True)