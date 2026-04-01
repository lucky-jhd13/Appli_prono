# ─────────────────────────────────────────────
# ui/graphiques.py — Graphiques interactifs (Plotly)
# ─────────────────────────────────────────────

import plotly.graph_objects as go
from typing import Dict, Any, List
from core.stats import StatsEquipe


def fig_radar(s1: StatsEquipe, s2: StatsEquipe, n1: str, n2: str, c: Dict[str, str]) -> go.Figure:
    """Superpose 2 profils d'équipes en radar pour voir d'un bloc leurs qualités."""
    cats: List[str] = ["Attaque", "Défense", "Victoires", "Constance"]
    
    # On boucle la donnée pour fermer le polygone (dernier point = 1er point)
    r1 = list(s1["radar"]) + [s1["radar"][0]]
    r2 = list(s2["radar"]) + [s2["radar"][0]]
    theta = cats + [cats[0]]
    
    fig = go.Figure()
    
    # Trace Domicile
    fig.add_trace(go.Scatterpolar(
        r=r1, theta=theta,
        fill="toself", name=n1,
        line=dict(color=c["acc"], width=2),
        fillcolor=c.get("acc_alpha", "rgba(59,130,246,0.15)")
    ))
    
    # Trace Extérieur
    fig.add_trace(go.Scatterpolar(
        r=r2, theta=theta,
        fill="toself", name=n2,
        line=dict(color=c.get("danger", "#ef4444"), width=2),
        fillcolor=c.get("danger_alpha", "rgba(239,68,68,0.15)")
    ))
    
    # Ajustements cosmétiques
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=c["grid"], tickfont=dict(color=c["txt"], size=9)),
            angularaxis=dict(gridcolor=c["grid"], tickfont=dict(color=c["txt"], size=11))
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=c["txt"]),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=c["txt"])),
        height=380, 
        margin=dict(l=40, r=40, t=30, b=30)
    )
    return fig


def fig_barres(s1: StatsEquipe, s2: StatsEquipe, n1: str, n2: str, c: Dict[str, str]) -> go.Figure:
    """Histogramme groupé comparant les KPIs réels de jeu."""
    cats = ["Buts Marq/match", "Encaissés/match", "Pts/match", "Diff de buts"]
    
    v1 = [round(s1["mbp"], 2), round(s1["mbc"], 2), round(s1["pts_par_match"], 2), s1["diff"]]
    v2 = [round(s2["mbp"], 2), round(s2["mbc"], 2), round(s2["pts_par_match"], 2), s2["diff"]]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name=n1, x=cats, y=v1, marker_color=c["acc"], opacity=0.85))
    fig.add_trace(go.Bar(name=n2, x=cats, y=v2, marker_color=c.get("danger", "#ef4444"), opacity=0.85))
    
    fig.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=c["txt"]),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=c["txt"])),
        height=280, 
        margin=dict(l=20, r=20, t=20, b=40),
        xaxis=dict(gridcolor=c["grid"]),
        yaxis=dict(gridcolor=c["grid"]),
    )
    return fig


def fig_heatmap(mat: List[List[float]], n1: str, n2: str, c: Dict[str, str]) -> go.Figure:
    """Affiche la distribution des probabilités croisées de Poisson (HeatMap N*N)."""
    n_dim = len(mat)
    
    # Transformer en % (z)
    z = [[round(mat[h][a] * 100.0, 1) for a in range(n_dim)] for h in range(n_dim)]
    
    # Texte des valeurs pour plot inline
    text_grid = [[f"{v:.1f}%" for v in row] for row in z]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=[f"{n2} {a}" for a in range(n_dim)],
        y=[f"{n1} {h}" for h in range(n_dim)],
        colorscale=[[0, c["card2"]], [0.5, c["acc"]], [1, c.get("acc_hover", "#60a5fa")]],
        showscale=True,
        hovertemplate="Score du Match : %{y} – %{x}<br>Confiance Algo : %{z:.1f}%<extra></extra>",
        text=text_grid,
        texttemplate="%{text}",
        textfont={"size": 10, "color": c["txt"]},
    ))
    
    fig.update_layout(
        title=dict(text="🎯 Matrice d'espérance des scores (Poisson)", font=dict(size=14, color=c["txt"])),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=c["txt"]),
        margin=dict(l=60, r=20, t=50, b=40),
        xaxis=dict(gridcolor=c["grid"]),
        yaxis=dict(gridcolor=c["grid"], autorange="reversed"),
    )
    return fig


def fig_jauge(prob: float, label: str, color: str, c: Dict[str, str]) -> go.Figure:
    """Tachymètre visuel montrant la confiance pure au grand jour (0% - 100%)."""
    val = round(prob * 100.0, 1)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        number={"suffix": "%", "font": {"size": 28, "color": color}},
        title={"text": label, "font": {"size": 13, "color": c["txt"]}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": c["grid"], "tickwidth": 1},
            "bar": {"color": color},
            "bgcolor": c["card"],
            "bordercolor": c["brd"],
            "steps": [
                {"range": [0, 40],   "color": c["card"]},
                {"range": [40, 60],  "color": c.get("card2", c["card"])},
                {"range": [60, 100], "color": c.get("card2", c["card"])},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.75, "value": val}
        }
    ))
    
    fig.update_layout(
        height=200, 
        margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)", 
        font=dict(color=c["txt"])
    )
    return fig
