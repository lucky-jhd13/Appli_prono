"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface AuthState {
  token: str | null;
  isPremium: boolean;
  userId: number | null;
}

interface AuthContextType extends AuthState {
  login: (token: str, isPremium: boolean, userId: number) => void;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>({
    token: null,
    isPremium: false,
    userId: null,
  });
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Restaurer la session depuis le localStorage
    const storedToken = localStorage.getItem("pf_token");
    const storedPremium = localStorage.getItem("pf_premium") === "true";
    const storedUserId = localStorage.getItem("pf_user_id");

    if (storedToken) {
      setAuthState({
        token: storedToken,
        isPremium: storedPremium,
        userId: storedUserId ? parseInt(storedUserId) : null,
      });
    }
    setIsLoading(false);
  }, []);

  const login = (token: str, isPremium: boolean, userId: number) => {
    localStorage.setItem("pf_token", token);
    localStorage.setItem("pf_premium", String(isPremium));
    localStorage.setItem("pf_user_id", String(userId));
    setAuthState({ token, isPremium, userId });
    router.push("/"); // Rediriger vers le dashboard
  };

  const logout = () => {
    localStorage.removeItem("pf_token");
    localStorage.removeItem("pf_premium");
    localStorage.removeItem("pf_user_id");
    setAuthState({ token: null, isPremium: false, userId: null });
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ ...authState, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
