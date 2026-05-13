from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.database import get_db
from backend.models import Bet, User
from backend.auth import get_current_user

router = APIRouter(prefix="/api/bankroll", tags=["Bankroll"])

class BetCreate(BaseModel):
    match_name: str
    bet_type: str
    odd: float
    stake: float
    model_prob: Optional[float] = None
    confidence_score: Optional[float] = None

class BetResolve(BaseModel):
    bet_id: int
    won: bool

@router.get("/")
def get_user_bankroll(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bets = db.query(Bet).filter(Bet.user_id == current_user.id).all()
    
    # Statistiques
    wins = [b for b in bets if b.status == "won"]
    losses = [b for b in bets if b.status == "lost"]
    total_resolved = len(wins) + len(losses)
    win_rate = (len(wins) / total_resolved * 100) if total_resolved > 0 else 0
    
    roi = 0.0
    if current_user.initial_bankroll > 0:
        roi = ((current_user.current_bankroll - current_user.initial_bankroll) / current_user.initial_bankroll) * 100
        
    return {
        "initial_bankroll": current_user.initial_bankroll,
        "current_bankroll": current_user.current_bankroll,
        "roi_pct": roi,
        "win_rate_pct": win_rate,
        "total_bets": len(bets),
        "pending_bets": len([b for b in bets if b.status == "pending"])
    }

@router.post("/bet")
def place_bet(bet_req: BetCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.current_bankroll < bet_req.stake:
        raise HTTPException(status_code=400, detail="Bankroll insuffisante")
        
    new_bet = Bet(
        user_id=current_user.id,
        match_name=bet_req.match_name,
        bet_type=bet_req.bet_type,
        odd=bet_req.odd,
        stake=bet_req.stake,
        model_prob=bet_req.model_prob,
        confidence_score=bet_req.confidence_score
    )
    
    # On déduit la mise de la bankroll immédiatement
    current_user.current_bankroll -= bet_req.stake
    
    db.add(new_bet)
    db.commit()
    db.refresh(new_bet)
    
    return {"message": "Pari enregistré", "bet_id": new_bet.id, "new_bankroll": current_user.current_bankroll}

@router.post("/resolve")
def resolve_bet(req: BetResolve, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bet = db.query(Bet).filter(Bet.id == req.bet_id, Bet.user_id == current_user.id).first()
    if not bet:
        raise HTTPException(status_code=404, detail="Pari non trouvé")
        
    if bet.status != "pending":
        raise HTTPException(status_code=400, detail="Ce pari a déjà été résolu")
        
    if req.won:
        bet.status = "won"
        profit = bet.stake * bet.odd
        current_user.current_bankroll += profit
    else:
        bet.status = "lost"
        
    bet.resolved_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Pari résolu", "new_bankroll": current_user.current_bankroll}
