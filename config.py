"""
PRO-FOOT AI V3 — Configuration & Données de démonstration
"""

APP_CONFIG = {
    'app_name': 'PRO-FOOT AI V3',
    'version': '3.0.0',
    'initial_bankroll': 1000.0,
    'kelly_fraction': 0.25,
    'max_bet_pct': 0.05,
    'min_edge': 0.03,
    'min_confidence': 50.0,
    'rho': -0.13,
    'home_advantage_xg': 0.25,
    'league_avg_goals': 1.40,
    'max_goals_matrix': 8,
}

# ─────────────────────────────────────────────
# BASE D'ÉQUIPES PAR COMPÉTITION
# ─────────────────────────────────────────────
LEAGUE_TEAMS = {
    'Ligue 1': [
        'PSG', 'Marseille', 'Monaco', 'Lyon', 'Lens', 'Nice', 'Lille', 'Rennes',
        'Montpellier', 'Strasbourg', 'Nantes', 'Brest', 'Toulouse', 'Reims',
        'Lorient', 'Metz', 'Clermont', 'Le Havre', 'Auxerre', 'Saint-Étienne',
    ],
    'Premier League': [
        'Manchester City', 'Arsenal', 'Liverpool', 'Chelsea', 'Manchester United',
        'Tottenham', 'Newcastle', 'Aston Villa', 'Brighton', 'West Ham',
        'Brentford', 'Fulham', 'Crystal Palace', 'Wolves', 'Everton',
        'Nottingham Forest', 'Bournemouth', 'Luton', 'Sheffield United', 'Burnley',
    ],
    'La Liga': [
        'Real Madrid', 'Barcelona', 'Atletico Madrid', 'Sevilla', 'Real Sociedad',
        'Villarreal', 'Athletic Bilbao', 'Valencia', 'Betis', 'Osasuna',
        'Celta Vigo', 'Girona', 'Getafe', 'Rayo Vallecano', 'Cadiz',
        'Almeria', 'Mallorca', 'Las Palmas', 'Alaves', 'Granada',
    ],
    'Bundesliga': [
        'Bayern Munich', 'Dortmund', 'Leverkusen', 'RB Leipzig', 'Union Berlin',
        'Freiburg', 'Hoffenheim', 'Eintracht Frankfurt', 'Wolfsburg', 'Mainz',
        'Borussia Mönchengladbach', 'Augsburg', 'Werder Bremen', 'Bochum',
        'Stuttgart', 'Cologne', 'Heidenheim', 'Darmstadt',
    ],
    'Serie A': [
        'Inter Milan', 'AC Milan', 'Juventus', 'Napoli', 'Roma', 'Lazio',
        'Atalanta', 'Fiorentina', 'Bologna', 'Torino', 'Sassuolo', 'Monza',
        'Udinese', 'Lecce', 'Frosinone', 'Empoli', 'Cagliari', 'Genoa',
        'Salernitana', 'Hellas Verona',
    ],
    'Ligue des Champions': [
        'Real Madrid', 'Manchester City', 'Bayern Munich', 'PSG', 'Barcelona',
        'Liverpool', 'Chelsea', 'Arsenal', 'Dortmund', 'Atletico Madrid',
        'Inter Milan', 'AC Milan', 'Porto', 'Benfica', 'Ajax',
        'Napoli', 'RB Leipzig', 'Leverkusen', 'Braga', 'Shakhtar Donetsk',
    ],
    'Europa League': [
        'Liverpool', 'Leverkusen', 'Roma', 'Villarreal', 'Sevilla',
        'Arsenal', 'Manchester United', 'Tottenham', 'West Ham', 'Fiorentina',
        'Atalanta', 'Lyon', 'Marseille', 'Lazio', 'Slavia Prague',
        'Sporting CP', 'Fenerbahce', 'Galatasaray', 'Rangers', 'Ajax',
    ],
    'Coupe du Monde': [
        'France', 'Argentine', 'Brésil', 'Espagne', 'Angleterre', 'Allemagne',
        'Portugal', 'Pays-Bas', 'Belgique', 'Italie', 'Uruguay', 'Croatie',
        'Maroc', 'Sénégal', 'Japon', 'États-Unis', 'Mexique', 'Canada',
        'Australie', 'Corée du Sud', 'Pologne', 'Suisse', 'Danemark', 'Serbie',
    ],
    'Toutes': [],  # Géré dynamiquement dans l'app
}

