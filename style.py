import streamlit as st
from typing import Dict

def get_couleurs(theme_clair: bool) -> Dict[str, str]:
    """Retourne la palette de couleurs dynamiquement selon le thème (Clair ou Sombre)."""
    if theme_clair:
        return dict(
            bg="#f8fafc",          # Slate 50 (fond principal)
            card="#ffffff",        # White (cartes)
            card2="#f1f5f9",       # Slate 100 (cartes secondaires)
            txt="#0f172a",         # Slate 900 (texte principal)
            brd="#e2e8f0",         # Slate 200 (bordures)
            grid="#cbd5e1",        # Slate 300 (grilles de graphiques)
            acc="#3b82f6",         # Blue 500 (accent)
            acc_hover="#2563eb",   # Blue 600 (accent hover)
            acc_alpha="rgba(59, 130, 246, 0.15)",
            danger_alpha="rgba(239, 68, 68, 0.15)",
            glass_bg="rgba(255, 255, 255, 0.7)",
            glass_brd="rgba(255, 255, 255, 0.4)",
            shadow="rgba(0, 0, 0, 0.05)",
            success="#10b981",     # Emerald 500
            warning="#f59e0b",     # Amber 500
            danger="#ef4444",      # Red 500
            chart_bg="rgba(255,255,255,0)",
        )
    return dict(
        bg="#0B0F19",          # Fond sombre bleuté
        card="#111827",        # Gray 900
        card2="#1f2937",       # Gray 800
        txt="#f3f4f6",         # Gray 100
        brd="#374151",         # Gray 700
        grid="#4b5563",        # Gray 600
        acc="#3b82f6",         # Blue 500
        acc_hover="#60a5fa",   # Blue 400
        acc_alpha="rgba(59, 130, 246, 0.15)",
        danger_alpha="rgba(239, 68, 68, 0.15)",
        glass_bg="rgba(17, 24, 39, 0.6)",
        glass_brd="rgba(255, 255, 255, 0.08)",
        shadow="rgba(0, 0, 0, 0.3)",
        success="#10b981",
        warning="#f59e0b",
        danger="#ef4444",
        chart_bg="rgba(0,0,0,0)"
    )

def couleur_prob(p: float) -> str:
    """Retourne un code hex selon la probabilité (vert, orange, rouge)."""
    if p >= 0.55: return "#10b981" # succés
    if p >= 0.40: return "#f59e0b" # warning
    return "#ef4444"               # danger


