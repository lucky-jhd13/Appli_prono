# ─────────────────────────────────────────────
# core/historique.py — Suivi des Performances
# ─────────────────────────────────────────────

import json
import os
from datetime import datetime

FICHIER_HISTORIQUE = "historique_pronos.json"


def charger_historique() -> list[dict]:
    """Charge l'historique des pronos depuis le fichier JSON."""
    if not os.path.exists(FICHIER_HISTORIQUE):
        return []
    try:
        with open(FICHIER_HISTORIQUE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def sauvegarder_historique(historique: list[dict]):
    """Sauvegarde l'historique complet dans le fichier JSON."""
    with open(FICHIER_HISTORIQUE, "w", encoding="utf-8") as f:
        json.dump(historique, f, ensure_ascii=False, indent=2)


def ajouter_prono(
    ligue: str,
    equipe_dom: str,
    equipe_ext: str,
    type_pari: str,
    label_pari: str,
    proba: float,
    cote_algo: float,
    cote_bookmaker: float,
    kelly: float,
    bankroll: float,
):
    """Ajoute un nouveau pronostic à l'historique."""
    historique = charger_historique()
    prono = {
        "id": len(historique) + 1,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ligue": ligue,
        "equipe_dom": equipe_dom,
        "equipe_ext": equipe_ext,
        "type_pari": type_pari,
        "label_pari": label_pari,
        "proba": round(proba, 4),
        "cote_algo": round(cote_algo, 2),
        "cote_bookmaker": round(cote_bookmaker, 2),
        "kelly_pct": round(kelly * 100, 1),
        "mise_euros": round(kelly * bankroll, 2),
        "bankroll_moment": round(bankroll, 2),
        "resultat": None,  # None = en attente, True = gagné, False = perdu
    }
    historique.append(prono)
    sauvegarder_historique(historique)
    return prono


def mettre_a_jour_resultat(prono_id: int, gagne: bool):
    """Met à jour le résultat d'un pronostic (gagné/perdu)."""
    historique = charger_historique()
    for p in historique:
        if p["id"] == prono_id:
            p["resultat"] = gagne
            break
    sauvegarder_historique(historique)


def stats_performances(historique: list[dict]) -> dict:
    """Calcule les statistiques de performance globales."""
    total = len(historique)
    resolus = [p for p in historique if p["resultat"] is not None]
    en_attente = total - len(resolus)
    gagnes = sum(1 for p in resolus if p["resultat"] is True)
    perdus = sum(1 for p in resolus if p["resultat"] is False)

    taux_reussite = (gagnes / len(resolus) * 100) if resolus else 0

    # Calcul du ROI
    total_mise = 0
    total_gains = 0
    for p in resolus:
        mise = p.get("mise_euros", 0)
        total_mise += mise
        if p["resultat"]:
            total_gains += mise * p.get("cote_bookmaker", 1)

    roi = ((total_gains - total_mise) / total_mise * 100) if total_mise > 0 else 0
    profit = total_gains - total_mise

    # Évolution du capital
    evolution = []
    capital = 1000  # Capital de départ par défaut
    for p in resolus:
        mise = p.get("mise_euros", 0)
        if p["resultat"]:
            capital += mise * (p.get("cote_bookmaker", 1) - 1)
        else:
            capital -= mise
        evolution.append({
            "date": p["date"],
            "capital": round(capital, 2),
            "match": f"{p['equipe_dom']} vs {p['equipe_ext']}",
        })

    return {
        "total": total,
        "en_attente": en_attente,
        "gagnes": gagnes,
        "perdus": perdus,
        "taux_reussite": round(taux_reussite, 1),
        "roi": round(roi, 1),
        "profit": round(profit, 2),
        "evolution": evolution,
    }
