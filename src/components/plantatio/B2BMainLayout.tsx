import { useState } from "react";
import { Link } from "@tanstack/react-router";
import { Sprout, BarChart3, Map, Cpu, ArrowLeft, Bell, Search } from "lucide-react";
import { ESGAnalyticsDashboard } from "./ESGAnalyticsDashboard";
import { MacroDataMap } from "./MacroDataMap";
import { DeviceManager } from "./DeviceManager";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { InsightEngine } from "./InsightEngine";
import { MessageSquareCode } from "lucide-react"; // Icon yang lebih teknis
import { MLPredictionManager } from "./MLPredictionManager";
import { BrainCircuit } from "lucide-react"; // Icon untuk ML

type View = "dashboard" | "map" | "devices" | "insights" | "predictions";

const NAV: { key: View; label: string; icon: React.ReactNode }[] = [
  { key: "dashboard", label: "ESG Analytics", icon: <BarChart3 className="h-4 w-4" /> },
  { key: "map", label: "Macro Data Map", icon: <Map className="h-4 w-4" /> },
  { key: "devices", label: "Device Manager", icon: <Cpu className="h-4 w-4" /> },
  { key: "insights", label: "Insight Engine", icon: <MessageSquareCode className="h-4 w-4" /> },
  // { key: "predictions", label: "ML Predictions", icon: <BrainCircuit className="h-4 w-4" /> }, // Tab baru
];

export function B2BMainLayout() {
  const [view, setView] = useState<View>("dashboard");

  return (
    <div className="flex min-h-screen bg-background">
      <aside className="hidden w-64 shrink-0 flex-col border-r bg-sidebar text-sidebar-foreground md:flex">
        <div className="flex items-center gap-2 px-5 py-5">
          <Sprout className="h-6 w-6 text-sidebar-primary" />
          <div className="text-lg font-semibold">PLANTATIO</div>
        </div>
        <nav className="flex-1 space-y-1 px-3">
          {NAV.map((n) => (
            <button
              key={n.key}
              onClick={() => setView(n.key)}
              className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors ${
                view === n.key
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground/70 hover:bg-sidebar-accent/60"
              }`}
            >
              {n.icon}
              {n.label}
            </button>
          ))}
        </nav>
        <div className="border-t border-sidebar-border p-4 text-xs">
          <div className="font-medium">Verra Auditor</div>
          <div className="opacity-70">Carbon Registry · v2</div>
        </div>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex items-center gap-3 border-b bg-card px-6 py-3">
          <Link to="/" className="text-sm text-muted-foreground hover:text-foreground md:hidden">
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <div className="relative max-w-md flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input placeholder="Search zones, nodes, species…" className="pl-9" />
          </div>
          <Button variant="ghost" size="icon"><Bell className="h-4 w-4" /></Button>
          <Link to="/" className="hidden text-sm text-muted-foreground hover:text-foreground md:inline">Switch role</Link>
        </header>
        <main className="flex-1 overflow-auto p-6">
          {view === "dashboard" && <ESGAnalyticsDashboard />}
          {view === "map" && <MacroDataMap />}
          {view === "devices" && <DeviceManager />}
          {view === "insights" && <InsightEngine />}
          {view === "predictions" && <MLPredictionManager />}
        </main>
      </div>
    </div>
  );
}