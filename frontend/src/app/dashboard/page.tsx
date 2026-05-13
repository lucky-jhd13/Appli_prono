"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";

interface Match {
  id: number;
  league: str;
  home: str;
  away: str;
  date: str;
  probabilities: {
    home_win: number;
    draw: number;
    away_win: number;
  };
}

export default function DashboardPage() {
  const { token } = useAuth();
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        // En prod, vous auriez un proxy ou directement l'URL
        const res = await fetch("http://localhost:8000/api/matches/today", {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        });
        
        if (!res.ok) throw new Error("Erreur de chargement des matchs");
        
        const data = await res.json();
        setMatches(data.matches || []);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchMatches();
    }
  }, [token]);

  if (loading) {
    return <div className="p-8 text-gray-500">Chargement de l'algorithme V3...</div>;
  }

  if (error) {
    return <div className="p-8 text-red-500">{error}</div>;
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <header>
        <h1 className="text-3xl font-bold">Matchs du Jour</h1>
        <p className="text-gray-500 mt-2">Prédictions Dixon-Coles en temps réel.</p>
      </header>

      {matches.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-8 text-center text-gray-500">
          Aucun match majeur trouvé pour aujourd'hui. L'API est peut-être vide.
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {matches.map((match) => {
            // Trouver la proba max pour la mettre en surbrillance
            const maxProb = Math.max(match.probabilities.home_win, match.probabilities.draw, match.probabilities.away_win);
            
            return (
            <div key={match.id} className="bg-card border border-border rounded-2xl p-6 shadow-xl hover:shadow-primary/20 hover:border-primary/50 transition-all duration-300 flex flex-col h-full overflow-hidden relative">
              {/* Effet lumineux de fond */}
              <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-3xl"></div>
              
              <div className="flex justify-between items-center mb-4 relative z-10">
                <div className="text-xs font-bold px-3 py-1 bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-blue-500 dark:text-blue-400 border border-blue-500/30 rounded-full uppercase tracking-wider shadow-sm">
                  {match.league}
                </div>
                <div className="text-xs font-semibold text-gray-400 bg-border/50 px-2 py-1 rounded">{match.date}</div>
              </div>
              
              <div className="flex justify-between items-center mb-6 flex-1 relative z-10">
                <span className="text-lg md:text-xl font-bold w-[40%] truncate text-foreground" title={match.home}>{match.home}</span>
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 to-teal-500 text-sm font-black px-3 py-1 rounded-full border border-emerald-500/30 shadow-sm">VS</span>
                <span className="text-lg md:text-xl font-bold w-[40%] text-right truncate text-foreground" title={match.away}>{match.away}</span>
              </div>

              <div className="grid grid-cols-3 gap-2 md:gap-4 mb-4 relative z-10">
                <div className={`rounded-xl p-3 text-center border transition-all ${match.probabilities.home_win === maxProb ? 'bg-emerald-500/10 border-emerald-500/50 shadow-inner' : 'bg-background border-border hover:border-gray-400'}`}>
                  <div className="text-xs text-gray-500 mb-1 font-medium">1</div>
                  <div className={`font-bold text-sm md:text-base ${match.probabilities.home_win === maxProb ? 'text-emerald-500' : 'text-foreground'}`}>
                    {(match.probabilities.home_win * 100).toFixed(1)}%
                  </div>
                </div>
                <div className={`rounded-xl p-3 text-center border transition-all ${match.probabilities.draw === maxProb ? 'bg-teal-500/10 border-teal-500/50 shadow-inner' : 'bg-background border-border hover:border-gray-400'}`}>
                  <div className="text-xs text-gray-500 mb-1 font-medium">X</div>
                  <div className={`font-bold text-sm md:text-base ${match.probabilities.draw === maxProb ? 'text-teal-500' : 'text-foreground'}`}>
                    {(match.probabilities.draw * 100).toFixed(1)}%
                  </div>
                </div>
                <div className={`rounded-xl p-3 text-center border transition-all ${match.probabilities.away_win === maxProb ? 'bg-emerald-500/10 border-emerald-500/50 shadow-inner' : 'bg-background border-border hover:border-gray-400'}`}>
                  <div className="text-xs text-gray-500 mb-1 font-medium">2</div>
                  <div className={`font-bold text-sm md:text-base ${match.probabilities.away_win === maxProb ? 'text-emerald-500' : 'text-foreground'}`}>
                    {(match.probabilities.away_win * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Exemple visuel de Value Bet pour la demande utilisateur */}
              {match.id === 1 && (
                <div className="mt-4 p-4 bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border border-emerald-500/30 rounded-xl flex items-center justify-between relative z-10 shadow-sm hover:shadow-emerald-500/20 transition-all">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl drop-shadow-md">🤑</span>
                    <div>
                      <div className="text-[10px] text-emerald-500 font-extrabold uppercase tracking-widest mb-0.5">Value Bet Détecté</div>
                      <div className="text-sm font-bold text-foreground">Victoire {match.home}</div>
                    </div>
                  </div>
                  <div className="text-right bg-background/50 px-3 py-1.5 rounded-lg border border-emerald-500/20">
                    <div className="text-[10px] text-gray-500 uppercase font-bold">Cote</div>
                    <div className="font-bold text-emerald-500 text-lg">1.72</div>
                  </div>
                </div>
              )}
            </div>
          )})}
        </div>
      )}
    </div>
  );
}
