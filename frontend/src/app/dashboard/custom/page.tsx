"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth-context";

export default function CustomMatchPage() {
  const { token } = useAuth();
  const [home, setHome] = useState("");
  const [away, setAway] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/custom/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ home_team: home, away_team: away })
      });
      if (res.ok) {
        setResult(await res.json());
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <header>
        <h1 className="text-3xl font-bold">Mon Match</h1>
        <p className="text-gray-500 mt-2">Analysez n'importe quelle rencontre en temps réel.</p>
      </header>

      <form onSubmit={handleAnalyze} className="bg-card border border-border p-6 rounded-2xl shadow-sm flex flex-col md:flex-row gap-4 items-end">
        <div className="flex-1">
          <label className="block text-sm font-medium mb-2">Équipe Domicile</label>
          <input 
            required
            className="w-full p-3 rounded-xl bg-background border border-border focus:border-primary outline-none"
            placeholder="Ex: Real Madrid"
            value={home}
            onChange={(e) => setHome(e.target.value)}
          />
        </div>
        <div className="flex-1">
          <label className="block text-sm font-medium mb-2">Équipe Extérieure</label>
          <input 
            required
            className="w-full p-3 rounded-xl bg-background border border-border focus:border-primary outline-none"
            placeholder="Ex: Barcelona"
            value={away}
            onChange={(e) => setAway(e.target.value)}
          />
        </div>
        <button 
          type="submit"
          disabled={loading}
          className="px-8 py-3 bg-primary text-white font-bold rounded-xl hover:bg-emerald-500 transition-colors"
        >
          {loading ? "Calcul..." : "Analyser"}
        </button>
      </form>

      {result && (
        <div className="space-y-6 mt-8">
          {/* Section 1N2 */}
          <div className="bg-card border border-border p-6 rounded-2xl shadow-sm">
            <h2 className="text-xl font-bold mb-6 text-center text-emerald-500">Probabilités 1N2</h2>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-background rounded-xl p-4 text-center border border-border hover:border-emerald-500/50 transition-colors">
                <div className="text-sm text-gray-500 mb-1">{result.teams.home}</div>
                <div className="text-3xl font-black text-foreground">{(result.probabilities.home_win * 100).toFixed(1)}%</div>
              </div>
              <div className="bg-background rounded-xl p-4 text-center border border-border hover:border-teal-500/50 transition-colors">
                <div className="text-sm text-gray-500 mb-1">Match Nul</div>
                <div className="text-3xl font-black text-foreground">{(result.probabilities.draw * 100).toFixed(1)}%</div>
              </div>
              <div className="bg-background rounded-xl p-4 text-center border border-border hover:border-emerald-500/50 transition-colors">
                <div className="text-sm text-gray-500 mb-1">{result.teams.away}</div>
                <div className="text-3xl font-black text-foreground">{(result.probabilities.away_win * 100).toFixed(1)}%</div>
              </div>
            </div>
          </div>

          {/* Section Stats Avancées */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-card border border-border p-6 rounded-2xl shadow-sm">
              <h2 className="text-lg font-bold mb-4 text-emerald-500">Marchés Alternatifs</h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-background rounded-lg border border-border">
                  <span className="font-medium">Plus de 1.5 buts</span>
                  <span className="font-bold text-emerald-500">{(result.probabilities["over_1.5"] * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-background rounded-lg border border-border">
                  <span className="font-medium">Plus de 2.5 buts</span>
                  <span className="font-bold text-emerald-500">{(result.probabilities["over_2.5"] * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-background rounded-lg border border-border">
                  <span className="font-medium">Les deux équipes marquent</span>
                  <span className="font-bold text-emerald-500">{(result.probabilities["btts_yes"] * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>

            <div className="bg-card border border-border p-6 rounded-2xl shadow-sm">
              <h2 className="text-lg font-bold mb-4 text-emerald-500">Score le plus probable</h2>
              <div className="flex items-center justify-center h-full pb-8">
                <div className="text-center">
                  <div className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 to-teal-500 mb-2">
                    {result.probabilities.most_likely_score[0]} - {result.probabilities.most_likely_score[1]}
                  </div>
                  <div className="text-gray-500 font-medium">
                    Probabilité : {(result.probabilities.most_likely_prob * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
