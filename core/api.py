# ─────────────────────────────────────────────
# core/api.py — Appels API football-data.org
# ─────────────────────────────────────────────

import requests
import streamlit as st
from config import API_KEY


@st.cache_data(ttl=3600)
def charger_classement(league_code: str):
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
    """Calcule la moyenne de buts marqués par match dans le championnat (pour normalisation Poisson)."""
    total_gf = sum(e.get("goalsFor", 0) for e in data_ligue)
    total_pj = sum(e.get("playedGames", 1) or 1 for e in data_ligue)
    return total_gf / total_pj if total_pj > 0 else 1.3
