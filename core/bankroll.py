"""
PRO-FOOT AI V3 — Bankroll Tracker & Backtesting
Historique des paris, ROI, simulation de stratégie
"""

import json
import os
from datetime import datetime, date
from dataclasses import dataclass, asdict, field
from typing import Optional
import numpy as np


# ─────────────────────────────────────────────
# STRUCTURES
# ─────────────────────────────────────────────

@dataclass
class BetRecord:
    id: str
    date: str
    match: str
    bet_type: str
    odd: float
    stake: float
    model_prob: float
    confidence_score: float
    status: str = "pending"     # pending / won / lost / void
    profit: float = 0.0
    bankroll_after: float = 0.0
    notes: str = ""


# ─────────────────────────────────────────────
# BANKROLL TRACKER
# ─────────────────────────────────────────────

class BankrollTracker:
    """
    Suit l'évolution de la bankroll et calcule les métriques de performance.
    Persistance: JSON local (compatible Streamlit session_state)
    """

    def __init__(self, initial_bankroll: float = 1000.0, storage_path: str = None):
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.storage_path = storage_path or "data/bankroll.json"
        self.bets: list = []
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.initial_bankroll = data.get('initial_bankroll', self.initial_bankroll)
                    self.current_bankroll = data.get('current_bankroll', self.initial_bankroll)
                    self.bets = [BetRecord(**b) for b in data.get('bets', [])]
            except Exception:
                pass

    def _save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump({
                'initial_bankroll': self.initial_bankroll,
                'current_bankroll': self.current_bankroll,
                'bets': [asdict(b) for b in self.bets]
            }, f, indent=2, default=str)

    def add_bet(self, match: str, bet_type: str, odd: float, stake: float,
                model_prob: float, confidence_score: float, notes: str = "") -> BetRecord:
        bet = BetRecord(
            id=f"bet_{len(self.bets)+1:04d}",
            date=datetime.now().strftime('%Y-%m-%d %H:%M'),
            match=match,
            bet_type=bet_type,
            odd=odd,
            stake=stake,
            model_prob=model_prob,
            confidence_score=confidence_score,
            notes=notes
        )
        self.bets.append(bet)
        self._save()
        return bet

    def resolve_bet(self, bet_id: str, won: bool):
        for bet in self.bets:
            if bet.id == bet_id:
                if won:
                    bet.status = 'won'
                    bet.profit = bet.stake * (bet.odd - 1)
                else:
                    bet.status = 'lost'
                    bet.profit = -bet.stake
                self.current_bankroll += bet.profit
                bet.bankroll_after = self.current_bankroll
                self._save()
                return bet
        return None

    def get_stats(self) -> dict:
        settled = [b for b in self.bets if b.status in ('won', 'lost')]
        if not settled:
            return self._empty_stats()

        wins = [b for b in settled if b.status == 'won']
        losses = [b for b in settled if b.status == 'lost']

        total_staked = sum(b.stake for b in settled)
        total_profit = sum(b.profit for b in settled)
        roi = (total_profit / total_staked * 100) if total_staked > 0 else 0.0
        win_rate = len(wins) / len(settled) * 100

        # Yield moyen
        yield_avg = np.mean([b.profit / b.stake for b in settled]) * 100 if settled else 0

        # Drawdown maximum
        bankroll_series = [self.initial_bankroll] + [
            b.bankroll_after for b in sorted(settled, key=lambda x: x.date)
            if b.bankroll_after > 0
        ]
        max_drawdown = self._max_drawdown(bankroll_series)

        # Stats par niveau de confiance
        high_conf = [b for b in settled if b.confidence_score >= 70]
        high_conf_roi = (
            sum(b.profit for b in high_conf) / sum(b.stake for b in high_conf) * 100
            if high_conf and sum(b.stake for b in high_conf) > 0 else 0
        )

        return {
            'n_bets': len(settled),
            'n_wins': len(wins),
            'n_losses': len(losses),
            'win_rate': round(win_rate, 1),
            'total_staked': round(total_staked, 2),
            'total_profit': round(total_profit, 2),
            'roi': round(roi, 2),
            'yield_avg': round(yield_avg, 2),
            'current_bankroll': round(self.current_bankroll, 2),
            'max_drawdown': round(max_drawdown, 2),
            'bankroll_growth': round(
                (self.current_bankroll - self.initial_bankroll) / self.initial_bankroll * 100, 2
            ),
            'high_conf_roi': round(high_conf_roi, 2),
            'avg_odd': round(np.mean([b.odd for b in settled]), 2),
            'avg_confidence': round(np.mean([b.confidence_score for b in settled]), 1),
        }

    def _max_drawdown(self, series: list) -> float:
        if len(series) < 2:
            return 0.0
        peak = series[0]
        max_dd = 0.0
        for val in series:
            peak = max(peak, val)
            dd = (peak - val) / peak * 100
            max_dd = max(max_dd, dd)
        return max_dd

    def _empty_stats(self) -> dict:
        return {
            'n_bets': 0, 'n_wins': 0, 'n_losses': 0, 'win_rate': 0,
            'total_staked': 0, 'total_profit': 0, 'roi': 0, 'yield_avg': 0,
            'current_bankroll': self.current_bankroll, 'max_drawdown': 0,
            'bankroll_growth': 0, 'high_conf_roi': 0, 'avg_odd': 0, 'avg_confidence': 0
        }

    def get_bankroll_history(self) -> list:
        """Retourne l'évolution de la bankroll pour le graphique."""
        settled_sorted = sorted(
            [b for b in self.bets if b.status in ('won', 'lost')],
            key=lambda x: x.date
        )
        history = [{'date': 'Start', 'bankroll': self.initial_bankroll, 'bet': ''}]
        for b in settled_sorted:
            history.append({
                'date': b.date[:10],
                'bankroll': b.bankroll_after,
                'bet': f"{b.match} ({b.bet_type})",
                'profit': b.profit
            })
        return history


