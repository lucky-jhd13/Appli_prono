# ─────────────────────────────────────────────
# config.py — Constantes & configuration globale
# ─────────────────────────────────────────────

from typing import Dict

# ── API ──────────────────────────────────────
API_KEY: str = "c490a4b8f2e3701f4fc450abd13d27f2"

# ── Compétitions supportées (Nouveaux IDs API-FOOTBALL) ──
CHAMPIONNATS: Dict[str, str] = {
    "🇫🇷 Ligue 1":          "61",
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": "39",
    "🇪🇸 La Liga":           "140",
    "🇩🇪 Bundesliga":        "78",
    "🇮🇹 Serie A":           "135",
    "🇳🇱 Eredivisie":        "88",
    "🇪🇺 Champions League": "2",
    "🇪🇺 Europa League":    "3",
}

# ── Modèle Poisson ───────────────────────────
# Nombre de buts max dans la matrice de probabilités
MAX_BUTS_MATRICE: int = 8

# Seuils de décision algorithmique
SEUIL_BTTS: float   = 0.50   # > 50% → BTTS OUI
SEUIL_OVER15: float = 0.52   # > 52% → Over 1.5
SEUIL_VALUE: float  = 0.15   # écart min cote_book - cote_algo pour déclarer une "Value"

# Modificateurs d'avantage domicile
DOM_BONUS_BASE: float = 1.05
DOM_BONUS_MAX: float  = 0.12  # +12% max selon performances à domicile (dynamique)

# Modificateurs de forme sur 5 matchs (±8%)
FORME_MIN: float   = 0.96
FORME_RANGE: float = 0.08

# Modificateurs d'effectif et de calendrier
BUTEUR_ABSENT_MULT: float = 0.78  # Impact de l'absence du buteur principal
REPOS_ELEVE_MULT: float   = 1.06  # Avantage si >= 5 jours de repos
REPOS_FAIBLE_MULT: float  = 0.88  # Malus si <= 2 jours de repos
