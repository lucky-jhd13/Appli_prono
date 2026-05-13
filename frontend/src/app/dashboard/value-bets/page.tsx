"use client";

import { useAuth } from "@/lib/auth-context";
import { Lock, AlertTriangle, TrendingUp, Target } from "lucide-react";
import { useEffect, useState } from "react";

export default function ValueBetsPage() {
  const { isPremium, token } = useAuth();
  const [valueBets, setValueBets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Pour le développement, on simule le fait d'être Premium si la vraie logique n'est pas encore prête
  // Mais ici on utilise le state de Auth.
  
  useEffect(() => {
    const fetchValueBets = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/matches/today", {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          const allValueBets: any[] = [];
          
          // Extraire tous les value bets de tous les matchs
          if (data.matches) {
            data.matches.forEach((match: any) => {
              if (match.value_bets && match.value_bets.length > 0) {
                match.value_bets.forEach((vb: any) => {
                  allValueBets.push({
                    ...vb,
                    match_id: match.id,
                    league: match.league,
                    home: match.home,
                    away: match.away,
                    date: match.date
                  });
                });
              }
            });
          }
          setValueBets(allValueBets.sort((a, b) => b.edge_pct - a.edge_pct));
        }
      } catch (err) {
        console.error("Failed to load value bets:", err);
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchValueBets();
    }
  }, [token]);

  if (!isPremium) {
    return (
      <div className="p-8 max-w-4xl mx-auto mt-12">
        <div className="bg-card border border-border rounded-3xl p-12 text-center shadow-xl relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-emerald-400 to-teal-600"></div>
          <div className="w-20 h-20 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
            <Lock className="w-10 h-10 text-emerald-500" />
          </div>
          <h2 className="text-3xl font-bold mb-4 text-foreground">Accès Restreint</h2>
          <p className="text-gray-500 text-lg max-w-lg mx-auto mb-8">
            L'algorithme de détection de Value Bets (Calculs d'Edge et de rentabilité) est strictement réservé aux membres Premium.
          </p>
          <button 
            onClick={() => {
              // Hack temporaire pour que l'utilisateur puisse tester l'interface
              localStorage.setItem("pf_premium", "true");
              window.location.reload();
            }}
            className="px-8 py-4 bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold rounded-xl shadow-lg hover:shadow-emerald-500/25 transition-all transform hover:-translate-y-1"
          >
            Débloquer les Value Bets (Test Mode)
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-emerald-500 flex items-center gap-3">
          🤑 Value Bets Détectés
        </h1>
        <p className="text-gray-500 mt-2">Les paris mathématiquement rentables selon notre algorithme.</p>
      </header>

      {loading ? (
        <div className="text-gray-500 text-center py-12">Analyse des opportunités en cours...</div>
      ) : valueBets.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-12 text-center flex flex-col items-center">
          <AlertTriangle className="w-12 h-12 text-amber-500 mb-4" />
          <h3 className="text-xl font-bold mb-2">Aucune Opportunité</h3>
          <p className="text-gray-500 max-w-md mx-auto">
            L'algorithme n'a détecté aucun Value Bet satisfaisant nos critères de rentabilité pour le moment.
            Revenez plus tard.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {valueBets.map((vb, idx) => (
            <div key={idx} className="bg-card border border-border rounded-2xl p-6 shadow-lg hover:shadow-emerald-500/10 transition-all relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-full blur-2xl group-hover:bg-emerald-500/10 transition-colors"></div>
              
              <div className="flex justify-between items-start mb-4 relative z-10">
                <span className="text-[10px] font-bold px-2 py-1 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 text-emerald-500 border border-emerald-500/30 rounded-full uppercase tracking-wider">
                  {vb.league}
                </span>
                <span className="text-xs text-gray-500 font-medium bg-background px-2 py-1 rounded-md border border-border">
                  Confiance: <span className={vb.confidence > 75 ? "text-emerald-500" : "text-amber-500"}>{vb.confidence}%</span>
                </span>
              </div>

              <div className="mb-4 relative z-10">
                <div className="text-sm text-gray-400 mb-1">{vb.date}</div>
                <div className="font-bold text-foreground line-clamp-1">{vb.home} <span className="text-gray-500 mx-1">vs</span> {vb.away}</div>
              </div>

              <div className="bg-background rounded-xl p-4 border border-border mb-4 relative z-10">
                <div className="text-sm text-gray-500 mb-1 font-medium flex items-center gap-2">
                  <Target size={14} className="text-primary"/> Prédiction
                </div>
                <div className="font-bold text-lg text-primary">{vb.label}</div>
              </div>

              <div className="flex justify-between items-center relative z-10">
                <div>
                  <div className="text-xs text-gray-500 uppercase font-bold mb-1">Cote Bookmaker</div>
                  <div className="text-2xl font-black text-foreground">{vb.odd.toFixed(2)}</div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-emerald-500 uppercase font-bold mb-1 flex items-center justify-end gap-1">
                    <TrendingUp size={12}/> Avantage (Edge)
                  </div>
                  <div className="text-xl font-bold text-emerald-500">+{vb.edge_pct.toFixed(1)}%</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
