# ─────────────────────────────────────────────
# app.py — Point d'entrée principal (orchestrateur)
# Lance avec : streamlit run app.py
# ─────────────────────────────────────────────

import streamlit as st
import pandas as pd

from config import CHAMPIONNATS, SEUIL_BTTS, SEUIL_OVER25, SEUIL_VALUE
from core.api     import charger_classement, moyenne_buts_ligue
from core.stats   import extraire_stats
from core.moteur  import (
    calculer_lambdas, matrice_scores,
    probabilites_depuis_matrice, score_le_plus_probable,
    kelly_criterion, poisson,
)
from ui.theme      import get_couleurs, injecter_css
from ui.composants import (
    match_header_html, stat_grid_html,
    verdict_card_html, kelly_html, couleur_prob,
)
from ui.graphiques import fig_radar, fig_barres, fig_heatmap, fig_jauge

# ─── Config page ────────────────────────────────
st.set_page_config(page_title="PRO-FOOT AI V12", page_icon="🏆", layout="wide")

# ─── Sidebar ────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ RÉGLAGES")
    theme_clair = st.toggle("☀️ Mode Clair", value=False)
    st.divider()
    choix_ligue = st.selectbox("🏆 CHAMPIONNAT", list(CHAMPIONNATS.keys()))
    st.info("Algorithme : Poisson Bivarié · Lambda Normalisé · Kelly")
    st.divider()
    st.markdown("**📖 Légende forme**")
    st.markdown("`W` Victoire · `D` Nul · `L` Défaite")

# ─── Thème & CSS ────────────────────────────────
c = get_couleurs(theme_clair)
injecter_css(c)

# ─── Chargement données ─────────────────────────
data_ligue = charger_classement(CHAMPIONNATS[choix_ligue])

if not data_ligue:
    st.error("⚠️ Impossible de récupérer les données. Vérifie ta clé API ou ton quota.")
    st.stop()

moy_gf = moyenne_buts_ligue(data_ligue)

# ─── Tabs ───────────────────────────────────────
tab1, tab2 = st.tabs(["🎯 ANALYSE MATCH", "📊 CLASSEMENT"])