DEMO_MATCHES = [
    {
        'id': 1, 'home': 'PSG', 'away': 'Marseille', 'league': 'Ligue 1',
        'date': '2025-04-15 20:45',
        'home_attack': 2.10, 'home_defense': 1.82, 'away_attack': 1.65, 'away_defense': 1.45,
        'home_xg': 1.85, 'away_xg': 1.10, 'home_elo': 1750, 'away_elo': 1640,
        'home_form': [(3,1),(2,0),(1,1),(2,2),(4,0)],
        'away_form': [(1,1),(2,1),(0,2),(1,0),(1,3)],
        'home_rest': 5, 'away_rest': 7, 'home_absent': 1, 'away_absent': 0,
        'odds': {'home_win': 1.72, 'draw': 3.80, 'away_win': 4.50,
                 'over_2.5': 1.85, 'under_2.5': 1.95, 'btts_yes': 1.75, 'btts_no': 2.05}
    },
    {
        'id': 2, 'home': 'Bayern Munich', 'away': 'Dortmund', 'league': 'Bundesliga',
        'date': '2025-04-15 18:30',
        'home_attack': 2.40, 'home_defense': 1.95, 'away_attack': 1.90, 'away_defense': 1.60,
        'home_xg': 2.20, 'away_xg': 1.40, 'home_elo': 1820, 'away_elo': 1690,
        'home_form': [(4,0),(3,1),(2,0),(5,2),(2,1)],
        'away_form': [(2,2),(1,0),(3,1),(1,2),(2,0)],
        'home_rest': 7, 'away_rest': 4, 'home_absent': 0, 'away_absent': 2,
        'odds': {'home_win': 1.55, 'draw': 4.20, 'away_win': 5.50,
                 'over_2.5': 1.60, 'under_2.5': 2.30, 'btts_yes': 1.68, 'btts_no': 2.10}
    },
    {
        'id': 3, 'home': 'Arsenal', 'away': 'Chelsea', 'league': 'Premier League',
        'date': '2025-04-16 16:00',
        'home_attack': 1.95, 'home_defense': 1.75, 'away_attack': 1.80, 'away_defense': 1.68,
        'home_xg': 1.70, 'away_xg': 1.35, 'home_elo': 1710, 'away_elo': 1695,
        'home_form': [(2,1),(1,1),(3,0),(1,2),(2,1)],
        'away_form': [(1,2),(2,0),(1,1),(0,1),(2,2)],
        'home_rest': 6, 'away_rest': 6, 'home_absent': 1, 'away_absent': 1,
        'odds': {'home_win': 2.10, 'draw': 3.40, 'away_win': 3.50,
                 'over_2.5': 1.95, 'under_2.5': 1.85, 'btts_yes': 1.72, 'btts_no': 2.05}
    },
    {
        'id': 4, 'home': 'Real Madrid', 'away': 'Atletico Madrid', 'league': 'La Liga',
        'date': '2025-04-16 21:00',
        'home_attack': 2.20, 'home_defense': 1.88, 'away_attack': 1.55, 'away_defense': 1.35,
        'home_xg': 1.95, 'away_xg': 1.05, 'home_elo': 1800, 'away_elo': 1720,
        'home_form': [(3,0),(2,1),(1,0),(4,1),(2,0)],
        'away_form': [(1,0),(0,0),(2,1),(1,1),(1,0)],
        'home_rest': 7, 'away_rest': 7, 'home_absent': 0, 'away_absent': 0,
        'odds': {'home_win': 1.95, 'draw': 3.60, 'away_win': 4.00,
                 'over_2.5': 2.00, 'under_2.5': 1.80, 'btts_yes': 1.78, 'btts_no': 2.00}
    },
    {
        'id': 5, 'home': 'Juventus', 'away': 'Inter Milan', 'league': 'Serie A',
        'date': '2025-04-17 20:45',
        'home_attack': 1.70, 'home_defense': 1.72, 'away_attack': 1.85, 'away_defense': 1.80,
        'home_xg': 1.45, 'away_xg': 1.50, 'home_elo': 1675, 'away_elo': 1700,
        'home_form': [(1,1),(1,2),(0,0),(2,1),(1,0)],
        'away_form': [(2,0),(3,1),(1,0),(2,2),(2,0)],
        'home_rest': 7, 'away_rest': 5, 'home_absent': 2, 'away_absent': 1,
        'odds': {'home_win': 2.50, 'draw': 3.10, 'away_win': 2.90,
                 'over_2.5': 2.10, 'under_2.5': 1.72, 'btts_yes': 1.82, 'btts_no': 1.95}
    },
    {
        'id': 6, 'home': 'Real Madrid', 'away': 'Man City', 'league': 'Ligue des Champions',
        'date': '2025-05-01 21:00',
        'home_attack': 2.30, 'home_defense': 1.85, 'away_attack': 2.50, 'away_defense': 1.95,
        'home_xg': 2.15, 'away_xg': 2.25, 'home_elo': 1900, 'away_elo': 1950,
        'home_form': [(3,1),(2,0),(1,1),(2,2),(4,0)],
        'away_form': [(2,2),(3,0),(1,1),(4,1),(2,0)],
        'home_rest': 6, 'away_rest': 5, 'home_absent': 0, 'away_absent': 1,
        'odds': {'home_win': 2.60, 'draw': 3.40, 'away_win': 2.50,
                 'over_2.5': 1.65, 'under_2.5': 2.10, 'btts_yes': 1.55, 'btts_no': 2.30}
    },
    {
        'id': 7, 'home': 'Liverpool', 'away': 'Leverkusen', 'league': 'Europa League',
        'date': '2025-05-02 21:00',
        'home_attack': 2.45, 'home_defense': 1.80, 'away_attack': 2.20, 'away_defense': 1.70,
        'home_xg': 2.30, 'away_xg': 1.90, 'home_elo': 1850, 'away_elo': 1780,
        'home_form': [(2,0),(3,1),(2,1),(1,1),(3,0)],
        'away_form': [(1,1),(2,0),(2,2),(3,1),(1,0)],
        'home_rest': 7, 'away_rest': 6, 'home_absent': 1, 'away_absent': 0,
        'odds': {'home_win': 1.95, 'draw': 3.70, 'away_win': 3.50,
                 'over_2.5': 1.55, 'under_2.5': 2.30, 'btts_yes': 1.50, 'btts_no': 2.40}
    },
    {
        'id': 8, 'home': 'France', 'away': 'Argentine', 'league': 'Coupe du Monde',
        'date': '2026-07-15 20:00',
        'home_attack': 2.35, 'home_defense': 2.10, 'away_attack': 2.25, 'away_defense': 2.05,
        'home_xg': 2.10, 'away_xg': 2.00, 'home_elo': 2050, 'away_elo': 2080,
        'home_form': [(2,0),(1,0),(3,1),(1,1),(2,0)],
        'away_form': [(1,0),(2,0),(1,1),(2,1),(3,0)],
        'home_rest': 5, 'away_rest': 6, 'home_absent': 0, 'away_absent': 0,
        'odds': {'home_win': 2.70, 'draw': 3.10, 'away_win': 2.70,
                 'over_2.5': 2.10, 'under_2.5': 1.70, 'btts_yes': 1.85, 'btts_no': 1.90}
    },
]

