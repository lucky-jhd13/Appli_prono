from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from core.data_mapper import KNOWN_ELO, DEFAULT_ELO
from backend.routers.matches import engine, detector

router = APIRouter(prefix="/api/custom", tags=["Custom Analysis"])

class CustomMatchRequest(BaseModel):
    home_team: str
    away_team: str
    # Cotes optionnelles pour calcul des Value Bets
    odd_home: Optional[float] = None
    odd_draw: Optional[float] = None
    odd_away: Optional[float] = None

@router.post("/analyze")
def analyze_custom_match(req: CustomMatchRequest):
    """
    Simule un match personnalisé avec les algorithmes V3.
    """
    home_elo = KNOWN_ELO.get(req.home_team, DEFAULT_ELO)
    away_elo = KNOWN_ELO.get(req.away_team, DEFAULT_ELO)
    
    elo_avg = 1700
    home_att = max(0.6, min(round(1.0 + (home_elo - elo_avg) / 1000, 2), 2.8))
    home_def = max(0.6, min(round(1.0 + (home_elo - elo_avg) / 1200, 2), 2.2))
    away_att = max(0.6, min(round(1.0 + (away_elo - elo_avg) / 1000, 2), 2.8))
    away_def = max(0.6, min(round(1.0 + (away_elo - elo_avg) / 1200, 2), 2.2))
    
    pred = engine.predict_match(
        home_team=req.home_team,
        away_team=req.away_team,
        home_attack_base=home_att,
        home_defense_base=home_def,
        away_attack_base=away_att,
        away_defense_base=away_def
    )
    
    vbs_json = []
    if req.odd_home and req.odd_draw and req.odd_away:
        odds_filtered = {
            'home_win': req.odd_home,
            'draw': req.odd_draw,
            'away_win': req.odd_away
        }
        probs_mapped = {
            'home_win': pred['probabilities']['home_win'],
            'draw': pred['probabilities']['draw'],
            'away_win': pred['probabilities']['away_win'],
            'over_2.5': pred['probabilities']['over_2.5'],
            'under_2.5': pred['probabilities']['under_2.5'],
            'btts_yes': pred['probabilities']['btts_yes'],
            'btts_no': pred['probabilities']['btts_no'],
        }
        vbs = detector.analyze_match(
            f"{req.home_team} vs {req.away_team}", 
            probs_mapped, 
            odds_filtered,
            pred['components']
        )
        vbs_json = [{
            "bet_type": vb.bet_type.value,
            "odd": vb.bookmaker_odd,
            "edge_pct": vb.edge_pct,
            "confidence": vb.confidence_score,
            "label": vb.label
        } for vb in vbs]

    return {
        "teams": {"home": req.home_team, "away": req.away_team},
        "features": pred['components'],
        "probabilities": pred['probabilities'],
        "value_bets": vbs_json
    }
