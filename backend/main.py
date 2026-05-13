from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
import backend.models as models
from backend.routers import matches, custom, bankroll
import backend.auth as auth

# Création des tables dans la base de données
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PRO-FOOT AI Backend",
    description="API SaaS pour les prédictions de football et la gestion de bankroll",
    version="1.0.0"
)

# Configuration CORS pour permettre au frontend Next.js de communiquer avec l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(matches.router)
app.include_router(custom.router)
app.include_router(bankroll.router)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API PRO-FOOT AI. Accédez à /docs pour la documentation."}
