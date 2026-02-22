# 🏆 PRO-FOOT AI V12

Application de pronostics football basée sur la **Loi de Poisson Bivariée Normalisée** et le **Kelly Criterion**.

## 📁 Structure du projet

```
appli_prono/
├── app.py                  ← Point d'entrée (orchestrateur)
├── config.py               ← Constantes & paramètres de l'algo
├── requirements.txt
├── core/
│   ├── api.py              ← Appels API football-data.org
│   ├── stats.py            ← Extraction & calcul des stats équipes
│   └── moteur.py           ← Moteur Poisson, lambdas, Kelly
└── ui/
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

## ⚙️ Paramètres (`config.py`)

Tous les seuils et multiplicateurs sont centralisés dans `config.py` :
- `SEUIL_BTTS`, `SEUIL_OVER25`, `SEUIL_VALUE`
- `DOM_BONUS_BASE`, `BUTEUR_ABSENT_MULT`, `REPOS_ELEVE_MULT`...
