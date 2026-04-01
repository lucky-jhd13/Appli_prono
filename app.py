"""
PRO-FOOT AI V3 — Interface Streamlit Premium
Dashboard professionnel de pronostics football
"""

import streamlit as st
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from core.engine_v3 import FootballEngineV3, EloSystem
from core.value_betting import ValueBetDetector, KellyCalculator, ConfidenceScorer
from core.bankroll import BankrollTracker, BacktestEngine
from config import APP_CONFIG, DEMO_MATCHES, DEMO_HISTORICAL

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
# CSS PREMIUM (Dark Mode avec accents verts)
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Rajdhani:wght@500;600;700&display=swap');

    :root {
        --bg-primary: #0a0e1a;
        --bg-secondary: #111827;
        --bg-card: #1a2235;
        --bg-card2: #1e2d45;
        --accent-green: #00d68f;
        --accent-gold: #f5a623;
        --accent-red: #ff4d6d;
        --accent-blue: #4facfe;
        --text-primary: #e8ecf0;
        --text-secondary: #8892a4;
        --border: #2a3a52;
    }

    .stApp {
        background: var(--bg-primary) !important;
        font-family: 'Space Grotesk', sans-serif;
    }

    section[data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border);
    }

    .block-container { padding: 1rem 2rem; }

    /* ── Cards ── */
    .pfa-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.8rem;
        transition: all 0.2s ease;
    }
    .pfa-card:hover {
        border-color: var(--accent-green);
        box-shadow: 0 0 20px rgba(0,214,143,0.08);
        transform: translateY(-1px);
    }

    /* ── Header ── */
    .pfa-header {
        background: linear-gradient(135deg, #0f1e35 0%, #0a1628 100%);
        border-bottom: 1px solid var(--border);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .pfa-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00d68f, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1px;
    }

    /* ── KPI Metrics ── */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.8rem;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .kpi-value {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.9rem;
        font-weight: 700;
        color: var(--accent-green);
    }
    .kpi-label {
        font-size: 0.75rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ── Match Cards ── */
    .match-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.4rem;
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
    }
    .match-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-green), var(--accent-blue));
    }
    .match-teams {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.35rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.3rem;
    }
    .match-meta {
        font-size: 0.78rem;
        color: var(--text-secondary);
        margin-bottom: 1rem;
    }

    /* ── Probability Bars ── */
    .prob-bar-container {
        display: flex;
        border-radius: 6px;
        overflow: hidden;
        height: 10px;
        margin: 0.4rem 0;
    }
    .prob-home { background: var(--accent-green); }
    .prob-draw { background: var(--accent-gold); }
    .prob-away { background: var(--accent-red); }

    /* ── Value Bet Badges ── */
    .badge-premium {
        background: linear-gradient(135deg, #f5a623, #f76b1c);
        color: #000;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
    }
    .badge-value {
        background: linear-gradient(135deg, #00d68f, #00b4d8);
        color: #000;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
    }
    .badge-risky {
        background: rgba(255,77,109,0.2);
        color: #ff4d6d;
        border: 1px solid #ff4d6d44;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-good {
        background: rgba(79,172,254,0.15);
        color: var(--accent-blue);
        border: 1px solid #4facfe44;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }

    /* ── Confidence Gauge ── */
    .confidence-bar-track {
        background: var(--border);
        border-radius: 4px;
        height: 8px;
        margin-top: 4px;
        overflow: hidden;
    }
    .confidence-bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.5s ease;
    }

    /* ── Section Headers ── */
    .section-header {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--text-primary);
        padding: 0.5rem 0;
        border-bottom: 2px solid var(--accent-green);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* ── General text ── */
    p, li, label, .stMarkdown { color: var(--text-primary) !important; }
    h1, h2, h3 { font-family: 'Rajdhani', sans-serif !important; color: var(--text-primary) !important; }
    .stMetric > div { color: var(--text-primary) !important; }
    .stSelectbox, .stSlider { color: var(--text-primary) !important; }

    /* ── Streamlit overrides ── */
    div[data-testid="metric-container"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 0.8rem !important;
    }
    div[data-testid="stMetricValue"] { color: var(--accent-green) !important; font-family: 'Rajdhani', sans-serif !important; }

    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-secondary);
        border-radius: 8px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        color: var(--text-secondary) !important;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 500;
        border-radius: 6px;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background: var(--bg-card) !important;
        color: var(--accent-green) !important;
    }

    /* Dataframe */
    .dataframe { background: var(--bg-card) !important; color: var(--text-primary) !important; }
    .stDataFrame { border: 1px solid var(--border) !important; border-radius: 8px !important; }

    /* Sidebar elements */
    .stSlider > div > div { background: var(--bg-card) !important; }
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
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

