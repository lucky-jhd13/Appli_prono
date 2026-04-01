"""
PRO-FOOT AI V3 — Data Mapper
Transforme les données brutes de l'API en profils compatibles avec le moteur Dixon-Coles+
"""

from datetime import datetime
from typing import Optional


# ELO de référence par défaut (si l'équipe est inconnue)
DEFAULT_ELO = 1600

# Base ELO connue pour les grandes équipes
KNOWN_ELO = {
    # Premier League
    "Manchester City": 1950, "Arsenal": 1810, "Liverpool": 1850,
    "Chelsea": 1780, "Manchester United": 1770, "Tottenham": 1720,
    "Newcastle": 1680, "Aston Villa": 1700,
    # La Liga
    "Real Madrid": 1900, "Barcelona": 1870, "Atletico Madrid": 1820,
    "Sevilla": 1700, "Real Sociedad": 1680, "Villarreal": 1660,
    # Bundesliga
    "Bayern Munich": 1920, "Dortmund": 1790, "Leverkusen": 1780,
    "RB Leipzig": 1770, "Union Berlin": 1640, "Freiburg": 1650,
    # Ligue 1
    "PSG": 1850, "Marseille": 1730, "Monaco": 1720, "Lyon": 1700,
    "Lens": 1660, "Nice": 1650,
    # Serie A
    "Inter Milan": 1810, "AC Milan": 1790, "Napoli": 1780,
    "Juventus": 1770, "Roma": 1730, "Lazio": 1700,
    # Nationales
    "France": 2050, "Argentine": 2080, "Angleterre": 1990,
    "Espagne": 2010, "Brésil": 2020, "Allemagne": 1960,
}


def parse_form(results_str: str) -> list:
    """
    Convertit une chaîne de forme (ex: 'W,W,D,L,W') en liste de tuples (buts_marqués, buts_encaissés).
    Utilisé pour l'estimation de forme interne au moteur.
    """
    mapping = {"W": (2, 0), "D": (1, 1), "L": (0, 2), "w": (2, 0), "d": (1, 1), "l": (0, 2)}
    return [mapping.get(r.strip(), (1, 1)) for r in results_str.split(",")[:5]]


def estimate_strength_from_stats(team_stats: dict, home: bool = True) -> tuple:
    """
    Estime la force offensive et défensive d'une équipe depuis ses stats de saison.
    Retourne (attack_strength, defense_strength) en valeur relative à 1.0 = moyenne.
    """
    if not team_stats:
        return (1.2 if home else 1.0), (1.0 if home else 1.1)

    goals = team_stats.get("goals", {})
    fixtures = team_stats.get("fixtures", {})

    n_played = fixtures.get("played", {}).get("total", 0)
    if n_played == 0:
        return (1.2 if home else 1.0), (1.0 if home else 1.1)

    scored = goals.get("for", {}).get("total", {}).get("total", 0)
    conceded = goals.get("against", {}).get("total", {}).get("total", 0)

    attack = round((scored / n_played) / 1.40, 2)   # 1.40 = moyenne ligues
    defense = round((conceded / n_played) / 1.10, 2) # 1.10 = moyenne concédée
    attack = max(0.5, min(attack, 3.0))
    defense = max(0.5, min(defense, 2.5))
    return attack, defense


def estimate_xg(attack_str: float, defense_opp: float) -> float:
    """Estime les xG attendus d'une équipe en fonction de sa force et de celle de l'adversaire."""
    return round(attack_str * 1.40 * (1.0 / max(defense_opp, 0.5)), 2)


def map_fixture_to_match(
    fixture: dict,
    odds: dict,
    home_stats: Optional[dict] = None,
    away_stats: Optional[dict] = None,
) -> dict:
    """
    Transforme un fixture brut de l'API + ses cotes + ses stats
    en un dictionnaire compatible avec le moteur Dixon-Coles V3.
    """
    league_info = fixture.get("league", {})
    home_info = fixture.get("teams", {}).get("home", {})
    away_info = fixture.get("teams", {}).get("away", {})
    fixture_info = fixture.get("fixture", {})

    home_name = home_info.get("name", "Domicile")
    away_name = away_info.get("name", "Extérieur")
    league_name = league_info.get("name", "Inconnue")

    # Date du match
    date_str_raw = fixture_info.get("date", "")
    try:
        dt = datetime.fromisoformat(date_str_raw.replace("Z", "+00:00"))
        date_fmt = dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        date_fmt = date_str_raw[:16]

    # ELO
    home_elo = KNOWN_ELO.get(home_name, DEFAULT_ELO)
    away_elo = KNOWN_ELO.get(away_name, DEFAULT_ELO)

    # Forces depuis stats si disponibles
    home_att, home_def = estimate_strength_from_stats(home_stats, home=True)
    away_att, away_def = estimate_strength_from_stats(away_stats, home=False)

    # xG estimés
    home_xg = estimate_xg(home_att, away_def)
    away_xg = estimate_xg(away_att, home_def)

    # Cotes par défaut si absentes
    odds_final = {
        "home_win": odds.get("home_win", 2.00),
        "draw": odds.get("draw", 3.40),
        "away_win": odds.get("away_win", 3.50),
        "over_2.5": odds.get("over_2.5", 1.90),
        "under_2.5": odds.get("under_2.5", 1.90),
        "btts_yes": odds.get("btts_yes", 1.80),
        "btts_no": odds.get("btts_no", 2.00),
    }

    fixture_id = fixture_info.get("id", 0)

    return {
        "id": fixture_id,
        "home": home_name,
        "away": away_name,
        "league": league_name,
        "date": date_fmt,
        "home_attack": home_att,
        "home_defense": home_def,
        "away_attack": away_att,
        "away_defense": away_def,
        "home_xg": home_xg,
        "away_xg": away_xg,
        "home_elo": home_elo,
        "away_elo": away_elo,
        "home_form": [(2, 1), (1, 1), (2, 0), (1, 0), (2, 1)],  # Form basique par défaut
        "away_form": [(1, 1), (0, 1), (1, 2), (2, 0), (1, 1)],
        "home_rest": 5,
        "away_rest": 5,
        "home_absent": 0,
        "away_absent": 0,
        "odds": odds_final,
    }
