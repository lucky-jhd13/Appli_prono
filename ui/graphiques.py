# ─────────────────────────────────────────────
# ui/graphiques.py — Graphiques Plotly
# ─────────────────────────────────────────────

import plotly.graph_objects as go


def fig_radar(s1: dict, s2: dict, n1: str, n2: str, c: dict) -> go.Figure:
    cats = ["Attaque", "Défense", "Victoires", "Constance"]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=s1["radar"] + [s1["radar"][0]], theta=cats + [cats[0]],
        fill="toself", name=n1,
        line=dict(color="#3b82f6", width=2),
        fillcolor="rgba(59,130,246,0.15)"
    ))
    fig.add_trace(go.Scatterpolar(
        r=s2["radar"] + [s2["radar"][0]], theta=cats + [cats[0]],
        fill="toself", name=n2,
        line=dict(color="#ef4444", width=2),
        fillcolor="rgba(239,68,68,0.15)"
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=c["grid"], tickfont=dict(color=c["txt"], size=9)),
            angularaxis=dict(gridcolor=c["grid"], tickfont=dict(color=c["txt"], size=11))
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=c["txt"]),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=c["txt"])),
        height=380, margin=dict(l=40, r=40, t=30, b=30)
    )
    return fig


def fig_barres(s1: dict, s2: dict, n1: str, n2: str, c: dict) -> go.Figure:
    cats = ["Buts/match", "Encaissés/match", "Pts/match", "Diff buts"]
    v1 = [round(s1["mbp"], 2), round(s1["mbc"], 2), round(s1["pts_par_match"], 2), s1["diff"]]
    v2 = [round(s2["mbp"], 2), round(s2["mbc"], 2), round(s2["pts_par_match"], 2), s2["diff"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(name=n1, x=cats, y=v1, marker_color="#3b82f6", opacity=0.85))
    fig.add_trace(go.Bar(name=n2, x=cats, y=v2, marker_color="#ef4444", opacity=0.85))
    fig.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=c["txt"]),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=c["txt"])),
        height=280, margin=dict(l=20, r=20, t=20, b=40),
        xaxis=dict(gridcolor=c["grid"]),
        yaxis=dict(gridcolor=c["grid"]),
    )
    return fig


def fig_heatmap(mat: list, n1: str, n2: str, c: dict) -> go.Figure:
    n = len(mat)
    z = [[round(mat[h][a] * 100, 1) for a in range(n)] for h in range(n)]
    fig = go.Figure(go.Heatmap(
        z=z,
        x=[f"{n2} {a}" for a in range(n)],
        y=[f"{n1} {h}" for h in range(n)],
        colorscale=[[0, c["card2"]], [0.5, c["acc"]], [1, "#60a5fa"]],
        showscale=True,
        hovertemplate="Score %{y} – %{x}<br>Probabilité : %{z:.1f}%<extra></extra>",
        text=[[f"{v:.1f}%" for v in row] for row in z],
        texttemplate="%{text}",
        textfont={"size": 10, "color": c["txt"]},
    ))
    fig.update_layout(
        title=dict(text="🎲 Matrice des scores les plus probables (%)", font=dict(size=14, color=c["txt"])),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=c["txt"]),
        margin=dict(l=60, r=20, t=50, b=40),
        xaxis=dict(gridcolor=c["grid"]),
        yaxis=dict(gridcolor=c["grid"], autorange="reversed"),
    )
    return fig


def fig_jauge(prob: float, label: str, color: str, c: dict) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(prob * 100, 1),
        number={"suffix": "%", "font": {"size": 28, "color": color}},
        title={"text": label, "font": {"size": 13, "color": c["txt"]}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": c["grid"], "tickwidth": 1},
            "bar": {"color": color},
            "bgcolor": c["card"],
            "bordercolor": c["brd"],
            "steps": [
                {"range": [0, 40],  "color": c["card"]},
                {"range": [40, 60], "color": c["card2"]},
                {"range": [60, 100],"color": c["card2"]},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.75, "value": prob * 100}
        }
    ))
    fig.update_layout(
        height=200, margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color=c["txt"])
    )
    return fig


def fig_evolution_capital(evolution: list[dict], c: dict) -> go.Figure:
    """Graphique d'évolution du capital au fil des pronos."""
    if not evolution:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=c["txt"]),
            annotations=[dict(text="Aucun pronostic résolu", showarrow=False,
                              font=dict(size=16, color=c["txt"]), xref="paper", yref="paper", x=0.5, y=0.5)],
            height=300,
        )
        return fig

    dates = [e["date"] for e in evolution]
    capitals = [e["capital"] for e in evolution]
    matches = [e["match"] for e in evolution]

    # Couleur dynamique selon profit/perte
    colors = ["#4ade80" if cap >= 1000 else "#f87171" for cap in capitals]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=capitals,
        mode="lines+markers",
        line=dict(color=c["acc"], width=3),
        marker=dict(color=colors, size=8, line=dict(color=c["card"], width=2)),
        text=matches,
        hovertemplate="<b>%{text}</b><br>Capital : %{y:.2f}€<extra></extra>",
        fill="tozeroy",
        fillcolor=f"{c['acc']}15",
    ))

    # Ligne de référence (capital initial)
    fig.add_hline(y=1000, line_dash="dash", line_color=c["grid"],
                  annotation_text="Capital initial", annotation_font_color=c["txt"])

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=c["txt"]),
        height=350, margin=dict(l=50, r=20, t=20, b=40),
        xaxis=dict(gridcolor=c["grid"], title="Date"),
        yaxis=dict(gridcolor=c["grid"], title="Capital (€)"),
        showlegend=False,
    )
    return fig