@st.cache_resource
def get_engine():
    elo = EloSystem()
    # Initialiser ELO à partir des données de démo
    for m in DEMO_MATCHES:
        elo.ratings[m['home']] = m['home_elo']
        elo.ratings[m['away']] = m['away_elo']
    return FootballEngineV3(elo_system=elo)


@st.cache_resource
def get_detector():
    return ValueBetDetector()


def run_prediction(match: dict, engine: FootballEngineV3) -> dict:
    key = match['id']
    if key in st.session_state.predictions_cache:
        return st.session_state.predictions_cache[key]

    result = engine.predict_match(
        home_attack_base=match['home_attack'],
        home_defense_base=match['home_defense'],
        away_attack_base=match['away_attack'],
        away_defense_base=match['away_defense'],
        home_xg=match.get('home_xg'),
        away_xg=match.get('away_xg'),
        home_team=match['home'],
        away_team=match['away'],
        home_form_results=match.get('home_form'),
        away_form_results=match.get('away_form'),
        home_rest_days=match.get('home_rest', 7),
        away_rest_days=match.get('away_rest', 7),
        home_key_players_absent=match.get('home_absent', 0),
        away_key_players_absent=match.get('away_absent', 0),
    )
    st.session_state.predictions_cache[key] = result
    return result


def confidence_color(score: float) -> str:
    if score >= 75:
        return "#00d68f"
    elif score >= 60:
        return "#f5a623"
    else:
        return "#ff4d6d"


def render_prob_bar(home: float, draw: float, away: float):
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


