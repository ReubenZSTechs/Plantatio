import { Link } from "@tanstack/react-router";
import { ArrowLeft, Sprout, Flower2, ChevronRight } from "lucide-react";
import { CognitiveAssistant } from "./CognitiveAssistant";
// BarcodeScannerMock dihapus dari import jika tidak digunakan lagi di tempat lain
import { WeatherSyncWidget } from "./WeatherSyncWidget";
import { Card } from "@/components/ui/card";

export function B2CMainLayout() {
  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-10 border-b bg-card/80 backdrop-blur">
        <div className="mx-auto flex max-w-md items-center justify-between px-4 py-3">
          <Link to="/" className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
            <ArrowLeft className="h-4 w-4" /> Back
          </Link>
          <div className="flex items-center gap-1.5 font-semibold">
            <Sprout className="h-5 w-5 text-primary" /> PLANTATIO
          </div>
          <div className="text-xs text-muted-foreground">B2C</div>
        </div>
      </header>
      
      <main className="mx-auto max-w-md space-y-5 px-4 py-5">
        {/* Sinkronisasi Cuaca Cerdas */}
        <WeatherSyncWidget />
        
        {/* Fitur BarcodeScannerMock telah dihapus dari sini */}

        {/* ─── PINTASAN KE HALAMAN GARDEN ─── */}
        <Link to="/garden" className="block transition-transform active:scale-[0.98]">
          <Card className="flex cursor-pointer items-center justify-between border-primary/20 bg-card p-4 shadow-sm transition-colors hover:bg-secondary/40">
            <div className="flex items-center gap-4">
              <div className="flex h-11 w-11 items-center justify-center rounded-full bg-primary/10">
                <Flower2 className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h3 className="text-sm font-bold tracking-tight">My Garden Collection</h3>
                <p className="text-xs text-muted-foreground">View, add, and water your plants</p>
              </div>
            </div>
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-secondary/50">
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            </div>
          </Card>
        </Link>

        {/* Asisten Kognitif (AI Chat) */}
        <CognitiveAssistant />
      </main>
    </div>
  );
}