# ─────────────────────────────────────────────
# BACKTESTING ENGINE
# ─────────────────────────────────────────────

class BacktestEngine:
    """
    Simule une stratégie sur des données historiques.
    Calcule performance, ROI, Sharpe, drawdown.
    """

    def __init__(self, initial_bankroll: float = 1000.0):
        self.initial_bankroll = initial_bankroll

    def run(self,
            historical_bets: list,
            strategy: str = 'kelly_quarter',
            kelly_fraction: float = 0.25,
            fixed_stake_pct: float = 0.02,
            min_confidence: float = 0.0,
            min_edge: float = 0.03) -> dict:
        """
        historical_bets: liste de dicts avec:
            - model_prob, odd, outcome (1=won, 0=lost), confidence_score, edge
        """
        bankroll = self.initial_bankroll
        bankroll_history = [bankroll]
        results = []
        skipped = 0

        for bet in historical_bets:
            # Filtres
            if bet.get('confidence_score', 100) < min_confidence:
                skipped += 1
                continue
            if bet.get('edge', 1.0) < min_edge:
                skipped += 1
                continue

            # Calcul de la mise
            if strategy == 'kelly_quarter':
                b = bet['odd'] - 1
                f = (bet['model_prob'] * b - (1 - bet['model_prob'])) / b
                stake_pct = max(0, f * kelly_fraction)
                stake_pct = min(stake_pct, 0.05)
            elif strategy == 'fixed_1pct':
                stake_pct = 0.01
            elif strategy == 'fixed_2pct':
                stake_pct = 0.02
            else:
                stake_pct = fixed_stake_pct

            stake = bankroll * stake_pct
            if stake < 0.01:
                continue

            # Résultat
            if bet['outcome'] == 1:
                profit = stake * (bet['odd'] - 1)
            else:
                profit = -stake

            bankroll += profit
            bankroll = max(0.01, bankroll)  # Évite bankroll < 0
            bankroll_history.append(bankroll)

            results.append({
                'stake': stake,
                'profit': profit,
                'bankroll': bankroll,
                'odd': bet['odd'],
                'outcome': bet['outcome'],
                'confidence': bet.get('confidence_score', 0),
                'edge': bet.get('edge', 0),
            })

        if not results:
            return {'error': 'Aucun pari valide avec ces filtres', 'skipped': skipped}

        profits = [r['profit'] for r in results]
        stakes = [r['stake'] for r in results]

        total_staked = sum(stakes)
        total_profit = sum(profits)
        roi = total_profit / total_staked * 100 if total_staked > 0 else 0
        win_rate = sum(1 for r in results if r['outcome'] == 1) / len(results) * 100

        # Sharpe (simplifié, annualisé sur 200 paris)
        returns = [p / s for p, s in zip(profits, stakes)]
        sharpe = (np.mean(returns) / np.std(returns) * np.sqrt(200)) if np.std(returns) > 0 else 0

        # Max drawdown
        peak = self.initial_bankroll
        max_dd = 0.0
        for bk in bankroll_history:
            peak = max(peak, bk)
            dd = (peak - bk) / peak * 100
            max_dd = max(max_dd, dd)

        return {
            'strategy': strategy,
            'n_bets': len(results),
            'n_skipped': skipped,
            'win_rate': round(win_rate, 1),
            'total_staked': round(total_staked, 2),
            'total_profit': round(total_profit, 2),
            'roi': round(roi, 2),
            'final_bankroll': round(bankroll, 2),
            'bankroll_growth_pct': round((bankroll - self.initial_bankroll) / self.initial_bankroll * 100, 2),
            'max_drawdown_pct': round(max_dd, 2),
            'sharpe': round(sharpe, 3),
            'bankroll_history': bankroll_history,
            'avg_stake': round(np.mean(stakes), 2),
            'best_run': round(max(profits), 2),
            'worst_run': round(min(profits), 2),
        }

    def compare_strategies(self, historical_bets: list) -> list:
        """Compare toutes les stratégies disponibles."""
        strategies = [
            ('kelly_quarter', {}),
            ('fixed_1pct', {}),
            ('fixed_2pct', {}),
        ]
        results = []
        for strategy, kwargs in strategies:
            r = self.run(historical_bets, strategy=strategy, **kwargs)
            if 'error' not in r:
                results.append(r)
        results.sort(key=lambda x: x['roi'], reverse=True)
        return results
