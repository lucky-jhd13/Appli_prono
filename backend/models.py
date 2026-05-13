from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Rôle & Abonnements
    is_premium = Column(Boolean, default=False)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    
    # Bankroll
    initial_bankroll = Column(Float, default=1000.0)
    current_bankroll = Column(Float, default=1000.0)
    
    # Relations
    bets = relationship("Bet", back_populates="owner")

class Bet(Base):
    __tablename__ = "bets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    match_name = Column(String, index=True)
    bet_type = Column(String) # ex: '1', 'X', '2', 'O2.5'
    odd = Column(Float)
    stake = Column(Float)
    
    # Algorithme
    model_prob = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Résultat
    status = Column(String, default="pending") # pending, won, lost
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relations
    owner = relationship("User", back_populates="bets")

class PredictionCache(Base):
    __tablename__ = "predictions_cache"
    
    id = Column(String, primary_key=True, index=True) # match_id + date
    match_data = Column(String) # JSON stringifié des probabilités et features
    created_at = Column(DateTime, default=datetime.utcnow)
