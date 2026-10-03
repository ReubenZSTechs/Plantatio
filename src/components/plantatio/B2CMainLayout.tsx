import { Link } from "@tanstack/react-router";
import { ChevronRight, Flower2, Sparkles } from "lucide-react";

import { AppHeader } from "@/components/layout/AppHeader";
import { Card } from "@/components/ui/card";
import { ChatPanel } from "./ChatPanel";
import { WeatherSyncWidget } from "./WeatherSyncWidget";

const SUGGESTIONS = [
  "Why are my tomato leaves yellowing?",
  "How often should I water this week?",
  "What causes brown spots on leaves?",
];

/** Home for consumer growers: conditions, their garden, and the assistant. */
export function B2CMainLayout() {
  return (
    <div className="min-h-screen bg-background">
      <AppHeader crumbs={[{ label: "For growers" }]} />

      <main className="mx-auto max-w-5xl px-4 py-6 sm:px-6">
        <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)]">
          <div className="space-y-5">
            <WeatherSyncWidget />

            <Link to="/garden" className="block transition-transform active:scale-[0.99]">
              <Card className="flex items-center justify-between gap-4 p-4 transition-colors hover:bg-secondary/40">
                <div className="flex min-w-0 items-center gap-4">
                  <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-primary/10">
                    <Flower2 className="h-5 w-5 text-primary" aria-hidden="true" />
                  </span>
                  <div className="min-w-0">
                    <h2 className="text-sm font-semibold">My garden</h2>
                    <p className="truncate text-xs text-muted-foreground">
                      Track your plants, log care, and scan leaves for disease
                    </p>
                  </div>
                </div>
                <ChevronRight
                  className="h-4 w-4 shrink-0 text-muted-foreground"
                  aria-hidden="true"
                />
              </Card>
            </Link>

            <Card className="p-4">
              <h2 className="flex items-center gap-1.5 text-sm font-semibold">
                <Sparkles className="h-4 w-4 text-primary" aria-hidden="true" />
                How the assistant answers
              </h2>
              <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
                Questions are broken into parts, matched against a knowledge graph built from tomato
                research, and answered from what it finds. Expand the sources under any reply to see
                the facts behind it.
              </p>
            </Card>
          </div>

          <ChatPanel
            scope="b2c"
            title="Growing assistant"
            subtitle="Grounded in agronomy research"
            greeting="Hello. Ask me anything about growing — I'll show you the evidence behind each answer."
            suggestions={SUGGESTIONS}
            className="h-[min(640px,calc(100vh-7rem))] lg:sticky lg:top-20"
          />
        </div>
      </main>
    </div>
  );
}