DEMO_HISTORICAL = [
    {'model_prob': 0.52, 'odd': 2.10, 'outcome': 1, 'confidence_score': 72, 'edge': 0.05},
    {'model_prob': 0.65, 'odd': 1.75, 'outcome': 1, 'confidence_score': 81, 'edge': 0.08},
    {'model_prob': 0.48, 'odd': 2.30, 'outcome': 0, 'confidence_score': 55, 'edge': 0.04},
    {'model_prob': 0.71, 'odd': 1.60, 'outcome': 1, 'confidence_score': 85, 'edge': 0.09},
    {'model_prob': 0.44, 'odd': 2.50, 'outcome': 1, 'confidence_score': 63, 'edge': 0.05},
    {'model_prob': 0.58, 'odd': 1.95, 'outcome': 0, 'confidence_score': 68, 'edge': 0.06},
    {'model_prob': 0.63, 'odd': 1.80, 'outcome': 1, 'confidence_score': 77, 'edge': 0.07},
    {'model_prob': 0.38, 'odd': 3.00, 'outcome': 0, 'confidence_score': 48, 'edge': 0.05},
    {'model_prob': 0.55, 'odd': 2.00, 'outcome': 1, 'confidence_score': 71, 'edge': 0.05},
    {'model_prob': 0.70, 'odd': 1.65, 'outcome': 1, 'confidence_score': 88, 'edge': 0.12},
    {'model_prob': 0.42, 'odd': 2.70, 'outcome': 0, 'confidence_score': 52, 'edge': 0.04},
    {'model_prob': 0.60, 'odd': 1.90, 'outcome': 1, 'confidence_score': 74, 'edge': 0.06},
    {'model_prob': 0.49, 'odd': 2.20, 'outcome': 0, 'confidence_score': 58, 'edge': 0.04},
    {'model_prob': 0.66, 'odd': 1.72, 'outcome': 1, 'confidence_score': 82, 'edge': 0.09},
    {'model_prob': 0.53, 'odd': 2.05, 'outcome': 1, 'confidence_score': 69, 'edge': 0.05},
    {'model_prob': 0.75, 'odd': 1.55, 'outcome': 1, 'confidence_score': 91, 'edge': 0.14},
    {'model_prob': 0.41, 'odd': 2.80, 'outcome': 1, 'confidence_score': 50, 'edge': 0.03},
    {'model_prob': 0.57, 'odd': 1.98, 'outcome': 0, 'confidence_score': 66, 'edge': 0.06},
    {'model_prob': 0.62, 'odd': 1.85, 'outcome': 1, 'confidence_score': 78, 'edge': 0.08},
    {'model_prob': 0.47, 'odd': 2.35, 'outcome': 0, 'confidence_score': 54, 'edge': 0.04},
]