def render_confidence_bar(score: float):
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

    # Bankroll
    st.markdown("**💰 Bankroll**")
    bankroll = st.number_input("Montant (€)", min_value=10.0, max_value=100000.0,
                                value=st.session_state.bankroll, step=50.0)
    if bankroll != st.session_state.bankroll:
        st.session_state.bankroll = bankroll

    st.divider()

    # Filtres
    st.markdown("**🔧 Filtres**")
    leagues = ['Toutes'] + list(set(m['league'] for m in DEMO_MATCHES))
    selected_league = st.selectbox("Ligue", leagues)

    min_conf = st.slider("Confiance min", 0, 100, 50, 5)
    min_edge_pct = st.slider("Edge min (%)", 0, 20, 3, 1)

    st.divider()

    # Kelly settings
    st.markdown("**⚙️ Stratégie Kelly**")
    kelly_frac = st.select_slider(
        "Fraction Kelly",
        options=[0.1, 0.15, 0.25, 0.33, 0.5],
        value=0.25,
        format_func=lambda x: f"1/{int(1/x)}"
    )
    max_bet = st.slider("Mise max (%)", 1, 10, 5, 1)

    st.divider()
    st.markdown("""
    <div style="color:#8892a4; font-size:0.7rem; text-align:center;">
        🔬 Modèle: Dixon-Coles + xG + ELO<br>
        ⚠️ À des fins éducatives uniquement
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# INIT ENGINE
# ─────────────────────────────────────────────
engine = get_engine()
detector = get_detector()
detector.kelly.kelly_fraction = kelly_frac
detector.kelly.max_bet_pct = max_bet / 100

# Filtrer les matchs
filtered_matches = DEMO_MATCHES
if selected_league != 'Toutes':
    filtered_matches = [m for m in DEMO_MATCHES if m['league'] == selected_league]

# Calculer toutes les prédictions
all_predictions = {}
all_value_bets = []

for match in filtered_matches:
    pred = run_prediction(match, engine)
    all_predictions[match['id']] = pred

    probs = pred['probabilities']
    odds_mapped = {
        'home_win': match['odds'].get('home_win'),
        'draw': match['odds'].get('draw'),
        'away_win': match['odds'].get('away_win'),
        'over_2.5': match['odds'].get('over_2.5'),
        'under_2.5': match['odds'].get('under_2.5'),
        'btts_yes': match['odds'].get('btts_yes'),
        'btts_no': match['odds'].get('btts_no'),
    }
    # Mapper les probs
    probs_mapped = {
        'home_win': probs['home_win'],
        'draw': probs['draw'],
        'away_win': probs['away_win'],
        'over_2.5': probs['over_2.5'],
        'under_2.5': probs['under_2.5'],
        'btts_yes': probs['btts_yes'],
        'btts_no': probs['btts_no'],
    }
    odds_filtered = {k: v for k, v in odds_mapped.items() if v is not None}

    vbs = detector.analyze_match(
        f"{match['home']} vs {match['away']}",
        probs_mapped, odds_filtered,
        pred['components'],
        data_completeness=0.85
    )

    # Appliquer filtres sidebar
    vbs = [v for v in vbs
           if v.confidence_score >= min_conf
           and v.edge_pct >= min_edge_pct]

    for vb in vbs:
        vb._match_id = match['id']
    all_value_bets.extend(vbs)


# ─────────────────────────────────────────────
# MAIN TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Dashboard", "📊 Analyse Match", "💰 Value Bets",
    "📈 Bankroll", "🔬 Backtesting"
])


# ═══════════════════════════════════════════════
# TAB 1: DASHBOARD
# ═══════════════════════════════════════════════
with tab1:
    # Header
    st.markdown("""
    <div class="pfa-header">
        <div>
            <div class="pfa-title">⚽ PRO-FOOT AI V3</div>
            <div style="color:#8892a4; font-size:0.85rem;">
                Moteur Dixon-Coles + xG + ELO Dynamique | Détection de value bets professionnelle
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    n_premium = sum(1 for v in all_value_bets if '💎' in v.label)
    n_value = sum(1 for v in all_value_bets if '🔥' in v.label)
    avg_conf = np.mean([v.confidence_score for v in all_value_bets]) if all_value_bets else 0
    avg_ev = np.mean([v.expected_value for v in all_value_bets]) if all_value_bets else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Matchs analysés", len(filtered_matches), help="Matchs du jour dans le scope")
    with col2:
        st.metric("Value Bets détectés", len(all_value_bets),
                  delta=f"{n_premium} premium" if n_premium > 0 else None)
    with col3:
        st.metric("Confiance moyenne", f"{avg_conf:.0f}/100")
    with col4:
        st.metric("EV moyen", f"{avg_ev:+.3f}", help="Expected Value par unité misée")

    st.markdown("---")

    # Matchs du jour
    st.markdown('<div class="section-header">📅 Matchs du Jour</div>', unsafe_allow_html=True)

    for match in filtered_matches:
        pred = all_predictions[match['id']]
        probs = pred['probabilities']
        match_vbs = [v for v in all_value_bets if hasattr(v, '_match_id') and v._match_id == match['id']]

        with st.container():
            st.markdown(f"""
            <div class="match-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div class="match-teams">{match['home']} <span style="color:#8892a4; font-size:1rem;">vs</span> {match['away']}</div>
                        <div class="match-meta">🏆 {match['league']} &nbsp;|&nbsp; 🕐 {match['date']}</div>
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
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("🏠 Domicile", f"{sel_probs['home_win']*100:.1f}%",
                      help=f"Cote équivalente: {1/sel_probs['home_win']:.2f}")
        with c2:
            st.metric("🤝 Nul", f"{sel_probs['draw']*100:.1f}%",
                      help=f"Cote équivalente: {1/sel_probs['draw']:.2f}")
        with c3:
            st.metric("✈️ Extérieur", f"{sel_probs['away_win']*100:.1f}%",
                      help=f"Cote équivalente: {1/sel_probs['away_win']:.2f}")

        st.markdown("#### ⚽ Over/Under & BTTS")
        c4, c5, c6, c7 = st.columns(4)
        with c4:
            st.metric("O1.5", f"{sel_probs['over_1.5']*100:.0f}%")
        with c5:
            st.metric("O2.5", f"{sel_probs['over_2.5']*100:.0f}%")
        with c6:
            st.metric("BTTS ✅", f"{sel_probs['btts_yes']*100:.0f}%")
        with c7:
            st.metric("BTTS ❌", f"{sel_probs['btts_no']*100:.0f}%")

        # Heatmap simplifiée
        st.markdown("#### 🎯 Matrice des Scores (Top probabilités)")
        import pandas as pd
        matrix = sel_pred['score_matrix']
        top_scores = sel_probs['top_scores']
        score_df = pd.DataFrame(
            [(f"{i}-{j}", f"{p*100:.2f}%") for i, j, p in top_scores],
            columns=['Score', 'Probabilité']
        )
        st.dataframe(score_df, use_container_width=True, hide_index=True)

    with col_b:
        st.markdown("#### 🔧 Features du Modèle")

        comp_display = {
            "xG Domicile": sel_pred['lambda'],
            "xG Extérieur": sel_pred['mu'],
            "ELO Dom.": sel_comp.get('elo_home', 'N/A'),
            "ELO Ext.": sel_comp.get('elo_away', 'N/A'),
            "Forme Dom.": f"{sel_comp.get('form_home_attack', 1.0):.2f}",
            "Forme Ext.": f"{sel_comp.get('form_away_attack', 1.0):.2f}",
            "Fatigue Dom.": f"{sel_comp.get('fatigue_home', 1.0):.2f}",
            "Fatigue Ext.": f"{sel_comp.get('fatigue_away', 1.0):.2f}",
        }

        for label, val in comp_display.items():
            if val != 'N/A':
                val_f = float(val) if not isinstance(val, str) else float(val)
                color = "#00d68f" if val_f >= 1.0 else "#ff4d6d"
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:4px 0;
                     border-bottom:1px solid #2a3a52;">
                    <span style="color:#8892a4; font-size:0.85rem;">{label}</span>
                    <span style="color:{color}; font-weight:600;">{val_f:.2f}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:4px 0;
                     border-bottom:1px solid #2a3a52;">
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
        st.info("Aucun value bet détecté avec les filtres actuels. Essayez de baisser le seuil de confiance ou d'edge.")
    else:
        # Sort options
        sort_by = st.selectbox("Trier par",
                               ["Confiance ↓", "Edge % ↓", "Expected Value ↓", "Cote ↓"])

        sorted_bets = list(all_value_bets)
        if "Confiance" in sort_by:
            sorted_bets.sort(key=lambda x: x.confidence_score, reverse=True)
        elif "Edge" in sort_by:
            sorted_bets.sort(key=lambda x: x.edge, reverse=True)
        elif "Expected Value" in sort_by:
            sorted_bets.sort(key=lambda x: x.expected_value, reverse=True)
        else:
            sorted_bets.sort(key=lambda x: x.bookmaker_odd, reverse=True)

        for vb in sorted_bets:
            conf_color = confidence_color(vb.confidence_score)
            badge_class = ("badge-premium" if "💎" in vb.label
                          else "badge-value" if "🔥" in vb.label
                          else "badge-risky" if "⚠️" in vb.label
                          else "badge-good")

            st.markdown(f"""
            <div class="pfa-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.8rem;">
                    <div>
                        <div style="font-family:'Rajdhani',sans-serif; font-size:1.1rem; font-weight:700;
                             color:#e8ecf0; margin-bottom:4px;">
                            {vb.match}
                        </div>
                        <span class="{badge_class}">{vb.label}</span>
                        <span style="color:#8892a4; font-size:0.85rem; margin-left:8px;">
                            {vb.bet_type.value}
                        </span>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-family:'Rajdhani',sans-serif; font-size:1.8rem;
                             font-weight:700; color:#4facfe;">@{vb.bookmaker_odd:.2f}</div>
                        <div style="font-size:0.75rem; color:#8892a4;">Cote bookmaker</div>
                    </div>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:0.8rem; margin-bottom:0.8rem;">
                    <div style="background:#111827; border-radius:8px; padding:0.6rem; text-align:center;">
                        <div style="color:#00d68f; font-weight:700; font-size:1rem;">{vb.model_prob*100:.1f}%</div>
                        <div style="color:#8892a4; font-size:0.7rem;">Prob. modèle</div>
                    </div>
                    <div style="background:#111827; border-radius:8px; padding:0.6rem; text-align:center;">
                        <div style="color:#f5a623; font-weight:700; font-size:1rem;">{vb.implied_prob*100:.1f}%</div>
                        <div style="color:#8892a4; font-size:0.7rem;">Prob. implicite</div>
                    </div>
                    <div style="background:#111827; border-radius:8px; padding:0.6rem; text-align:center;">
                        <div style="color:#00d68f; font-weight:700; font-size:1rem;">+{vb.edge_pct:.1f}%</div>
                        <div style="color:#8892a4; font-size:0.7rem;">Edge</div>
                    </div>
                    <div style="background:#111827; border-radius:8px; padding:0.6rem; text-align:center;">
                        <div style="color:#4facfe; font-weight:700; font-size:1rem;">{vb.kelly_fraction*100:.1f}%</div>
                        <div style="color:#8892a4; font-size:0.7rem;">Kelly mise</div>
                    </div>
                </div>
                <div style="margin-bottom:0.5rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                        <span style="color:#8892a4; font-size:0.8rem;">Score de confiance</span>
                        <span style="color:{conf_color}; font-weight:700;">{vb.confidence_score:.0f}/100</span>
                    </div>
                    {render_confidence_bar(vb.confidence_score)}
                </div>
                <div style="background:rgba(0,214,143,0.05); border:1px solid rgba(0,214,143,0.15);
                     border-radius:8px; padding:0.6rem; margin-top:0.5rem;">
                    <div style="color:#8892a4; font-size:0.75rem; margin-bottom:2px;">📌 Explication</div>
                    <div style="color:#c8d0dc; font-size:0.8rem;">{vb.explanation}</div>
                </div>
                <div style="margin-top:0.6rem; display:flex; justify-content:space-between; align-items:center;">
                    <div style="color:#8892a4; font-size:0.78rem;">
                        Mise conseillée:
                        <span style="color:#00d68f; font-weight:700;">
                            €{st.session_state.bankroll * vb.kelly_fraction:.2f}
                        </span>
                        sur bankroll €{st.session_state.bankroll:.0f}
                    </div>
                    <div style="color:#8892a4; font-size:0.78rem;">
                        EV: <span style="color:{'#00d68f' if vb.expected_value > 0 else '#ff4d6d'}; font-weight:600;">
                            {vb.expected_value:+.3f}
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# TAB 4: BANKROLL
# ═══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">💰 Suivi Bankroll</div>', unsafe_allow_html=True)

    tracker = st.session_state.tracker
    stats = tracker.get_stats()

    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Bankroll actuelle", f"€{stats['current_bankroll']:.2f}",
                  delta=f"{stats['bankroll_growth']:+.1f}%")
    with c2:
        st.metric("ROI total", f"{stats['roi']:+.1f}%")
    with c3:
        st.metric("Taux de réussite", f"{stats['win_rate']:.0f}%",
                  delta=f"{stats['n_wins']}W / {stats['n_losses']}L")
    with c4:
        st.metric("Max Drawdown", f"-{stats['max_drawdown']:.1f}%")

    st.markdown("---")

    # Ajouter un pari manuellement
    with st.expander("➕ Enregistrer un pari"):
        col1, col2 = st.columns(2)
        with col1:
            bet_match = st.text_input("Match (ex: PSG vs Marseille)")
            bet_type_str = st.selectbox("Type de pari", ["1", "X", "2", "O2.5", "U2.5", "BTTS+"])
            bet_odd = st.number_input("Cote", min_value=1.01, value=2.00, step=0.05)
        with col2:
            bet_stake = st.number_input("Mise (€)", min_value=1.0, value=20.0, step=5.0)
            bet_prob = st.slider("Prob. modèle (%)", 0, 100, 55) / 100
            bet_conf = st.slider("Score confiance", 0, 100, 70)

        if st.button("💾 Enregistrer le pari", type="primary"):
            if bet_match:
                tracker.add_bet(bet_match, bet_type_str, bet_odd, bet_stake, bet_prob, bet_conf)
                st.success(f"Pari enregistré: {bet_match} — {bet_type_str} @{bet_odd}")
                st.rerun()

    # Liste des paris en attente
    pending = [b for b in tracker.bets if b.status == 'pending']
    if pending:
        st.markdown("#### ⏳ Paris en attente")
        for bet in pending:
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            with c1:
                st.write(f"**{bet.match}** — {bet.bet_type} @{bet.odd:.2f}")
            with c2:
                st.write(f"€{bet.stake:.2f}")
            with c3:
                if st.button("✅ Gagné", key=f"win_{bet.id}"):
                    tracker.resolve_bet(bet.id, True)
                    st.rerun()
            with c4:
                if st.button("❌ Perdu", key=f"loss_{bet.id}"):
                    tracker.resolve_bet(bet.id, False)
                    st.rerun()


# ═══════════════════════════════════════════════
# TAB 5: BACKTESTING
# ═══════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">🔬 Backtesting & Simulation</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("#### ⚙️ Paramètres de simulation")
        bt_strategy = st.selectbox("Stratégie",
            ['kelly_quarter', 'fixed_1pct', 'fixed_2pct'],
            format_func=lambda x: {
                'kelly_quarter': 'Kelly 1/4',
                'fixed_1pct': 'Mise fixe 1%',
                'fixed_2pct': 'Mise fixe 2%',
            }[x])
        bt_min_conf = st.slider("Confiance min (backtest)", 0, 100, 60, 5)
        bt_min_edge = st.slider("Edge min (backtest, %)", 0, 15, 3, 1) / 100
        bt_bankroll = st.number_input("Bankroll initiale", 100, 100000, 1000, 100)

        if st.button("🚀 Lancer le backtest", type="primary"):
            bt_engine = BacktestEngine(initial_bankroll=float(bt_bankroll))
            result = bt_engine.run(
                DEMO_HISTORICAL,
                strategy=bt_strategy,
                min_confidence=float(bt_min_conf),
                min_edge=bt_min_edge
            )
            st.session_state.bt_result = result

    with col2:
        if 'bt_result' in st.session_state:
            r = st.session_state.bt_result
            if 'error' in r:
                st.error(r['error'])
            else:
                st.markdown(f"#### 📊 Résultats — {r['strategy']}")

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("ROI", f"{r['roi']:+.1f}%",
                              delta="profitable" if r['roi'] > 0 else "perte")
                with c2:
                    st.metric("Win Rate", f"{r['win_rate']:.0f}%")
                with c3:
                    st.metric("Bankroll finale", f"€{r['final_bankroll']:.0f}",
                              delta=f"{r['bankroll_growth_pct']:+.1f}%")

                c4, c5, c6 = st.columns(3)
                with c4:
                    st.metric("Max Drawdown", f"-{r['max_drawdown_pct']:.1f}%")
                with c5:
                    st.metric("Sharpe ratio", f"{r['sharpe']:.2f}")
                with c6:
                    st.metric("Paris analysés", r['n_bets'])

                # Courbe bankroll
                if r['bankroll_history']:
                    import pandas as pd
                    bk_df = pd.DataFrame({
                        'Paris': range(len(r['bankroll_history'])),
                        'Bankroll (€)': r['bankroll_history']
                    })
                    st.line_chart(bk_df.set_index('Paris'), color='#00d68f')

                    # Comparer stratégies
                    bt_all = BacktestEngine(initial_bankroll=float(bt_bankroll))
                    comparaison = bt_all.compare_strategies(DEMO_HISTORICAL)
                    if comparaison:
                        st.markdown("#### 📋 Comparaison des stratégies")
                        comp_df = pd.DataFrame([{
                            'Stratégie': r['strategy'],
                            'ROI': f"{r['roi']:+.1f}%",
                            'Win Rate': f"{r['win_rate']:.0f}%",
                            'Bankroll finale': f"€{r['final_bankroll']:.0f}",
                            'Max DD': f"-{r['max_drawdown_pct']:.1f}%",
                            'Sharpe': f"{r['sharpe']:.2f}",
                        } for r in comparaison])
                        st.dataframe(comp_df, use_container_width=True, hide_index=True)
        else:
            st.info("👈 Configurez et lancez un backtest pour voir les résultats")
            st.markdown("""
            <div class="pfa-card">
                <div style="color:#e8ecf0; font-size:0.9rem;">
                    <strong>📚 Guide backtesting</strong><br><br>
                    Le backtesting simule votre stratégie sur <strong>20 paris historiques</strong>
                    avec des résultats réels. Il compare:<br><br>
                    • <strong>Kelly 1/4</strong> — mise dynamique selon l'edge détecté<br>
                    • <strong>Mise fixe 1%</strong> — conservative, drawdown limité<br>
                    • <strong>Mise fixe 2%</strong> — balance risque/rendement<br><br>
                    Filtrez par confiance minimum et edge minimum pour tester
                    l'impact de vos critères de sélection.
                </div>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center; padding:2rem; color:#8892a4; font-size:0.75rem; border-top:1px solid #2a3a52; margin-top:2rem;">
    ⚽ PRO-FOOT AI V3 · Moteur Dixon-Coles + xG + ELO · Usage éducatif uniquement<br>
    ⚠️ Ce système est un outil d'aide à la décision — pariez de manière responsable
</div>
""", unsafe_allow_html=True)
