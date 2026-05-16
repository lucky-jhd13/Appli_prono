// frontend/src/app/dashboard/custom/page.tsx
"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import LeagueSidebar from "@/components/league-sidebar";
import { fetchCustomAnalysis } from "@/lib/apiClient";
import type { CustomAnalysis } from "@/types/custom";

export default function CustomMatchPage() {
  const { token } = useAuth();
  const [home, setHome] = useState<string>("");
  const [away, setAway] = useState<string>("");
  const [result, setResult] = useState<CustomAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!home || !away) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchCustomAnalysis(home, away, token);
      setResult(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erreur inconnue");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar for league & team selection */}
      <LeagueSidebar onSelectHome={setHome} onSelectAway={setAway} />

      {/* Main content area */}
      <main className="p-8 flex-1 max-w-4xl mx-auto space-y-8">
        <header>
          <h1 className="text-3xl font-bold">Mon Match</h1>
          <p className="text-gray-500 mt-2">
            Analysez n&apos;importe quelle rencontre en temps réel.
          </p>
        </header>

        {/* Selection summary */}
        {(home || away) && (
          <div className="bg-card border border-border rounded-xl p-4 flex items-center gap-4">
            <span className="text-emerald-400 font-semibold">{home || "—"}</span>
            <span className="text-gray-500">vs</span>
            <span className="text-emerald-400 font-semibold">{away || "—"}</span>
          </div>
        )}

        <button
          onClick={handleAnalyze}
          disabled={loading || !home || !away}
          className="px-8 py-3 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-500 transition-colors disabled:opacity-50"
        >
          {loading ? "Calcul…" : "Analyser"}
        </button>

        {error && (
          <div className="bg-red-900/20 border border-red-500/40 text-red-400 rounded-xl p-4">
            {error}
          </div>
        )}

        {result && (
          <div className="space-y-6 mt-8">
            {/* Probabilités 1N2 */}
            <div className="bg-card border border-border p-6 rounded-2xl shadow-sm">
              <h2 className="text-xl font-bold mb-6 text-center text-emerald-500">
                Probabilités 1N2
              </h2>
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-background rounded-xl p-4 text-center border border-border hover:border-emerald-500/50 transition-colors">
                  <div className="text-sm text-gray-500 mb-1">{result.teams.home}</div>
                  <div className="text-3xl font-black text-foreground">
                    {(result.probabilities.home_win * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="bg-background rounded-xl p-4 text-center border border-border hover:border-teal-500/50 transition-colors">
                  <div className="text-sm text-gray-500 mb-1">Match Nul</div>
                  <div className="text-3xl font-black text-foreground">
                    {(result.probabilities.draw * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="bg-background rounded-xl p-4 text-center border border-border hover:border-emerald-500/50 transition-colors">
                  <div className="text-sm text-gray-500 mb-1">{result.teams.away}</div>
                  <div className="text-3xl font-black text-foreground">
                    {(result.probabilities.away_win * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>

            {/* Marchés alternatifs + Score probable */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-card border border-border p-6 rounded-2xl shadow-sm">
                <h2 className="text-lg font-bold mb-4 text-emerald-500">Marchés Alternatifs</h2>
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-background rounded-lg border border-border">
                    <span className="font-medium">Plus de 1.5 buts</span>
                    <span className="font-bold text-emerald-500">
                      {(result.probabilities["over_1.5"] * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-background rounded-lg border border-border">
                    <span className="font-medium">Plus de 2.5 buts</span>
                    <span className="font-bold text-emerald-500">
                      {(result.probabilities["over_2.5"] * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-background rounded-lg border border-border">
                    <span className="font-medium">Les deux équipes marquent</span>
                    <span className="font-bold text-emerald-500">
                      {(result.probabilities["btts_yes"] * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>

              <div className="bg-card border border-border p-6 rounded-2xl shadow-sm">
                <h2 className="text-lg font-bold mb-4 text-emerald-500">Score le plus probable</h2>
                <div className="flex items-center justify-center h-full pb-8">
                  <div className="text-center">
                    <div className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 to-teal-500 mb-2">
                      {result.probabilities.most_likely_score[0]} -{" "}
                      {result.probabilities.most_likely_score[1]}
                    </div>
                    <div className="text-gray-500 font-medium">
                      Probabilité : {(result.probabilities.most_likely_prob * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Value Bets */}
            {result.value_bets && result.value_bets.length > 0 && (
              <div className="bg-card border border-border p-6 rounded-2xl shadow-sm">
                <h2 className="text-lg font-bold mb-4 text-emerald-500">Value Bets</h2>
                <ul className="space-y-2">
                  {result.value_bets.map((vb, idx) => (
                    <li
                      key={idx}
                      className="flex justify-between items-center border-b border-border pb-1"
                    >
                      <span>{vb.label}</span>
                      <span className="font-medium text-emerald-600">
                        {vb.bet_type} – {vb.odd.toFixed(2)} ({(vb.edge_pct * 100).toFixed(1)}%
                        edge)
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
