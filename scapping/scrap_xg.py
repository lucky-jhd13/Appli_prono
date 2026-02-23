import requests
import json
import os

def get_ligue1_xg_stats():
    # API URL that loads the tournament stats
    url = "https://theanalyst.com/wp-json/sdapi/v1/soccerdata/tournamentstats?tmcl=dbxs75cag7zyip5re0ppsanmc"
    
    headers = {
        "x-sdapi-token": "LRkJ2MjwlC8RxUfVkne4",
        "Referer": "https://theanalyst.com/competition/ligue-1/stats",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print("Fetching data from API...\n")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        team_stats = data.get('team', {}).get('attack', {}).get('overall', [])
        
        # We need mapping for short names similar to the website
        name_map = {
            "Paris Saint-Germain FC": "Paris SG",
            "Racing Club de Lens": "Lens",
            "Olympique de Marseille": "Marseille",
            "AS Monaco FC": "Monaco",
            "Lille OSC": "Lille",
            "RC Strasbourg Alsace": "Strasbourg",
            "Olympique Lyonnais": "Lyon",
            "Stade Rennais FC": "Rennes",
            "Stade Brestois 29": "Brest",
            "Toulouse FC": "Toulouse",
            "FC Lorient": "Lorient",
            "OGC Nice Côte d'Azur": "Nice",
            "Paris FC": "Paris FC",
            "Le Havre AC": "Le Havre",
            "Association Jeunesse Auxerroise": "Auxerre",
            "FC Metz": "Metz",
            "FC Nantes": "Nantes",
            "Angers Sporting Club de l'Ouest": "Angers"
        }
        
        results = []
        for team in team_stats:
            raw_name = team.get('contestantName')
            short_name = name_map.get(raw_name, raw_name)
            
            played = team.get('matchesPlayed', 23)
            if played == 0:
                continue
                
            goals = team.get('goals', 0)
            xg = team.get('xg', 0.0)
            
            # Calcul per match
            goals_pm = round(goals / played, 2)
            xg_pm = round(xg / played, 2)
            
            results.append({
                "name": short_name,
                "played": played,
                "goals_pm": goals_pm,
                "xg_pm": xg_pm,
                "goals_total": goals,
                "xg_total": round(xg, 2)
            })
            
        # 1. TABLEAU PAR MATCH (Trié par xG par match)
        results_pm = sorted(results, key=lambda x: x['xg_pm'], reverse=True)
        
        print("======== STATS PAR MATCH ========")
        print("{:<15} {:<8} {:<8} {:<8}".format("NAME", "PLAYED", "GOALS", "XG"))
        print("-" * 43)
        for r in results_pm:
            print("{:<15} {:<8} {:.2f}     {:.2f}".format(
                r['name'], r['played'], r['goals_pm'], r['xg_pm']
            ))
            
        print("\n\n======== STATS TOTALES (SAISON) ========")
        # 2. TABLEAU SAISON (Trié par xG total)
        results_total = sorted(results, key=lambda x: x['xg_total'], reverse=True)
        
        print("{:<15} {:<8} {:<8} {:<8}".format("NAME", "PLAYED", "GOALS", "XG"))
        print("-" * 43)
        for r in results_total:
            print("{:<15} {:<8} {:<8} {:.2f}".format(
                r['name'], r['played'], r['goals_total'], r['xg_total']
            ))
            
        # Creation du fichier JSON de sortie
        export_data = {
            "stats_par_match": results_pm,
            "stats_saison_totale": results_total
        }
        
        output_file = "ligue1_xg_stats.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=4)
            
        print(f"\n✅ Les données ont été sauvegardées avec succès dans le fichier: {os.path.abspath(output_file)}")
            
    else:
        print(f"Erreur HTTP: {response.status_code}")

if __name__ == "__main__":
    get_ligue1_xg_stats()
