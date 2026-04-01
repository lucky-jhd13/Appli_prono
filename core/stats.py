# ─────────────────────────────────────────────
# core/stats.py — Extraction & traitement des stats avancées
# ─────────────────────────────────────────────

from typing import TypedDict, List, Any, Dict

class StatsEquipe(TypedDict):
    """
    Spécification stricte des données collectées pour un club.
    Garantit la présence de certains clés pour le modèle.
    """
    pj: int
    gf: int
    ga: int
    pts: int
    won: int
    draw: int
    lost: int
    mbp: float
    mbc: float
    pts_par_match: float
    form: str
    pts_forme: int
    forme_pct: float
    diff: int
    radar: List[int]


def extraire_stats(equipe_data: Dict[str, Any]) -> StatsEquipe:
    """
    Récupère, nettoie et calcule toutes les statistiques nécessaires
    pour une équipe, récupérée depuis l'API.

    Génère également les notations (0-100) pour le diagramme Radar.
    """
    # ── Extraction et gestion stricte des cas None ──
    pj   = equipe_data.get("playedGames") or 1
    gf   = int(equipe_data.get("goalsFor", 0) or 0)
    ga   = int(equipe_data.get("goalsAgainst", 0) or 0)
    pts  = int(equipe_data.get("points", 0) or 0)
    won  = int(equipe_data.get("won", 0) or 0)
    draw = int(equipe_data.get("draw", 0) or 0)
    lost = int(equipe_data.get("lost", 0) or 0)

    # ── Calculs primaires moyennes ──
    mbp = float(gf / pj)
    mbc = float(ga / pj)
    pts_par_match = float(pts / pj)

    # ── Calcul de la forme récente (5 matchs min/max) ──
    form_raw = str(equipe_data.get("form") or "").replace(",", "").replace(" ", "").upper()
    form_raw = form_raw[-5:]  # Prendre les 5 derniers résultats max

    pts_forme = 0
    for c in form_raw:
        if c == "W": pts_forme += 3
        elif c == "D": pts_forme += 1
        # Les défaites ou L valent 0

    # Un club avec 5 victoires de suite a 15 points (100% de forme)
    forme_pct = (pts_forme / 15.0) * 100 if len(form_raw) >= 1 else 50.0

    # ── Scores du graphique Radar (Normalisés sur 100) ──
    # Plus de 2.2 buts par match = max attaque (2.22*45 ≈ 100)
    att_score  = min(mbp * 45.0, 100.0)
    # Plus de 2 buts encaissés = 0 défense (100 - 2.0*50)
    def_score  = max(100.0 - mbc * 50.0, 0.0)
    # Pourcentage de victoires direct
    vic_score  = (won / pj) * 100.0 if pj > 0 else 0.0
    # Consistance (3 points / match => score de 100)
    const_score = (pts_par_match / 3.0) * 100.0

    return {
        "pj":           pj,
        "gf":           gf,
        "ga":           ga,
        "pts":          pts,
        "won":          won,
        "draw":         draw,
        "lost":         lost,
        "mbp":          mbp,
        "mbc":          mbc,
        "pts_par_match": pts_par_match,
        "form":         form_raw,
        "pts_forme":    pts_forme,
        "forme_pct":    forme_pct,
        "diff":         gf - ga,
        "radar":        [int(att_score), int(def_score), int(vic_score), int(const_score)],
    }
