import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import math

# --- 1. CONFIGURATION ---
API_KEY = "6845fbe629e041bdb8f0cad7488a9fe2"
CHAMPIONNATS = {
    "🇫🇷 Ligue 1": "FL1", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": "PL", "🇪🇸 La Liga": "PD",
    "🇩🇪 Bundesliga": "BL1", "🇮🇹 Serie A": "SA", "🇳🇱 Eredivisie": "DED"
}

st.set_page_config(page_title="PRO-FOOT AI V11.5", page_icon="🏆", layout="wide")

# --- 2. SIDEBAR (LOGIQUE PRIORITAIRE) ---
with st.sidebar:
    st.markdown("### ⚙️ RÉGLAGES")
    theme_clair = st.toggle("☀️ Mode Clair", value=False, key="force_theme_toggle")
    st.divider()
    choix_ligue = st.selectbox("🏆 CHAMPIONNAT", list(CHAMPIONNATS.keys()))
    st.info("Algorithme : Poisson Matriciel Bivarié")

# --- 3. COULEURS DYNAMIQUES ET CSS DE SURVIE ---
if theme_clair:
    bg, card, txt, brd, grid = "#FFFFFF", "#F8FAFC", "#0F172A", "#E2E8F0", "#94A3B8"
else:
    bg, card, txt, brd, grid = "#0E1117", "#1D2129", "#FFFFFF", "#30363D", "#444444"

