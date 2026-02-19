import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import math

# ─────────────────────────────────────────────
# 1. CONFIGURATION
# ─────────────────────────────────────────────
API_KEY = "6845fbe629e041bdb8f0cad7488a9fe2"
CHAMPIONNATS = {
    "🇫🇷 Ligue 1": "FL1", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": "PL", "🇪🇸 La Liga": "PD",
    "🇩🇪 Bundesliga": "BL1", "🇮🇹 Serie A": "SA", "🇳🇱 Eredivisie": "DED"
}

st.set_page_config(page_title="PRO-FOOT AI V12", page_icon="🏆", layout="wide")

# ─────────────────────────────────────────────
# 2. SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ RÉGLAGES")
    theme_clair = st.toggle("☀️ Mode Clair", value=False, key="force_theme_toggle")
    st.divider()
    choix_ligue = st.selectbox("🏆 CHAMPIONNAT", list(CHAMPIONNATS.keys()))
    st.info("Algorithme : Poisson Bivarié · Lambda Normalisé · Kelly")
    st.divider()
    st.markdown("**📖 Légende forme**")
    st.markdown("`W` Victoire · `D` Nul · `L` Défaite")

# ─────────────────────────────────────────────
# 3. THÈME & CSS
# ─────────────────────────────────────────────
if theme_clair:
    bg, card, txt, brd, grid, acc = "#F0F4F8", "#FFFFFF", "#0F172A", "#CBD5E1", "#94A3B8", "#3b82f6"
    card2 = "#EFF6FF"
else:
    bg, card, txt, brd, grid, acc = "#0A0E17", "#131920", "#E8EDF5", "#1E2936", "#2A3545", "#3b82f6"
    card2 = "#0D1B2A"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Inter:wght@300;400;500&display=swap');

header[data-testid="stHeader"] {{ background: transparent !important; border: none !important; }}
.stApp {{ background-color: {bg}; color: {txt}; font-family: 'Inter', sans-serif; }}
.stApp, .stMarkdown, p, h1, h2, h3, h4, span, label, li {{ color: {txt} !important; }}

div[data-baseweb="select"] > div {{ background-color: {card} !important; color: {txt} !important; border-color: {brd} !important; }}
div[data-baseweb="popover"] ul {{ background-color: {card} !important; }}
div[data-baseweb="popover"] li {{ color: {txt} !important; }}
[data-testid="stSidebar"] {{ background-color: {card} !important; min-width: 260px !important; }}
.stTabs [data-baseweb="tab-list"] {{ background-color: {card}; border-radius: 12px; padding: 4px; }}
.stTabs [data-baseweb="tab"] {{ color: {txt}; border-radius: 8px; }}
.stTabs [aria-selected="true"] {{ background-color: {acc} !important; color: white !important; }}

/* ── CARDS ── */
.match-header {{
    background: linear-gradient(135deg, {card} 0%, {card2} 100%);
    border: 1px solid {brd};
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
}}
.team-block {{
    text-align: center;
    flex: 1;
}}
.team-logo {{ width: 70px; height: 70px; object-fit: contain; margin-bottom: 8px; }}
.team-name {{
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: {txt};
    margin: 0;
}}
.vs-block {{
    font-family: 'Rajdhani', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: {acc};
    padding: 0 20px;
}}
.prob-big {{
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    line-height: 1;
}}
.prob-label {{
    font-size: 0.75rem;
    opacity: 0.6;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* ── STAT CARDS ── */
.stat-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin: 16px 0;
}}
.stat-card {{
    background: {card};
    border: 1px solid {brd};
    border-radius: 14px;
    padding: 16px;
    text-align: center;
}}
.stat-value {{
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: {acc};
    display: block;
}}
.stat-label {{
    font-size: 0.72rem;
    opacity: 0.55;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}}

