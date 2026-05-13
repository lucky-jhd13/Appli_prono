from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import date
import os

from core.api_client import FootballAPIClient
from core.data_mapper import map_fixture_to_match
from core.engine_v3 import FootballEngineV3, EloSystem
from core.value_betting import ValueBetDetector
from config import DEMO_MATCHES

router = APIRouter(prefix="/api/matches", tags=["Matches"])

# Initialisation du moteur au démarrage
elo = EloSystem()
engine = FootballEngineV3(elo_system=elo)
detector = ValueBetDetector()

@router.get("/today")
def get_matches_today(target_date: Optional[str] = Query(None)):
    """
    Récupère les matchs du jour et calcule les probabilités 1N2 et Value Bets en direct.
    """
    dt = date.fromisoformat(target_date) if target_date else date.today()
    api_key = os.environ.get("API_FOOTBALL_KEY", "")
    
    raw_matches = []
    source = "demo"
    
    if not api_key:
        raw_matches = DEMO_MATCHES
    else:
        client = FootballAPIClient(api_key=api_key)
        fixtures = client.get_fixtures(dt)
        source = "live"
        
        for fix in fixtures[:10]: # Limite à 10 pour la perf
            fixture_id = fix.get("fixture", {}).get("id", 0)
            try:
                odds = client.get_odds(fixture_id)
            except Exception:
                odds = {}
            match = map_fixture_to_match(fix, odds)
            match['id'] = fixture_id
            match['league'] = fix.get("league", {}).get("name", "")
            raw_matches.append(match)
            
    results = []
    for match in raw_matches:
        # Calcul des probabilités
        pred = engine.predict_match(
            home_team=match['home_team'] if 'home_team' in match else match['home'],
            away_team=match['away_team'] if 'away_team' in match else match['away'],
            home_attack_base=match.get('home_attack', 1.0),
            home_defense_base=match.get('home_defense', 1.0),
            away_attack_base=match.get('away_attack', 1.0),
            away_defense_base=match.get('away_defense', 1.0)
        )
        
        # Conversion des types Numpy pour la sérialisation JSON
        pred_probs_clean = {}
        for k, v in pred['probabilities'].items():
            if k == 'top_scores':
                pred_probs_clean[k] = [(int(s[0]), int(s[1]), float(s[2])) for s in v]
            elif k == 'most_likely_score':
                pred_probs_clean[k] = (int(v[0]), int(v[1]))
            elif hasattr(v, "item"):
                pred_probs_clean[k] = v.item()
            else:
                pred_probs_clean[k] = float(v) if isinstance(v, (int, float)) else v
                
        
        # Détection des value bets
        probs_mapped = {
            'home_win': pred_probs_clean['home_win'],
            'draw': pred_probs_clean['draw'],
            'away_win': pred_probs_clean['away_win'],
            'over_2.5': pred_probs_clean.get('over_2.5', 0.0),
            'under_2.5': pred_probs_clean.get('under_2.5', 0.0),
            'btts_yes': pred_probs_clean.get('btts_yes', 0.0),
            'btts_no': pred_probs_clean.get('btts_no', 0.0),
        }
        
        odds_mapped = {
            'home_win': match.get('odds', {}).get('home_win'),
            'draw': match.get('odds', {}).get('draw'),
            'away_win': match.get('odds', {}).get('away_win'),
        }
        odds_filtered = {k: float(v) for k, v in odds_mapped.items() if v is not None}
        
        home_name = match.get('home_team') or match.get('home')
        away_name = match.get('away_team') or match.get('away')
        
        vbs = detector.analyze_match(
            f"{home_name} vs {away_name}", 
            probs_mapped, 
            odds_filtered,
            pred['components'], 
            data_completeness=0.85
        )
        
        vbs_json = [{
            "bet_type": vb.bet_type.value,
            "odd": float(vb.bookmaker_odd),
            "edge_pct": float(vb.edge_pct),
            "confidence": int(vb.confidence_score),
            "label": str(vb.label)
        } for vb in vbs]
        
        results.append({
            "id": int(match.get("id", 0)),
            "league": str(match.get("league", "")),
            "home": str(home_name),
            "away": str(away_name),
            "date": str(match.get("date", "")),
            "probabilities": pred_probs_clean,
            "value_bets": vbs_json
        })
        
    return {"source": source, "matches": results}