st.markdown(f"""
    <style>
    /* Forçage visuel global */
    header[data-testid="stHeader"] {{ background: transparent !important; border: none !important; }}
    .stApp {{ background-color: {bg}; color: {txt}; }}
    .stApp, .stMarkdown, p, h1, h2, h3, span, label, li {{ color: {txt} !important; }}

    /* FIX SELECTBOX CONTRASTES */
    div[data-baseweb="select"] > div {{ background-color: {card} !important; color: {txt} !important; }}
    div[data-baseweb="popover"] ul {{ background-color: {card} !important; }}
    div[data-baseweb="popover"] li {{ color: {txt} !important; }}

    /* Sidebar Fix */
    [data-testid="stSidebar"] {{ background-color: {card} !important; min-width: 250px !important; }}
    
    .team-card {{
        background-color: {card};
        padding: 25px;
        border-radius: 20px;
        border: 1px solid {brd};
        text-align: center;
        margin-bottom: 15px;
        transition: transform 0.3s;
    }}
    .team-card:hover {{ transform: scale(1.02); border-color: #3b82f6; }}
    
    .verdict-box {{
        background-color: {card};
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #3b82f6;
        margin-top: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. FONCTIONS MATHÉMATIQUES (MOTEUR PRO) ---
def loi_de_poisson(moyenne_lambda, k):
    if moyenne_lambda <= 0: return 0
    return (math.pow(moyenne_lambda, k) * math.exp(-moyenne_lambda)) / math.factorial(k)

def calculer_probabilites_completes(l_h, l_a):
    prob_1, prob_n, prob_2, prob_btts = 0, 0, 0, 0
    for h in range(10): # On monte à 10 buts pour la précision
        for a in range(10):
            p = loi_de_poisson(l_h, h) * loi_de_poisson(l_a, a)
            if h > a: prob_1 += p
            elif h == a: prob_n += p
            else: prob_2 += p
            if h > 0 and a > 0: prob_btts += p
    return prob_1, prob_n, prob_2, prob_btts

# --- 5. CHARGEMENT ET TRAITEMENT DES DONNÉES ---
@st.cache_data(ttl=3600)
def charger_donnees(league_code):
    url = f"https://api.football-data.org/v4/competitions/{league_code}/standings"
    headers = {"X-Auth-Token": API_KEY}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()['standings'][0]['table']
        return None
    except: return None

def calculer_base_stats(equipe_data):
    if not equipe_data: return [50, 50, 50, 50], 1.0, 1.0
    pj = equipe_data.get('playedGames', 0)
    if pj == 0: return [50, 50, 50, 50], 1.0, 1.0
    
    mbp = equipe_data.get('goalsFor', 0) / pj
    mbc = equipe_data.get('goalsAgainst', 0) / pj
    
    att = min(mbp * 45, 100)
    defe = max(100 - (mbc * 50), 0)
    
    f_str = str(equipe_data.get('form', 'DDDDD')).replace(',', '')[-5:]
    pts_f = (f_str.count('W') * 3) + f_str.count('D')
    forme_f = (pts_f / 15) * 100
    vic = (equipe_data.get('won', 0) / pj) * 100
    
    return [int(att), int(defe), int(vic), int(forme_f)], mbp, mbc

# --- 6. LOGIQUE D'ANALYSE ---
data_ligue = charger_donnees(CHAMPIONNATS[choix_ligue])

if data_ligue:
    tab1, tab2 = st.tabs(["🎯 ANALYSE POISSON", "📈 CLASSEMENT"])
    
    with tab1:
        equipes = sorted([e['team']['name'] for e in data_ligue])
        c1, c2 = st.columns(2)
        n1 = c1.selectbox("🏠 Domicile", equipes, index=0)
        n2 = c2.selectbox("✈️ Extérieur", equipes, index=min(1, len(equipes)-1))

        e1 = next(e for e in data_ligue if e['team']['name'] == n1)
        e2 = next(e for e in data_ligue if e['team']['name'] == n2)
        
        st.markdown("### 🛠️ AJUSTEMENTS TERRAIN")
        aj1, aj2 = st.columns(2)
        but1 = aj1.toggle(f"Buteur {n1} présent", value=True, key="bt1")
        rep1 = aj1.slider(f"Repos {n1} (Jours)", 1, 14, 7, key="sl1")
        but2 = aj2.toggle(f"Buteur {n2} présent", value=True, key="bt2")
        rep2 = aj2.slider(f"Repos {n2} (Jours)", 1, 14, 7, key="sl2")

        stats1, mbp1, mbc1 = calculer_base_stats(e1)
        stats2, mbp2, mbc2 = calculer_base_stats(e2)
        
        # --- CALCUL LAMBDA (Moyennes ajustées) ---
        l_h = mbp1 * mbc2 * (1.0 if but1 else 0.75) * (1.1 if rep1 > 4 else 0.85)
        l_a = mbp2 * mbc1 * (1.0 if but2 else 0.75) * (1.1 if rep2 > 4 else 0.85)
        
        # Avantage domicile dynamique
        l_h *= 1.10 

        p1, pn, p2, pbtts = calculer_probabilites_completes(l_h, l_a)

        st.divider()
        cl, cr = st.columns(2)
        cl.markdown(f'<div class="team-card"><img src="{e1["team"]["crest"]}" width="70"><h3>{n1}</h3><h1>{p1*100:.1f}%</h1><p>Expected Goals : {l_h:.2f}</p></div>', unsafe_allow_html=True)
        cr.markdown(f'<div class="team-card"><img src="{e2["team"]["crest"]}" width="70"><h3>{n2}</h3><h1>{p2*100:.1f}%</h1><p>Expected Goals : {l_a:.2f}</p></div>', unsafe_allow_html=True)

        # Radar Chart Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=stats1, theta=['Attaque','Défense','Victoires','Forme'], fill='toself', name=n1, line_color='#3b82f6'))
        fig.add_trace(go.Scatterpolar(r=stats2, theta=['Attaque','Défense','Victoires','Forme'], fill='toself', name=n2, line_color='#ef4444'))
        fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=True, range=[0, 100], gridcolor=grid)), paper_bgcolor="rgba(0,0,0,0)", font=dict(color=txt), height=450)
        st.plotly_chart(fig, use_container_width=True)

        # --- VERDICT EXPERT ---
        st.markdown("### 🏆 VERDICT EXPERT")
        v1, v2, v3 = st.columns(3)
        
        with v1:
            st.markdown("**PRONO 1N2**")
            if p1 > p2 and p1 > pn: res, prob_f = n1, p1
            elif p2 > p1 and p2 > pn: res, prob_f = n2, p2
            else: res, prob_f = "Match Nul", pn
            
            st.metric("Prono", res, f"{int(prob_f*100)}%")
            cote_algo = round(1 / prob_f, 2)
            st.caption(f"📊 Cote Algo : {cote_algo}")
            
            c_book = st.number_input("Cote Bookmaker", 1.01, 20.0, float(cote_algo), 0.05, key="k1")
            if c_book > (cote_algo + 0.20): st.success("🔥 VALUE BET DETECTÉ")

        with v2:
            st.markdown("**BUTS (+2.5)**")
            p_over25 = 1 - (loi_de_poisson(l_h+l_a, 0) + loi_de_poisson(l_h+l_a, 1) + loi_de_poisson(l_h+l_a, 2))
            st.metric("Confiance", f"{int(p_over25*100)}%")
            if p_over25 > 0.55: st.error("📈 OVER 2.5")
            else: st.info("📉 UNDER 2.5")
            
            cote_o_algo = round(1/p_over25, 2) if p_over25 > 0 else 9.99
            st.caption(f"📊 Cote Algo Over : {cote_o_algo}")
            c_book_o = st.number_input("Cote Bookmaker Over", 1.01, 10.0, 1.90, 0.05, key="k2")

        with v3:
            st.markdown("**BTTS (2 marquent)**")
            st.metric("Probabilité", f"{int(pbtts*100)}%")
            if pbtts > 0.58: st.success("✅ OUI")
            else: st.error("❌ NON")
            
            cote_b_algo = round(1/pbtts, 2) if pbtts > 0 else 9.99
            st.caption(f"📊 Cote Algo BTTS : {cote_b_algo}")
            c_book_b = st.number_input("Cote Bookmaker BTTS", 1.01, 10.0, 1.85, 0.05, key="k3")

    with tab2:
        st.markdown("### 📊 CLASSEMENT ACTUEL")
        df = pd.DataFrame([
            {
                "Rang": e['position'], 
                "Équipe": e['team']['name'], 
                "MJ": e['playedGames'],
                "Pts": e['points'], 
                "Buts +": e['goalsFor'],
                "Buts -": e['goalsAgainst'],
                "Forme": e['form']
            } for e in data_ligue
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.error("⚠️ Impossible de récupérer les données. Vérifie ta clé API-Football-Data ou ton quota.")

# --- 7. FOOTER ---
st.divider()
st.caption("PRO-FOOT AI - Utilise la Loi de Poisson Bivariée pour estimer les probabilités sportives.")