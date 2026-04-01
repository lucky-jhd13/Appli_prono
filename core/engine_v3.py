"""
PRO-FOOT AI V3 — Moteur de prédiction niveau bookmaker
Dixon-Coles + xG + ELO dynamique + forme + avantage domicile
"""

import numpy as np
from scipy.stats import poisson
from scipy.optimize import minimize
from scipy.special import factorial
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# CORRECTION DIXON-COLES
# ─────────────────────────────────────────────

def dixon_coles_tau(x: int, y: int, lambda_: float, mu_: float, rho: float) -> float:
    """
    Facteur de correction pour les scores bas (0-0, 1-0, 0-1, 1-1).
    Corrige la sous/sur-représentation des faibles scores dans Poisson.
    """
    if x == 0 and y == 0:
        return 1 - lambda_ * mu_ * rho
    elif x == 1 and y == 0:
        return 1 + mu_ * rho
    elif x == 0 and y == 1:
        return 1 + lambda_ * rho
    elif x == 1 and y == 1:
        return 1 - rho
    else:
        return 1.0


def dixon_coles_probability(x: int, y: int, lambda_: float, mu_: float, rho: float = -0.13) -> float:
    """
    Probabilité P(X=x, Y=y) avec correction Dixon-Coles.
    rho ≈ -0.13 (valeur calibrée sur données historiques UEFA)
    """
    tau = dixon_coles_tau(x, y, lambda_, mu_, rho)
    p = poisson.pmf(x, lambda_) * poisson.pmf(y, mu_) * tau
    return max(p, 1e-10)


# ─────────────────────────────────────────────
# SYSTÈME ELO DYNAMIQUE
# ─────────────────────────────────────────────

class EloSystem:
    """
    ELO adaptatif pour le football.
    K-factor variable selon l'importance du match et la cote.
    """

    BASE_RATING = 1500.0
    K_BASE = 32.0

    def __init__(self, ratings: dict = None):
        self.ratings = ratings or {}

    def get_rating(self, team: str) -> float:
        return self.ratings.get(team, self.BASE_RATING)

    def expected_result(self, rating_a: float, rating_b: float, home_advantage: float = 100.0) -> float:
        """Probabilité de victoire pour l'équipe A (domicile)."""
        return 1.0 / (1.0 + 10 ** ((rating_b - rating_a - home_advantage) / 400.0))

    def update(self, team_home: str, team_away: str, result: float,
               k_factor: float = None, home_advantage: float = 100.0):
        """
        result: 1.0 = victoire domicile, 0.5 = nul, 0.0 = victoire extérieur
        """
        ra = self.get_rating(team_home)
        rb = self.get_rating(team_away)
        k = k_factor or self.K_BASE
        ea = self.expected_result(ra, rb, home_advantage)
        self.ratings[team_home] = ra + k * (result - ea)
        self.ratings[team_away] = rb + k * ((1 - result) - (1 - ea))

    def to_strength_multiplier(self, team: str, baseline: float = None) -> float:
        """Convertit l'ELO en multiplicateur de force (centré sur 1.0)."""
        base = baseline or self.BASE_RATING
        return 10 ** ((self.get_rating(team) - base) / 400.0)


# ─────────────────────────────────────────────
# FORME PONDÉRÉE (DÉCROISSANCE EXPONENTIELLE)
# ─────────────────────────────────────────────

def compute_weighted_form(results: list, decay: float = 0.75) -> float:
    """
    Calcule la forme récente d'une équipe.
    results: liste de résultats récents [(goals_scored, goals_conceded), ...]
             du plus récent au plus ancien
    decay: facteur de décroissance (0.75 = les derniers matchs comptent bien plus)
    Retourne: score de forme normalisé [0, 1]
    """
    if not results:
        return 0.5

    weights = [decay ** i for i in range(len(results))]
    total_weight = sum(weights)

    form_score = 0.0
    for i, (scored, conceded) in enumerate(results):
        if scored > conceded:
            pts = 1.0
        elif scored == conceded:
            pts = 0.5
        else:
            pts = 0.0
        form_score += weights[i] * pts

    return form_score / total_weight


