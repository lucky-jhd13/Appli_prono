# Documentation du Scraper de Statistiques xG (Expected Goals)

Ce module permet de récupérer automatiquement les statistiques offensives réelles (notamment les **xG = Expected Goals** et les buts) de toutes les équipes de Ligue 1 en temps réel, directement depuis l'API sécurisée d'Opta Analyst.

## But de ce script

Le script `scrap_xg.py` a pour objectif de remplacer le travail fastidieux de recopie manuelle depuis le site de *The Analyst* (Opta).
Au lieu de scraper visuellement la page web (qui est dynamique), ce fichier interroge directement l'API source en arrière-plan. Cela permet d'obtenir un format propre, structuré et instantané sans même ouvrir un navigateur.

## Qu'est-ce que l'API récupère ?

Ces statistiques sont axées sur les performances offensives globales (OVERALL) sur toute la saison en cours :
- **Matchs joués** (`played`)
- **Buts marqués** (`goals` ou `goals_pm` par match)
- **Expected Goals** (`xg_total` ou `xg_pm` par match), qui représente la probabilité statistique qu'une équipe marque lors de ses actions offensives.

### Pourquoi ces deux valeurs (Par Match & Total) ?

Le site web affiche par défaut les données **par match**. L'API, elle, fournit la statistique **totale** depuis le début de la saison.
Le script se charge donc automatiquement de faire la conversion :
- `xg_pm` (xG par Match) : La donnée divisée par le nombre de matchs joués. C'est l'indicateur principal de performance à utiliser dans un outil de pronostics.
- `xg_total` (xG Total) : L'accumulation des xG sur l'intégralité de la saison de l'équipe.

## Comment l'utiliser ?

1. **Assurez-vous d'avoir installé les librairies nécessaires :**
   ```bash
   pip install requests
   ```

2. **Lancer le script :**
   ```bash
   python scrap_xg.py
   ```

3. **Résultat :**
   Le script effectuera une requête à Opta Analyst, récupèrera les données, harmonisera les noms d'équipes pour pouvoir correspondre plus facilement à l'outil `PronoFoot` (ex: "Olympique Lyonnais" -> "Lyon"), et créera un fichier final propre nommé `ligue1_xg_stats.json`.

## Structure du fichier généré `ligue1_xg_stats.json`

Le fichier de sortie inclut les données triées selon le Par Match et sur le Total pour répondre à n'importe quel besoin algorithmique ultérieur :

```json
{
  "stats_par_match": [
    {
      "name": "Paris SG",
      "played": 23,
      "goals_pm": 2.26,
      "xg_pm": 2.03,
      "goals_total": 52,
      "xg_total": 46.68
    },
    ...
  ],
  "stats_saison_totale": [ ... ]
}
```

## Intégration future avec PronoFoot

L'objectif ultime est de lier les modèles de prédiction existants (réseaux de neurones, forêts de décision) ou la simple pondération de score aux valeurs **xG**. Les modèles se nourriront du fichier `ligue1_xg_stats.json` pour pondérer mathématiquement les chances qu'une équipe gagne face à une autre, basé sur la véritable dangerosité offensive observée statistiquement (Opta), et non plus seulement sur le classement !


## Ancienne Explication

Le xg_total (44.5 si c'était pour Lens par exemple) correspond à la somme totale de tous les Expected Goals (xG) accumulés par l'équipe depuis le TOUT DEBUT de la saison.

Sur la capture d'écran du site que tu m'as envoyée, ils affichaient le xG par match (ex: 1.93 xG / match pour Lens). L'API qu'on a piratée renvoie quant à elle par défaut les stats totales (le xg_total).

Dans notre fichier .json :

xg_pm (xG per match) : C'est le chiffre que tu vois sur ta capture (ex: 1.93), qui est calculé en faisant xg_total divisé par le nombre de matchs (played). C'est la moyenne de danger offensif créé par l'équipe à chaque match !
xg_total : C'est le score d'xG brut, totalisé sur les 23 matchs joués (soit environ 23 x 1.93 = 44.5).
En bref: C'est avec le xg_pm (xG Par Match) que tu as tout intérêt à comparer des équipes dans tes algorithmes de prédiction (PronoFoot), tandis que le xg_total est juste la "réserve totale" de dangerosité d'une équipe sur sa saison.