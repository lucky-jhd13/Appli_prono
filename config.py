# ─────────────────────────────────────────────
# config.py — Constantes & configuration globale
# ─────────────────────────────────────────────

API_KEY = "6845fbe629e041bdb8f0cad7488a9fe2"

CHAMPIONNATS = {
    "🇫🇷 Ligue 1":          "FL1",
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": "PL",
    "🇪🇸 La Liga":           "PD",
    "🇩🇪 Bundesliga":        "BL1",
    "🇮🇹 Serie A":           "SA",
    "🇳🇱 Eredivisie":        "DED",
}

# Nombre de buts max dans la matrice de Poisson
MAX_BUTS_MATRICE = 8

# Seuils de décision
SEUIL_BTTS    = 0.50   # > 50% → BTTS OUI
SEUIL_OVER25  = 0.52   # > 52% → Over 2.5
SEUIL_VALUE   = 0.15   # écart min cote_book - cote_algo pour value bet

# Avantage domicile
DOM_BONUS_BASE = 1.05
DOM_BONUS_MAX  = 0.12  # +12% max selon perfs domicile

# Modificateurs forme (±8%)
FORME_MIN = 0.96
FORME_RANGE = 0.08

# Modificateurs buteur / repos
BUTEUR_ABSENT_MULT = 0.78
REPOS_ELEVE_MULT   = 1.06   # >= 5 jours
REPOS_FAIBLE_MULT  = 0.88   # <= 2 jours
