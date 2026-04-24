"""
PRO-FOOT AI V3 — API-Football Client
Récupère les matchs en temps réel depuis api-sports.io
"""

import urllib.request
import urllib.error
import json
import os
from datetime import datetime, date
from typing import Optional
import time


class FootballAPIClient:
    """
    Client pour l'API api-sports.io (API-Football).
    Documentation : https://www.api-football.com/documentation-v3
    """

    BASE_URL = "https://v3.football.api-sports.io"

    # Grandes ligues supportées (ID api-sports)
    SUPPORTED_LEAGUES = {
        39: "Premier League",
        61: "Ligue 1",
        78: "Bundesliga",
        135: "Serie A",
        140: "La Liga",
        2:  "Ligue des Champions",
        3:  "Europa League",
        1:  "Coupe du Monde",
    }

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("API_FOOTBALL_KEY", "")
        if not self.api_key:
            raise ValueError(
                "Clé API manquante. Définissez API_FOOTBALL_KEY dans .env ou dans les secrets Streamlit."
            )

    def _get(self, endpoint: str, params: dict) -> dict:
        """Effectue une requête GET sécurisée vers l'API."""
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{self.BASE_URL}/{endpoint}?{qs}"
        req = urllib.request.Request(url)
        req.add_header("x-apisports-key", self.api_key)
        req.add_header("x-apisports-host", "v3.football.api-sports.io")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Erreur API {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"Réseau indisponible: {e.reason}")

    def check_status(self) -> dict:
        """Vérifie que la clé API est valide."""
        data = self._get("status", {})
        return data.get("response", {})

    def get_fixtures(self, target_date: Optional[date] = None) -> list:
        """
        Retourne les matchs pour une date donnée (défaut = aujourd'hui).
        Filtre sur les ligues supportées uniquement.
        """
        target_date = target_date or date.today()
        date_str = target_date.strftime("%Y-%m-%d")
        data = self._get("fixtures", {"date": date_str, "timezone": "Europe/Paris"})
        fixtures = data.get("response", [])
        return [
            f for f in fixtures
            if f.get("league", {}).get("id") in self.SUPPORTED_LEAGUES
        ]

    def get_odds(self, fixture_id: int) -> dict:
        """
        Retourne les cotes pre-match pour un match donné.
        Bookmaker par défaut = Bet365 (id=6) ou le premier disponible.
        """
        data = self._get("odds", {"fixture": fixture_id, "bookmaker": 6})
        bkms = data.get("response", [])
        if not bkms:
            # Retenter sans filtre bookmaker
            data = self._get("odds", {"fixture": fixture_id})
            bkms = data.get("response", [])
        if not bkms:
            return {}
        # Récupérer le premier bookmaker disponible
        bookmaker = bkms[0].get("bookmakers", [{}])[0]
        bets = bookmaker.get("bets", [])
        odds_map = {}
        for bet in bets:
            name = bet.get("name", "")
            values = {v["value"]: float(v["odd"]) for v in bet.get("values", [])}
            if name == "Match Winner":
                odds_map["home_win"] = values.get("Home")
                odds_map["draw"] = values.get("Draw")
                odds_map["away_win"] = values.get("Away")
            elif name == "Goals Over/Under":
                odds_map["over_2.5"] = values.get("Over 2.5")
                odds_map["under_2.5"] = values.get("Under 2.5")
            elif name == "Both Teams Score":
                odds_map["btts_yes"] = values.get("Yes")
                odds_map["btts_no"] = values.get("No")
        return {k: v for k, v in odds_map.items() if v is not None}

    def get_team_stats(self, team_id: int, league_id: int, season: int = 2024) -> dict:
        """
        Retourne les statistiques d'une équipe pour la saison en cours.
        Utilisé pour estimer la force offensive/défensive.
        """
        data = self._get("teams/statistics", {
            "team": team_id,
            "league": league_id,
            "season": season,
        })
        return data.get("response", {})

    def get_fixture_stats(self, fixture_id: int) -> list:
        """Retourne les statistiques détaillées (xG, possession, tirs) d'un match."""
        data = self._get("fixtures/statistics", {"fixture": fixture_id})
        return data.get("response", [])
