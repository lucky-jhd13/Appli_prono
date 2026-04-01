# ─────────────────────────────────────────────
# core/moteur.py — Algorithme de prédiction (Poisson & Kelly)
# ─────────────────────────────────────────────

import math
from typing import Tuple, List
from config import (
    MAX_BUTS_MATRICE,
    DOM_BONUS_BASE, DOM_BONUS_MAX,
    FORME_MIN, FORME_RANGE,
    BUTEUR_ABSENT_MULT, REPOS_ELEVE_MULT, REPOS_FAIBLE_MULT,
)
from core.stats import StatsEquipe


# ── Modèle Bivarié ────────────────────────────
def poisson(lam: float, k: int) -> float:
    """Distribue une probabilité Poissonienne (e^-λ * λ^k / k!)."""
    if lam <= 0:
        return 0.0
    return (math.pow(lam, k) * math.exp(-lam)) / math.factorial(k)


def matrice_scores(l_h: float, l_a: float, n: int = MAX_BUTS_MATRICE) -> List[List[float]]:
    """Génère la matrice carrée N×N des probabilités croisées."""
    return [
        [poisson(l_h, h) * poisson(l_a, a) for a in range(n)]
        for h in range(n)
    ]


# ── Agrégation probabiliste ───────────────────
def probabilites_depuis_matrice(mat: List[List[float]]) -> Tuple[float, float, float, float, float]:
    """
    Parcourt la matrice O(n²) pour extraire les différentes issues.
    Retourne : (P(1), P(N), P(2), P(BTTS OUI), P(Over 1.5))
    """
    p1 = pn = p2 = pbtts = p_over15 = 0.0
    
    for h, row in enumerate(mat):
        for a, p in enumerate(row):
            # Issues 1N2
            if h > a:
                p1 += p
            elif h == a:
                pn += p
            else:
                p2 += p
                
            # Both Teams To Score (BTTS)
            if h > 0 and a > 0:
                pbtts += p
                
            # Over 1.5 total buts (Score minimal : 2 buts cumulés)
            if h + a >= 2:
                p_over15 += p
                
    return p1, pn, p2, pbtts, p_over15


def score_le_plus_probable(mat: List[List[float]]) -> Tuple[int, int, float]:
    """Extrait le pic de probabilité dans la grille (Buts_Home, Buts_Away, Prob)."""
    best_p = 0.0
    best_h = best_a = 0
    
    for h, row in enumerate(mat):
        for a, p in enumerate(row):
            if p > best_p:
                best_p, best_h, best_a = p, h, a
                
    return best_h, best_a, best_p


# ── Espérance Mathématique (Lambdas) ──────────
def calculer_lambdas(
    s1: StatsEquipe, 
    s2: StatsEquipe,
    moy_gf_ligue: float,
    but1: bool, 
    but2: bool,
    repos1: int, 
    repos2: int,
) -> Tuple[float, float]:
    """
    La clé de voûte de l'algorithme : ajuster les Expected Goals (xG).
    Utilise la pondération dynamique du domicile, contexte et forme des 5 dernières semaines.
    """
    # Moyenne de sécurité
    moy = float(moy_gf_ligue) if moy_gf_ligue > 0 else 1.3

    # Force Attaque / Défense théorique vs Moyenne Ligue
    fa1 = s1["mbp"] / moy
    fd1 = s1["mbc"] / moy
    fa2 = s2["mbp"] / moy
    fd2 = s2["mbc"] / moy

    # Avantage domicile progressif (un très bon club à domicile est encore plus favorisé)
    dom_bonus = float(DOM_BONUS_BASE + (s1["pts_par_match"] / 3.0) * DOM_BONUS_MAX)

    # Momentum (Forme de l'équipe) : Variation autour de ±8%
    fm1 = FORME_MIN + (s1["forme_pct"] / 100.0) * FORME_RANGE
    fm2 = FORME_MIN + (s2["forme_pct"] / 100.0) * FORME_RANGE

    # Buteur clé forfait/présent ?
    bm1 = 1.0 if but1 else BUTEUR_ABSENT_MULT
    bm2 = 1.0 if but2 else BUTEUR_ABSENT_MULT

    # Fatigue / Repos (Bonus élevé > 4j / Malus < 3j)
    rm1 = REPOS_ELEVE_MULT if repos1 >= 5 else (REPOS_FAIBLE_MULT if repos1 <= 2 else 1.0)
    rm2 = REPOS_ELEVE_MULT if repos2 >= 5 else (REPOS_FAIBLE_MULT if repos2 <= 2 else 1.0)

    # Formulation de l'xG
    l_h = fa1 * fd2 * moy * dom_bonus * fm1 * bm1 * rm1
    l_a = fa2 * fd1 * moy * fm2 * bm2 * rm2

    # Assurer au moins 0.1 but espéré minimum pour éviter le ZeroDivision ou crash log
    return round(max(l_h, 0.1), 3), round(max(l_a, 0.1), 3)


# ── Critère de Kelly ──────────────────────────
def kelly_criterion(prob: float, cote: float) -> float:
    """
    Optimisation stricte du portefeuille (Kelly Fraction).
    Retourne la portion de capital à jouer (en décimales).
    Protège contre les values négatives qui donneraient une fraction sous 0.
    """
    if cote <= 1.0 or prob <= 0.0:
        return 0.0
        
    b = cote - 1.0
    f = (b * prob - (1.0 - prob)) / b
    
    return max(f, 0.0)
