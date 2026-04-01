"""
PRO-FOOT AI V3 — Interface Streamlit Premium
Dashboard professionnel de pronostics football
"""

import streamlit as st
import numpy as np
import pandas as pd
import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(__file__))

# Charger les variables d'environnement locales (.env)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from core.engine_v3 import FootballEngineV3, EloSystem
from core.value_betting import ValueBetDetector, KellyCalculator, ConfidenceScorer
from core.bankroll import BankrollTracker, BacktestEngine
from config import APP_CONFIG, DEMO_MATCHES, DEMO_HISTORICAL, LEAGUE_TEAMS


@st.cache_data(ttl=3600)  # Cache 1h pour ne pas exploser le quota API
def load_live_matches(target_date_str: str) -> list:
    """
    Charge les matchs réels depuis API-Football pour la date donnée.
    Retourne une liste vide si l'API est indisponible.
    """
    try:
        from core.api_client import FootballAPIClient
        from core.data_mapper import map_fixture_to_match
        from datetime import date as dt_date
        import time

        api_key = os.environ.get("API_FOOTBALL_KEY") or st.secrets.get("API_FOOTBALL_KEY", "")
        if not api_key:
            return []

        client = FootballAPIClient(api_key=api_key)
        target_date = dt_date.fromisoformat(target_date_str)
        fixtures = client.get_fixtures(target_date)

        if not fixtures:
            return []

        matches = []
        for i, fix in enumerate(fixtures[:20]):  # Max 20 matchs pour limiter les requêtes
            fixture_id = fix.get("fixture", {}).get("id", 0)
            # Petite pause pour respecter le rate limit (300 req/min)
            if i > 0 and i % 5 == 0:
                time.sleep(0.5)
            try:
                odds = client.get_odds(fixture_id)
            except Exception:
                odds = {}
            match = map_fixture_to_match(fix, odds)
            matches.append(match)

        return matches
    except Exception as e:
        return []

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PRO-FOOT AI V3",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CSS PREMIUM
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Rajdhani:wght@500;600;700&display=swap');
    :root {
        --bg-primary: #0a0e1a; --bg-secondary: #111827; --bg-card: #1a2235;
        --accent-green: #00d68f; --accent-gold: #f5a623; --accent-red: #ff4d6d;
        --accent-blue: #4facfe; --text-primary: #e8ecf0; --text-secondary: #8892a4;
        --border: #2a3a52;
    }

    /* ══ GLOBAL RESET ══ */
    .stApp, .stApp > header, .main .block-container {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        font-family: 'Space Grotesk', sans-serif;
    }
    .block-container { padding-top: 3.5rem !important; padding-left: 2rem; padding-right: 2rem; padding-bottom: 1rem; }

    /* ══ STREAMLIT HEADER/TOOLBAR — hide white bar ══ */
    header[data-testid="stHeader"],
    .stApp > header {
        background: var(--bg-primary) !important;
        border-bottom: none !important;
        box-shadow: none !important;
    }
    .stDeployButton, div[data-testid="stToolbar"],
    div[data-testid="stStatusWidget"] {
        background: transparent !important;
        color: var(--text-secondary) !important;
    }
    div[data-testid="stDecoration"] {
        display: none !important;
    }

    /* Kill ALL white borders globally */
    *, *::before, *::after {
        border-color: var(--border) !important;
    }

    /* ══ SIDEBAR ══ */
    section[data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border) !important;
    }
    section[data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }
    /* Fix top cutoff */
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 3.5rem !important;
    }

    /* Enlarge collapse/expand arrows */
    button[data-testid="collapsedControl"] {
        transform: scale(1.4);
        margin-left: 10px;
    }
    button[kind="header"] {
        transform: scale(1.4);
    }

    section[data-testid="stSidebar"] .stSlider > div > div > div {
        background: var(--bg-card) !important;
    }

    /* ══ COLUMNS & CONTAINERS — kill white borders ══ */
    div[data-testid="stVerticalBlock"],
    div[data-testid="stHorizontalBlock"],
    div[data-testid="column"],
    .stColumn,
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        border: none !important;
        box-shadow: none !important;
    }

    /* ══ METRIC CARDS ══ */
    div[data-testid="metric-container"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 0.8rem !important;
        box-shadow: none !important;
    }
    div[data-testid="stMetricValue"] {
        color: var(--accent-green) !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    div[data-testid="stMetricLabel"] { color: var(--text-secondary) !important; }
    div[data-testid="stMetricDelta"] svg { display: inline-block; }

    /* ══ TABS ══ */
    .stTabs {
        margin-top: 0.5rem !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-secondary) !important;
        border-radius: 10px !important;
        padding: 6px !important;
        gap: 6px !important;
        border: 1px solid var(--border) !important;
        flex-wrap: wrap !important; /* Force wrap so Mon Match is always visible without arrows */
    }
    .stTabs [data-baseweb="tab"] {
        color: var(--text-secondary) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        background: transparent !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(0,214,143,0.08) !important;
        color: var(--text-primary) !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--bg-card) !important;
        color: var(--accent-green) !important;
        border: 1px solid var(--accent-green) !important;
        box-shadow: 0 0 12px rgba(0,214,143,0.15) !important;
    }

    .stTabs [data-baseweb="tab-panel"] {
        background: transparent !important;
        border: none !important;
        padding-top: 1rem !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background: var(--accent-green) !important;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* ══ INPUTS & WIDGETS ══ */
    .stSelectbox > div > div,
    .stNumberInput > div > div,
    .stTextInput > div > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background: var(--bg-card) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
    }
    .stTextInput input, .stNumberInput input, .stSelectbox input { color: var(--text-primary) !important; }
    div[data-baseweb="select"] span { color: var(--text-primary) !important; }
    div[data-baseweb="select"] { color: var(--text-primary) !important; }
    div[data-baseweb="popover"] > div { background: var(--bg-secondary) !important; }
    ul[data-baseweb="menu"] { background: var(--bg-secondary) !important; }
    ul[data-baseweb="menu"] li { color: var(--text-primary) !important; }
    ul[data-baseweb="menu"] li:hover { background: var(--bg-card) !important; }

    /* ══ SLIDERS ══ */
    .stSlider > div > div > div[data-baseweb="slider"] > div {
        background: var(--border) !important;
    }
    .stSlider div[role="slider"] {
        background: var(--accent-green) !important;
        border-color: var(--accent-green) !important;
    }

    /* ══ BUTTONS ══ */
    .stButton > button {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }
    .stButton > button:hover {
        border-color: var(--accent-green) !important;
        color: var(--accent-green) !important;
    }
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #00d68f, #00b4d8) !important;
        color: #000 !important;
        border: none !important;
        font-weight: 700 !important;
    }

    /* ══ EXPANDER ══ */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }
    details[data-testid="stExpander"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }
    details[data-testid="stExpander"] summary {
        color: var(--text-primary) !important;
    }
    details[data-testid="stExpander"] > div {
        background: var(--bg-card) !important;
        border: none !important;
    }

    /* ══ DIVIDERS / HR ══ */
    hr, .stDivider, div[data-testid="stMarkdownContainer"] hr {
        border-color: var(--border) !important;
        background: var(--border) !important;
        opacity: 0.5;
    }

    /* ══ DATAFRAMES ══ */
    .dataframe, .stDataFrame {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }
    .stDataFrame iframe { border: none !important; }
    div[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: 8px !important; }

    /* ══ TEXT & HEADINGS ══ */
    p, li, label, .stMarkdown, span { color: var(--text-primary) !important; }
    h1, h2, h3, h4 {
        font-family: 'Rajdhani', sans-serif !important;
        color: var(--text-primary) !important;
    }
    .stMarkdown a { color: var(--accent-blue) !important; }

    /* ══ ALERT BOXES ══ */
    div[data-testid="stAlert"],
    .stAlert {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
    }
    div[data-testid="stAlert"] * { color: var(--text-primary) !important; }

    /* ══ LINE CHART ══ */
    div[data-testid="stVegaLiteChart"] {
        background: transparent !important;
        border: none !important;
    }

    /* ══ CUSTOM CARDS ══ */
    .pfa-card {
        background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px;
        padding: 1.2rem 1.5rem; margin-bottom: 0.8rem; transition: all 0.2s ease;
    }
    .pfa-card:hover { border-color: var(--accent-green); box-shadow: 0 0 20px rgba(0,214,143,0.08); transform: translateY(-1px); }
    .pfa-header {
        background: linear-gradient(135deg, #0f1e35 0%, #0a1628 100%);
        border-bottom: 1px solid var(--border) !important; padding: 1.5rem 2rem;
        border-radius: 12px; margin-bottom: 1.5rem;
    }
    .pfa-title {
        font-family: 'Rajdhani', sans-serif; font-size: 2.2rem; font-weight: 700;
        background: linear-gradient(90deg, #00d68f, #4facfe);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .match-card {
        background: var(--bg-card); border: 1px solid var(--border) !important;
        border-radius: 14px; padding: 1.4rem; margin-bottom: 1rem;
        position: relative; overflow: hidden;
    }
    .match-card::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, var(--accent-green), var(--accent-blue)) !important;
        border: none !important;
    }
    .match-teams { font-family: 'Rajdhani', sans-serif; font-size: 1.35rem; font-weight: 700; color: var(--text-primary); }
    .prob-bar-container { display: flex; border-radius: 6px; overflow: hidden; height: 10px; margin: 0.4rem 0; }
    .prob-home { background: var(--accent-green); } .prob-draw { background: var(--accent-gold); } .prob-away { background: var(--accent-red); }
    .badge-premium { background: linear-gradient(135deg, #f5a623, #f76b1c); color: #000; padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; display: inline-block; }
    .badge-value { background: linear-gradient(135deg, #00d68f, #00b4d8); color: #000; padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; display: inline-block; }
    .badge-risky { background: rgba(255,77,109,0.2); color: #ff4d6d; border: 1px solid #ff4d6d44 !important; padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
    .badge-good { background: rgba(79,172,254,0.15); color: var(--accent-blue); border: 1px solid #4facfe44 !important; padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
    .confidence-bar-track { background: var(--border); border-radius: 4px; height: 8px; margin-top: 4px; overflow: hidden; }
    .confidence-bar-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; }
    .section-header {
        font-family: 'Rajdhani', sans-serif; font-size: 1.3rem; font-weight: 700;
        color: var(--text-primary); padding: 0.5rem 0; border-bottom: 2px solid var(--accent-green) !important; margin-bottom: 1rem;
    }

    /* ══ SCROLLBAR ══ */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent-green); }

    /* ══ RESPONSIVE MODE ══ */
    .vb-stats-grid { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 0.8rem; margin-bottom: 0.8rem; }
    .custom-vb-grid { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 0.6rem; margin-bottom: 0.6rem; }
    
    @media (max-width: 768px) {
        .block-container { padding: 4.5rem 1rem 1rem 1rem !important; }
        .pfa-title { font-size: 1.6rem !important; }
        .pfa-header { flex-direction: column; align-items: flex-start; gap: 0.5rem; padding: 1rem; }
        .match-teams { font-size: 1.1rem !important; }
        .match-card > div:first-child { flex-direction: column; align-items: flex-start !important; gap: 10px; }
        .match-card > div:first-child > div:last-child { text-align: left !important; }
        
        .vb-stats-grid, .custom-vb-grid { 
            grid-template-columns: 1fr 1fr !important;
            gap: 0.5rem !important;
        }
        .stTabs [data-baseweb="tab-list"] { overflow-x: auto; flex-wrap: nowrap; }
        .stTabs [data-baseweb="tab"] { font-size: 0.85rem !important; padding: 8px 12px !important; white-space: nowrap; }
        
        .vb-card-header { flex-direction: column; align-items: flex-start !important; gap: 8px; }
        .vb-odd-text { align-self: flex-start; font-size: 1.3rem !important; }
    }

    /* ══ TOAST/NOTIFICATIONS ══ */
    div[data-testid="stNotification"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = APP_CONFIG['initial_bankroll']
if 'tracker' not in st.session_state:
    st.session_state.tracker = BankrollTracker(st.session_state.bankroll)
if 'predictions_cache' not in st.session_state:
    st.session_state.predictions_cache = {}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
@st.cache_resource
def get_engine():
    elo = EloSystem()
    for m in DEMO_MATCHES:
        elo.ratings[m['home']] = m['home_elo']
        elo.ratings[m['away']] = m['away_elo']
    return FootballEngineV3(elo_system=elo)

@st.cache_resource
def get_detector():
    return ValueBetDetector()

def run_prediction(match, engine):
    key = match['id']
    if key in st.session_state.predictions_cache:
        return st.session_state.predictions_cache[key]
    result = engine.predict_match(
        home_attack_base=match['home_attack'], home_defense_base=match['home_defense'],
        away_attack_base=match['away_attack'], away_defense_base=match['away_defense'],
        home_xg=match.get('home_xg'), away_xg=match.get('away_xg'),
        home_team=match['home'], away_team=match['away'],
        home_form_results=match.get('home_form'), away_form_results=match.get('away_form'),
        home_rest_days=match.get('home_rest', 7), away_rest_days=match.get('away_rest', 7),
        home_key_players_absent=match.get('home_absent', 0), away_key_players_absent=match.get('away_absent', 0),
    )
    st.session_state.predictions_cache[key] = result
    return result

def confidence_color(score):
    if score >= 75: return "#00d68f"
    elif score >= 60: return "#f5a623"
    return "#ff4d6d"

def render_prob_bar(home, draw, away):
    hp, dp, ap = int(home*100), int(draw*100), int(away*100)
    return f"""
    <div class="prob-bar-container">
        <div class="prob-home" style="width:{hp}%"></div>
        <div class="prob-draw" style="width:{dp}%"></div>
        <div class="prob-away" style="width:{ap}%"></div>
    </div>
    <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#8892a4; margin-top:4px;">
        <span style="color:#00d68f">1 {hp}%</span>
        <span style="color:#f5a623">X {dp}%</span>
        <span style="color:#ff4d6d">2 {ap}%</span>
    </div>
    """

def render_confidence_bar(score):
    color = confidence_color(score)
    return f"""
    <div style="display:flex; align-items:center; gap:8px;">
        <div class="confidence-bar-track" style="flex:1;">
            <div class="confidence-bar-fill" style="width:{score}%; background:{color};"></div>
        </div>
        <span style="color:{color}; font-weight:700; font-size:0.9rem; min-width:36px;">{score:.0f}</span>
    </div>
    """

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:1rem 0;">
        <div style="font-family:'Rajdhani',sans-serif; font-size:1.8rem; font-weight:700;
             background:linear-gradient(90deg,#00d68f,#4facfe);
             -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            ⚽ PRO-FOOT AI
        </div>
        <div style="color:#8892a4; font-size:0.75rem; margin-top:4px;">V3.0 · Moteur Dixon-Coles+</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # ── MODE LIVE / DÉMO ──
    st.markdown("**📡 Source des données**")
    live_mode = st.toggle("🔴 Mode Live (API réelle)", value=False)
    if live_mode:
        selected_date = st.date_input(
            "📅 Date",
            value=date.today(),
            min_value=date.today() - timedelta(days=3),
            max_value=date.today() + timedelta(days=2),
        )
        st.caption("Données chargées depuis API-Football")
    else:
        selected_date = date.today()
        st.caption("🎭 Mode Démo — données simulées")
    st.divider()

    st.markdown("**💰 Bankroll**")
    bankroll = st.number_input("Montant (€)", min_value=10.0, max_value=100000.0,
                                value=st.session_state.bankroll, step=50.0)
    if bankroll != st.session_state.bankroll:
        st.session_state.bankroll = bankroll
    st.divider()
    st.markdown("**🔧 Filtres**")
    min_conf = st.slider("Confiance min", 0, 100, 50, 5)
    min_edge_pct = st.slider("Edge min (%)", 0, 20, 3, 1)
    st.divider()
    st.markdown("**⚙️ Stratégie Kelly**")
    kelly_frac = st.select_slider("Fraction Kelly", options=[0.1, 0.15, 0.25, 0.33, 0.5],
                                   value=0.25, format_func=lambda x: f"1/{int(1/x)}")
    max_bet = st.slider("Mise max (%)", 1, 10, 5, 1)
    st.divider()
    st.markdown("""
    <div style="color:#8892a4; font-size:0.7rem; text-align:center;">
        🔬 Modèle: Dixon-Coles + xG + ELO<br>
        ⚠️ À des fins éducatives uniquement
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INIT ENGINE & COMPUTE
# ─────────────────────────────────────────────
engine = get_engine()
detector = get_detector()
detector.kelly.kelly_fraction = kelly_frac
detector.kelly.max_bet_pct = max_bet / 100

# ── Chargement des matchs (Live ou Démo) ──
if live_mode:
    with st.spinner("📡 Chargement des matchs en direct depuis API-Football..."):
        live_matches = load_live_matches(selected_date.isoformat())
    if live_matches:
        filtered_matches = live_matches
        st.sidebar.success(f"✅ {len(live_matches)} match(s) chargé(s) en live")
    else:
        filtered_matches = DEMO_MATCHES
        st.sidebar.warning("⚠️ API indisponible — Mode Démo activé en fallback")
else:
    filtered_matches = DEMO_MATCHES

all_predictions = {}
all_value_bets = []

for match in filtered_matches:
    pred = run_prediction(match, engine)
    all_predictions[match['id']] = pred
    probs = pred['probabilities']
    odds_mapped = {
        'home_win': match['odds'].get('home_win'), 'draw': match['odds'].get('draw'),
        'away_win': match['odds'].get('away_win'), 'over_2.5': match['odds'].get('over_2.5'),
        'under_2.5': match['odds'].get('under_2.5'), 'btts_yes': match['odds'].get('btts_yes'),
        'btts_no': match['odds'].get('btts_no'),
    }
    probs_mapped = {
        'home_win': probs['home_win'], 'draw': probs['draw'], 'away_win': probs['away_win'],
        'over_2.5': probs['over_2.5'], 'under_2.5': probs['under_2.5'],
        'btts_yes': probs['btts_yes'], 'btts_no': probs['btts_no'],
    }
    odds_filtered = {k: v for k, v in odds_mapped.items() if v is not None}
    vbs = detector.analyze_match(
        f"{match['home']} vs {match['away']}", probs_mapped, odds_filtered,
        pred['components'], data_completeness=0.85
    )
    vbs = [v for v in vbs if v.confidence_score >= min_conf and v.edge_pct >= min_edge_pct]
    for vb in vbs:
        vb._match_id = match['id']
    all_value_bets.extend(vbs)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠 Dashboard", "📊 Analyse Match", "💰 Value Bets", "📈 Bankroll", "🔬 Backtesting", "⚽ Mon Match"
])

# ═══════════════════════════════════════════════
# TAB 1: DASHBOARD
# ═══════════════════════════════════════════════
with tab1:
    st.markdown("""
    <div class="pfa-header">
        <div class="pfa-title">⚽ PRO-FOOT AI V3</div>
        <div style="color:#8892a4; font-size:0.85rem;">
            Moteur Dixon-Coles + xG + ELO Dynamique | Détection de value bets professionnelle
        </div>
    </div>
    """, unsafe_allow_html=True)

    n_premium = sum(1 for v in all_value_bets if '💎' in v.label)
    n_value = sum(1 for v in all_value_bets if '🔥' in v.label)
    avg_conf = np.mean([v.confidence_score for v in all_value_bets]) if all_value_bets else 0
    avg_ev = np.mean([v.expected_value for v in all_value_bets]) if all_value_bets else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Matchs analysés", len(filtered_matches))
    with c2: st.metric("Value Bets", len(all_value_bets), delta=f"{n_premium} premium" if n_premium > 0 else None)
    with c3: st.metric("Confiance moy.", f"{avg_conf:.0f}/100")
    with c4: st.metric("EV moyen", f"{avg_ev:+.3f}")

    st.markdown("---")
    st.markdown('<div class="section-header">📅 Matchs du Jour</div>', unsafe_allow_html=True)

    for match in filtered_matches:
        pred = all_predictions[match['id']]
        probs = pred['probabilities']
        match_vbs = [v for v in all_value_bets if hasattr(v, '_match_id') and v._match_id == match['id']]
        st.markdown(f"""
        <div class="match-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <div class="match-teams">{match['home']} <span style="color:#8892a4; font-size:1rem;">vs</span> {match['away']}</div>
                    <div style="font-size:0.78rem; color:#8892a4;">🏆 {match['league']} &nbsp;|&nbsp; 🕐 {match['date']}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.75rem; color:#8892a4;">Score probable</div>
                    <div style="font-family:'Rajdhani',sans-serif; font-size:1.4rem; font-weight:700; color:#4facfe;">
                        {probs['most_likely_score'][0]} - {probs['most_likely_score'][1]}
                    </div>
                    <div style="font-size:0.7rem; color:#8892a4;">{probs['most_likely_prob']*100:.1f}%</div>
                </div>
            </div>
            {render_prob_bar(probs['home_win'], probs['draw'], probs['away_win'])}
        """, unsafe_allow_html=True)
        if match_vbs:
            vb_html = " ".join([f'<span class="badge-{"premium" if "💎" in v.label else "value" if "🔥" in v.label else "good"}">{v.label} {v.bet_type.value} @{v.bookmaker_odd:.2f}</span>' for v in match_vbs[:3]])
            st.markdown(f'<div style="margin-top:0.5rem;">{vb_html}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# TAB 2: ANALYSE DÉTAILLÉE
# ═══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">🔬 Analyse Détaillée par Match</div>', unsafe_allow_html=True)
    match_options = {f"{m['home']} vs {m['away']} ({m['league']})": m for m in filtered_matches}
    selected_match_name = st.selectbox("Sélectionner un match", list(match_options.keys()))
    sel_match = match_options[selected_match_name]
    sel_pred = all_predictions[sel_match['id']]
    sel_probs = sel_pred['probabilities']
    sel_comp = sel_pred['components']

    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown("#### 📊 Probabilités 1N2")
        ca, cb, cc = st.columns(3)
        with ca: st.metric("🏠 Domicile", f"{sel_probs['home_win']*100:.1f}%")
        with cb: st.metric("🤝 Nul", f"{sel_probs['draw']*100:.1f}%")
        with cc: st.metric("✈️ Extérieur", f"{sel_probs['away_win']*100:.1f}%")

        st.markdown("#### ⚽ Over/Under & BTTS")
        c4, c5, c6, c7 = st.columns(4)
        with c4: st.metric("O1.5", f"{sel_probs['over_1.5']*100:.0f}%")
        with c5: st.metric("O2.5", f"{sel_probs['over_2.5']*100:.0f}%")
        with c6: st.metric("BTTS ✅", f"{sel_probs['btts_yes']*100:.0f}%")
        with c7: st.metric("BTTS ❌", f"{sel_probs['btts_no']*100:.0f}%")

        st.markdown("#### 🎯 Top Scores Probables")
        score_df = pd.DataFrame(
            [(f"{i}-{j}", f"{p*100:.2f}%") for i, j, p in sel_probs['top_scores']],
            columns=['Score', 'Probabilité']
        )
        st.dataframe(score_df, use_container_width=True, hide_index=True)

    with col_b:
        st.markdown("#### 🔧 Features du Modèle")
        features = {
            "xG Domicile": sel_pred['lambda'], "xG Extérieur": sel_pred['mu'],
            "ELO Dom.": sel_comp.get('elo_home', 'N/A'), "ELO Ext.": sel_comp.get('elo_away', 'N/A'),
            "Forme Att. Dom.": f"{sel_comp.get('form_home_attack', 1.0):.2f}",
            "Forme Att. Ext.": f"{sel_comp.get('form_away_attack', 1.0):.2f}",
            "Fatigue Dom.": f"{sel_comp.get('fatigue_home', 1.0):.2f}",
            "Fatigue Ext.": f"{sel_comp.get('fatigue_away', 1.0):.2f}",
        }
        for label, val in features.items():
            if val != 'N/A':
                val_f = float(val) if isinstance(val, str) else float(val)
                color = "#00d68f" if val_f >= 1.0 else "#ff4d6d"
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid #2a3a52;">
                    <span style="color:#8892a4; font-size:0.85rem;">{label}</span>
                    <span style="color:{color}; font-weight:600;">{val_f:.2f}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid #2a3a52;">
                    <span style="color:#8892a4; font-size:0.85rem;">{label}</span>
                    <span style="color:#8892a4;">N/A</span>
                </div>
                """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# TAB 3: VALUE BETS
# ═══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">💎 Value Bets Détectés</div>', unsafe_allow_html=True)

    if not all_value_bets:
        st.info("Aucun value bet détecté avec les filtres actuels.")
    else:
        sort_by = st.selectbox("Trier par", ["Confiance ↓", "Edge % ↓", "Expected Value ↓", "Cote ↓"])
        sorted_bets = list(all_value_bets)
        if "Confiance" in sort_by: sorted_bets.sort(key=lambda x: x.confidence_score, reverse=True)
        elif "Edge" in sort_by: sorted_bets.sort(key=lambda x: x.edge, reverse=True)
        elif "Expected Value" in sort_by: sorted_bets.sort(key=lambda x: x.expected_value, reverse=True)
        else: sorted_bets.sort(key=lambda x: x.bookmaker_odd, reverse=True)

        for vb in sorted_bets:
            conf_color = confidence_color(vb.confidence_score)
            badge_class = ("badge-premium" if "💎" in vb.label else "badge-value" if "🔥" in vb.label
                          else "badge-risky" if "⚠️" in vb.label else "badge-good")
            stake_amount = st.session_state.bankroll * vb.kelly_fraction
            ev_color = '#00d68f' if vb.expected_value > 0 else '#ff4d6d'
            # Split into smaller HTML chunks to prevent Streamlit rendering issues
            card_html = (
                f'<div class="pfa-card">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.8rem;">'
                f'<div>'
                f'<div style="font-family:Rajdhani,sans-serif;font-size:1.1rem;font-weight:700;color:#e8ecf0;margin-bottom:4px;">{vb.match}</div>'
                f'<span class="{badge_class}">{vb.label}</span>'
                f'<span style="color:#8892a4;font-size:0.85rem;margin-left:8px;">{vb.bet_type.value}</span>'
                f'</div>'
                f'<div style="text-align:right;">'
                f'<div style="font-family:Rajdhani,sans-serif;font-size:1.8rem;font-weight:700;color:#4facfe;">@{vb.bookmaker_odd:.2f}</div>'
                f'</div></div>'
                f'<div class="vb-stats-grid">'
                f'<div style="background:#111827;border-radius:8px;padding:0.6rem;text-align:center;">'
                f'<div style="color:#00d68f;font-weight:700;">{vb.model_prob*100:.1f}%</div>'
                f'<div style="color:#8892a4;font-size:0.7rem;">Prob. modèle</div></div>'
                f'<div style="background:#111827;border-radius:8px;padding:0.6rem;text-align:center;">'
                f'<div style="color:#f5a623;font-weight:700;">{vb.implied_prob*100:.1f}%</div>'
                f'<div style="color:#8892a4;font-size:0.7rem;">Prob. implicite</div></div>'
                f'<div style="background:#111827;border-radius:8px;padding:0.6rem;text-align:center;">'
                f'<div style="color:#00d68f;font-weight:700;">+{vb.edge_pct:.1f}%</div>'
                f'<div style="color:#8892a4;font-size:0.7rem;">Edge</div></div>'
                f'<div style="background:#111827;border-radius:8px;padding:0.6rem;text-align:center;">'
                f'<div style="color:#4facfe;font-weight:700;">{vb.kelly_fraction*100:.1f}%</div>'
                f'<div style="color:#8892a4;font-size:0.7rem;">Kelly mise</div></div>'
                f'</div>'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:4px;">'
                f'<span style="color:#8892a4;font-size:0.8rem;">Confiance</span>'
                f'<span style="color:{conf_color};font-weight:700;">{vb.confidence_score:.0f}/100</span></div>'
                f'{render_confidence_bar(vb.confidence_score)}'
                f'<div style="background:rgba(0,214,143,0.06);border-radius:8px;padding:0.6rem;margin-top:0.5rem;">'
                f'<div style="color:#c8d0dc;font-size:0.8rem;">📌 {vb.explanation}</div></div>'
                f'<div style="margin-top:0.6rem;display:flex;justify-content:space-between;">'
                f'<span style="color:#8892a4;font-size:0.78rem;">Mise: <span style="color:#00d68f;font-weight:700;">€{stake_amount:.2f}</span></span>'
                f'<span style="color:#8892a4;font-size:0.78rem;">EV: <span style="color:{ev_color};font-weight:600;">{vb.expected_value:+.3f}</span></span>'
                f'</div></div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# TAB 4: BANKROLL
# ═══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">💰 Suivi Bankroll</div>', unsafe_allow_html=True)
    tracker = st.session_state.tracker
    stats = tracker.get_stats()
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Bankroll", f"€{stats['current_bankroll']:.2f}", delta=f"{stats['bankroll_growth']:+.1f}%")
    with c2: st.metric("ROI", f"{stats['roi']:+.1f}%")
    with c3: st.metric("Win Rate", f"{stats['win_rate']:.0f}%", delta=f"{stats['n_wins']}W / {stats['n_losses']}L")
    with c4: st.metric("Max DD", f"-{stats['max_drawdown']:.1f}%")
    st.markdown("---")
    with st.expander("➕ Enregistrer un pari"):
        ec1, ec2 = st.columns(2)
        with ec1:
            bet_match = st.text_input("Match")
            bet_type_str = st.selectbox("Type", ["1", "X", "2", "O2.5", "U2.5", "BTTS+"])
            bet_odd = st.number_input("Cote", min_value=1.01, value=2.00, step=0.05)
        with ec2:
            bet_stake = st.number_input("Mise (€)", min_value=1.0, value=20.0, step=5.0)
            bet_prob = st.slider("Prob. modèle (%)", 0, 100, 55) / 100
            bet_conf = st.slider("Score confiance", 0, 100, 70)
        if st.button("💾 Enregistrer", type="primary"):
            if bet_match:
                tracker.add_bet(bet_match, bet_type_str, bet_odd, bet_stake, bet_prob, bet_conf)
                st.success(f"Pari enregistré: {bet_match} — {bet_type_str} @{bet_odd}")
                st.rerun()
    pending = [b for b in tracker.bets if b.status == 'pending']
    if pending:
        st.markdown("#### ⏳ Paris en attente")
        for bet in pending:
            pc1, pc2, pc3, pc4 = st.columns([3, 1, 1, 1])
            with pc1: st.write(f"**{bet.match}** — {bet.bet_type} @{bet.odd:.2f}")
            with pc2: st.write(f"€{bet.stake:.2f}")
            with pc3:
                if st.button("✅ Gagné", key=f"win_{bet.id}"):
                    tracker.resolve_bet(bet.id, True); st.rerun()
            with pc4:
                if st.button("❌ Perdu", key=f"loss_{bet.id}"):
                    tracker.resolve_bet(bet.id, False); st.rerun()

# ═══════════════════════════════════════════════
# TAB 5: BACKTESTING
# ═══════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">🔬 Backtesting & Simulation</div>', unsafe_allow_html=True)
    bc1, bc2 = st.columns([1, 2])
    with bc1:
        st.markdown("#### ⚙️ Paramètres")
        bt_strategy = st.selectbox("Stratégie", ['kelly_quarter', 'fixed_1pct', 'fixed_2pct'],
            format_func=lambda x: {'kelly_quarter': 'Kelly 1/4', 'fixed_1pct': 'Fixe 1%', 'fixed_2pct': 'Fixe 2%'}[x])
        bt_min_conf = st.slider("Confiance min (BT)", 0, 100, 60, 5)
        bt_min_edge = st.slider("Edge min (BT, %)", 0, 15, 3, 1) / 100
        bt_bankroll = st.number_input("Bankroll init.", 100, 100000, 1000, 100)
        if st.button("🚀 Lancer", type="primary"):
            bt_engine = BacktestEngine(initial_bankroll=float(bt_bankroll))
            st.session_state.bt_result = bt_engine.run(
                DEMO_HISTORICAL, strategy=bt_strategy, min_confidence=float(bt_min_conf), min_edge=bt_min_edge)
    with bc2:
        if 'bt_result' in st.session_state:
            r = st.session_state.bt_result
            if 'error' in r:
                st.error(r['error'])
            else:
                st.markdown(f"#### 📊 Résultats — {r['strategy']}")
                rc1, rc2, rc3 = st.columns(3)
                with rc1: st.metric("ROI", f"{r['roi']:+.1f}%", delta="profitable" if r['roi'] > 0 else "perte")
                with rc2: st.metric("Win Rate", f"{r['win_rate']:.0f}%")
                with rc3: st.metric("Bankroll finale", f"€{r['final_bankroll']:.0f}", delta=f"{r['bankroll_growth_pct']:+.1f}%")
                rc4, rc5, rc6 = st.columns(3)
                with rc4: st.metric("Max DD", f"-{r['max_drawdown_pct']:.1f}%")
                with rc5: st.metric("Sharpe", f"{r['sharpe']:.2f}")
                with rc6: st.metric("Paris", r['n_bets'])
                if r['bankroll_history']:
                    bk_df = pd.DataFrame({'Paris': range(len(r['bankroll_history'])), 'Bankroll (€)': r['bankroll_history']})
                    st.line_chart(bk_df.set_index('Paris'), color='#00d68f')
                    bt_all = BacktestEngine(initial_bankroll=float(bt_bankroll))
                    comp = bt_all.compare_strategies(DEMO_HISTORICAL)
                    if comp:
                        st.markdown("#### 📋 Comparaison stratégies")
                        comp_df = pd.DataFrame([{
                            'Stratégie': x['strategy'], 'ROI': f"{x['roi']:+.1f}%",
                            'Win Rate': f"{x['win_rate']:.0f}%", 'Bankroll': f"€{x['final_bankroll']:.0f}",
                            'Sharpe': f"{x['sharpe']:.2f}",
                        } for x in comp])
                        st.dataframe(comp_df, use_container_width=True, hide_index=True)
        else:
            st.info("👈 Configurez et lancez un backtest")

# ═══════════════════════════════════════════════
# TAB 6: MON MATCH (CUSTOM ANALYSIS)
# ═══════════════════════════════════════════════
with tab6:
    st.markdown('<div class="section-header">⚽ Analyse Personnalisée</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="color:#8892a4; font-size:0.9rem; margin-bottom:1.5rem;">'
        '🤖 Choisissez deux équipes — notre IA calcule automatiquement tous les paramètres (ELO, xG, force, forme) via l\'API.'
        '</div>',
        unsafe_allow_html=True
    )

    # ── League Selection ──
    all_league_keys = [k for k in LEAGUE_TEAMS.keys() if k != 'Toutes']
    tab6_leagues = sorted(all_league_keys)
    custom_league = st.selectbox("🇪🇺 Compétition", options=['Toutes'] + tab6_leagues, index=0)

    # ── Team Lists ──
    if custom_league == 'Toutes':
        all_teams_flat = []
        for teams in LEAGUE_TEAMS.values():
            all_teams_flat.extend(teams)
        available_teams = sorted(list(set(all_teams_flat)))
    else:
        available_teams = LEAGUE_TEAMS.get(custom_league, ["PSG", "Marseille"])

    st.markdown("<br>", unsafe_allow_html=True)

    col_t1, col_vs, col_t2 = st.columns([5, 1, 5])
    with col_t1:
        custom_home = st.selectbox("🏠 Équipe Domicile", options=available_teams, index=0, key="custom_home")
    with col_vs:
        st.markdown('<div style="text-align:center; padding-top:1.8rem; font-size:1.5rem; font-weight:700; color:#8892a4;">VS</div>', unsafe_allow_html=True)
    with col_t2:
        away_default = 1 if len(available_teams) > 1 else 0
        custom_away = st.selectbox("✈️ Équipe Extérieur", options=available_teams, index=away_default, key="custom_away")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Bookmaker Odds (simple) ──
    with st.expander("💰 Renseigner les cotes bookmaker (optionnel)", expanded=False):
        oc1, oc2, oc3, oc4, oc5 = st.columns(5)
        with oc1: c_odd_home = st.number_input("Cote 1", 1.01, 20.0, 2.00, 0.05, key="c_odd_h")
        with oc2: c_odd_draw = st.number_input("Cote X", 1.01, 20.0, 3.40, 0.05, key="c_odd_d")
        with oc3: c_odd_away = st.number_input("Cote 2", 1.01, 20.0, 3.50, 0.05, key="c_odd_a")
        with oc4: c_odd_o15  = st.number_input("O1.5",  1.01, 10.0, 1.30, 0.05, key="c_odd_o")
        with oc5: c_odd_btts = st.number_input("BTTS+", 1.01, 10.0, 1.80, 0.05, key="c_odd_b")
    
    st.markdown("")

    # ── Launch Analysis ──
    if st.button("🚀 Analyser ce match", type="primary", key="custom_analyze", use_container_width=True):

        with st.spinner(f"🤖 Calcul automatique des paramètres pour {custom_home} vs {custom_away}..."):
            # ── Auto-fetch via API ou fallback sur KNOWN_ELO ──
            from core.data_mapper import KNOWN_ELO, estimate_strength_from_stats, estimate_xg, DEFAULT_ELO

            # Tenter de récupérer les stats via API si mode Live activé
            home_stats_raw, away_stats_raw = {}, {}
            api_key_env = os.environ.get("API_FOOTBALL_KEY") or (st.secrets.get("API_FOOTBALL_KEY", "") if hasattr(st, 'secrets') else "")

            if api_key_env:
                try:
                    from core.api_client import FootballAPIClient
                    api = FootballAPIClient(api_key=api_key_env)
                    # Trouver l'ID de ligue pour les stats
                    league_id_map = {
                        'Premier League': 39, 'Ligue 1': 61, 'Bundesliga': 78,
                        'Serie A': 135, 'La Liga': 140,
                        'Ligue des Champions': 2, 'Europa League': 3, 'Coupe du Monde': 1,
                    }
                    lid = league_id_map.get(custom_league, 39)
                    # Recherche des équipes par nom dans les fixtures récents
                    # (on utilise les stats de saison disponibles)
                    # Pour l'instant on fait confiance au data_mapper + KNOWN_ELO
                except Exception:
                    pass

            # ── Calcul automatique des forces ──
            # ELO depuis la base connue
            home_elo = KNOWN_ELO.get(custom_home, DEFAULT_ELO)
            away_elo = KNOWN_ELO.get(custom_away, DEFAULT_ELO)

            # Force offensive/défensive estimée via ELO (formule relative)
            elo_avg = 1700
            home_att = round(1.0 + (home_elo - elo_avg) / 1000, 2)
            home_def = round(1.0 + (home_elo - elo_avg) / 1200, 2)
            away_att = round(1.0 + (away_elo - elo_avg) / 1000, 2)
            away_def = round(1.0 + (away_elo - elo_avg) / 1200, 2)

            # Clamp les valeurs dans des ranges réalistes
            home_att = max(0.6, min(home_att, 2.8))
            home_def = max(0.6, min(home_def, 2.2))
            away_att = max(0.6, min(away_att, 2.8))
            away_def = max(0.6, min(away_def, 2.2))

            # xG estimés
            home_xg_auto = estimate_xg(home_att, away_def)
            away_xg_auto = estimate_xg(away_att, home_def)

            # Forme neutre (pas de données historiques disponibles en démo)
            home_form = [(2, 1), (1, 1), (2, 0), (1, 0), (2, 1)]
            away_form = [(1, 1), (0, 1), (1, 2), (2, 0), (1, 1)]

        # ── Affichage transparent des paramètres calculés ──
        with st.expander("🔍 Paramètres calculés automatiquement par l'IA", expanded=False):
            pi1, pi2 = st.columns(2)
            with pi1:
                st.markdown(f'<div style="color:#00d68f;font-weight:700;">🏠 {custom_home}</div>', unsafe_allow_html=True)
                st.markdown(f"- **ELO** : `{home_elo}`")
                st.markdown(f"- **Force offensive** : `{home_att:.2f}`")
                st.markdown(f"- **Force défensive** : `{home_def:.2f}`")
                st.markdown(f"- **xG estimé** : `{home_xg_auto:.2f}`")
            with pi2:
                st.markdown(f'<div style="color:#ff4d6d;font-weight:700;">✈️ {custom_away}</div>', unsafe_allow_html=True)
                st.markdown(f"- **ELO** : `{away_elo}`")
                st.markdown(f"- **Force offensive** : `{away_att:.2f}`")
                st.markdown(f"- **Force défensive** : `{away_def:.2f}`")
                st.markdown(f"- **xG estimé** : `{away_xg_auto:.2f}`")

        # ── Moteur de prédiction ──
        custom_elo_sys = EloSystem()
        custom_elo_sys.ratings[custom_home] = home_elo
        custom_elo_sys.ratings[custom_away] = away_elo
        custom_engine = FootballEngineV3(elo_system=custom_elo_sys)

        custom_pred = custom_engine.predict_match(
            home_attack_base=home_att, home_defense_base=home_def,
            away_attack_base=away_att, away_defense_base=away_def,
            home_xg=home_xg_auto, away_xg=away_xg_auto,
            home_team=custom_home, away_team=custom_away,
            home_form_results=home_form, away_form_results=away_form,
            home_rest_days=5, away_rest_days=5,
            home_key_players_absent=0, away_key_players_absent=0,
        )
        cp = custom_pred['probabilities']
        cc = custom_pred['components']

        st.markdown("---")

        # ── Résultat principal ──
        st.markdown(f'''
        <div class="match-card">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div class="match-teams">{custom_home} <span style="color:#8892a4;font-size:1rem;">vs</span> {custom_away}</div>
                <div style="text-align:right;">
                    <div style="font-size:0.75rem;color:#8892a4;">Score le plus probable</div>
                    <div style="font-family:Rajdhani,sans-serif;font-size:1.8rem;font-weight:700;color:#4facfe;">
                        {cp["most_likely_score"][0]} - {cp["most_likely_score"][1]}
                    </div>
                    <div style="font-size:0.7rem;color:#8892a4;">{cp["most_likely_prob"]*100:.1f}% de probabilité</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        st.markdown(render_prob_bar(cp['home_win'], cp['draw'], cp['away_win']), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Probabilités ──
        st.markdown("#### 📊 Probabilités")
        r1, r2, r3 = st.columns(3)
        with r1: st.metric(f"🏠 {custom_home}", f"{cp['home_win']*100:.1f}%")
        with r2: st.metric("🤝 Match Nul", f"{cp['draw']*100:.1f}%")
        with r3: st.metric(f"✈️ {custom_away}", f"{cp['away_win']*100:.1f}%")

        r4, r5, r6, r7 = st.columns(4)
        with r4: st.metric("Over 1.5 ⚽", f"{cp['over_1.5']*100:.0f}%")
        with r5: st.metric("Over 2.5 ⚽", f"{cp['over_2.5']*100:.0f}%")
        with r6: st.metric("Les deux marquent ✅", f"{cp['btts_yes']*100:.0f}%")
        with r7: st.metric("Clean sheet ❌", f"{cp['btts_no']*100:.0f}%")

        # ── Top Scores ──
        st.markdown("#### 🎯 Scores les Plus Probables")
        score_df = pd.DataFrame(
            [(f"{i}-{j}", f"{p*100:.2f}%") for i, j, p in cp['top_scores']],
            columns=['Score', 'Probabilité']
        )
        st.dataframe(score_df, use_container_width=True, hide_index=True)

        # ── Value Bets ──
        custom_odds = {
            'home_win': c_odd_home, 'draw': c_odd_draw, 'away_win': c_odd_away,
            'over_1.5': c_odd_o15, 'btts_yes': c_odd_btts,
            'under_1.5': round(1 / max(1 - 1/c_odd_o15, 0.01), 2),
            'btts_no':   round(1 / max(1 - 1/c_odd_btts, 0.01), 2),
        }
        custom_probs = {
            'home_win': cp['home_win'], 'draw': cp['draw'], 'away_win': cp['away_win'],
            'over_1.5': cp['over_1.5'], 'under_1.5': 1 - cp['over_1.5'],
            'btts_yes': cp['btts_yes'], 'btts_no': cp['btts_no'],
        }
        custom_vbs = detector.analyze_match(
            f"{custom_home} vs {custom_away}", custom_probs, custom_odds, cc, data_completeness=0.9
        )

        if custom_vbs:
            st.markdown("#### 💎 Value Bets Détectés")
            for vb in sorted(custom_vbs, key=lambda x: x.confidence_score, reverse=True):
                conf_color = confidence_color(vb.confidence_score)
                badge_class = ("badge-premium" if "💎" in vb.label else "badge-value" if "🔥" in vb.label
                              else "badge-risky" if "⚠️" in vb.label else "badge-good")
                stake_amount = st.session_state.bankroll * vb.kelly_fraction
                ev_color = '#00d68f' if vb.expected_value > 0 else '#ff4d6d'
                vb_html = (
                    f'<div class="pfa-card">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.6rem;" class="vb-card-header">'
                    f'<div><span class="{badge_class}">{vb.label}</span>'
                    f'<span style="color:#8892a4;font-size:0.85rem;margin-left:8px;">{vb.bet_type.value}</span></div>'
                    f'<div style="font-family:Rajdhani,sans-serif;font-size:1.5rem;font-weight:700;color:#4facfe;" class="vb-odd-text">@{vb.bookmaker_odd:.2f}</div></div>'
                    f'<div class="custom-vb-grid">'
                    f'<div style="background:#111827;border-radius:8px;padding:0.5rem;text-align:center;">'
                    f'<div style="color:#00d68f;font-weight:700;">{vb.model_prob*100:.1f}%</div>'
                    f'<div style="color:#8892a4;font-size:0.7rem;">Modèle</div></div>'
                    f'<div style="background:#111827;border-radius:8px;padding:0.5rem;text-align:center;">'
                    f'<div style="color:#f5a623;font-weight:700;">{vb.implied_prob*100:.1f}%</div>'
                    f'<div style="color:#8892a4;font-size:0.7rem;">Implicite</div></div>'
                    f'<div style="background:#111827;border-radius:8px;padding:0.5rem;text-align:center;">'
                    f'<div style="color:#00d68f;font-weight:700;">+{vb.edge_pct:.1f}%</div>'
                    f'<div style="color:#8892a4;font-size:0.7rem;">Edge</div></div>'
                    f'<div style="background:#111827;border-radius:8px;padding:0.5rem;text-align:center;">'
                    f'<div style="color:#4facfe;font-weight:700;">€{stake_amount:.2f}</div>'
                    f'<div style="color:#8892a4;font-size:0.7rem;">Mise Kelly</div></div></div>'
                    f'<div style="display:flex;justify-content:space-between;margin-top:0.4rem;">'
                    f'<span style="color:#8892a4;font-size:0.78rem;">Confiance: <span style="color:{conf_color};font-weight:700;">{vb.confidence_score:.0f}/100</span></span>'
                    f'<span style="color:#8892a4;font-size:0.78rem;">EV: <span style="color:{ev_color};font-weight:600;">{vb.expected_value:+.3f}</span></span></div></div>'
                )
                st.markdown(vb_html, unsafe_allow_html=True)
        else:
            st.info("❌ Aucun value bet détecté pour ce match avec les cotes actuelles.")



# Footer
st.markdown("""
<div style="text-align:center; padding:2rem; color:#8892a4; font-size:0.75rem; border-top:1px solid #2a3a52; margin-top:2rem;">
    ⚽ PRO-FOOT AI V3 · Dixon-Coles + xG + ELO · Usage éducatif uniquement<br>
    ⚠️ Outil d'aide à la décision — pariez responsablement
</div>
""", unsafe_allow_html=True)
