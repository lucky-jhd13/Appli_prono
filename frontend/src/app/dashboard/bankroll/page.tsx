"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";

export default function BankrollPage() {
  const { token } = useAuth();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const fetchBankroll = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/bankroll/", {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (res.ok) {
          setData(await res.json());
        }
      } catch (err) {
        console.error(err);
      }
    };
    if (token) fetchBankroll();
  }, [token]);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <header>
        <h1 className="text-3xl font-bold">Gestion de Bankroll</h1>
        <p className="text-gray-500 mt-2">Suivez vos performances en temps réel.</p>
      </header>

      {data ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-card border border-border rounded-2xl p-6 shadow-sm flex flex-col justify-between">
            <h3 className="text-gray-500 text-sm font-medium mb-2 line-clamp-2">Capital Actuel</h3>
            <p className="text-3xl lg:text-4xl font-bold text-primary truncate" title={`${data.current_bankroll.toFixed(2)} €`}>
              {data.current_bankroll.toFixed(2)} €
            </p>
          </div>
          <div className="bg-card border border-border rounded-2xl p-6 shadow-sm flex flex-col justify-between">
            <h3 className="text-gray-500 text-sm font-medium mb-2 line-clamp-2">Retour sur Investissement (ROI)</h3>
            <p className={`text-3xl lg:text-4xl font-bold truncate ${data.roi_pct >= 0 ? "text-emerald-500" : "text-red-500"}`}>
              {data.roi_pct > 0 ? "+" : ""}{data.roi_pct.toFixed(2)}%
            </p>
          </div>
          <div className="bg-card border border-border rounded-2xl p-6 shadow-sm flex flex-col justify-between">
            <h3 className="text-gray-500 text-sm font-medium mb-2 line-clamp-2">Taux de Réussite</h3>
            <p className="text-3xl lg:text-4xl font-bold truncate">{data.win_rate_pct.toFixed(1)}%</p>
          </div>
        </div>
      ) : (
        <div className="text-gray-500">Chargement des données...</div>
      )}
    </div>
  );
}
