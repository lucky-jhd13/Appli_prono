"use client";

import { ThemeToggle } from "@/components/theme-toggle";
import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-background text-foreground transition-colors duration-300 p-8">
      <div className="max-w-7xl mx-auto space-y-12">
        <header className="flex justify-between items-center bg-card border border-border rounded-2xl p-6 shadow-sm">
          <div>
            <h1 className="text-4xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500 tracking-tight">
              PRO-FOOT AI
            </h1>
            <p className="text-gray-500 dark:text-gray-400 mt-2">
              Votre moteur de pronostics professionnel
            </p>
          </div>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <Link 
              href="/dashboard"
              className="px-6 py-2 bg-gradient-to-r from-primary to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 transition-all rounded-full font-semibold text-white shadow-lg transform hover:-translate-y-1"
            >
              Tableau de bord
            </Link>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card example */}
          <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
            <h3 className="font-bold text-xl mb-2">Matchs du Jour</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              Consultez les prédictions Dixon-Coles pour les matchs d'aujourd'hui.
            </p>
            <div className="flex justify-between items-center bg-border/20 p-4 rounded-lg">
              <span className="font-bold">Real Madrid vs Barcelona</span>
              <span className="bg-primary text-white text-xs px-2 py-1 rounded">Premium</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
