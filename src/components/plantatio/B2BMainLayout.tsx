import { useState } from "react";
import { Link, Outlet, useRouterState } from "@tanstack/react-router";
import {
  BarChart3,
  BrainCircuit,
  Cpu,
  Map,
  Menu,
  MessageSquareCode,
  Sprout,
  TreeDeciduous,
  X,
} from "lucide-react";

import { AppHeader } from "@/components/layout/AppHeader";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface NavItem {
  to: string;
  label: string;
  icon: React.ReactNode;
}

/**
 * Each view is a route, not a tab.
 *
 * These were `useState` values, so views could not be linked to or
 * bookmarked, browser Back left the console entirely, and a refresh reset to
 * the dashboard. ML Predictions was unreachable because its entry was
 * commented out while its render branch stayed live.
 */
const NAV: NavItem[] = [
  { to: "/b2b/esg", label: "ESG Analytics", icon: <BarChart3 className="h-4 w-4" /> },
  { to: "/b2b/green-lands", label: "Green Lands", icon: <TreeDeciduous className="h-4 w-4" /> },
  { to: "/b2b/map", label: "Site Map", icon: <Map className="h-4 w-4" /> },
  { to: "/b2b/devices", label: "Devices", icon: <Cpu className="h-4 w-4" /> },
  { to: "/b2b/insights", label: "Insight Engine", icon: <MessageSquareCode className="h-4 w-4" /> },
  { to: "/b2b/predictions", label: "Models", icon: <BrainCircuit className="h-4 w-4" /> },
];

export function B2BMainLayout() {
  const [isNavOpen, setIsNavOpen] = useState(false);
  const pathname = useRouterState({ select: (state) => state.location.pathname });

  const current = NAV.find((item) => pathname.startsWith(item.to));

  return (
    <div className="min-h-screen bg-background">
      <AppHeader
        crumbs={[
          { label: "Enterprise", to: "/b2b" },
          ...(current ? [{ label: current.label }] : []),
        ]}
        actions={
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setIsNavOpen(true)}
            aria-label="Open navigation"
          >
            <Menu className="h-4 w-4" aria-hidden="true" />
          </Button>
        }
      />

      <div className="mx-auto flex max-w-7xl">
        {/* Desktop sidebar */}
        <aside className="hidden w-60 shrink-0 border-r md:block">
          <nav aria-label="Enterprise sections" className="sticky top-14 space-y-1 p-3">
            {NAV.map((item) => (
              <NavLink key={item.to} item={item} isActive={pathname.startsWith(item.to)} />
            ))}
          </nav>
        </aside>

        {/* Mobile drawer. Without this the sidebar simply vanished below
            768px, leaving five of six views unreachable on a phone. */}
        {isNavOpen && (
          <div className="fixed inset-0 z-50 md:hidden">
            <button
              type="button"
              className="absolute inset-0 bg-foreground/40"
              onClick={() => setIsNavOpen(false)}
              aria-label="Close navigation"
            />
            <nav
              aria-label="Enterprise sections"
              className="absolute inset-y-0 left-0 w-64 space-y-1 bg-background p-3 shadow-xl"
            >
              <div className="mb-2 flex items-center justify-between px-2 py-1">
                <span className="flex items-center gap-2 font-semibold">
                  <Sprout className="h-4 w-4 text-primary" aria-hidden="true" />
                  Plantatio
                </span>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsNavOpen(false)}
                  aria-label="Close navigation"
                >
                  <X className="h-4 w-4" aria-hidden="true" />
                </Button>
              </div>

              {NAV.map((item) => (
                <NavLink
                  key={item.to}
                  item={item}
                  isActive={pathname.startsWith(item.to)}
                  onNavigate={() => setIsNavOpen(false)}
                />
              ))}
            </nav>
          </div>
        )}

        <main className="min-w-0 flex-1 p-4 sm:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

function NavLink({
  item,
  isActive,
  onNavigate,
}: {
  item: NavItem;
  isActive: boolean;
  onNavigate?: () => void;
}) {
  return (
    <Link
      to={item.to}
      onClick={onNavigate}
      aria-current={isActive ? "page" : undefined}
      className={cn(
        "flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors",
        isActive
          ? "bg-secondary font-medium text-foreground"
          : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground",
      )}
    >
      {item.icon}
      {item.label}
    </Link>
  );
}
