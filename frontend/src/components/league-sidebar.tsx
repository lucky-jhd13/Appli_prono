// frontend/src/components/league-sidebar.tsx
"use client";

import { useState } from "react";
import { LEAGUES_DATA } from "@/lib/leagues-data";

interface LeagueSidebarProps {
  onSelectHome: (team: string) => void;
  onSelectAway: (team: string) => void;
}

export default function LeagueSidebar({
  onSelectHome,
  onSelectAway,
}: LeagueSidebarProps) {
  const [selectedLeague, setSelectedLeague] = useState<string>("");
  const [home, setHome] = useState<string>("");
  const [away, setAway] = useState<string>("");

  const currentLeague = LEAGUES_DATA.find((l) => l.name === selectedLeague);
  const teams = currentLeague?.teams ?? [];

  const handleLeagueChange = (league: string) => {
    setSelectedLeague(league);
    setHome("");
    setAway("");
    onSelectHome("");
    onSelectAway("");
  };

  const handleHomeChange = (val: string) => {
    setHome(val);
    onSelectHome(val);
  };

  const handleAwayChange = (val: string) => {
    setAway(val);
    onSelectAway(val);
  };

  return (
    <aside className="w-72 bg-card border-r border-border flex flex-col h-screen sticky top-0 overflow-y-auto">
      {/* Header */}
      <div className="p-5 border-b border-border">
        <h2 className="text-base font-bold text-emerald-400 uppercase tracking-wider">
          Sélection du match
        </h2>
        <p className="text-xs text-gray-500 mt-1">Choisissez un championnat puis les équipes</p>
      </div>

      <div className="p-4 space-y-6 flex-1">
        {/* Championnat */}
        <div>
          <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
            Championnat
          </label>
          <div className="space-y-1">
            {LEAGUES_DATA.map((league) => (
              <button
                key={league.name}
                onClick={() => handleLeagueChange(league.name)}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all ${
                  selectedLeague === league.name
                    ? "bg-emerald-600/20 border border-emerald-500/50 text-emerald-400 font-semibold"
                    : "hover:bg-white/5 text-gray-300 border border-transparent"
                }`}
              >
                <span className="mr-2">{league.country.split(" ")[0]}</span>
                {league.name}
                <span className="ml-2 text-xs text-gray-500">
                  ({league.teams.length})
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Équipes — visibles seulement après sélection d'une ligue */}
        {selectedLeague && (
          <>
            {/* Domicile */}
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                🏠 Équipe Domicile
              </label>
              <select
                className="w-full p-2.5 rounded-lg bg-background border border-border text-sm focus:border-emerald-500 focus:outline-none transition-colors"
                value={home}
                onChange={(e) => handleHomeChange(e.target.value)}
              >
                <option value="">— Choisir une équipe —</option>
                {teams
                  .filter((t) => t !== away)
                  .map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
              </select>
            </div>

            {/* Extérieur */}
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                ✈️ Équipe Extérieure
              </label>
              <select
                className="w-full p-2.5 rounded-lg bg-background border border-border text-sm focus:border-emerald-500 focus:outline-none transition-colors"
                value={away}
                onChange={(e) => handleAwayChange(e.target.value)}
              >
                <option value="">— Choisir une équipe —</option>
                {teams
                  .filter((t) => t !== home)
                  .map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
              </select>
            </div>

            {/* Résumé */}
            {home && away && (
              <div className="bg-emerald-900/20 border border-emerald-500/30 rounded-xl p-3 text-center">
                <div className="text-xs text-gray-400 mb-1">Match sélectionné</div>
                <div className="font-bold text-emerald-400 text-sm">
                  {home}
                </div>
                <div className="text-gray-500 text-xs my-1">vs</div>
                <div className="font-bold text-emerald-400 text-sm">
                  {away}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </aside>
  );
}