def injecter_css(c: Dict[str, str]) -> None:
    """Injecte la feuille de styles CSS dans l'application Streamlit."""
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

    /* === GLOBAL DYNAMICS === */
    .stApp {{
        background-color: {c['bg']};
        color: {c['txt']};
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
    }}
    .stApp, .stMarkdown, p, h1, h2, h3, h4, span, label, li {{
        color: {c['txt']} !important;
    }}
    h1, h2, h3 {{
        font-family: 'Outfit', sans-serif !important;
    }}

    /* === SCROLLBAR === */
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: {c['brd']}; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {c['grid']}; }}

    /* === SIDEBAR === */
    [data-testid="stSidebar"] {{
        background-color: {c['card']} !important;
        border-right: 1px solid {c['brd']} !important;
        min-width: 280px !important;
    }}
    /* Hide the default generic Streamlit text navigation */
    [data-testid="stSidebarNav"] {{ display: none; }}

    /* === HEADER ALERTS === */
    header[data-testid="stHeader"] {{
        background: transparent !important;
        border: none !important;
    }}

    /* === STREAMLIT TABS === */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: transparent;
        border-bottom: 2px solid {c['brd']};
        gap: 20px;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: {c['txt']};
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 10px 20px;
        border-radius: 8px 8px 0 0;
        transition: all 0.2s;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: transparent !important;
        color: {c['acc']} !important;
        border-bottom: 3px solid {c['acc']} !important;
        border-bottom-color: {c['acc']} !important;
    }}

    /* === METRICS BUTTONS === */
    .stButton button {{
        background-color: {c['acc']} !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px {c['shadow']} !important;
    }}
    .stButton button:hover {{
        background-color: {c['acc_hover']} !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px {c['shadow']} !important;
    }}

    /* Specific logic for sidebar button mapping (Force full-width) */
    section[data-testid="stSidebar"] .stButton button {{
        height: 3rem !important;
        width: 100% !important;
    }}

    /* === SELECTBOX / INPUTS === */
    div[data-baseweb="select"] > div {{
        background-color: {c['card']} !important;
        color: {c['txt']} !important;
        border: 1px solid {c['brd']} !important;
        border-radius: 10px !important;
        transition: border-color 0.2s ease;
    }}
    div[data-baseweb="select"] > div:hover {{ border-color: {c['acc']} !important; }}
    
    div[data-baseweb="popover"] ul {{ background-color: {c['card']} !important; border: 1px solid {c['brd']}; border-radius: 10px; }}
    div[data-baseweb="popover"] li {{ color: {c['txt']} !important; padding: 10px 16px; transition: background 0.2s; }}
    div[data-baseweb="popover"] li:hover {{ background-color: {c['card2']} !important; color: {c['acc']} !important; }}

    div[data-baseweb="input"] > div {{
        background-color: {c['card']} !important;
        border-radius: 10px !important;
        border: 1px solid {c['brd']} !important;
    }}

    /* === TITLES SECTION === */
    .section-title {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: {c['txt']};
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 32px 0 16px 0;
    }}
    .section-title::before {{
        content: '';
        display: inline-block;
        width: 6px;
        height: 24px;
        background: {c['acc']};
        border-radius: 4px;
    }}

    /* === MATCH VS HEADER === */
    .match-header {{
        background: linear-gradient(135deg, {c['glass_bg']} 0%, {c['card2']} 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid {c['glass_brd']};
        border-radius: 24px;
        padding: 32px;
        margin-bottom: 24px;
        display: flex;
        flex-wrap: wrap;       /* Adds Mobile Responsive wrapping */
        align-items: center;
        justify-content: space-evenly;
        gap: 20px;
        box-shadow: 0 8px 32px {c['shadow']};
    }}
    .team-block {{ text-align: center; flex: 1; min-width: 150px; }}
    .team-logo {{ width: 80px; height: 80px; object-fit: contain; margin-bottom: 12px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1)); }}
    .team-name {{ font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 700; color: {c['txt']}; margin: 0; }}
    .vs-block {{ font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; color: {c['brd']}; padding: 0 20px; }}
    .prob-big {{ font-family: 'Outfit', sans-serif; font-size: 2.8rem; font-weight: 800; line-height: 1.1; margin-top: 8px; }}
    .prob-label {{ font-size: 0.8rem; opacity: 0.6; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 4px; font-weight: 500; font-family: 'Inter', sans-serif; }}

    /* === STAT DATA GRID === */
    .stat-grid {{ 
        display: grid; 
        grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); 
        gap: 16px; 
        margin: 16px 0; 
    }}
    .stat-card {{ 
        background: {c['glass_bg']}; 
        border: 1px solid {c['glass_brd']}; 
        border-radius: 16px; 
        padding: 16px; 
        text-align: center; 
        transition: transform 0.2s;
        box-shadow: 0 4px 12px {c['shadow']};
    }}
    .stat-card:hover {{ transform: translateY(-3px); }}
    .stat-value {{ font-family: 'Outfit', sans-serif; font-size: 1.8rem; font-weight: 700; color: {c['txt']}; display: block; line-height: 1.2; }}
    .stat-label {{ font-size: 0.75rem; opacity: 0.6; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; font-family: 'Inter', sans-serif; }}

    /* === VERDICT CARDS === */
    .verdict-card {{ 
        background: linear-gradient(180deg, {c['card']} 0%, {c['card2']} 100%);
        border: 1px solid {c['glass_brd']}; 
        border-radius: 20px; 
        padding: 24px; 
        text-align: center; 
        height: 100%; 
        box-shadow: 0 4px 20px {c['shadow']};
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}
    .verdict-title {{ font-family: 'Outfit', sans-serif; font-size: 0.95rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; color: {c['txt']}; opacity: 0.7; margin-bottom: 12px; width: 100%; }}
    .verdict-main {{ font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; color: {c['txt']}; margin: 8px 0; }}
    .verdict-prob {{ font-size: 0.95rem; opacity: 0.7; font-weight: 500; }}

    /* === MICRO BADGES === */
    .badge-green {{ background:{c['success']}22; color:{c['success']}; border:1px solid {c['success']}44; border-radius:12px; padding:6px 14px; font-size:0.85rem; font-weight:600; display:inline-block; margin-top:12px; font-family: 'Outfit', sans-serif; }}
    .badge-red   {{ background:{c['danger']}22; color:{c['danger']}; border:1px solid {c['danger']}44; border-radius:12px; padding:6px 14px; font-size:0.85rem; font-weight:600; display:inline-block; margin-top:12px; font-family: 'Outfit', sans-serif; }}
    .badge-blue  {{ background:{c['acc']}22; color:{c['acc']}; border:1px solid {c['acc']}44; border-radius:12px; padding:6px 14px; font-size:0.85rem; font-weight:600; display:inline-block; margin-top:12px; font-family: 'Outfit', sans-serif; }}

    /* === WIN / DRAW / LOSE FORME BADGES === */
    .forme-container {{ display:flex; gap:6px; justify-content:center; margin-top:12px; }}
    .forme-w {{ background:linear-gradient(135deg, {c['success']}, #059669); color:white; border-radius:8px; padding:4px 10px; font-size:0.8rem; font-weight:700; box-shadow: 0 2px 4px rgba(16,185,129,0.3); }}
    .forme-d {{ background:linear-gradient(135deg, {c['warning']}, #d97706); color:white; border-radius:8px; padding:4px 10px; font-size:0.8rem; font-weight:700; box-shadow: 0 2px 4px rgba(245,158,11,0.3); }}
    .forme-l {{ background:linear-gradient(135deg, {c['danger']}, #dc2626); color:white; border-radius:8px; padding:4px 10px; font-size:0.8rem; font-weight:700; box-shadow: 0 2px 4px rgba(239,68,68,0.3); }}

    /* === BANKROLL AND ALERTS === */
    .kelly-box     {{ background: linear-gradient(135deg, {c['success']}11, {c['success']}22); border: 1px solid {c['success']}55; border-radius: 16px; padding: 16px; margin-top: 16px; font-size: 0.95rem; font-weight: 500; box-shadow: 0 2px 10px rgba(16,185,129,0.1); width: 100%; }}
    .kelly-box-neg {{ background: {c['card']}; border: 1px dashed {c['brd']}; border-radius: 16px; padding: 16px; margin-top: 16px; opacity: 0.6; font-size: 0.9rem; font-weight: 400; width: 100%; }}

    /* VALUE INJECTORS */
    .diff-pos {{ color: {c['success']} !important; }}
    .diff-neg {{ color: {c['danger']} !important; }}
    </style>
    """, unsafe_allow_html=True)