def compute_attack_defense_form(results: list, decay: float = 0.75) -> tuple:
    """
    Retourne (attaque_normalisée, defense_normalisée) basées sur les derniers matchs.
    """
    if not results:
        return 1.0, 1.0

    weights = [decay ** i for i in range(len(results))]
    total_weight = sum(weights)

    avg_scored = sum(w * r[0] for w, r in zip(weights, results)) / total_weight
    avg_conceded = sum(w * r[1] for w, r in zip(weights, results)) / total_weight

    # Normalisation: moyenne européenne ~1.4 buts/match
    LEAGUE_AVG = 1.40
    attack_form = avg_scored / LEAGUE_AVG if avg_scored > 0 else 0.5
    defense_form = LEAGUE_AVG / avg_conceded if avg_conceded > 0 else 1.5

    return attack_form, defense_form


# ─────────────────────────────────────────────
# MOTEUR PRINCIPAL V3
# ─────────────────────────────────────────────

class FootballEngineV3:
    """
    Moteur de prédiction complet Dixon-Coles + ELO + xG + forme + contexte.
    """

    # Paramètre rho optimisé sur données Poisson bivariées
    RHO_DEFAULT = -0.13
    # Avantage domicile standard en expected goals
    HOME_ADV_XG = 0.25
    # Limite de la matrice de scores
    MAX_GOALS = 10

    def __init__(self,
                 rho: float = None,
                 home_advantage_xg: float = None,
                 elo_system: EloSystem = None):
        self.rho = rho or self.RHO_DEFAULT
        self.home_advantage_xg = home_advantage_xg or self.HOME_ADV_XG
        self.elo = elo_system or EloSystem()

    def compute_expected_goals(self,
                                # Stats historiques brutes
                                home_attack_base: float,
                                home_defense_base: float,
                                away_attack_base: float,
                                away_defense_base: float,
                                league_avg_goals: float = 1.40,
                                # xG optionnel
                                home_xg: float = None,
                                away_xg: float = None,
                                # ELO
                                home_team: str = None,
                                away_team: str = None,
                                # Forme récente
                                home_form_results: list = None,
                                away_form_results: list = None,
                                # Contexte
                                home_rest_days: int = 7,
                                away_rest_days: int = 7,
                                home_key_players_absent: int = 0,
                                away_key_players_absent: int = 0
                                ) -> tuple:
        """
        Calcule lambda (xG domicile) et mu (xG extérieur) en combinant toutes les sources.
        Retourne: (lambda_adjusted, mu_adjusted, components_dict)
        """
        components = {}

        # ── 1. Base Poisson (Dixon-Robins style) ──
        lambda_base = (home_attack_base * away_defense_base) / league_avg_goals
        mu_base = (away_attack_base * home_defense_base) / league_avg_goals

        # Avantage domicile
        lambda_base += self.home_advantage_xg
        mu_base = max(mu_base, 0.3)
        lambda_base = max(lambda_base, 0.3)
        components['lambda_base'] = lambda_base
        components['mu_base'] = mu_base

        # ── 2. Intégration xG (si dispo) ──
        if home_xg is not None and away_xg is not None:
            # Pondération: 60% xG, 40% Poisson classique
            lambda_xg = home_xg + self.home_advantage_xg * 0.5
            mu_xg = away_xg
            lambda_blended = 0.60 * lambda_xg + 0.40 * lambda_base
            mu_blended = 0.60 * mu_xg + 0.40 * mu_base
            components['lambda_xg_blend'] = lambda_blended
            components['mu_xg_blend'] = mu_blended
        else:
            lambda_blended = lambda_base
            mu_blended = mu_base

        # ── 3. Ajustement ELO ──
        elo_multiplier_home = 1.0
        elo_multiplier_away = 1.0
        if home_team and away_team:
            elo_mult_h = self.elo.to_strength_multiplier(home_team)
            elo_mult_a = self.elo.to_strength_multiplier(away_team)
            # Normaliser pour que le rapport soit conservé
            elo_ratio_h = elo_mult_h / ((elo_mult_h + elo_mult_a) / 2)
            elo_ratio_a = elo_mult_a / ((elo_mult_h + elo_mult_a) / 2)
            # Pondération douce: ELO compte pour 25%
            elo_multiplier_home = 0.75 + 0.25 * elo_ratio_h
            elo_multiplier_away = 0.75 + 0.25 * elo_ratio_a
            components['elo_home'] = self.elo.get_rating(home_team)
            components['elo_away'] = self.elo.get_rating(away_team)

        lambda_elo = lambda_blended * elo_multiplier_home
        mu_elo = mu_blended * elo_multiplier_away

        # ── 4. Ajustement forme récente ──
        form_home_attack, form_home_defense = (1.0, 1.0)
        form_away_attack, form_away_defense = (1.0, 1.0)

        if home_form_results:
            form_home_attack, form_home_defense = compute_attack_defense_form(home_form_results)
            components['form_home_attack'] = form_home_attack
            components['form_home_defense'] = form_home_defense

        if away_form_results:
            form_away_attack, form_away_defense = compute_attack_defense_form(away_form_results)
            components['form_away_attack'] = form_away_attack
            components['form_away_defense'] = form_away_defense

        # Pondération forme: 20%
        form_weight = 0.20
        lambda_form = lambda_elo * (1 - form_weight + form_weight * form_home_attack)
        mu_form = mu_elo * (1 - form_weight + form_weight * form_away_attack)

        # ── 5. Facteurs contextuels ──
        # Fatigue (moins de repos = moins performant)
        REST_OPTIMAL = 7  # jours
        fatigue_home = max(0.88, min(1.0, home_rest_days / REST_OPTIMAL))
        fatigue_away = max(0.88, min(1.0, away_rest_days / REST_OPTIMAL))
        components['fatigue_home'] = fatigue_home
        components['fatigue_away'] = fatigue_away

        # Absences joueurs clés (−4% par absent clé, max −15%)
        absence_home = max(0.85, 1.0 - 0.04 * home_key_players_absent)
        absence_away = max(0.85, 1.0 - 0.04 * away_key_players_absent)
        components['absence_home'] = absence_home
        components['absence_away'] = absence_away

        # ── 6. Lambda/Mu finaux ──
        lambda_final = max(0.20, lambda_form * fatigue_home * absence_home)
        mu_final = max(0.20, mu_form * fatigue_away * absence_away)

        components['lambda_final'] = lambda_final
        components['mu_final'] = mu_final

        return lambda_final, mu_final, components

    def score_matrix(self, lambda_: float, mu_: float, max_goals: int = None) -> np.ndarray:
        """
        Génère la matrice de probabilités des scores avec correction Dixon-Coles.
        shape: (max_goals+1, max_goals+1)
        """
        n = (max_goals or self.MAX_GOALS) + 1
        matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                matrix[i, j] = dixon_coles_probability(i, j, lambda_, mu_, self.rho)

        # Normaliser pour que la somme = 1 (correction numérique)
        total = matrix.sum()
        if total > 0:
            matrix /= total

        return matrix

    def compute_probabilities(self, score_matrix: np.ndarray) -> dict:
        """
        Calcule toutes les probabilités utiles à partir de la matrice de scores.
        """
        probs = {}
        n = score_matrix.shape[0]

        # ── 1N2 ──
        home_win = np.sum(np.tril(score_matrix, -1))  # i > j
        draw = np.sum(np.diag(score_matrix))
        away_win = np.sum(np.triu(score_matrix, 1))

        # Normalisation
        total_1x2 = home_win + draw + away_win
        probs['home_win'] = home_win / total_1x2
        probs['draw'] = draw / total_1x2
        probs['away_win'] = away_win / total_1x2

        # ── Over/Under ──
        for threshold in [1.5, 2.5, 3.5, 4.5]:
            over = 0.0
            for i in range(n):
                for j in range(n):
                    if i + j > threshold:
                        over += score_matrix[i, j]
            probs[f'over_{threshold}'] = over
            probs[f'under_{threshold}'] = 1.0 - over

        # ── BTTS ──
        btts = sum(score_matrix[i, j] for i in range(1, n) for j in range(1, n))
        probs['btts_yes'] = btts
        probs['btts_no'] = 1.0 - btts

        # ── Score le plus probable ──
        idx = np.unravel_index(np.argmax(score_matrix), score_matrix.shape)
        probs['most_likely_score'] = (idx[0], idx[1])
        probs['most_likely_prob'] = score_matrix[idx]

        # ── Top 5 scores ──
        flat = score_matrix.flatten()
        top5_idx = np.argsort(flat)[::-1][:5]
        probs['top_scores'] = [
            (divmod(i, n)[0], divmod(i, n)[1], flat[i])
            for i in top5_idx
        ]

        # ── Double chance ──
        probs['home_or_draw'] = probs['home_win'] + probs['draw']
        probs['away_or_draw'] = probs['away_win'] + probs['draw']
        probs['home_or_away'] = probs['home_win'] + probs['away_win']

        return probs

    def predict_match(self, **kwargs) -> dict:
        """
        Point d'entrée principal. Retourne toutes les prédictions.
        """
        lambda_, mu_, components = self.compute_expected_goals(**kwargs)
        matrix = self.score_matrix(lambda_, mu_)
        probs = self.compute_probabilities(matrix)

        return {
            'lambda': lambda_,
            'mu': mu_,
            'score_matrix': matrix,
            'probabilities': probs,
            'components': components,
            'model': 'Dixon-Coles V3'
        }


