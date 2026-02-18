import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import math
import numpy as np

# --- 1. CONFIGURATION ---
API_KEY = "6845fbe629e041bdb8f0cad7488a9fe2"
CHAMPIONNATS = {
    "🇫🇷 Ligue 1": "FL1", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": "PL", "🇪🇸 La Liga": "PD",
    "🇩🇪 Bundesliga": "BL1", "🇮🇹 Serie A": "SA", "🇳🇱 Eredivisie": "DED"
}

st.set_page_config(page_title="PRO-FOOT AI V11", page_icon="⚽", layout="wide")

# --- 2. CSS CUSTOM (DARK/LIGHT) ---
with st.sidebar:
    st.markdown("### ⚙️ RÉGLAGES")
    theme_clair = st.toggle("☀️ Mode Clair", value=False)
    choix_ligue = st.selectbox("🏆 CHAMPIONNAT", list(CHAMPIONNATS.keys()))

bg = "#FFFFFF" if theme_clair else "#0E1117"
txt = "#0F172A" if theme_clair else "#FFFFFF"
card = "#F1F5F9" if theme_clair else "#1E293B"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    .team-card {{
        background-color: {card};
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #3b82f6;
        text-align: center;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIQUE MATHÉMATIQUE AVANCÉE ---
def proba_poisson(lmbda, k):
    return (math.exp(-lmbda) * (lmbda**k)) / math.factorial(k)

def calculer_probabilites_match(lambda_h, lambda_a):
    """Calcule la matrice des scores pour 1N2 et BTTS"""
    prob_1, prob_n, prob_2 = 0, 0, 0
    prob_btts = 0
    max_buts = 8 # On calcule jusqu'à 8 buts pour la précision
    
    for h in range(max_buts):
        for a in range(max_buts):
            p = proba_poisson(lambda_h, h) * proba_poisson(lambda_a, a)
            if h > a: prob_1 += p
            elif h == a: prob_n += p
            else: prob_2 += p
            
            if h > 0 and a > 0:
                prob_btts += p
                
    return prob_1, prob_n, prob_2, prob_btts

# --- 4. DATA ET STATS ---
@st.cache_data(ttl=3600)
def charger_donnees(league_code):
    url = f"https://api.football-data.org/v4/competitions/{league_code}/standings"
    headers = {"X-Auth-Token": API_KEY}
    try:
        r = requests.get(url, headers=headers)
        return r.json()['standings'][0]['table']
    except: return None

def extraire_stats(equipe_data):
    pj = equipe_data['playedGames']
    if pj == 0: return 1.0, 1.0, 50
    mbp = equipe_data['goalsFor'] / pj
    mbc = equipe_data['goalsAgainst'] / pj
    # Calcul de forme (3 derniers matchs)
    forme_str = str(equipe_data.get('form', 'DDDDD')).replace(',', '')[-3:]
    pts_forme = (forme_str.count('W') * 3) + forme_str.count('D')
    return mbp, mbc, (pts_forme / 9) * 100

# --- 5. INTERFACE ---
data = charger_donnees(CHAMPIONNATS[choix_ligue])

if data:
    equipes = sorted([e['team']['name'] for e in data])
    col1, col2 = st.columns(2)
    n1 = col1.selectbox("🏠 Domicile", equipes, index=0)
    n2 = col2.selectbox("✈️ Extérieur", equipes, index=1)

    e1 = next(e for e in data if e['team']['name'] == n1)
    e2 = next(e for e in data if e['team']['name'] == n2)

    # Stats de base
    mbp1, mbc1, forme1 = extraire_stats(e1)
    mbp2, mbc2, forme2 = extraire_stats(e2)

    # Paramètres utilisateur
    with st.expander("🛠️ Ajustements Tactiques"):
        c_a, c_b = st.columns(2)
        but1 = c_a.toggle(f"Buteur {n1} présent", value=True)
        but2 = c_b.toggle(f"Buteur {n2} présent", value=True)
        repos1 = c_a.slider(f"Repos {n1} (jours)", 1, 10, 7)
        repos2 = c_b.slider(f"Repos {n2} (jours)", 1, 10, 7)

    # --- LE COEUR DU CALCUL ---
    # Moyenne de buts attendue (Lambda)
    l_h = mbp1 * mbc2 * (1.1 if repos1 > 4 else 0.8) * (1.0 if but1 else 0.7)
    l_a = mbp2 * mbc1 * (1.1 if repos2 > 4 else 0.8) * (1.0 if but2 else 0.7)
    
    # Ajout du bonus domicile dynamique (basé sur le classement)
    bonus_dom = (20 - e1['position']) / 20 * 0.2
    l_h += bonus_dom

    p1, pn, p2, pbtts = calculer_probabilites_match(l_h, l_a)

    # --- AFFICHAGE ---
    st.divider()
    ca, cb = st.columns(2)
    ca.markdown(f'<div class="team-card"><h3>{n1}</h3><h1>{p1*100:.1f}%</h1><p>Buts attendus : {l_h:.2f}</p></div>', unsafe_allow_html=True)
    cb.markdown(f'<div class="team-card"><h3>{n2}</h3><h1>{p2*100:.1f}%</h1><p>Buts attendus : {l_a:.2f}</p></div>', unsafe_allow_html=True)

    st.markdown(f"### ⚖️ Probabilité du Nul : **{pn*100:.1f}%**")

    # --- VERDICT EXPERT ---
    st.subheader("🎯 Pronostics IA")
    v1, v2, v3 = st.columns(3)

    with v1:
        st.info("**MODÈLE 1N2**")
        final_1n2 = "1" if p1 > p2 and p1 > pn else ("2" if p2 > p1 and p2 > pn else "N")
        st.metric("Prono", final_1n2)
        st.caption(f"Cote Algo : {1/max(p1,p2,pn):.2f}")

    with v2:
        st.info("**BUTS +2.5**")
        p_over25 = 1 - (proba_poisson(l_h+l_a, 0) + proba_poisson(l_h+l_a, 1) + proba_poisson(l_h+l_a, 2))
        st.metric("Probabilité", f"{p_over25*100:.1f}%")
        st.write("🔥 OUI" if p_over25 > 0.52 else "❄️ NON")

    with v3:
        st.info("**BTTS**")
        st.metric("Les 2 marquent", f"{pbtts*100:.1f}%")
        st.write("✅ OUI" if pbtts > 0.55 else "❌ NON")

    # Radar Chart pour le fun
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=[forme1, mbp1*40, 100-mbc1*40], theta=['Forme','Attaque','Défense'], fill='toself', name=n1))
    fig.add_trace(go.Scatterpolar(r=[forme2, mbp2*40, 100-mbc2*40], theta=['Forme','Attaque','Défense'], fill='toself', name=n2))
    st.plotly_chart(fig)
else:
    st.error("Impossible de charger les données. Vérifie ta clé API ou ta connexion.")