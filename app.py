# ─────────────────────────────────────────────
# app.py — Point d'entrée principal (orchestrateur)
# Lance avec : streamlit run app.py
# ─────────────────────────────────────────────

import streamlit as st
import pandas as pd

from config import CHAMPIONNATS, SEUIL_BTTS, SEUIL_OVER15, SEUIL_VALUE
from core.api import charger_classement, moyenne_buts_ligue
from core.stats import extraire_stats
from core.moteur import (
    calculer_lambdas, matrice_scores,
    probabilites_depuis_matrice, score_le_plus_probable,
    kelly_criterion
)
from style import get_couleurs, injecter_css, couleur_prob
from ui.composants import (
    match_header_html, stat_grid_html,
    verdict_card_html, kelly_html,
)
from ui.graphiques import fig_radar, fig_barres, fig_heatmap, fig_jauge

# ─── Config page ────────────────────────────────
st.set_page_config(page_title="PRO-FOOT AI V12", page_icon="🏆", layout="wide")


# ─── Composants modulaires Streamlit ────────────
def render_sidebar() -> tuple[str, bool]:
    """Gère l'affichage de la barre latérale et retourne les champs."""
    with st.sidebar:
        st.markdown("### ⚙️ RÉGLAGES")
        choix_ligue = st.selectbox("🏆 CHAMPIONNAT", list(CHAMPIONNATS.keys()))
        
        st.divider()
        if st.button("🔄 ACTUALISER LES DONNÉES", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.divider()
        theme_clair = st.toggle("☀️ Mode Clair", value=False)
        
    return choix_ligue, theme_clair


def tab_analyse(data_ligue: list, moy_gf: float, c: dict):
    """Gère l'affichage complet de l'onglet d'analyse."""
    equipes = sorted([e["team"]["name"] for e in data_ligue])
    
    col_sel1, col_sel2 = st.columns(2)
    n1 = col_sel1.selectbox("🏠 Domicile", equipes, index=0)
    n2 = col_sel2.selectbox("✈️ Extérieur", equipes, index=min(1, len(equipes) - 1))

    if n1 == n2:
        st.warning("⚠️ Sélectionne deux équipes différentes.")
        st.stop()

    e1 = next(e for e in data_ligue if e["team"]["name"] == n1)
    e2 = next(e for e in data_ligue if e["team"]["name"] == n2)
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

    with st.spinner("Analyse du moteur bivarié en cours..."):
        # ── Calcul ──
        l_h, l_a = calculer_lambdas(s1, s2, moy_gf, but1, but2, rep1, rep2)
        mat = matrice_scores(l_h, l_a)
        p1, pn, p2, pbtts, p_over15 = probabilites_depuis_matrice(mat)
        score_h, score_a, score_prob = score_le_plus_probable(mat)

        logo1 = e1["team"].get("crest", "")
        logo2 = e2["team"].get("crest", "")

        # ── En-tête match ──
        st.markdown(
            match_header_html(n1, n2, logo1, logo2, p1, pn, p2, s1["form"], s2["form"]),
            unsafe_allow_html=True
        )

        # ── Stats comparées ──
        st.markdown('<div class="section-title">📋 Statistiques avancées</div>', unsafe_allow_html=True)
        cs1, cs2 = st.columns(2)
        with cs1:
            st.markdown(f"**🏠 {n1}** — Rang #{e1.get('position', '?')}")
            st.markdown(stat_grid_html(s1, l_h, c["acc"]), unsafe_allow_html=True)
        with cs2:
            st.markdown(f"**✈️ {n2}** — Rang #{e2.get('position', '?')}")
            st.markdown(stat_grid_html(s2, l_a, c["danger"]), unsafe_allow_html=True)

        # ── Graphiques ──
        st.markdown('<div class="section-title">📊 Synthèse visuelle</div>', unsafe_allow_html=True)
        gc1, gc2 = st.columns(2)
        with gc1:
            st.plotly_chart(fig_radar(s1, s2, n1, n2, c), use_container_width=True)
        with gc2:
            st.plotly_chart(fig_barres(s1, s2, n1, n2, c), use_container_width=True)

        st.plotly_chart(fig_heatmap(mat, n1, n2, c), use_container_width=True)
        st.markdown(
            f'<div class="text-center w-100" style="opacity:0.6;font-size:14px;">Score le plus probable : <strong>{n1} {score_h}–{score_a} {n2}</strong> ({score_prob*100:.1f}%)</div><br>',
            unsafe_allow_html=True
        )

        # ── Jauges de confiance ──
        st.markdown('<div class="section-title">🎯 Profil Probabiliste</div>', unsafe_allow_html=True)
        gj1, gj2, gj3 = st.columns(3)
        with gj1:
            st.plotly_chart(fig_jauge(p1, f"Victoire {n1}", couleur_prob(p1), c), use_container_width=True)
        with gj2:
            st.plotly_chart(fig_jauge(p_over15, "Over 1.5 buts", couleur_prob(p_over15), c), use_container_width=True)
        with gj3:
            st.plotly_chart(fig_jauge(pbtts, "Both Teams To Score", couleur_prob(pbtts), c), use_container_width=True)

        # ── Verdict Expert & Value ──
        st.markdown('<div class="section-title">🏆 Value Bets & Bankroll</div>', unsafe_allow_html=True)

        # Identification du favori 1N2
        if p1 > p2 and p1 > pn:   res, prob_f, coul_r = n1, p1, c["acc"]
        elif p2 > p1 and p2 > pn: res, prob_f, coul_r = n2, p2, c["danger"]
        else:                     res, prob_f, coul_r = "Match Nul", pn, c["warning"]
        
        cote_1n2 = round(1 / prob_f, 2) if prob_f > 0 else 99.0

        vd1, vd2, vd3 = st.columns(3)

        # Carte 1N2
        with vd1:
            badge_1n2 = f'<span class="badge-blue">👉 {res}</span>'
            st.markdown(
                verdict_card_html("🏆 Prono 1N2", f'<span style="color:{coul_r}">{res}</span>', prob_f, badge_1n2,
                                  f"Cote algo : {cote_1n2} · Score attendu : {score_h}–{score_a}"),
                unsafe_allow_html=True
            )
            c_bk1 = st.number_input("Cote proposée 1N2", 1.01, 30.0, float(cote_1n2), 0.05, key="k1")
            kelly_1 = kelly_criterion(prob_f, c_bk1)
            st.markdown(kelly_html(kelly_1, c_bk1 > cote_1n2 + SEUIL_VALUE), unsafe_allow_html=True)

        # Carte Over 1.5
        with vd2:
            cote_o = round(1 / p_over15, 2) if p_over15 > 0 else 9.99
            cote_u = round(1 / (1 - p_over15), 2) if p_over15 < 1 else 9.99
            label_o = "OVER 1.5" if p_over15 > SEUIL_OVER15 else "UNDER 1.5"
            badge_o = '<span class="badge-green">📈 OVER 1.5</span>' if p_over15 > SEUIL_OVER15 else '<span class="badge-red">📉 UNDER 1.5</span>'
            st.markdown(
                verdict_card_html("⚽ Marché des Buts", label_o, p_over15 if p_over15 > SEUIL_OVER15 else (1-p_over15), badge_o,
                                  f"Cote algo Over : {cote_o} · Under : {cote_u}"),
                unsafe_allow_html=True
            )
            c_bk_o = st.number_input("Cote proposée Over 1.5", 1.01, 10.0, float(cote_o) if p_over15 > SEUIL_OVER15 else 1.25, 0.05, key="k2")
            kelly_o = kelly_criterion(p_over15 if p_over15 > SEUIL_OVER15 else (1-p_over15), c_bk_o)
            st.markdown(kelly_html(kelly_o, c_bk_o > (cote_o if p_over15 > SEUIL_OVER15 else cote_u) + SEUIL_VALUE), unsafe_allow_html=True)

        # Carte BTTS
        with vd3:
            cote_b = round(1 / pbtts, 2) if pbtts > 0 else 9.99
            cote_nb = round(1 / (1 - pbtts), 2) if pbtts < 1 else 9.99
            label_b = "OUI" if pbtts > SEUIL_BTTS else "NON"
            badge_b = '<span class="badge-green">✅ BTTS OUI</span>' if pbtts > SEUIL_BTTS else '<span class="badge-red">❌ BTTS NON</span>'
            st.markdown(
                verdict_card_html("🎯 BTTS (Les 2 marquent)", label_b, pbtts if pbtts > SEUIL_BTTS else (1-pbtts), badge_b,
                                  f"Cote algo BTTS : {cote_b} - Non: {cote_nb}"),
                unsafe_allow_html=True
            )
            c_bk_b = st.number_input("Cote proposée BTTS", 1.01, 10.0, float(cote_b) if pbtts > SEUIL_BTTS else 1.85, 0.05, key="k3")
            kelly_b = kelly_criterion(pbtts if pbtts > SEUIL_BTTS else (1-pbtts), c_bk_b)
            st.markdown(kelly_html(kelly_b, c_bk_b > (cote_b if pbtts > SEUIL_BTTS else cote_nb) + SEUIL_VALUE), unsafe_allow_html=True)


def tab_classement(data_ligue: list):
    """Affiche le DataFrame du championnat sélectionné."""
    st.markdown('<div class="section-title">📊 Classement Actuel</div>', unsafe_allow_html=True)
    df = pd.DataFrame([{
        "Rang":   e.get("position", "?"),
        "Équipe": e["team"]["name"],
        "MJ":     e.get("playedGames", 0),
        "V":      e.get("won", 0),
        "N":      e.get("draw", 0),
        "D":      e.get("lost", 0),
        "Pts":    e.get("points", 0),
        "Buts +": e.get("goalsFor", 0),
        "Buts -": e.get("goalsAgainst", 0),
        "Diff":   e.get("goalsFor", 0) - e.get("goalsAgainst", 0),
        "Forme":  str(e.get("form", "") or "").replace(",", "")[-5:],
    } for e in data_ligue])
    
    st.dataframe(
        df, 
        use_container_width=True, 
        hide_index=True,
        column_config={"Diff": st.column_config.NumberColumn(format="%+d")}
    )


# ─── Logique principale ─────────────────────────
def main():
    choix_ligue, theme_clair = render_sidebar()
    c = get_couleurs(theme_clair)
    injecter_css(c)

    # Récupération au niveau de l'orchestrateur (Streamlit cache en natif)
    data_ligue = charger_classement(CHAMPIONNATS[choix_ligue])

    if not data_ligue:
        st.stop()  # L'erreur est gérée via le module core.api de manière propre

    moy_gf = moyenne_buts_ligue(data_ligue)

    # UI structure
    t1, t2 = st.tabs(["🎯 ANALYSE DU MATCH", "📊 TABLEAU DU CHAMPIONNAT"])

    with t1:
        tab_analyse(data_ligue, moy_gf, c)

    with t2:
        tab_classement(data_ligue)

    # ─── Footer ───
    st.divider()
    st.caption("🚀 PRO-FOOT AI V12.1 · Poisson Bivarié Normalisé · Kelly Criterion · Design Premium")


if __name__ == "__main__":
    main()
