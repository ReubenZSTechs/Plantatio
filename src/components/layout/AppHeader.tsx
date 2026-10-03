import { Link } from "@tanstack/react-router";
import { Sprout } from "lucide-react";

import { ThemeToggle } from "./ThemeToggle";
import { cn } from "@/lib/utils";

export interface Crumb {
  label: string;
  to?: string;
}

interface AppHeaderProps {
  crumbs?: Crumb[];
  actions?: React.ReactNode;
  className?: string;
}

/**
 * The single application header.
 *
 * Five pages previously drew their own, with different widths, heights and
 * back-link behaviour.
 */
export function AppHeader({ crumbs = [], actions, className }: AppHeaderProps) {
  return (
    <header className={cn("sticky top-0 z-30 border-b bg-background/85 backdrop-blur", className)}>
      <div className="mx-auto flex h-14 max-w-7xl items-center gap-3 px-4 sm:px-6">
        <Link to="/" className="flex shrink-0 items-center gap-2 font-semibold tracking-tight">
          <Sprout className="h-5 w-5 text-primary" aria-hidden="true" />
          <span className="hidden sm:inline">Plantatio</span>
        </Link>

        {crumbs.length > 0 && (
          <nav aria-label="Breadcrumb" className="min-w-0 flex-1">
            <ol className="flex min-w-0 items-center gap-1.5 text-sm text-muted-foreground">
              {crumbs.map((crumb, index) => (
                <li key={crumb.label} className="flex min-w-0 items-center gap-1.5">
                  {index > 0 && <span aria-hidden="true">/</span>}
                  {crumb.to ? (
                    <Link
                      to={crumb.to}
                      className="truncate transition-colors hover:text-foreground"
                    >
                      {crumb.label}
                    </Link>
                  ) : (
                    <span className="truncate text-foreground" aria-current="page">
                      {crumb.label}
                    </span>
                  )}
                </li>
              ))}
            </ol>
          </nav>
        )}

        <div className="ml-auto flex items-center gap-1">
          {actions}
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
