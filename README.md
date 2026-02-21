# 🏆 PronoFoot

Application de pronostics football basée sur la **Loi de Poisson Bivariée Normalisée** et le **Kelly Criterion**.

## 📁 Structure du projet

```
pronofoot/
├── app.py                  ← Point d'entrée (orchestrateur)
├── config.py               ← Constantes & paramètres de l'algo
├── requirements.txt
├── prono-foot.jpg          ← Logo de l'application
├── core/
│   ├── __init__.py
│   ├── api.py              ← Appels API football-data.org
│   ├── stats.py            ← Extraction & calcul des stats équipes
│   ├── moteur.py           ← Moteur Poisson, lambdas, Kelly
│   ├── scanner.py          ← Scanner de value bets automatique
│   ├── historique.py       ← Sauvegarde & suivi des pronostics
│   └── export_pdf.py       ← Génération de rapports PDF
└── ui/
    ├── __init__.py
    ├── theme.py            ← Thème, couleurs, injection CSS
    ├── composants.py       ← Composants HTML réutilisables
    └── graphiques.py       ← Graphiques Plotly (radar, barres, heatmap, jauges)
```

## 🚀 Lancement

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🧠 Algorithme

| Étape | Description |
|-------|-------------|
| **Lambda normalisé** | `λ_h = force_att_1 × force_def_2 × moy_championnat × bonus_dom` |
| **Bonus domicile** | Dynamique selon les perfs réelles (pts/match) |
| **Forme** | ±8% sur le lambda selon les 5 derniers matchs |
| **Matrice 8×8** | Probabilités de chaque score exact |
| **Kelly Criterion** | Fraction de mise optimale sur chaque marché |

## 🎯 Fonctionnalités

- **Analyse de match** — Pronostic 1N2, Over/Under 2.5, BTTS avec probabilités détaillées
- **Classement** — Tableau complet du championnat sélectionné
- **Scanner d'opportunités** — Détection automatique des value bets sur toute la ligue
- **Prochains matchs** — Calendrier des rencontres à venir
- **Combiné / Accumulateur** — Construction de paris combinés avec calcul Kelly
- **Suivi de performances** — Historique des pronos, ROI, évolution du capital
- **Export PDF** — Rapport d'analyse complet avec logo

## ⚙️ Paramètres (`config.py`)

Tous les seuils et multiplicateurs sont centralisés dans `config.py` :
- `SEUIL_BTTS`, `SEUIL_OVER25`, `SEUIL_VALUE`
- `DOM_BONUS_BASE`, `BUTEUR_ABSENT_MULT`, `REPOS_ELEVE_MULT`...
