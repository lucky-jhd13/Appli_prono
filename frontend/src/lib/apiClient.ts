// frontend/src/lib/apiClient.ts

import { apiFetch } from "@/lib/api";
import type { Match } from "@/types/match";
import type { CustomAnalysis } from "@/types/custom";
import type { BankrollInfo } from "@/types/bankroll";

/**
 * Récupère les matchs du jour depuis le backend.
 * Retourne un tableau de Match tel que défini côté frontend.
 */
export async function fetchMatchesToday(): Promise<Match[]> {
  const res = await apiFetch("/api/matches/today", {}, undefined);
  if (!res.ok) {
    throw new Error("Erreur lors du chargement des matchs du jour");
  }
  const data = await res.json();
  // Le backend renvoie { source, matches }
  return data.matches as Match[];
}

/**
 * Analyse d'un match personnalisé (page "Mon Match").
 * Envoie les équipes (et éventuelles cotes) puis reçoit les probabilités et value‑bets.
 */
export async function fetchCustomAnalysis(
  homeTeam: string,
  awayTeam: string,
  token: string | null,
  odds?: { home?: number; draw?: number; away?: number }
): Promise<CustomAnalysis> {
  const body: any = { home_team: homeTeam, away_team: awayTeam };
  if (odds) {
    body.odd_home = odds.home;
    body.odd_draw = odds.draw;
    body.odd_away = odds.away;
  }

  const res = await apiFetch("/api/custom/analyze", {
    method: "POST",
    body: JSON.stringify(body),
  }, token ?? undefined);

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Erreur d'analyse personnalisée");
  }

  return (await res.json()) as CustomAnalysis;
}

/**
 * Récupère les données de bankroll de l'utilisateur connecté.
 */
export async function fetchBankroll(token: string | null): Promise<BankrollInfo> {
  const res = await apiFetch("/api/bankroll/", {}, token ?? undefined);
  if (!res.ok) {
    throw new Error("Impossible de récupérer la bankroll");
  }
  return (await res.json()) as BankrollInfo;
}

/**
 * Envoie un pari (utilisé dans la page Bankroll).
 */
export async function placeBet(
  bet: {
    match_name: string;
    bet_type: string;
    odd: number;
    stake: number;
    model_prob?: number;
    confidence_score?: number;
  },
  token: string | null
) {
  const res = await apiFetch("/api/bankroll/bet", {
    method: "POST",
    body: JSON.stringify(bet),
  }, token ?? undefined);

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Erreur lors de l'enregistrement du pari");
  }
  return await res.json();
}

/**
 * Résout un pari (gagné / perdu).
 */
export async function resolveBet(
  betId: number,
  won: boolean,
  token: string | null
) {
  const res = await apiFetch("/api/bankroll/resolve", {
    method: "POST",
    body: JSON.stringify({ bet_id: betId, won }),
  }, token ?? undefined);

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Erreur lors de la résolution du pari");
  }
  return await res.json();
}
