"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ThemeToggle } from "@/components/theme-toggle";
import { useAuth } from "@/lib/auth-context";
import { useState } from "react";
import { 
  LayoutDashboard, 
  TrendingUp, 
  Swords, 
  Wallet, 
  LogOut,
  ShieldCheck,
  Menu,
  X
} from "lucide-react";

const NAV_LINKS = [
  { href: "/dashboard", label: "Matchs du Jour", icon: LayoutDashboard },
  { href: "/dashboard/value-bets", label: "Value Bets", icon: TrendingUp, premium: true },
  { href: "/dashboard/custom", label: "Mon Match", icon: Swords },
  { href: "/dashboard/bankroll", label: "Bankroll", icon: Wallet },
];

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { logout, isPremium } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <div className="flex h-screen bg-background text-foreground transition-colors duration-300">
      {/* Mobile Header */}
      <div className="md:hidden fixed top-0 left-0 right-0 h-16 bg-card border-b border-border z-50 flex items-center justify-between px-4">
        <h1 className="text-xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500">
          PRO-FOOT AI
        </h1>
        <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="p-2">
          {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Sidebar */}
      <aside className={`
        fixed md:static inset-y-0 left-0 z-40 w-64 border-r border-border bg-card flex flex-col transform transition-transform duration-300
        ${isMobileMenuOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}
      `}>
        <div className="p-6 hidden md:block">
          <h1 className="text-2xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500 tracking-tight">
            PRO-FOOT AI
          </h1>
          <div className="mt-2 text-xs flex items-center gap-1 font-semibold">
            {isPremium ? (
              <span className="text-primary flex items-center gap-1"><ShieldCheck size={14}/> Premium Actif</span>
            ) : (
              <span className="text-gray-500">Compte Standard</span>
            )}
          </div>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-4">
          {NAV_LINKS.map((link) => {
            const isActive = pathname === link.href;
            const Icon = link.icon;
            
            return (
              <Link 
                key={link.href} 
                href={link.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all ${
                  isActive 
                    ? "bg-primary/10 text-primary" 
                    : "text-gray-500 hover:bg-border/50 hover:text-foreground"
                }`}
              >
                <Icon size={20} />
                {link.label}
                {link.premium && !isPremium && (
                  <span className="ml-auto text-[10px] uppercase tracking-wider bg-orange-500/20 text-orange-500 px-2 py-0.5 rounded-full">Pro</span>
                )}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-border space-y-4">
          <ThemeToggle />
          <button 
            onClick={logout}
            className="flex items-center gap-3 px-4 py-3 w-full text-red-500 hover:bg-red-500/10 rounded-xl transition-all font-medium"
          >
            <LogOut size={20} />
            Déconnexion
          </button>
        </div>
      </aside>

      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto pt-16 md:pt-0">
        {children}
      </main>
    </div>
  );
}