# ════════════════════════════════════════════════
# TAB 1 — ANALYSE
# ════════════════════════════════════════════════
with tab1:
    equipes = sorted([e["team"]["name"] for e in data_ligue])
    col_sel1, col_sel2 = st.columns(2)
    n1 = col_sel1.selectbox("🏠 Domicile",  equipes, index=0)
    n2 = col_sel2.selectbox("✈️ Extérieur", equipes, index=min(1, len(equipes) - 1))

    if n1 == n2:
        st.warning("⚠️ Sélectionne deux équipes différentes.")
        st.stop()

    e1 = next(e for e in data_ligue if e["team"]["name"] == n1)
    e2 = next(e for e in data_ligue if e["team"]["name"] == n2)
    s1 = extraire_stats(e1)
    s2 = extraire_stats(e2)

    # ── Ajustements terrain ──────────────────────
    st.markdown('<div class="section-title">🛠️ Ajustements terrain</div>', unsafe_allow_html=True)
    aj1, aj2 = st.columns(2)
    with aj1:
        but1 = st.toggle(f"Buteur principal {n1} présent", value=True, key="bt1")
        rep1 = st.slider(f"Jours de repos — {n1}", 1, 14, 7, key="sl1")
    with aj2:
        but2 = st.toggle(f"Buteur principal {n2} présent", value=True, key="bt2")
        rep2 = st.slider(f"Jours de repos — {n2}", 1, 14, 7, key="sl2")

    # ── Calcul ──────────────────────────────────
    l_h, l_a = calculer_lambdas(s1, s2, moy_gf, but1, but2, rep1, rep2)
    mat       = matrice_scores(l_h, l_a)
    p1, pn, p2, pbtts, p_over25 = probabilites_depuis_matrice(mat)
    score_h, score_a, score_prob = score_le_plus_probable(mat)

    logo1 = e1["team"].get("crest", "")
    logo2 = e2["team"].get("crest", "")

    # ── En-tête match ────────────────────────────
    st.markdown(
        match_header_html(n1, n2, logo1, logo2, p1, pn, p2, s1["form"], s2["form"]),
        unsafe_allow_html=True
    )

    # ── Stats comparées ──────────────────────────
    st.markdown('<div class="section-title">📋 Stats saison comparées</div>', unsafe_allow_html=True)
    cs1, cs2 = st.columns(2)
    with cs1:
        st.markdown(f"**🏠 {n1}** — Rang #{e1['position']}")
        st.markdown(stat_grid_html(s1, l_h, c["acc"]), unsafe_allow_html=True)
    with cs2:
        st.markdown(f"**✈️ {n2}** — Rang #{e2['position']}")
        st.markdown(stat_grid_html(s2, l_a, "#ef4444"), unsafe_allow_html=True)

    # ── Graphiques ───────────────────────────────
    st.markdown('<div class="section-title">📊 Visualisations</div>', unsafe_allow_html=True)
    gc1, gc2 = st.columns(2)
    with gc1:
        st.plotly_chart(fig_radar(s1, s2, n1, n2, c), use_container_width=True)
    with gc2:
        st.plotly_chart(fig_barres(s1, s2, n1, n2, c), use_container_width=True)

    st.plotly_chart(fig_heatmap(mat, n1, n2, c), use_container_width=True)
    st.markdown(
        f'<div class="heatmap-note">Score le plus probable : <strong>{n1} {score_h}–{score_a} {n2}</strong> ({score_prob*100:.1f}%)</div>',
        unsafe_allow_html=True
    )

    # ── Jauges ───────────────────────────────────
    st.markdown('<div class="section-title">🎯 Probabilités détaillées</div>', unsafe_allow_html=True)
    gj1, gj2, gj3 = st.columns(3)
    with gj1:
        st.plotly_chart(fig_jauge(p1, f"Victoire {n1}", couleur_prob(p1), c), use_container_width=True)
    with gj2:
        st.plotly_chart(fig_jauge(p_over25, "Over 2.5 buts", couleur_prob(p_over25), c), use_container_width=True)
    with gj3:
        st.plotly_chart(fig_jauge(pbtts, "BTTS", couleur_prob(pbtts), c), use_container_width=True)

    # ── Verdict expert ───────────────────────────
    st.markdown('<div class="section-title">🏆 Verdict Expert & Value Bets</div>', unsafe_allow_html=True)

    if p1 > p2 and p1 > pn:   res, prob_f, coul_r = n1, p1, "#3b82f6"
    elif p2 > p1 and p2 > pn: res, prob_f, coul_r = n2, p2, "#ef4444"
    else:                       res, prob_f, coul_r = "Match Nul", pn, "#fbbf24"
    cote_1n2 = round(1 / prob_f, 2) if prob_f > 0 else 99

    vd1, vd2, vd3 = st.columns(3)

    # 1N2
    with vd1:
        badge_1n2 = f'<span class="badge-blue">👉 {res}</span>'
        st.markdown(
            verdict_card_html("🏆 Prono 1N2", f'<span style="color:{coul_r}">{res}</span>', prob_f, badge_1n2,
                              f"Cote algo : {cote_1n2} · Score probable : {score_h}–{score_a}"),
            unsafe_allow_html=True
        )
        c_bk1 = st.number_input("Cote bookmaker 1N2", 1.01, 30.0, float(cote_1n2), 0.05, key="k1")
        kelly_1 = kelly_criterion(prob_f, c_bk1)
        st.markdown(kelly_html(kelly_1, c_bk1 > cote_1n2 + SEUIL_VALUE), unsafe_allow_html=True)

    # Over/Under
    with vd2:
        cote_o = round(1 / p_over25, 2) if p_over25 > 0 else 9.99
        cote_u = round(1 / (1 - p_over25), 2) if p_over25 < 1 else 9.99
        label_o = "OVER 2.5" if p_over25 > SEUIL_OVER25 else "UNDER 2.5"
        badge_o = '<span class="badge-green">📈 OVER 2.5</span>' if p_over25 > SEUIL_OVER25 else '<span class="badge-red">📉 UNDER 2.5</span>'
        st.markdown(
            verdict_card_html("⚽ Buts Over/Under", label_o, p_over25, badge_o,
                              f"Cote algo Over : {cote_o} · Under : {cote_u}"),
            unsafe_allow_html=True
        )
        c_bk_o = st.number_input("Cote bookmaker Over 2.5", 1.01, 10.0, 1.90, 0.05, key="k2")
        kelly_o = kelly_criterion(p_over25, c_bk_o)
        st.markdown(kelly_html(kelly_o, c_bk_o > cote_o + SEUIL_VALUE), unsafe_allow_html=True)

    # BTTS
    with vd3:
        cote_b = round(1 / pbtts, 2) if pbtts > 0 else 9.99
        label_b = "OUI" if pbtts > SEUIL_BTTS else "NON"
        badge_b = '<span class="badge-green">✅ BTTS OUI</span>' if pbtts > SEUIL_BTTS else '<span class="badge-red">❌ BTTS NON</span>'
        st.markdown(
            verdict_card_html("🎯 BTTS (2 marquent)", label_b, pbtts, badge_b,
                              f"Cote algo BTTS : {cote_b}"),
            unsafe_allow_html=True
        )
        c_bk_b = st.number_input("Cote bookmaker BTTS", 1.01, 10.0, 1.85, 0.05, key="k3")
        kelly_b = kelly_criterion(pbtts, c_bk_b)
        st.markdown(kelly_html(kelly_b, c_bk_b > cote_b + SEUIL_VALUE), unsafe_allow_html=True)

# ════════════════════════════════════════════════
# TAB 2 — CLASSEMENT
# ════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">📊 Classement actuel</div>', unsafe_allow_html=True)
    df = pd.DataFrame([{
        "Rang":   e["position"],
        "Équipe": e["team"]["name"],
        "MJ":     e["playedGames"],
        "V":      e.get("won", 0),
        "N":      e.get("draw", 0),
        "D":      e.get("lost", 0),
        "Pts":    e["points"],
        "Buts +": e["goalsFor"],
        "Buts -": e["goalsAgainst"],
        "Diff":   e["goalsFor"] - e["goalsAgainst"],
        "Forme":  str(e.get("form", "") or "").replace(",", "")[-5:],
    } for e in data_ligue])
    st.dataframe(df, use_container_width=True, hide_index=True,
                 column_config={"Diff": st.column_config.NumberColumn(format="%+d")})

# ─── Footer ─────────────────────────────────────
st.divider()
st.caption("PRO-FOOT AI V12 · Poisson Bivarié Normalisé · Kelly Criterion · football-data.org")
