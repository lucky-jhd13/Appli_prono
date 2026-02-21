# ─────────────────────────────────────────────
# core/scanner.py — Scanner de Value Bets
# ─────────────────────────────────────────────

from core.stats import extraire_stats
from core.moteur import (
    calculer_lambdas, matrice_scores,
    probabilites_depuis_matrice, score_le_plus_probable,
)
from config import SEUIL_BTTS, SEUIL_OVER25


def scanner_ligue(data_ligue: list, moy_gf: float, seuil_confiance: float = 0.55) -> list[dict]:
    """
    Scanne toutes les combinaisons domicile/extérieur d'une ligue.
    Retourne les matchs présentant une value bet potentielle,
    triés par confiance décroissante.
    """
    opportunites = []

    for e1 in data_ligue:
        for e2 in data_ligue:
            if e1["team"]["name"] == e2["team"]["name"]:
                continue

            s1 = extraire_stats(e1)
            s2 = extraire_stats(e2)

            l_h, l_a = calculer_lambdas(s1, s2, moy_gf, True, True, 7, 7)
            mat = matrice_scores(l_h, l_a)
            p1, pn, p2, pbtts, p_over25 = probabilites_depuis_matrice(mat)
            score_h, score_a, score_prob = score_le_plus_probable(mat)

            # Identifier le meilleur marché
            marches = []

            # 1N2
            if p1 > p2 and p1 > pn:
                cote_algo = round(1 / p1, 2) if p1 > 0 else 99
                marches.append({
                    "type": "1N2",
                    "label": f"Victoire {e1['team']['name']}",
                    "proba": p1,
                    "cote_algo": cote_algo,
                    "emoji": "🏠",
                })
            elif p2 > p1 and p2 > pn:
                cote_algo = round(1 / p2, 2) if p2 > 0 else 99
                marches.append({
                    "type": "1N2",
                    "label": f"Victoire {e2['team']['name']}",
                    "proba": p2,
                    "cote_algo": cote_algo,
                    "emoji": "✈️",
                })

            # Over 2.5
            if p_over25 > SEUIL_OVER25:
                cote_algo_o = round(1 / p_over25, 2) if p_over25 > 0 else 99
                marches.append({
                    "type": "Over 2.5",
                    "label": "Over 2.5 buts",
                    "proba": p_over25,
                    "cote_algo": cote_algo_o,
                    "emoji": "📈",
                })

            # BTTS
            if pbtts > SEUIL_BTTS:
                cote_algo_b = round(1 / pbtts, 2) if pbtts > 0 else 99
                marches.append({
                    "type": "BTTS",
                    "label": "BTTS Oui",
                    "proba": pbtts,
                    "cote_algo": cote_algo_b,
                    "emoji": "🎯",
                })

            # Garder le meilleur marché (proba la + haute)
            if marches:
                meilleur = max(marches, key=lambda m: m["proba"])
                if meilleur["proba"] >= seuil_confiance:
                    opportunites.append({
                        "equipe_dom": e1["team"]["name"],
                        "equipe_ext": e2["team"]["name"],
                        "logo_dom": e1["team"].get("crest", ""),
                        "logo_ext": e2["team"].get("crest", ""),
                        "rang_dom": e1["position"],
                        "rang_ext": e2["position"],
                        "p1": p1, "pn": pn, "p2": p2,
                        "p_over25": p_over25,
                        "p_btts": pbtts,
                        "score_h": score_h,
                        "score_a": score_a,
                        "score_prob": score_prob,
                        "meilleur_pari": meilleur,
                        "tous_marches": marches,
                    })

    # Trier par confiance du meilleur pari
    opportunites.sort(key=lambda x: x["meilleur_pari"]["proba"], reverse=True)
    return opportunites
