# ─────────────────────────────────────────────
# core/stats.py — Extraction & traitement des stats
# ─────────────────────────────────────────────


def extraire_stats(equipe_data: dict) -> dict:
    """
    Extrait toutes les statistiques utiles d'une entrée du classement API.

    Retourne un dict avec :
      pj, gf, ga, pts, won, draw, lost
      mbp (moy buts marqués/match), mbc (moy buts encaissés/match)
      pts_par_match, forme_pct, form (str brut)
      diff (différence de buts)
      radar (liste [att, def, vic, const] sur 100)
    """
    pj   = equipe_data.get("playedGames", 1) or 1
    gf   = equipe_data.get("goalsFor", 0)
    ga   = equipe_data.get("goalsAgainst", 0)
    pts  = equipe_data.get("points", 0)
    won  = equipe_data.get("won", 0)
    draw = equipe_data.get("draw", 0)
    lost = equipe_data.get("lost", 0)

    mbp = gf / pj
    mbc = ga / pj
    pts_par_match = pts / pj

    # Forme sur 5 derniers matchs
    form_raw = str(equipe_data.get("form", "") or "").replace(",", "").replace(" ", "")[-5:]
    pts_forme = sum(3 if c == "W" else 1 if c == "D" else 0 for c in form_raw)
    forme_pct = (pts_forme / 15) * 100

    # Scores radar normalisés sur 100
    att_score  = min(mbp * 45, 100)
    def_score  = max(100 - mbc * 50, 0)
    vic_score  = (won / pj) * 100
    const_score = (pts_par_match / 3) * 100

    return {
        "pj":           pj,
        "gf":           gf,
        "ga":           ga,
        "pts":          pts,
        "won":          won,
        "draw":         draw,
        "lost":         lost,
        "mbp":          mbp,
        "mbc":          mbc,
        "pts_par_match": pts_par_match,
        "form":         form_raw,
        "pts_forme":    pts_forme,
        "forme_pct":    forme_pct,
        "diff":         gf - ga,
        "radar":        [int(att_score), int(def_score), int(vic_score), int(const_score)],
    }