/* ── VERDICT CARDS ── */
.verdict-card {{
    background: {card};
    border: 1px solid {brd};
    border-radius: 16px;
    padding: 22px 20px;
    text-align: center;
    height: 100%;
}}
.verdict-title {{
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    opacity: 0.6;
    margin-bottom: 10px;
}}
.verdict-main {{
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: {txt};
}}
.verdict-prob {{
    font-size: 0.9rem;
    opacity: 0.7;
    margin-top: 4px;
}}
.badge-green {{ background:#16a34a22; color:#4ade80; border:1px solid #16a34a44; border-radius:8px; padding:4px 12px; font-size:0.8rem; font-weight:600; display:inline-block; margin-top:8px; }}
.badge-red {{ background:#dc262622; color:#f87171; border:1px solid #dc262644; border-radius:8px; padding:4px 12px; font-size:0.8rem; font-weight:600; display:inline-block; margin-top:8px; }}
.badge-blue {{ background:#3b82f622; color:#60a5fa; border:1px solid #3b82f644; border-radius:8px; padding:4px 12px; font-size:0.8rem; font-weight:600; display:inline-block; margin-top:8px; }}
.badge-yellow {{ background:#ca8a0422; color:#fbbf24; border:1px solid #ca8a0444; border-radius:8px; padding:4px 12px; font-size:0.8rem; font-weight:600; display:inline-block; margin-top:8px; }}

/* ── FORME BADGES ── */
.forme-container {{ display:flex; gap:5px; justify-content:center; margin-top:8px; }}
.forme-w {{ background:#16a34a; color:white; border-radius:6px; padding:3px 8px; font-size:0.78rem; font-weight:700; }}
.forme-d {{ background:#ca8a04; color:white; border-radius:6px; padding:3px 8px; font-size:0.78rem; font-weight:700; }}
.forme-l {{ background:#dc2626; color:white; border-radius:6px; padding:3px 8px; font-size:0.78rem; font-weight:700; }}

/* ── KELLY INDICATOR ── */
.kelly-box {{
    background: linear-gradient(135deg, #16a34a22, #16a34a11);
    border: 1px solid #16a34a55;
    border-radius: 12px;
    padding: 12px 16px;
    margin-top: 12px;
}}
.kelly-box-neg {{
    background: {card};
    border: 1px solid {brd};
    border-radius: 12px;
    padding: 12px 16px;
    margin-top: 12px;
    opacity: 0.5;
}}

/* ── SECTION TITLES ── */
.section-title {{
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: {acc};
    border-left: 3px solid {acc};
    padding-left: 12px;
    margin: 24px 0 14px 0;
}}

/* ── SCORE HEATMAP BOX ── */
.heatmap-note {{
    font-size: 0.75rem;
    opacity: 0.5;
    text-align: center;
    margin-top: 6px;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 4. MATHÉMATIQUES (MOTEUR POISSON AMÉLIORÉ)
# ─────────────────────────────────────────────
def poisson(lam, k):
    if lam <= 0: return 0
    return (math.pow(lam, k) * math.exp(-lam)) / math.factorial(k)

def matrice_scores(l_h, l_a, n=8):
    """Retourne une matrice n×n de probabilités de scores."""
    mat = [[poisson(l_h, h) * poisson(l_a, a) for a in range(n)] for h in range(n)]
    return mat

def probabilites_depuis_matrice(mat):
    n = len(mat)
    p1 = pn = p2 = pbtts = p_over25 = 0
    for h in range(n):
        for a in range(n):
            p = mat[h][a]
            if h > a: p1 += p
            elif h == a: pn += p
            else: p2 += p
            if h > 0 and a > 0: pbtts += p
            if h + a >= 3: p_over25 += p
    return p1, pn, p2, pbtts, p_over25

def score_le_plus_probable(mat):
    n = len(mat)
    best_p, best_h, best_a = 0, 0, 0
    for h in range(n):
        for a in range(n):
            if mat[h][a] > best_p:
                best_p, best_h, best_a = mat[h][a], h, a
    return best_h, best_a, best_p

def kelly_criterion(prob, cote):
    """Fraction de mise optimale Kelly."""
    if cote <= 1 or prob <= 0: return 0
    b = cote - 1
    f = (b * prob - (1 - prob)) / b
    return max(f, 0)

# ─────────────────────────────────────────────
# 5. API & TRAITEMENT DONNÉES
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def charger_donnees(league_code):
    url = f"https://api.football-data.org/v4/competitions/{league_code}/standings"
    headers = {"X-Auth-Token": API_KEY}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json()['standings'][0]['table']
        return None
    except:
        return None

def extraire_stats(e):
    pj = e.get('playedGames', 1) or 1
    gf = e.get('goalsFor', 0)
    ga = e.get('goalsAgainst', 0)
    pts = e.get('points', 0)
    won = e.get('won', 0)
    draw = e.get('draw', 0)
    lost = e.get('lost', 0)
    form_raw = str(e.get('form', '') or '').replace(',', '').replace(' ', '')[-5:]

    mbp = gf / pj
    mbc = ga / pj
    pts_par_match = pts / pj

    # Forme numérique (points sur 5 derniers matchs)
    pts_forme = sum(3 if c == 'W' else 1 if c == 'D' else 0 for c in form_raw)
    forme_pct = (pts_forme / 15) * 100

    # Scores radar
    att_score  = min(mbp * 45, 100)
    def_score  = max(100 - mbc * 50, 0)
    vic_score  = (won / pj) * 100
    const_score = pts_par_match / 3 * 100

    return {
        "pj": pj, "gf": gf, "ga": ga, "pts": pts,
        "won": won, "draw": draw, "lost": lost,
        "mbp": mbp, "mbc": mbc,
        "pts_par_match": pts_par_match,
        "form": form_raw,
        "pts_forme": pts_forme,
        "forme_pct": forme_pct,
        "radar": [int(att_score), int(def_score), int(vic_score), int(const_score)],
        "diff": gf - ga,
    }

def calculer_lambdas(s1, s2, moy_gf_ligue, moy_ga_ligue,
                     but1, but2, repos1, repos2):
    """
    Modèle de Poisson normalisé par la moyenne du championnat.
    force_att = mbp / moy_gf   |   force_def = mbc / moy_ga
    lambda_h  = force_att_1 × force_def_2 × moy_gf × dom_bonus × ajustements
    """
    fa1 = s1["mbp"] / moy_gf_ligue if moy_gf_ligue > 0 else 1
    fd1 = s1["mbc"] / moy_ga_ligue if moy_ga_ligue > 0 else 1
    fa2 = s2["mbp"] / moy_gf_ligue if moy_gf_ligue > 0 else 1
    fd2 = s2["mbc"] / moy_ga_ligue if moy_ga_ligue > 0 else 1

    # Avantage domicile DYNAMIQUE (basé sur pts_par_match de l'équipe)
    dom_bonus = 1.05 + (s1["pts_par_match"] / 3) * 0.12  # entre 1.05 et 1.17

    # Ajustement forme (±8%)
    forme_mult1 = 0.96 + (s1["forme_pct"] / 100) * 0.08
    forme_mult2 = 0.96 + (s2["forme_pct"] / 100) * 0.08

    # Ajustements terrain
    but_mult1 = 1.0 if but1 else 0.78
    but_mult2 = 1.0 if but2 else 0.78
    rep_mult1 = 1.06 if repos1 >= 5 else (0.88 if repos1 <= 2 else 1.0)
    rep_mult2 = 1.06 if repos2 >= 5 else (0.88 if repos2 <= 2 else 1.0)

    l_h = fa1 * fd2 * moy_gf_ligue * dom_bonus * forme_mult1 * but_mult1 * rep_mult1
    l_a = fa2 * fd1 * moy_gf_ligue * forme_mult2 * but_mult2 * rep_mult2

    return round(max(l_h, 0.1), 3), round(max(l_a, 0.1), 3)

# ─────────────────────────────────────────────
# 6. HELPERS AFFICHAGE
# ─────────────────────────────────────────────
def forme_html(form_str):
    badges = []
    for c in form_str.upper():
        if c == 'W': badges.append('<span class="forme-w">V</span>')
        elif c == 'D': badges.append('<span class="forme-d">N</span>')
        elif c == 'L': badges.append('<span class="forme-l">D</span>')
    return f'<div class="forme-container">{"".join(badges)}</div>'

def couleur_prob(p):
    if p >= 0.55: return "#4ade80"
    if p >= 0.40: return "#fbbf24"
    return "#f87171"

def fig_jauge(prob, label, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(prob * 100, 1),
        number={"suffix": "%", "font": {"size": 28, "color": color}},
        title={"text": label, "font": {"size": 13, "color": txt}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": grid, "tickwidth": 1},
            "bar": {"color": color},
            "bgcolor": card,
            "bordercolor": brd,
            "steps": [
                {"range": [0, 40], "color": f"{card}"},
                {"range": [40, 60], "color": f"{card2}"},
                {"range": [60, 100], "color": f"{card2}"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.75, "value": prob * 100}
        }
    ))
    fig.update_layout(
        height=200, margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color=txt)
    )
    return fig

def fig_heatmap_scores(mat, n1, n2):
    n = len(mat)
    labels_h = [str(i) for i in range(n)]
    labels_a = [str(i) for i in range(n)]
    z = [[round(mat[h][a] * 100, 1) for a in range(n)] for h in range(n)]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=[f"{n2} {a}" for a in range(n)],
        y=[f"{n1} {h}" for h in range(n)],
        colorscale=[[0, card2], [0.5, acc], [1, "#60a5fa"]],
        showscale=True,
        hovertemplate="Score %{y} - %{x}<br>Probabilité : %{z:.1f}%<extra></extra>",
        text=[[f"{v:.1f}%" for v in row] for row in z],
        texttemplate="%{text}",
        textfont={"size": 10, "color": txt},
    ))
    fig.update_layout(
        title=dict(text="🎲 Matrice des scores les plus probables (%)", font=dict(size=14, color=txt)),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=txt),
        margin=dict(l=60, r=20, t=50, b=40),
        xaxis=dict(gridcolor=grid),
        yaxis=dict(gridcolor=grid, autorange="reversed"),
    )
    return fig

def fig_radar(s1, s2, n1, n2):
    cats = ['Attaque', 'Défense', 'Victoires', 'Constance']
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=s1["radar"] + [s1["radar"][0]], theta=cats + [cats[0]],
        fill='toself', name=n1,
        line=dict(color='#3b82f6', width=2),
        fillcolor='rgba(59,130,246,0.15)'
    ))
    fig.add_trace(go.Scatterpolar(
        r=s2["radar"] + [s2["radar"][0]], theta=cats + [cats[0]],
        fill='toself', name=n2,
        line=dict(color='#ef4444', width=2),
        fillcolor='rgba(239,68,68,0.15)'
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=grid, tickfont=dict(color=txt, size=9)),
            angularaxis=dict(gridcolor=grid, tickfont=dict(color=txt, size=11))
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=txt),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=txt)),
        height=380,
        margin=dict(l=40, r=40, t=30, b=30)
    )
    return fig

def fig_barre_comparaison(s1, s2, n1, n2):
    cats = ["Buts/match", "Encaissés/match", "Pts/match", "Diff buts"]
    v1 = [round(s1["mbp"], 2), round(s1["mbc"], 2), round(s1["pts_par_match"], 2), s1["diff"]]
    v2 = [round(s2["mbp"], 2), round(s2["mbc"], 2), round(s2["pts_par_match"], 2), s2["diff"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(name=n1, x=cats, y=v1, marker_color='#3b82f6', opacity=0.85))
    fig.add_trace(go.Bar(name=n2, x=cats, y=v2, marker_color='#ef4444', opacity=0.85))
    fig.update_layout(
        barmode='group',
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=txt),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=txt)),
        height=280,
        margin=dict(l=20, r=20, t=20, b=40),
        xaxis=dict(gridcolor=grid),
        yaxis=dict(gridcolor=grid),
    )
    return fig

# ─────────────────────────────────────────────
# 7. CHARGEMENT DONNÉES
# ─────────────────────────────────────────────
data_ligue = charger_donnees(CHAMPIONNATS[choix_ligue])

if not data_ligue:
    st.error("⚠️ Impossible de récupérer les données. Vérifie ta clé API ou ton quota.")
    st.stop()

# Moyennes du championnat (pour normalisation Poisson)
all_gf = [e.get('goalsFor', 0) for e in data_ligue]
all_pj = [e.get('playedGames', 1) or 1 for e in data_ligue]
moy_gf_ligue = sum(all_gf) / sum(all_pj) if sum(all_pj) > 0 else 1.3
moy_ga_ligue = moy_gf_ligue  # symétrique par définition

# ─────────────────────────────────────────────
# 8. INTERFACE PRINCIPALE
# ─────────────────────────────────────────────
tab1, tab2 = st.tabs(["🎯 ANALYSE MATCH", "📊 CLASSEMENT"])

with tab1:
    equipes = sorted([e['team']['name'] for e in data_ligue])
    c1, c2 = st.columns(2)
    n1 = c1.selectbox("🏠 Domicile", equipes, index=0)
    n2 = c2.selectbox("✈️ Extérieur", equipes, index=min(1, len(equipes)-1))

    if n1 == n2:
        st.warning("⚠️ Sélectionne deux équipes différentes.")
        st.stop()

    e1 = next(e for e in data_ligue if e['team']['name'] == n1)
    e2 = next(e for e in data_ligue if e['team']['name'] == n2)
    s1 = extraire_stats(e1)
    s2 = extraire_stats(e2)

    # ── Ajustements terrain ──
    st.markdown('<div class="section-title">🛠️ Ajustements terrain</div>', unsafe_allow_html=True)
    aj1, aj2 = st.columns(2)
    with aj1:
        but1 = st.toggle(f"Buteur principal {n1} présent", value=True, key="bt1")
        rep1 = st.slider(f"Jours de repos — {n1}", 1, 14, 7, key="sl1")
    with aj2:
        but2 = st.toggle(f"Buteur principal {n2} présent", value=True, key="bt2")
        rep2 = st.slider(f"Jours de repos — {n2}", 1, 14, 7, key="sl2")

    # ── Calcul ──
    l_h, l_a = calculer_lambdas(s1, s2, moy_gf_ligue, moy_ga_ligue, but1, but2, rep1, rep2)
    mat = matrice_scores(l_h, l_a, n=8)
    p1, pn, p2, pbtts, p_over25 = probabilites_depuis_matrice(mat)
    score_h, score_a, score_prob = score_le_plus_probable(mat)

    # ── EN-TÊTE MATCH ──
    logo1 = e1["team"].get("crest", "")
    logo2 = e2["team"].get("crest", "")
    st.markdown(f"""
    <div class="match-header">
        <div class="team-block">
            <img class="team-logo" src="{logo1}" onerror="this.style.display='none'">
            <p class="team-name">{n1}</p>
            <div class="prob-big" style="color:{couleur_prob(p1)}">{p1*100:.1f}%</div>
            <div class="prob-label">Victoire Domicile</div>
            {forme_html(s1["form"])}
        </div>
        <div class="vs-block">VS</div>
        <div class="team-block" style="opacity:0.75">
            <div class="prob-big" style="color:{couleur_prob(pn)}">{pn*100:.1f}%</div>
            <div class="prob-label">Match Nul</div>
        </div>
        <div class="vs-block" style="opacity:0.3">·</div>
        <div class="team-block">
            <img class="team-logo" src="{logo2}" onerror="this.style.display='none'">
            <p class="team-name">{n2}</p>
            <div class="prob-big" style="color:{couleur_prob(p2)}">{p2*100:.1f}%</div>
            <div class="prob-label">Victoire Extérieur</div>
            {forme_html(s2["form"])}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── STATS COMPARÉES ──
    st.markdown('<div class="section-title">📋 Stats saison comparées</div>', unsafe_allow_html=True)
    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.markdown(f"**🏠 {n1}** — Rang #{e1['position']}")
        st.markdown(f"""
        <div class="stat-grid">
            <div class="stat-card"><span class="stat-value">{s1['mbp']:.2f}</span><span class="stat-label">Buts / match</span></div>
            <div class="stat-card"><span class="stat-value">{s1['mbc']:.2f}</span><span class="stat-label">Encaissés / match</span></div>
            <div class="stat-card"><span class="stat-value">{s1['pts_par_match']:.2f}</span><span class="stat-label">Pts / match</span></div>
            <div class="stat-card"><span class="stat-value">{s1['won']}</span><span class="stat-label">Victoires</span></div>
            <div class="stat-card"><span class="stat-value">{s1['draw']}</span><span class="stat-label">Nuls</span></div>
            <div class="stat-card"><span class="stat-value" style="color:{'#f87171' if s1['diff']<0 else '#4ade80'}">{'+' if s1['diff']>0 else ''}{s1['diff']}</span><span class="stat-label">Diff buts</span></div>
        </div>
        <p style="font-size:0.8rem;opacity:0.55;">λ (Expected Goals) : <strong style="color:{acc}">{l_h:.2f}</strong></p>
        """, unsafe_allow_html=True)

    with col_s2:
        st.markdown(f"**✈️ {n2}** — Rang #{e2['position']}")
        st.markdown(f"""
        <div class="stat-grid">
            <div class="stat-card"><span class="stat-value">{s2['mbp']:.2f}</span><span class="stat-label">Buts / match</span></div>
            <div class="stat-card"><span class="stat-value">{s2['mbc']:.2f}</span><span class="stat-label">Encaissés / match</span></div>
            <div class="stat-card"><span class="stat-value">{s2['pts_par_match']:.2f}</span><span class="stat-label">Pts / match</span></div>
            <div class="stat-card"><span class="stat-value">{s2['won']}</span><span class="stat-label">Victoires</span></div>
            <div class="stat-card"><span class="stat-value">{s2['draw']}</span><span class="stat-label">Nuls</span></div>
            <div class="stat-card"><span class="stat-value" style="color:{'#f87171' if s2['diff']<0 else '#4ade80'}">{'+' if s2['diff']>0 else ''}{s2['diff']}</span><span class="stat-label">Diff buts</span></div>
        </div>
        <p style="font-size:0.8rem;opacity:0.55;">λ (Expected Goals) : <strong style="color:#ef4444">{l_a:.2f}</strong></p>
        """, unsafe_allow_html=True)

    # ── GRAPHIQUES ──
    st.markdown('<div class="section-title">📊 Visualisations</div>', unsafe_allow_html=True)
    gc1, gc2 = st.columns(2)
    with gc1:
        st.plotly_chart(fig_radar(s1, s2, n1, n2), use_container_width=True)
    with gc2:
        st.plotly_chart(fig_barre_comparaison(s1, s2, n1, n2), use_container_width=True)

    # Heatmap scores
    st.plotly_chart(fig_heatmap_scores(mat, n1, n2), use_container_width=True)
    st.markdown(f'<div class="heatmap-note">Score le plus probable : <strong>{n1} {score_h} – {score_a} {n2}</strong> ({score_prob*100:.1f}%)</div>', unsafe_allow_html=True)

    # ── JAUGES ──
    st.markdown('<div class="section-title">🎯 Probabilités détaillées</div>', unsafe_allow_html=True)
    gj1, gj2, gj3 = st.columns(3)
    with gj1:
        st.plotly_chart(fig_jauge(p1, f"Victoire {n1}", couleur_prob(p1)), use_container_width=True)
    with gj2:
        st.plotly_chart(fig_jauge(p_over25, "Over 2.5 buts", couleur_prob(p_over25)), use_container_width=True)
    with gj3:
        st.plotly_chart(fig_jauge(pbtts, "BTTS (2 équipes marquent)", couleur_prob(pbtts)), use_container_width=True)

    # ── VERDICT EXPERT ──
    st.markdown('<div class="section-title">🏆 Verdict Expert & Value Bets</div>', unsafe_allow_html=True)

    # Résultat 1N2
    if p1 > p2 and p1 > pn:    res, prob_f, coul_res = n1, p1, "#3b82f6"
    elif p2 > p1 and p2 > pn:  res, prob_f, coul_res = n2, p2, "#ef4444"
    else:                        res, prob_f, coul_res = "Match Nul", pn, "#fbbf24"
    cote_1n2 = round(1 / prob_f, 2) if prob_f > 0 else 99

    vd1, vd2, vd3 = st.columns(3)

    with vd1:
        st.markdown(f"""
        <div class="verdict-card">
            <div class="verdict-title">🏆 Prono 1N2</div>
            <div class="verdict-main" style="color:{coul_res}">{res}</div>
            <div class="verdict-prob">{prob_f*100:.1f}% de confiance</div>
            <div style="font-size:0.8rem;opacity:0.5;margin-top:6px;">Cote algo : {cote_1n2}</div>
            <div style="font-size:0.8rem;opacity:0.5;">Score probable : {n1} <strong>{score_h}–{score_a}</strong> {n2}</div>
        </div>
        """, unsafe_allow_html=True)
        c_bk_1 = st.number_input("Cote bookmaker 1N2", 1.01, 30.0, float(cote_1n2), 0.05, key="k1")
        kelly_1 = kelly_criterion(prob_f, c_bk_1)
        if c_bk_1 > cote_1n2 + 0.15:
            st.markdown(f'<div class="kelly-box">🔥 <strong>VALUE BET</strong><br>Kelly : miser <strong>{kelly_1*100:.1f}%</strong> de ta bankroll</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="kelly-box-neg">Pas de value sur ce marché.</div>', unsafe_allow_html=True)

    with vd2:
        label_o = "OVER 2.5" if p_over25 > 0.52 else "UNDER 2.5"
        badge_o = '<span class="badge-green">📈 OVER 2.5</span>' if p_over25 > 0.52 else '<span class="badge-red">📉 UNDER 2.5</span>'
        cote_o = round(1 / p_over25, 2) if p_over25 > 0 else 9.99
        cote_u = round(1 / (1 - p_over25), 2) if p_over25 < 1 else 9.99
        st.markdown(f"""
        <div class="verdict-card">
            <div class="verdict-title">⚽ Buts Over/Under</div>
            <div class="verdict-main">{label_o}</div>
            <div class="verdict-prob">{p_over25*100:.1f}% chance Over 2.5</div>
            {badge_o}
            <div style="font-size:0.8rem;opacity:0.5;margin-top:8px;">Cote algo Over : {cote_o} · Under : {cote_u}</div>
        </div>
        """, unsafe_allow_html=True)
        c_bk_o = st.number_input("Cote bookmaker Over 2.5", 1.01, 10.0, 1.90, 0.05, key="k2")
        kelly_o = kelly_criterion(p_over25, c_bk_o)
        if c_bk_o > cote_o + 0.15:
            st.markdown(f'<div class="kelly-box">🔥 <strong>VALUE BET</strong><br>Kelly : <strong>{kelly_o*100:.1f}%</strong> bankroll</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="kelly-box-neg">Pas de value sur ce marché.</div>', unsafe_allow_html=True)

    with vd3:
        label_b = "OUI" if pbtts > 0.55 else "NON"
        badge_b = '<span class="badge-green">✅ BTTS OUI</span>' if pbtts > 0.55 else '<span class="badge-red">❌ BTTS NON</span>'
        cote_b = round(1 / pbtts, 2) if pbtts > 0 else 9.99
        st.markdown(f"""
        <div class="verdict-card">
            <div class="verdict-title">🎯 BTTS (2 marquent)</div>
            <div class="verdict-main">{label_b}</div>
            <div class="verdict-prob">{pbtts*100:.1f}% probabilité</div>
            {badge_b}
            <div style="font-size:0.8rem;opacity:0.5;margin-top:8px;">Cote algo BTTS : {cote_b}</div>
        </div>
        """, unsafe_allow_html=True)
        c_bk_b = st.number_input("Cote bookmaker BTTS", 1.01, 10.0, 1.85, 0.05, key="k3")
        kelly_b = kelly_criterion(pbtts, c_bk_b)
        if c_bk_b > cote_b + 0.15:
            st.markdown(f'<div class="kelly-box">🔥 <strong>VALUE BET</strong><br>Kelly : <strong>{kelly_b*100:.1f}%</strong> bankroll</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="kelly-box-neg">Pas de value sur ce marché.</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section-title">📊 Classement actuel</div>', unsafe_allow_html=True)
    df = pd.DataFrame([{
        "Rang": e['position'],
        "Équipe": e['team']['name'],
        "MJ": e['playedGames'],
        "V": e.get('won', 0),
        "N": e.get('draw', 0),
        "D": e.get('lost', 0),
        "Pts": e['points'],
        "Buts +": e['goalsFor'],
        "Buts -": e['goalsAgainst'],
        "Diff": e['goalsFor'] - e['goalsAgainst'],
        "Forme": str(e.get('form', '') or '').replace(',', '')[-5:],
    } for e in data_ligue])
    st.dataframe(df, use_container_width=True, hide_index=True,
                 column_config={
                     "Diff": st.column_config.NumberColumn(format="%+d"),
                     "Forme": st.column_config.TextColumn(),
                 })

# ── FOOTER ──
st.divider()
st.caption("PRO-FOOT AI V12 · Poisson Bivarié Normalisé · Kelly Criterion · football-data.org")