# ─────────────────────────────────────────────
# CALIBRATION DES PROBABILITÉS (PLATT SCALING)
# ─────────────────────────────────────────────

class ProbabilityCalibrator:
    """
    Calibre les probabilités brutes du modèle pour éviter les biais.
    Utilise une régression logistique (Platt scaling) ou isotonic regression.
    """

    def __init__(self):
        self.is_fitted = False
        self.params = {'a': 1.0, 'b': 0.0}  # P_calib = sigmoid(a * logit(p) + b)

    def _logit(self, p: float) -> float:
        p = np.clip(p, 1e-6, 1 - 1e-6)
        return np.log(p / (1 - p))

    def _sigmoid(self, x: float) -> float:
        return 1.0 / (1.0 + np.exp(-x))

    def fit(self, raw_probs: list, outcomes: list):
        """
        raw_probs: probabilités brutes du modèle [0,1]
        outcomes: résultats réels (1 = événement réalisé, 0 sinon)
        """
        from scipy.optimize import minimize as sp_minimize

        def neg_log_likelihood(params):
            a, b = params
            total = 0.0
            for p, y in zip(raw_probs, outcomes):
                p_cal = self._sigmoid(a * self._logit(p) + b)
                p_cal = np.clip(p_cal, 1e-10, 1 - 1e-10)
                total -= y * np.log(p_cal) + (1 - y) * np.log(1 - p_cal)
            return total

        result = sp_minimize(neg_log_likelihood, [1.0, 0.0], method='Nelder-Mead')
        self.params['a'] = result.x[0]
        self.params['b'] = result.x[1]
        self.is_fitted = True

    def calibrate(self, p: float) -> float:
        """Applique la calibration à une probabilité brute."""
        if not self.is_fitted:
            return p
        return self._sigmoid(self.params['a'] * self._logit(p) + self.params['b'])

    def calibrate_all(self, probs: dict) -> dict:
        """Calibre toutes les probabilités 1N2 d'un dictionnaire."""
        calibrated = probs.copy()
        for key in ['home_win', 'draw', 'away_win']:
            if key in probs:
                calibrated[f'{key}_calibrated'] = self.calibrate(probs[key])
        return calibrated
