# ─────────────────────────────────────────────
# ui/composants.py — Composants UI purs (HTML / Streamlit Wrappers)
# ─────────────────────────────────────────────

from typing import Dict, Any, Tuple
from style import couleur_prob
from core.stats import StatsEquipe


def forme_html(form_str: str) -> str:
    """Génère la composante visuelle (série de badges) pour le momentum V/N/D."""
    # Couleure le badge selon match gagné/nul/perdu
    mapping = {
        "W": ("forme-w", "V"), 
        "D": ("forme-d", "N"), 
        "L": ("forme-l", "D")
    }
    
    badges = []
    # On garantit qu'on parse un objet chaine s'il n'est pas None
    for c in (form_str or "").upper():
        cls, label = mapping.get(c, ("forme-d", "?"))
        badges.append(f'<span class="{cls}">{label}</span>')
        
    return f'<div class="forme-container">{"".join(badges)}</div>'


def match_header_html(
    n1: str, n2: str,
    logo1: str, logo2: str,
    p1: float, pn: float, p2: float,
    forme1: str, forme2: str,
) -> str:
    """Design principal de la cartouche 'Affrontement' en top header."""
    c1 = couleur_prob(p1)
    c2 = couleur_prob(p2)
    cn = couleur_prob(pn)
    return f"""
<div class="match-header">
    <div class="team-block">
        <img class="team-logo" src="{logo1}" onerror="this.style.display='none'" alt="{n1}">
        <p class="team-name">{n1}</p>
        <div class="prob-big" style="color:{c1}">{p1*100:.1f}%</div>
        <div class="prob-label">Victoire Domicile</div>
        {forme_html(forme1)}
    </div>
    <div class="vs-block">VS</div>
    <div class="team-block" style="opacity:0.75">
        <div class="prob-big" style="color:{cn}">{pn*100:.1f}%</div>
        <div class="prob-label">Match Nul</div>
    </div>
    <div class="vs-block" style="opacity:0.3">·</div>
    <div class="team-block">
        <img class="team-logo" src="{logo2}" onerror="this.style.display='none'" alt="{n2}">
        <p class="team-name">{n2}</p>
        <div class="prob-big" style="color:{c2}">{p2*100:.1f}%</div>
        <div class="prob-label">Victoire Extérieur</div>
        {forme_html(forme2)}
    </div>
</div>
"""


def stat_grid_html(s: StatsEquipe, lambda_val: float, color: str) -> str:
    """Grille Data (Stats de base + Lambda Expected Goals) formatée HTML 3x2."""
    diff_val = s.get("diff", 0)
    diff_cls = "diff-neg" if diff_val < 0 else "diff-pos"
    diff_str = f"+{diff_val}" if diff_val > 0 else str(diff_val)
    return f"""
<div class="stat-grid">
    <div class="stat-card">
        <span class="stat-value">{s.get('mbp', 0.0):.2f}</span>
        <span class="stat-label">Buts M/match</span>
    </div>
    <div class="stat-card">
        <span class="stat-value">{s.get('mbc', 0.0):.2f}</span>
        <span class="stat-label">Encaissés/match</span>
    </div>
    <div class="stat-card">
        <span class="stat-value">{s.get('pts_par_match', 0.0):.2f}</span>
        <span class="stat-label">Pts / match</span>
    </div>
    <div class="stat-card">
        <span class="stat-value">{s.get('won', 0)}</span>
        <span class="stat-label">Victoires</span>
    </div>
    <div class="stat-card">
        <span class="stat-value">{s.get('draw', 0)}</span>
        <span class="stat-label">Nuls</span>
    </div>
    <div class="stat-card">
        <span class="stat-value {diff_cls}">{diff_str}</span>
        <span class="stat-label">Diff. Buts</span>
    </div>
</div>
<p style="font-size:0.8rem;opacity:0.55;">
    λ (Expected Goals Modélisés) : <strong style="color:{color}">{lambda_val:.2f}</strong>
</p>
"""


def verdict_card_html(
    titre: str, valeur: str, prob: float,
    badge: str, info_extra: str = ""
) -> str:
    """Carte de verdict qui donne la Value / Confidence."""
    return f"""
<div class="verdict-card">
    <div class="verdict-title">{titre}</div>
    <div class="verdict-main">{valeur}</div>
    <div class="verdict-prob">{prob*100:.1f}% de confiance</div>
    {badge}
    <div style="font-size:0.8rem;opacity:0.5;margin-top:6px;">{info_extra}</div>
</div>
"""


def kelly_html(kelly: float, is_value: bool) -> str:
    """Injection de recommandation de BankRoll (Kelly fraction)."""
    if is_value and kelly > 0:
        return f'<div class="kelly-box">🔥 <strong>VALUE BET</strong><br>Kelly : miser <strong>{kelly*100:.1f}%</strong> de ta bankroll max</div>'
    return '<div class="kelly-box-neg">Pas de Value identifiée sur cette cote bookmaker.</div>'
