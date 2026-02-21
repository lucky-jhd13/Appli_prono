# ─────────────────────────────────────────────
# ui/composants.py — Composants HTML & helpers visuels
# ─────────────────────────────────────────────

from style import couleur_prob

def forme_html(form_str: str) -> str:
    """Génère les badges colorés de forme (V/N/D)."""
    mapping = {"W": ("forme-w", "V"), "D": ("forme-d", "N"), "L": ("forme-l", "D")}
    badges = []
    for c in form_str.upper():
        cls, label = mapping.get(c, ("forme-d", "?"))
        badges.append(f'<span class="{cls}">{label}</span>')
    return f'<div class="forme-container">{"".join(badges)}</div>'

def match_header_html(
    n1: str, n2: str,
    logo1: str, logo2: str,
    p1: float, pn: float, p2: float,
    forme1: str, forme2: str,
) -> str:
    """Bloc HTML principal d'en-tête de match."""
    c1 = couleur_prob(p1)
    c2 = couleur_prob(p2)
    cn = couleur_prob(pn)
    return f"""
    <div class="match-header">
        <div class="team-block">
            <img class="team-logo" src="{logo1}" onerror="this.style.display='none'">
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
            <img class="team-logo" src="{logo2}" onerror="this.style.display='none'">
            <p class="team-name">{n2}</p>
            <div class="prob-big" style="color:{c2}">{p2*100:.1f}%</div>
            <div class="prob-label">Victoire Extérieur</div>
            {forme_html(forme2)}
        </div>
    </div>
    """


def stat_grid_html(s: dict, lambda_val: float, color: str) -> str:
    """Grille 3×2 de statistiques pour une équipe."""
    diff_cls = "diff-neg" if s["diff"] < 0 else "diff-pos"
    diff_str = f"+{s['diff']}" if s["diff"] > 0 else str(s["diff"])
    return f"""
    <div class="stat-grid">
        <div class="stat-card"><span class="stat-value">{s['mbp']:.2f}</span><span class="stat-label">Buts / match</span></div>
        <div class="stat-card"><span class="stat-value">{s['mbc']:.2f}</span><span class="stat-label">Encaissés / match</span></div>
        <div class="stat-card"><span class="stat-value">{s['pts_par_match']:.2f}</span><span class="stat-label">Pts / match</span></div>
        <div class="stat-card"><span class="stat-value">{s['won']}</span><span class="stat-label">Victoires</span></div>
        <div class="stat-card"><span class="stat-value">{s['draw']}</span><span class="stat-label">Nuls</span></div>
        <div class="stat-card"><span class="stat-value {diff_cls}">{diff_str}</span><span class="stat-label">Diff buts</span></div>
    </div>
    <p style="font-size:0.8rem;opacity:0.55;">λ (Expected Goals) : <strong style="color:{color}">{lambda_val:.2f}</strong></p>
    """


def verdict_card_html(
    titre: str, valeur: str, prob: float,
    badge: str, info_extra: str = ""
) -> str:
    return f"""
    <div class="verdict-card">
        <div class="verdict-title">{titre}</div>
        <div class="verdict-main">{valeur}</div>
        <div class="verdict-prob">{prob*100:.1f}% de confiance</div>
        {badge}
        <div style="font-size:0.8rem;opacity:0.5;margin-top:6px;">{info_extra}</div>
    </div>
    """


def kelly_html(kelly: float, value: bool) -> str:
    if value:
        return f'<div class="kelly-box">🔥 <strong>VALUE BET</strong><br>Kelly : miser <strong>{kelly*100:.1f}%</strong> de ta bankroll</div>'
    return '<div class="kelly-box-neg">Pas de value sur ce marché.</div>'
