# ⚽️ PRO-FOOT AI V3 - Refonte SaaS

PRO-FOOT AI V3 est une plateforme professionnelle de prédictions sportives (football) basée sur l'algorithme mathématique de **Dixon-Coles** et le système **Elo**. 

Cette refonte transforme l'ancien script monolithique Streamlit en une véritable architecture SaaS moderne, séparant un **Backend API ultra-rapide** et un **Frontend interactif de dernière génération**.

---

## 🏗️ Architecture Technique

Le projet adopte désormais une architecture "Backend-First" pour une séparation stricte entre la logique de calcul (Data Science) et l'interface utilisateur.

*   **Backend (API & Data Science)** : 
    *   Construit avec **FastAPI** (Python 3.9+).
    *   Moteur statistique Dixon-Coles et système de classement Elo.
    *   Authentification JWT avec hachage sécurisé (bcrypt).
    *   Intégration d'API tierces pour la récupération des cotes en direct.
*   **Frontend (Interface Utilisateur)** : 
    *   Construit avec **Next.js 14+** (React) et TailwindCSS.
    *   Thème "Dark Mode" Premium immersif (Émeraude / Sarcelle).
    *   Expérience utilisateur fluide (SPA) sans rechargement de page.
*   **Base de Données** : 
    *   **SQLite** (via SQLAlchemy) pour la gestion des utilisateurs, des abonnements Premium et de la Bankroll.

---

## 🚀 Fonctionnalités Principales

*   **📊 Matchs du Jour** : Analyse automatique des rencontres majeures de la journée.
*   **💎 Value Bets (Premium)** : Détection d'anomalies de cotes chez les bookmakers avec calcul de l'"Edge" (Avantage mathématique) en temps réel.
*   **⚙️ Mon Match** : Outil d'analyse personnalisée avec probabilités 1N2, Over/Under, BTTS (Les deux équipes marquent) et score exact probable.
*   **💰 Gestion de Bankroll** : Suivi des performances, Taux de réussite et ROI.

---

## 🛠️ Installation et Lancement en Local

### 1. Configuration du Backend (FastAPI)

Dans un terminal, placez-vous à la racine du projet :

```bash
# Activation de l'environnement virtuel
source .venv/bin/activate

# Installation des dépendances (si nécessaire)
pip install -r requirements.txt

# Création du fichier d'environnement
cp .env.example .env
# N'oubliez pas d'éditer le fichier .env avec votre JWT_SECRET_KEY et API_FOOTBALL_KEY

# Lancement du serveur API (sur le port 8000)
uvicorn backend.main:app --reload
```

L'API sera disponible sur : `http://localhost:8000`
Documentation interactive Swagger : `http://localhost:8000/docs`

### 2. Configuration du Frontend (Next.js)

Ouvrez un **deuxième terminal** et allez dans le dossier frontend :

```bash
cd frontend

# Installation des packages Node
npm install

# Lancement du serveur de développement (sur le port 3001)
npm run dev -- -p 3001
```

L'interface SaaS est maintenant accessible sur : `http://localhost:3001`

---

## 🔒 Variables d'Environnement (.env)

Le backend requiert un fichier `.env` à la racine contenant au minimum :

```ini
DATABASE_URL=sqlite:///./profoot.db
JWT_SECRET_KEY=votre_cle_secrete_longue_ici
API_FOOTBALL_KEY=votre_cle_api_football_live
```


## 🧹 Clean‑up Log

- `frontend/AGENTS.md` – redundant dev guide, merged into README.
- `.streamlit/` – legacy Streamlit configuration, not used by Next.js UI.
- `app.py` – duplicate FastAPI entry point, backend now starts via `backend/main.py`.
- `tests/` – removed because no test suite is present; can be re‑added later.
- `.gitignore` – updated to remove the `.streamlit/secrets.toml` entry.

---

*Développé avec 💚 pour dompter les bookmakers grâce aux mathématiques.*

*Développé avec 💚 pour dompter les bookmakers grâce aux mathématiques.*
