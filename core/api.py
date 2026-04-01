# ─────────────────────────────────────────────
# core/api.py — Appels API football-data.org avec gestion d'erreurs
# ─────────────────────────────────────────────

import requests
import logging
import streamlit as st
from typing import Optional, List, Dict, Any
from config import API_KEY

# Configuration des logs pour tracer les soucis de requêtes API
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@st.cache_data(ttl=3600)
def charger_classement(league_code: str) -> Optional[List[Dict[str, Any]]]:
    """
    Retourne le tableau de classement complet d'un championnat.
    Utilise le cache de Streamlit pour éviter d'exploser le quota API (1h de TTL).
    """
    url = f"https://api.football-data.org/v4/competitions/{league_code}/standings"
    headers = {"X-Auth-Token": API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=12)
        response.raise_for_status()  # Lève une exception si statut != 2xx
        
        data = response.json()
        # Sécurise le parsing de la structure JSON de football-data.org
        if "standings" in data and len(data["standings"]) > 0:
            return data["standings"][0].get("table", [])
            
        logger.warning(f"La structure API pour {league_code} ne contient pas de tableau (table).")
        return None
        
    except requests.exceptions.HTTPError as he:
        if response.status_code == 429:
            logger.error("🛑 Erreur 429: Limite d'appels API atteinte (Rate Limit).")
            st.error("⚠️ Quota API de données sportives atteint. Veuillez réessayer plus tard.")
        else:
            logger.error(f"❌ Erreur HTTP : {he}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erreur de connexion / Timeout : {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Erreur inattendue : {e}")
        return None


def moyenne_buts_ligue(data_ligue: List[Dict[str, Any]]) -> float:
    """
    Calcule la moyenne de buts marqués par match dans l'ensemble du championnat.
    Cette donnée sert de base globale pour la normalisation du modèle de Poisson.
    Si erreur grave, retombe sur 1.3 buts.
    """
    if not data_ligue:
        return 1.3
        
    total_gf = sum(equipe.get("goalsFor", 0) for equipe in data_ligue)
    total_pj = sum(equipe.get("playedGames", 1) or 1 for equipe in data_ligue)
    
    return float(total_gf / total_pj) if total_pj > 0 else 1.3
