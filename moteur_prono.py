def calculer_force_attaque(buts_marques, top_buteur_present):
    moyenne = buts_marques / 5
    if moyenne >= 2.5: note = 95
    elif moyenne >= 1.8: note = 80
    elif moyenne >= 1.2: note = 65
    elif moyenne >= 0.6: note = 40
    else: note = 20

    if top_buteur_present.lower() == "non":
        note *= 0.75 
    return note

def calculer_force_defense(buts_encaisses):
    moyenne = buts_encaisses / 5
    # Moins on encaisse, plus la note est haute
    if moyenne <= 0.6: return 90
    elif moyenne <= 1.2: return 70
    elif moyenne <= 1.8: return 45
    else: return 20

def calculer_fatigue(jours_repos):
    if jours_repos >= 7: return 0
    if jours_repos >= 4: return 5
    return 15 # Malus important si match très proche

def demarrer_analyse_pro():
    print("\n🚀 --- PRONO APP : MOTEUR D'ANALYSE V4 (HYBRIDE) ---")
    
    # --- DONNÉES ÉQUIPE 1 (DOMICILE) ---
    nom_1 = input("Nom Équipe 1 (Domicile) : ")
    buts_m_1 = int(input(f"   - Buts marqués (5 derniers matchs) : "))
    buts_e_1 = int(input(f"   - Buts encaissés (5 derniers matchs) : "))
    pts_dom_1 = int(input(f"   - Points pris à DOMICILE (sur 15 possibles) : "))
    jours_1 = int(input(f"   - Jours de repos : "))
    buteur_1 = input(f"   - Meilleur buteur présent ? (oui/non) : ")
    
    # --- DONNÉES ÉQUIPE 2 (EXTÉRIEUR) ---
    print("-" * 30)
    nom_2 = input("Nom Équipe 2 (Extérieur) : ")
    buts_m_2 = int(input(f"   - Buts marqués (5 derniers matchs) : "))
    buts_e_2 = int(input(f"   - Buts encaissés (5 derniers matchs) : "))
    pts_ext_2 = int(input(f"   - Points pris à l'EXTÉRIEUR (sur 15 possibles) : "))
    jours_2 = int(input(f"   - Jours de repos : "))
    buteur_2 = input(f"   - Meilleur buteur présent ? (oui/non) : ")

    # --- CALCUL DES SCORES DE PUISSANCE ---
    # Équipe 1
    att_1 = calculer_force_attaque(buts_m_1, buter_1)
    def_1 = calculer_force_defense(buts_e_1)
    fat_1 = calculer_fatigue(jours_1)
    bonus_dom = (pts_dom_1 / 15) * 15 # Bonus dynamique basé sur la force réelle à domicile
    puissance_1 = (att_1 * 0.6 + def_1 * 0.4) - fat_1 + bonus_dom

    # Équipe 2
    att_2 = calculer_force_attaque(buts_m_2, buteur_2)
    def_2 = calculer_force_defense(buts_e_2)
    fat_2 = calculer_fatigue(jours_2)
    bonus_ext = (pts_ext_2 / 15) * 10 # Bonus de "bon voyageur"
    puissance_2 = (att_2 * 0.6 + def_2 * 0.4) - fat_2 + bonus_ext

    print("\n" + "="*45)
    print(f"📊 PUISSANCE {nom_1.upper()} : {int(puissance_1)}")
    print(f"📊 PUISSANCE {nom_2.upper()} : {int(puissance_2)}")
    print("="*45)

    # --- VERDICT MODÈLE N1 (1N2) ---
    ecart = puissance_1 - puissance_2
    
    print("\n🏆 PRONOSTIC 1N2 :")
    if ecart > 18:
        print(f"   👉 Résultat : Victoire de {nom_1}")
    elif ecart < -12: # Seuil plus bas car l'extérieur est plus difficile
        print(f"   👉 Résultat : Victoire de {nom_2}")
    else:
        print(f"   👉 Résultat : Match Nul (ou match très serré)")

    # --- VERDICT MODÈLE N2 (BUTS) ---
    print("\n⚽ ANALYSE DES BUTS :")
    potentiel_offensif = (att_1 + att_2) / 2
    fragilite_defensive = ( (100-def_1) + (100-def_2) ) / 2

    if potentiel_offensif > 70:
        print("   👉 Over 2.5 buts : OUI")
    else:
        print("   👉 Over 2.5 buts : NON (Match fermé)")

    if att_1 > 50 and att_2 > 50 and fragilite_defensive > 40:
        print("   👉 Les deux équipes marquent : OUI")
    else:
        print("   👉 Les deux équipes marquent : NON")
    print("="*45 + "\n")

demarrer_analyse_pro()