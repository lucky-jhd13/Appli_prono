# ─────────────────────────────────────────────
# core/api.py — Appels API football-data.org
# ─────────────────────────────────────────────

import requests
import streamlit as st
from config import API_KEY


@st.cache_data(ttl=3600)
def charger_classement(league_code: str) -> list | None:
    """Retourne le tableau de classement d'une ligue ou None en cas d'erreur."""
    url = f"https://api.football-data.org/v4/competitions/{league_code}/standings"
    headers = {"X-Auth-Token": API_KEY}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json()["standings"][0]["table"]
        return None
    except Exception:
        return None


def moyenne_buts_ligue(data_ligue: list) -> float:
    """
    Calcule la moyenne de buts marqués par match dans le championnat.
    Chaque équipe joue N matchs → total réel = somme(pj) / 2 (chaque match est compté 2x).
    """
    total_gf = sum(e.get("goalsFor", 0) for e in data_ligue)
    total_pj = sum(e.get("playedGames", 1) or 1 for e in data_ligue)
    # total_pj compte chaque match 2 fois (dom + ext), donc nb_matchs = total_pj / 2
    # Buts par match = total_gf / nb_matchs = total_gf / (total_pj / 2) = 2 * total_gf / total_pj
    # Mais on veut la moyenne de buts MARQUÉS par équipe par match → total_gf / total_pj
    return total_gf / total_pj if total_pj > 0 else 1.3


@st.cache_data(ttl=3600)
def charger_prochains_matchs(league_code: str, limit: int = 20) -> list:
    """Retourne les prochains matchs planifiés d'une ligue."""
    url = f"https://api.football-data.org/v4/competitions/{league_code}/matches"
    params = {"status": "SCHEDULED", "limit": limit}
    headers = {"X-Auth-Token": API_KEY}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code == 200:
            return r.json().get("matches", [])
        return []
    except Exception:
        return []
