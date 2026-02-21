# ─────────────────────────────────────────────
# app.py — Point d'entrée principal (orchestrateur)
# Lance avec : streamlit run app.py
# ─────────────────────────────────────────────

import streamlit as st
import pandas as pd
import base64
from PIL import Image
from datetime import datetime

from config import CHAMPIONNATS, CHAMPIONNATS_META, SEUIL_BTTS, SEUIL_OVER25, SEUIL_VALUE
from core.api       import charger_classement, moyenne_buts_ligue, charger_prochains_matchs
from core.stats     import extraire_stats
from core.moteur    import (
    calculer_lambdas, matrice_scores,
    probabilites_depuis_matrice, score_le_plus_probable,
    kelly_criterion, poisson,
)
from core.scanner    import scanner_ligue
from core.historique import (
    charger_historique, ajouter_prono, mettre_a_jour_resultat, stats_performances,
)
from core.export_pdf import generer_pdf_analyse
from ui.theme      import get_couleurs, injecter_css
from ui.composants import (
    match_header_html, stat_grid_html,
    verdict_card_html, kelly_html, couleur_prob, opportunite_card_html,
)
from ui.graphiques import fig_radar, fig_barres, fig_heatmap, fig_jauge, fig_evolution_capital


# ─── Config page ────────────────────────────────
def get_base64_img(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

icon_b64 = get_base64_img("prono-foot.jpg")
img_icon  = Image.open("prono-foot.jpg")

st.set_page_config(page_title="PronoFoot", page_icon=img_icon, layout="wide")

# ─── Session state ──────────────────────────────
if "theme_toggle" not in st.session_state:
    st.session_state.theme_toggle = (st.query_params.get("theme", "white") == "dark")
if "bankroll" not in st.session_state:
    st.session_state.bankroll = 1000.0
if "panier" not in st.session_state:
    st.session_state.panier = []
if "ligue_active" not in st.session_state:
    st.session_state.ligue_active = list(CHAMPIONNATS.keys())[0]

def update_theme():
    current_q = st.query_params.get("theme", "white")
    new_q = "dark" if st.session_state.theme_toggle else "white"
    if current_q != new_q:
        st.query_params["theme"] = new_q

# ─── Thème & CSS ────────────────────────────────
c = get_couleurs(not st.session_state.theme_toggle)
injecter_css(c)

# ─── Header ─────────────────────────────────────
ligues = list(CHAMPIONNATS.keys())

st.markdown(f"""
<div class="pronofoot-header">
    <div class="header-inner">
        <div class="header-brand">
            <img src="data:image/jpg;base64,{icon_b64}" class="header-logo" alt="PronoFoot">
            <div>
                <div class="header-title">PronoFoot</div>
                <div class="header-subtitle">Analyse · Prédictions · Value Bets</div>
            </div>
        </div>
        <div class="theme-control" id="theme-placeholder"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Toggle thème — visible sur toutes les tailles
st.toggle("🌙 Mode sombre", key="theme_toggle", on_change=update_theme)

# ─── Sélecteur de ligues (boutons natifs Streamlit) ───
league_cols = st.columns(len(ligues), gap="small")
for i, ligue in enumerate(ligues):
    meta = CHAMPIONNATS_META[ligue]
    with league_cols[i]:
        label = f"{meta['flag']} {ligue.split(' ', 1)[1]}"
        btn_type = "primary" if ligue == st.session_state.ligue_active else "secondary"
        if st.button(label, key=f"league_{ligue}", use_container_width=True, type=btn_type):
            st.session_state.ligue_active = ligue
            st.query_params["ligue"] = CHAMPIONNATS[ligue]
            st.rerun()

# ─── Synchroniser la ligue depuis query params ───
qp_ligue = st.query_params.get("ligue", "")
ligue_from_code = {v: k for k, v in CHAMPIONNATS.items()}
if qp_ligue in ligue_from_code:
    st.session_state.ligue_active = ligue_from_code[qp_ligue]

choix_ligue = st.session_state.ligue_active
meta_ligue  = CHAMPIONNATS_META[choix_ligue]

# Indicateur de la ligue active
st.markdown(f"""
<div style="display:flex; align-items:center; gap:10px; margin-bottom:20px; padding: 10px 16px;
     background:{c['card']}; border:1px solid {c['brd']}; border-radius:12px; width:fit-content;">
    <span style="font-size:1.8rem">{meta_ligue['flag']}</span>
    <div>
        <div style="font-family:'Rajdhani',sans-serif; font-size:1.1rem; font-weight:700; color:{c['txt']};">{choix_ligue.split(' ', 1)[1]}</div>
        <div style="font-size:0.7rem; opacity:0.5; text-transform:uppercase; letter-spacing:1px;">{meta_ligue['country']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Chargement données ─────────────────────────
data_ligue = charger_classement(CHAMPIONNATS[choix_ligue])

if not data_ligue:
    st.error("⚠️ Impossible de récupérer les données. Vérifie ta clé API ou ton quota.")
    st.stop()

moy_gf = moyenne_buts_ligue(data_ligue)

# ─── Tabs ───────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 ANALYSE", "📊 CLASSEMENT", "🔍 OPPORTUNITÉS",
    "📅 MATCHS", "🎰 COMBINÉ", "📈 PERFORMANCES"
])

# ════════════════════════════════════════════════
# TAB 1 — ANALYSE
# ════════════════════════════════════════════════
with tab1:
    equipes = sorted([e["team"]["name"] for e in data_ligue])
    col_sel1, col_sel2 = st.columns(2, gap="small")
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
    aj1, aj2 = st.columns(2, gap="small")
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
    cs1, cs2 = st.columns(2, gap="small")
    with cs1:
        st.markdown(f"**🏠 {n1}** — Rang #{e1['position']}")
        st.markdown(stat_grid_html(s1, l_h, c["acc"]), unsafe_allow_html=True)
    with cs2:
        st.markdown(f"**✈️ {n2}** — Rang #{e2['position']}")
        st.markdown(stat_grid_html(s2, l_a, "#ef4444"), unsafe_allow_html=True)

    # ── Graphiques ───────────────────────────────
    st.markdown('<div class="section-title">📊 Visualisations</div>', unsafe_allow_html=True)
    gc1, gc2 = st.columns(2, gap="small")
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
    gj1, gj2, gj3 = st.columns(3, gap="small")
    with gj1:
        st.plotly_chart(fig_jauge(p1, f"Victoire {n1}", couleur_prob(p1), c), use_container_width=True)
    with gj2:
        st.plotly_chart(fig_jauge(p_over25, "Over 2.5 buts", couleur_prob(p_over25), c), use_container_width=True)
    with gj3:
        st.plotly_chart(fig_jauge(pbtts, "BTTS", couleur_prob(pbtts), c), use_container_width=True)

    # ── Verdict expert ───────────────────────────
    st.markdown('<div class="section-title">🏆 Verdict Expert & Value Bets</div>', unsafe_allow_html=True)

    bk_col1, _, _ = st.columns([1, 1, 1], gap="small")
    with bk_col1:
        bankroll = st.number_input("💰 Capital (€)", 10.0, 100000.0, st.session_state.bankroll, 50.0, key="bankroll_input")
        st.session_state.bankroll = bankroll

    if p1 > p2 and p1 > pn:     res, prob_f, coul_r = n1,           p1, "#3b82f6"
    elif p2 > p1 and p2 > pn:   res, prob_f, coul_r = n2,           p2, "#ef4444"
    else:                         res, prob_f, coul_r = "Match Nul", pn, "#fbbf24"
    cote_1n2 = round(1 / prob_f, 2) if prob_f > 0 else 99.0

    vd1, vd2, vd3 = st.columns(3, gap="small")

    # 1N2
    with vd1:
        badge_1n2 = f'<span class="badge-blue">👉 {res}</span>'
        st.markdown(
            verdict_card_html("🏆 Prono 1N2", f'<span style="color:{coul_r}">{res}</span>', prob_f, badge_1n2,
                              f"Cote algo : {cote_1n2} · Score probable : {score_h}–{score_a}"),
            unsafe_allow_html=True
        )
        c_bk1   = st.number_input("Cote book. 1N2", 1.01, 30.0, float(cote_1n2), 0.05, key="k1")
        kelly_1 = kelly_criterion(prob_f, c_bk1)
        st.markdown(kelly_html(kelly_1, c_bk1 > cote_1n2 + SEUIL_VALUE, bankroll), unsafe_allow_html=True)

    # Over/Under
    with vd2:
        cote_o  = round(1 / p_over25, 2) if p_over25 > 0 else 9.99
        cote_u  = round(1 / (1 - p_over25), 2) if p_over25 < 1 else 9.99
        label_o = "OVER 2.5" if p_over25 > SEUIL_OVER25 else "UNDER 2.5"
        badge_o = '<span class="badge-green">📈 OVER 2.5</span>' if p_over25 > SEUIL_OVER25 else '<span class="badge-red">📉 UNDER 2.5</span>'
        st.markdown(
            verdict_card_html("⚽ Buts Over/Under", label_o, p_over25, badge_o,
                              f"Cote algo Over : {cote_o} · Under : {cote_u}"),
            unsafe_allow_html=True
        )
        c_bk_o  = st.number_input("Cote book. Over", 1.01, 10.0, 1.90, 0.05, key="k2")
        kelly_o = kelly_criterion(p_over25, c_bk_o)
        st.markdown(kelly_html(kelly_o, c_bk_o > cote_o + SEUIL_VALUE, bankroll), unsafe_allow_html=True)

    # BTTS
    with vd3:
        cote_b  = round(1 / pbtts, 2) if pbtts > 0 else 9.99
        label_b = "OUI" if pbtts > SEUIL_BTTS else "NON"
        badge_b = '<span class="badge-green">✅ BTTS OUI</span>' if pbtts > SEUIL_BTTS else '<span class="badge-red">❌ BTTS NON</span>'
        st.markdown(
            verdict_card_html("🎯 BTTS (2 marquent)", label_b, pbtts, badge_b,
                              f"Cote algo BTTS : {cote_b}"),
            unsafe_allow_html=True
        )
        c_bk_b  = st.number_input("Cote book. BTTS", 1.01, 10.0, 1.85, 0.05, key="k3")
        kelly_b = kelly_criterion(pbtts, c_bk_b)
        st.markdown(kelly_html(kelly_b, c_bk_b > cote_b + SEUIL_VALUE, bankroll), unsafe_allow_html=True)

    # ── Sauvegarder pronos ────────────────────────
    sv1, sv2, sv3 = st.columns(3, gap="small")
    with sv1:
        if kelly_1 > 0 and st.button("💾 Save 1N2", key="save_1n2", use_container_width=True):
            ajouter_prono(choix_ligue, n1, n2, "1N2", res, prob_f, cote_1n2, c_bk1, kelly_1, bankroll)
            st.success("✅ Enregistré !")
    with sv2:
        if kelly_o > 0 and st.button("💾 Save Over", key="save_over", use_container_width=True):
            ajouter_prono(choix_ligue, n1, n2, "Over 2.5", label_o, p_over25, cote_o, c_bk_o, kelly_o, bankroll)
            st.success("✅ Enregistré !")
    with sv3:
        if kelly_b > 0 and st.button("💾 Save BTTS", key="save_btts", use_container_width=True):
            ajouter_prono(choix_ligue, n1, n2, "BTTS", f"BTTS {label_b}", pbtts, cote_b, c_bk_b, kelly_b, bankroll)
            st.success("✅ Enregistré !")

    # ── Actions rapides ────────────────────────────
    st.markdown("---")
    ac1, ac2, ac3, ac4 = st.columns(4, gap="small")
    with ac1:
        if st.button(f"🎰 {res} @ {c_bk1}", key="combo_1n2", use_container_width=True):
            st.session_state.panier.append({"match": f"{n1} vs {n2}", "pari": res, "cote": c_bk1, "proba": prob_f})
            st.success("Ajouté !")
    with ac2:
        if st.button(f"🎰 {label_o} @ {c_bk_o}", key="combo_over", use_container_width=True):
            st.session_state.panier.append({"match": f"{n1} vs {n2}", "pari": label_o, "cote": c_bk_o, "proba": p_over25})
            st.success("Ajouté !")
    with ac3:
        if st.button(f"🎰 BTTS {label_b} @ {c_bk_b}", key="combo_btts", use_container_width=True):
            st.session_state.panier.append({"match": f"{n1} vs {n2}", "pari": f"BTTS {label_b}", "cote": c_bk_b, "proba": pbtts})
            st.success("Ajouté !")
    with ac4:
        pdf_bytes = generer_pdf_analyse(
            n1, n2, choix_ligue, p1, pn, p2, p_over25, pbtts,
            score_h, score_a, kelly_1, kelly_o, kelly_b,
            c_bk1, c_bk_o, c_bk_b, bankroll, SEUIL_VALUE, res,
        )
        st.download_button(
            "📄 Export PDF",
            data=pdf_bytes,
            file_name=f"PronoFoot_{n1}_vs_{n2}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

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

# ════════════════════════════════════════════════
# TAB 3 — OPPORTUNITÉS (SCANNER)
# ════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">🔍 Scanner de Value Bets</div>', unsafe_allow_html=True)
    st.caption("Scan automatique de toutes les combinaisons dom/ext du championnat sélectionné.")

    seuil_slider = st.slider("Seuil de confiance minimum", 0.45, 0.80, 0.55, 0.05, key="seuil_opp")

    with st.spinner("Scan en cours..."):
        opps = scanner_ligue(data_ligue, moy_gf, seuil_slider)

    if not opps:
        st.info("Aucune opportunité détectée au-dessus du seuil. Essaye de baisser le curseur.")
    else:
        st.markdown(f"**{len(opps)} opportunité(s)** détectée(s) au-dessus de {seuil_slider*100:.0f}% de confiance")
        for opp in opps[:30]:
            st.markdown(opportunite_card_html(opp), unsafe_allow_html=True)
            m = opp["meilleur_pari"]
            if st.button(
                f"🎰 Ajouter · {m['label']} @ {m['cote_algo']}",
                key=f"combo_opp_{opp['equipe_dom']}_{opp['equipe_ext']}",
                use_container_width=True,
            ):
                st.session_state.panier.append({
                    "match": f"{opp['equipe_dom']} vs {opp['equipe_ext']}",
                    "pari": m["label"], "cote": m["cote_algo"], "proba": m["proba"],
                })
                st.success("✅ Ajouté au combiné !")

# ════════════════════════════════════════════════
# TAB 4 — PROCHAINS MATCHS
# ════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">📅 Prochains Matchs</div>', unsafe_allow_html=True)

    matchs = charger_prochains_matchs(CHAMPIONNATS[choix_ligue])

    if not matchs:
        st.info("Aucun match planifié trouvé pour cette ligue.")
    else:
        for m in matchs:
            home     = m.get("homeTeam", {})
            away     = m.get("awayTeam", {})
            date_str = m.get("utcDate", "")[:16].replace("T", " à ")
            logo_h   = home.get("crest", "")
            logo_a   = away.get("crest", "")
            name_h   = home.get("name", "?")
            name_a   = away.get("name", "?")

            st.markdown(f"""
            <div class="opp-card">
                <div class="opp-header">
                    <div class="opp-teams">
                        <img src="{logo_h}" class="opp-logo" onerror="this.style.display='none'">
                        <span class="opp-team-name">{name_h}</span>
                        <span class="opp-vs">vs</span>
                        <span class="opp-team-name">{name_a}</span>
                        <img src="{logo_a}" class="opp-logo" onerror="this.style.display='none'">
                    </div>
                    <div style="font-size:0.8rem; opacity:0.6;">📅 {date_str} UTC</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════
# TAB 5 — COMBINÉ
# ════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">🎰 Combiné / Accumulateur</div>', unsafe_allow_html=True)

    panier = st.session_state.panier

    if not panier:
        st.info("Ton combiné est vide. Ajoute des paris depuis l'onglet Analyse ou Opportunités.")
    else:
        cote_combo  = round(1.0 * (c_prod := 1.0) or 1.0, 2)  # recalcul ci-dessous
        cote_combo  = round(1.0, 2)
        proba_combo = 1.0
        for p in panier:
            cote_combo  *= p["cote"]
            proba_combo *= p["proba"]
        cote_combo = round(cote_combo, 2)

        bankroll_combo = st.session_state.bankroll
        kelly_combo    = kelly_criterion(proba_combo, cote_combo)
        mise_kelly     = round(kelly_combo * bankroll_combo, 2) if kelly_combo > 0 else 0.0

        st.markdown(f"""
        <div class="perf-grid">
            <div class="perf-stat">
                <span class="perf-stat-value" style="color:{c['acc']}">{len(panier)}</span>
                <span class="perf-stat-label">Sélections</span>
            </div>
            <div class="perf-stat">
                <span class="perf-stat-value" style="color:#fbbf24">{cote_combo}</span>
                <span class="perf-stat-label">Cote totale</span>
            </div>
            <div class="perf-stat">
                <span class="perf-stat-value" style="color:#4ade80">{proba_combo*100:.1f}%</span>
                <span class="perf-stat-label">Probabilité</span>
            </div>
            <div class="perf-stat">
                <span class="perf-stat-value" style="color:{c['acc']}">{mise_kelly}€</span>
                <span class="perf-stat-label">Mise Kelly</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">📊 Jauge de confiance</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_jauge(proba_combo, "Probabilité combiné", c["acc"], c), use_container_width=True)

        st.markdown('<div class="section-title">💶 Mise personnalisée</div>', unsafe_allow_html=True)
        col_mise, col_gain = st.columns(2, gap="small")
        with col_mise:
            mise_defaut = min(mise_kelly if mise_kelly > 0 else 5.0, bankroll_combo)
            mise_perso  = st.number_input("Ta mise (€)", 0.50, float(bankroll_combo), mise_defaut, 0.50, key="mise_combo")
        with col_gain:
            gain       = round(mise_perso * cote_combo, 2)
            profit_net = round(gain - mise_perso, 2)
            st.markdown(f"""
            <div class="bankroll-box" style="margin-top:8px;">
                <div class="bankroll-value">💰 Gain : {gain}€</div>
                <span style="font-size:0.85rem;color:#4ade80;">Profit net : +{profit_net}€</span><br>
                <span style="font-size:0.75rem;opacity:0.5;">Mise {mise_perso}€ × cote {cote_combo}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">📋 Détail du combiné</div>', unsafe_allow_html=True)
        for i, p in enumerate(panier):
            col_detail, col_del = st.columns([5, 1], gap="small")
            with col_detail:
                st.markdown(f"""
                <div class="opp-card">
                    <div class="opp-body">
                        <span class="badge-blue">{p['pari']}</span>
                        <span style="font-size:0.85rem; margin-left:12px;">{p['match']}</span>
                        <span style="font-size:0.8rem; opacity:0.6; margin-left:auto;">@ {p['cote']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_del:
                if st.button("🗑️", key=f"del_combo_{i}"):
                    st.session_state.panier.pop(i)
                    st.rerun()

        if st.button("🗑️ Vider le combiné", key="clear_combo", use_container_width=True):
            st.session_state.panier = []
            st.rerun()

# ════════════════════════════════════════════════
# TAB 6 — PERFORMANCES
# ════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="section-title">📈 Suivi des Performances</div>', unsafe_allow_html=True)

    historique = charger_historique()
    perf       = stats_performances(historique)

    st.markdown(f"""
    <div class="perf-grid">
        <div class="perf-stat">
            <span class="perf-stat-value" style="color:{c['acc']}">{perf['total']}</span>
            <span class="perf-stat-label">Total pronos</span>
        </div>
        <div class="perf-stat">
            <span class="perf-stat-value" style="color:#4ade80">{perf['taux_reussite']}%</span>
            <span class="perf-stat-label">Taux réussite</span>
        </div>
        <div class="perf-stat">
            <span class="perf-stat-value" style="color:{'#4ade80' if perf['roi'] >= 0 else '#f87171'}">{perf['roi']:+.1f}%</span>
            <span class="perf-stat-label">ROI</span>
        </div>
        <div class="perf-stat">
            <span class="perf-stat-value" style="color:{'#4ade80' if perf['profit'] >= 0 else '#f87171'}">{perf['profit']:+.2f}€</span>
            <span class="perf-stat-label">Profit / Perte</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">📊 Évolution du Capital</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_evolution_capital(perf["evolution"], c), use_container_width=True)

    st.markdown('<div class="section-title">📋 Historique des Pronos</div>', unsafe_allow_html=True)

    if not historique:
        st.info("Aucun pronostic enregistré. Va dans l'onglet Analyse pour sauvegarder un prono.")
    else:
        for p in reversed(historique):
            statut_emoji = "⏳" if p["resultat"] is None else ("✅" if p["resultat"] else "❌")
            statut_txt   = "En attente" if p["resultat"] is None else ("Gagné" if p["resultat"] else "Perdu")

            with st.expander(f"{statut_emoji} {p['date']} — {p['equipe_dom']} vs {p['equipe_ext']} ({p['type_pari']})"):
                col_info, col_action = st.columns([3, 1])
                with col_info:
                    st.markdown(f"""
                    **Pari :** {p['label_pari']}  
                    **Probabilité :** {p['proba']*100:.1f}%  
                    **Cote algo :** {p['cote_algo']} · **Cote bookmaker :** {p['cote_bookmaker']}  
                    **Kelly :** {p['kelly_pct']}% · **Mise :** {p['mise_euros']}€  
                    **Statut :** {statut_txt}
                    """)
                with col_action:
                    if p["resultat"] is None:
                        if st.button("✅ Gagné", key=f"win_{p['id']}"):
                            mettre_a_jour_resultat(p["id"], True)
                            st.rerun()
                        if st.button("❌ Perdu", key=f"lose_{p['id']}"):
                            mettre_a_jour_resultat(p["id"], False)
                            st.rerun()

# ─── Footer ─────────────────────────────────────
st.divider()
st.caption(f"PronoFoot · football-data.org · {meta_ligue['flag']} {choix_ligue.split(' ', 1)[1]}")
