"""
PRO-FOOT AI V3 — Module Value Betting & Kelly Criterion avancé
Détection intelligente des value bets + sizing des mises
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# ─────────────────────────────────────────────
# STRUCTURES DE DONNÉES
# ─────────────────────────────────────────────

class BetType(Enum):
    HOME_WIN = "1"
    DRAW = "X"
    AWAY_WIN = "2"
    OVER_25 = "O2.5"
    UNDER_25 = "U2.5"
    OVER_15 = "O1.5"
    BTTS_YES = "BTTS+"
    BTTS_NO = "BTTS-"
    HOME_OR_DRAW = "1X"
    AWAY_OR_DRAW = "X2"


@dataclass
class ValueBet:
    match: str
    bet_type: BetType
    model_prob: float          # Probabilité modèle
    bookmaker_odd: float       # Cote bookmaker
    implied_prob: float        # Probabilité implicite bookmaker
    edge: float                # Edge = model_prob - implied_prob
    edge_pct: float            # Edge en %
    kelly_fraction: float      # Mise Kelly fractionnée
    confidence_score: float    # Score propriétaire [0, 100]
    expected_value: float      # EV par unité misée
    label: str = ""            # 🔥 value / ⚠️ risky / 💎 premium
    explanation: str = ""      # Explication auto

    # Détails pour audit
    model_components: dict = field(default_factory=dict)


# ─────────────────────────────────────────────
# CONVERTISSEURS DE COTES
# ─────────────────────────────────────────────

def odd_to_prob(odd: float) -> float:
    """Cote décimale → probabilité implicite (avec marge bookmaker)."""
    return 1.0 / odd if odd > 1 else 0.0


def remove_vig(probs_implied: dict) -> dict:
    """
    Retire la marge bookmaker (vig) des probabilités implicites.
    Méthode: normalisation par la somme des probabilités implicites.
    """
    total = sum(probs_implied.values())
    if total <= 0:
        return probs_implied
    return {k: v / total for k, v in probs_implied.items()}


def margin_from_odds(odds: list) -> float:
    """Calcule la marge bookmaker (overround)."""
    return sum(1 / o for o in odds if o > 1) - 1.0


# ─────────────────────────────────────────────
# KELLY CRITERION AVANCÉ
# ─────────────────────────────────────────────

class KellyCalculator:
    """
    Kelly Criterion fractionné avec gestion du risque.
    """

    KELLY_FRACTION = 0.25    # Kelly 1/4 (conservateur)
    MAX_BET_PCT = 0.05       # Cap max: 5% de la bankroll
    MIN_EDGE = 0.03          # Edge minimum pour parier (3%)
    MIN_ODD = 1.30           # Cote minimale acceptable

    def __init__(self,
                 kelly_fraction: float = None,
                 max_bet_pct: float = None,
                 min_edge: float = None):
        self.kelly_fraction = kelly_fraction or self.KELLY_FRACTION
        self.max_bet_pct = max_bet_pct or self.MAX_BET_PCT
        self.min_edge = min_edge or self.MIN_EDGE

    def full_kelly(self, prob: float, odd: float) -> float:
        """
        Kelly complet: f = (p * b - q) / b
        où b = odd - 1, p = probabilité modèle, q = 1 - p
        """
        b = odd - 1.0
        if b <= 0 or prob <= 0:
            return 0.0
        q = 1.0 - prob
        f = (prob * b - q) / b
        return max(0.0, f)

    def fractional_kelly(self, prob: float, odd: float) -> float:
        """Kelly fractionné + cap max."""
        fk = self.full_kelly(prob, odd)
        fractional = fk * self.kelly_fraction
        return min(fractional, self.max_bet_pct)

    def stake_amount(self, bankroll: float, prob: float, odd: float) -> float:
        """Montant à miser en euros/unités."""
        fraction = self.fractional_kelly(prob, odd)
        return bankroll * fraction

    def is_worth_betting(self, edge: float, odd: float) -> bool:
        return edge >= self.min_edge and odd >= self.MIN_ODD


# ─────────────────────────────────────────────
# SCORE DE CONFIANCE PROPRIÉTAIRE
# ─────────────────────────────────────────────

class ConfidenceScorer:
    """
    Score propriétaire combinant plusieurs signaux de qualité.
    Score final: 0-100 (100 = signal parfait)
    """

    # Pondérations des composantes
    WEIGHTS = {
        'edge': 0.35,           # Edge modèle vs bookmaker
        'model_prob': 0.20,     # Force de la probabilité modèle
        'stability': 0.20,      # Stabilité/cohérence des features
        'odd_quality': 0.15,    # Qualité de la cote (ni trop basse, ni suspecte)
        'data_quality': 0.10,   # Qualité des données d'entrée
    }

    def compute(self,
                model_prob: float,
                implied_prob: float,
                odd: float,
                components: dict,
                data_completeness: float = 1.0) -> dict:
        """
        Calcule le score de confiance détaillé.
        data_completeness: 0-1, proportion de features disponibles
        """
        scores = {}

        # ── 1. Score Edge ──
        edge = model_prob - implied_prob
        edge_score = self._score_edge(edge)
        scores['edge'] = edge_score

        # ── 2. Score probabilité modèle ──
        # Une probabilité claire (>45% ou <25%) est plus fiable qu'une zone grise
        prob_score = self._score_probability(model_prob)
        scores['model_prob'] = prob_score

        # ── 3. Score stabilité (cohérence des features) ──
        stability_score = self._score_stability(components)
        scores['stability'] = stability_score

        # ── 4. Score qualité de cote ──
        odd_score = self._score_odd(odd)
        scores['odd_quality'] = odd_score

        # ── 5. Score qualité données ──
        data_score = data_completeness * 100
        scores['data_quality'] = data_score

        # ── Score final pondéré ──
        final = sum(
            scores[k] * self.WEIGHTS[k]
            for k in self.WEIGHTS
        )
        final = np.clip(final, 0, 100)

        return {
            'total': round(final, 1),
            'components': scores,
            'grade': self._grade(final)
        }

    def _score_edge(self, edge: float) -> float:
        """Edge 3-15% = excellent."""
        if edge < 0:
            return 0.0
        elif edge < 0.03:
            return edge / 0.03 * 40  # 0-40
        elif edge <= 0.12:
            return 40 + (edge - 0.03) / 0.09 * 60  # 40-100
        else:
            # Edge trop élevé = suspect
            return max(50, 100 - (edge - 0.12) * 200)

    def _score_probability(self, p: float) -> float:
        """Signal clair = confiance haute."""
        if p >= 0.55 or p <= 0.20:
            return 90.0
        elif p >= 0.45 or p <= 0.30:
            return 65.0
        else:
            return 40.0  # Zone grise

    def _score_stability(self, components: dict) -> float:
        """
        Mesure si les différents signaux (xG, ELO, forme) convergent.
        """
        score = 50.0  # Base

        # Bonus si xG disponible
        if 'lambda_xg_blend' in components:
            score += 20.0

        # Bonus si ELO disponible
        if 'elo_home' in components:
            score += 15.0

        # Bonus si forme disponible
        if 'form_home_attack' in components:
            score += 10.0

        # Vérification cohérence: lambda et mu pas trop extrêmes
        lambda_ = components.get('lambda_final', 1.4)
        mu_ = components.get('mu_final', 1.1)
        if 0.5 <= lambda_ <= 3.0 and 0.3 <= mu_ <= 2.5:
            score += 5.0
        else:
            score -= 10.0

        return min(100.0, score)

    def _score_odd(self, odd: float) -> float:
        """Cotes entre 1.5 et 4.0 = zone idéale Kelly."""
        if 1.50 <= odd <= 2.50:
            return 90.0
        elif 1.30 <= odd < 1.50 or 2.50 < odd <= 4.00:
            return 65.0
        elif 1.15 <= odd < 1.30:
            return 35.0
        else:
            return 20.0  # Cote très haute = incertitude forte

    def _grade(self, score: float) -> str:
        if score >= 80:
            return 'A'
        elif score >= 65:
            return 'B'
        elif score >= 50:
            return 'C'
        else:
            return 'D'


# ─────────────────────────────────────────────
# DÉTECTEUR DE VALUE BETS
# ─────────────────────────────────────────────

class ValueBetDetector:
    """
    Détecte et classe les value bets.
    Combine model probs + cotes bookmaker + seuils dynamiques.
    """

    # Seuil edge DYNAMIQUE selon la probabilité
    DYNAMIC_THRESHOLDS = {
        # (p_min, p_max): edge_min
        (0.00, 0.20): 0.04,  # Outsider: edge requis plus fort
        (0.20, 0.40): 0.04,
        (0.40, 0.60): 0.03,  # Milieu: edge standard
        (0.60, 0.80): 0.025,
        (0.80, 1.00): 0.02,  # Favori: edge plus faible acceptable
    }

    def __init__(self,
                 kelly_calc: KellyCalculator = None,
                 confidence_scorer: ConfidenceScorer = None):
        self.kelly = kelly_calc or KellyCalculator()
        self.scorer = confidence_scorer or ConfidenceScorer()

    def _dynamic_threshold(self, prob: float) -> float:
        """Seuil d'edge dynamique basé sur la probabilité."""
        for (p_min, p_max), threshold in self.DYNAMIC_THRESHOLDS.items():
            if p_min <= prob < p_max:
                return threshold
        return 0.04

    def _get_label(self, confidence: float, edge: float) -> str:
        """Attribue un badge au bet."""
        if confidence >= 80 and edge >= 0.07:
            return "💎 PREMIUM"
        elif confidence >= 65 and edge >= 0.04:
            return "🔥 VALUE"
        elif confidence < 50 or edge < 0.03:
            return "⚠️ RISKY"
        else:
            return "✅ GOOD"

    def _generate_explanation(self, bet: dict) -> str:
        """Génère une explication automatique de la value."""
        edge_pct = bet['edge'] * 100
        model_pct = bet['model_prob'] * 100
        implied_pct = bet['implied_prob'] * 100

        lines = [
            f"📊 Probabilité modèle: {model_pct:.1f}% vs probabilité implicite: {implied_pct:.1f}%",
            f"📈 Edge détecté: +{edge_pct:.1f}% en faveur du modèle",
        ]

        if bet.get('xg_available'):
            lines.append("⚡ Signal xG intégré — renforce la confiance")
        if bet.get('elo_available'):
            lines.append(f"🏆 ELO: {bet.get('elo_diff', 0):+.0f} pts d'écart")
        if bet.get('form_signal') == 'strong':
            lines.append("📈 Forme récente favorable à ce pari")

        lines.append(
            f"💰 Kelly fractionné recommande {bet['kelly_fraction'] * 100:.1f}% de bankroll"
        )

        return " | ".join(lines)

    def analyze_match(self,
                       match_name: str,
                       model_probs: dict,
                       bookmaker_odds: dict,
                       components: dict,
                       data_completeness: float = 0.8) -> list:
        """
        Analyse un match et retourne la liste des value bets détectés.

        model_probs: {'home_win': 0.52, 'draw': 0.26, 'away_win': 0.22, ...}
        bookmaker_odds: {'home_win': 1.90, 'draw': 3.50, 'away_win': 4.20, ...}
        """
        value_bets = []

        # Mapping bet_type → clé dans model_probs
        BET_MAP = {
            BetType.HOME_WIN: 'home_win',
            BetType.DRAW: 'draw',
            BetType.AWAY_WIN: 'away_win',
            BetType.OVER_25: 'over_2.5',
            BetType.UNDER_25: 'under_2.5',
            BetType.OVER_15: 'over_1.5',
            BetType.BTTS_YES: 'btts_yes',
            BetType.BTTS_NO: 'btts_no',
        }

        # Retirer la vig bookmaker
        implied_raw = {k: odd_to_prob(v) for k, v in bookmaker_odds.items() if v > 1}
        implied_fair = remove_vig(implied_raw)

        for bet_type, prob_key in BET_MAP.items():
            if prob_key not in model_probs:
                continue
            odd_key = prob_key
            if odd_key not in bookmaker_odds:
                continue

            model_prob = model_probs[prob_key]
            odd = bookmaker_odds[odd_key]
            implied_prob = implied_fair.get(odd_key, odd_to_prob(odd))

            edge = model_prob - implied_prob
            threshold = self._dynamic_threshold(model_prob)

            # Filtrage: ignorer les non-values
            if edge < threshold:
                continue

            # Kelly
            kelly_frac = self.kelly.fractional_kelly(model_prob, odd)
            if kelly_frac <= 0:
                continue

            # EV
            ev = model_prob * (odd - 1) - (1 - model_prob)

            # Score confiance
            conf_result = self.scorer.compute(
                model_prob, implied_prob, odd, components, data_completeness
            )
            confidence = conf_result['total']

            # Infos pour explication
            bet_meta = {
                'edge': edge,
                'model_prob': model_prob,
                'implied_prob': implied_prob,
                'kelly_fraction': kelly_frac,
                'xg_available': 'lambda_xg_blend' in components,
                'elo_available': 'elo_home' in components,
                'elo_diff': (components.get('elo_home', 1500) - components.get('elo_away', 1500)),
                'form_signal': 'strong' if components.get('form_home_attack', 1) > 1.1 else 'normal',
            }

            label = self._get_label(confidence, edge)
            explanation = self._generate_explanation(bet_meta)

            vb = ValueBet(
                match=match_name,
                bet_type=bet_type,
                model_prob=model_prob,
                bookmaker_odd=odd,
                implied_prob=implied_prob,
                edge=edge,
                edge_pct=edge * 100,
                kelly_fraction=kelly_frac,
                confidence_score=confidence,
                expected_value=ev,
                label=label,
                explanation=explanation,
                model_components=components
            )
            value_bets.append(vb)

        # Trier par score de confiance décroissant
        value_bets.sort(key=lambda x: x.confidence_score, reverse=True)
        return value_bets

    def portfolio_analysis(self, all_bets: list, bankroll: float) -> dict:
        """
        Analyse du portefeuille de paris du jour.
        Calcule la mise optimale totale et les statistiques.
        """
        if not all_bets:
            return {'total_stake': 0, 'bets': [], 'risk_level': 'N/A'}

        premium = [b for b in all_bets if '💎' in b.label]
        good_value = [b for b in all_bets if '🔥' in b.label]

        total_kelly = sum(b.kelly_fraction for b in all_bets)
        # Cap: max 20% de bankroll total tous paris confondus
        scale_factor = min(1.0, 0.20 / total_kelly) if total_kelly > 0 else 1.0

        portfolio = []
        for bet in all_bets:
            scaled_kelly = bet.kelly_fraction * scale_factor
            stake = bankroll * scaled_kelly
            portfolio.append({
                'match': bet.match,
                'bet': bet.bet_type.value,
                'odd': bet.bookmaker_odd,
                'stake': round(stake, 2),
                'stake_pct': round(scaled_kelly * 100, 2),
                'ev': round(bet.expected_value * stake, 2),
                'confidence': bet.confidence_score,
                'label': bet.label,
            })

        avg_confidence = np.mean([b.confidence_score for b in all_bets])
        avg_ev = np.mean([b.expected_value for b in all_bets])

        return {
            'total_stake': round(sum(p['stake'] for p in portfolio), 2),
            'bets': portfolio,
            'n_premium': len(premium),
            'n_value': len(good_value),
            'avg_confidence': round(avg_confidence, 1),
            'avg_ev': round(avg_ev, 4),
            'risk_level': 'HIGH' if avg_confidence < 55 else 'MEDIUM' if avg_confidence < 70 else 'LOW',
        }
