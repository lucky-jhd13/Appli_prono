# PRO-FOOT AI V3

Application Streamlit de pronostics football avec interface premium, mode demo et mode live via API-Football.

## Fonctionnalites

- Dashboard de synthese avec matchs du jour et indicateurs globaux
- Analyse detaillee d'un match
- Detection de value bets
- Suivi de bankroll et gestion Kelly
- Backtesting sur historique de demo
- Onglet "Mon Match" pour une analyse personnalisee
- Mode live avec fallback automatique en mode demo

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Lancement

```bash
.venv/bin/streamlit run app.py
```

## Configuration

Pour activer le mode live, creez un fichier `.env` a partir de `.env.example` puis renseignez :

```bash
API_FOOTBALL_KEY=...
```

Vous pouvez aussi utiliser `secrets.toml` pour Streamlit.
