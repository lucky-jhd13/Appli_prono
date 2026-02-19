# ─────────────────────────────────────────────
# core/moteur.py — Moteur Poisson Bivarié Normalisé + Kelly
# ─────────────────────────────────────────────

import math
from config import (
    MAX_BUTS_MATRICE,
    DOM_BONUS_BASE, DOM_BONUS_MAX,
    FORME_MIN, FORME_RANGE,
    BUTEUR_ABSENT_MULT, REPOS_ELEVE_MULT, REPOS_FAIBLE_MULT,
)


# ── Loi de Poisson ────────────────────────────
def poisson(lam: float, k: int) -> float:
    if lam <= 0:
        return 0.0
    return (math.pow(lam, k) * math.exp(-lam)) / math.factorial(k)


# ── Matrice des scores ─────────────────────────
def matrice_scores(l_h: float, l_a: float, n: int = MAX_BUTS_MATRICE) -> list[list[float]]:
    """Retourne une matrice n×n de probabilités P(score_h, score_a)."""
    return [
        [poisson(l_h, h) * poisson(l_a, a) for a in range(n)]
        for h in range(n)
    ]


# ── Probabilités depuis la matrice ────────────
def probabilites_depuis_matrice(mat: list[list[float]]) -> tuple:
    """
    Retourne (p1, pn, p2, pbtts, p_over25) depuis la matrice des scores.
    """
    p1 = pn = p2 = pbtts = p_over25 = 0.0
    for h, row in enumerate(mat):
        for a, p in enumerate(row):
            if h > a:   p1 += p
            elif h == a: pn += p
            else:        p2 += p
            if h > 0 and a > 0:   pbtts   += p
            if h + a >= 3:        p_over25 += p
    return p1, pn, p2, pbtts, p_over25


# ── Score le plus probable ─────────────────────
def score_le_plus_probable(mat: list[list[float]]) -> tuple:
    """Retourne (buts_h, buts_a, probabilité) du score le plus probable."""
    best_p = best_h = best_a = 0
    for h, row in enumerate(mat):
        for a, p in enumerate(row):
            if p > best_p:
                best_p, best_h, best_a = p, h, a
    return best_h, best_a, best_p


# ── Calcul des lambdas normalisés ─────────────
def calculer_lambdas(
    s1: dict, s2: dict,
    moy_gf_ligue: float,
    but1: bool, but2: bool,
    repos1: int, repos2: int,
) -> tuple[float, float]:
    """
    Modèle de Poisson normalisé par la moyenne du championnat.

    force_att = mbp / moy_ligue
    force_def = mbc / moy_ligue
    lambda_h  = force_att_1 × force_def_2 × moy_ligue × bonus_dom × correctifs
    lambda_a  = force_att_2 × force_def_1 × moy_ligue × correctifs
    """
    moy = moy_gf_ligue if moy_gf_ligue > 0 else 1.3

    fa1 = s1["mbp"] / moy
    fd1 = s1["mbc"] / moy
    fa2 = s2["mbp"] / moy
    fd2 = s2["mbc"] / moy

    # Avantage domicile dynamique selon perfs réelles
    dom_bonus = DOM_BONUS_BASE + (s1["pts_par_match"] / 3) * DOM_BONUS_MAX

    # Modificateur forme (±FORME_RANGE)
    fm1 = FORME_MIN + (s1["forme_pct"] / 100) * FORME_RANGE
    fm2 = FORME_MIN + (s2["forme_pct"] / 100) * FORME_RANGE

    # Modificateurs buteur
    bm1 = 1.0 if but1 else BUTEUR_ABSENT_MULT
    bm2 = 1.0 if but2 else BUTEUR_ABSENT_MULT

    # Modificateurs repos
    rm1 = REPOS_ELEVE_MULT if repos1 >= 5 else (REPOS_FAIBLE_MULT if repos1 <= 2 else 1.0)
    rm2 = REPOS_ELEVE_MULT if repos2 >= 5 else (REPOS_FAIBLE_MULT if repos2 <= 2 else 1.0)

    l_h = fa1 * fd2 * moy * dom_bonus * fm1 * bm1 * rm1
    l_a = fa2 * fd1 * moy * fm2 * bm2 * rm2

    return round(max(l_h, 0.1), 3), round(max(l_a, 0.1), 3)


# ── Kelly Criterion ────────────────────────────
def kelly_criterion(prob: float, cote: float) -> float:
    """
    Fraction de mise optimale (Kelly).
    f* = (b·p - q) / b   où b = cote - 1, q = 1 - p
    Retourne 0 si négatif (pas de value).
    """
    if cote <= 1 or prob <= 0:
        return 0.0
    b = cote - 1
    f = (b * prob - (1 - prob)) / b
    return max(f, 0.0)
