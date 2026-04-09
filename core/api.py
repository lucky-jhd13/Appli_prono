# ─────────────────────────────────────────────
# core/api.py — Appels API API-FOOTBALL.com
# ─────────────────────────────────────────────

import requests
import logging
import streamlit as st
from typing import Optional, List, Dict, Any
from config import API_KEY

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@st.cache_data(ttl=3600)
def charger_classement(league_id: str) -> Optional[List[Dict[str, Any]]]:
    """
    Retourne le tableau de classement complet d'un championnat depuis API-FOOTBALL.
    """
    url = "https://v3.football.api-sports.io/standings"
    params = {"league": league_id, "season": "2023"} # Note: On peut dynamiser la saison
    headers = {
        "x-apisports-key": API_KEY,
        "x-rapidapi-host": "v3.football.api-sports.io"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=12)
        response.raise_for_status()
        
        data = response.json()
        
        if "response" in data and len(data["response"]) > 0:
            league_data = data["response"][0].get("league", {})
            standings = league_data.get("standings", [])
            
            if standings:
                # API-FOOTBALL renvoie parfois une liste de listes (groupes)
                table = standings[0] 
                
                # Conversion du format API-FOOTBALL vers le format attendu par notre app
                formatted_table = []
                for entry in table:
                    formatted_table.append({
                        "team": {
                            "name": entry["team"]["name"],
                            "crest": entry["team"]["logo"]
                        },
                        "position": entry["rank"],
                        "playedGames": entry["all"]["played"],
                        "won": entry["all"]["win"],
                        "draw": entry["all"]["draw"],
                        "lost": entry["all"]["lost"],
                        "points": entry["points"],
                        "goalsFor": entry["all"]["goals"]["for"],
                        "goalsAgainst": entry["all"]["goals"]["against"],
                        "form": entry["form"]
                    })
                return formatted_table
            
        logger.warning(f"La structure API pour {league_id} ne contient pas de tableau.")
        return None
        
    except Exception as e:
        logger.error(f"❌ Erreur API : {e}")
        st.error(f"⚠️ Erreur lors de la récupération des données : {e}")
        return None


def moyenne_buts_ligue(data_ligue: List[Dict[str, Any]]) -> float:
    """
    Calcule la moyenne de buts marqués par match dans l'ensemble du championnat.
    """
    if not data_ligue:
        return 1.3
        
    total_gf = sum(equipe.get("goalsFor", 0) for equipe in data_ligue)
    total_pj = sum(equipe.get("playedGames", 1) or 1 for equipe in data_ligue)
    
    return float(total_gf / total_pj) if total_pj > 0 else 1.3
