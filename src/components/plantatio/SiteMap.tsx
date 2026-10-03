import { lazy, Suspense } from "react";
import { Loader2 } from "lucide-react";

import type { IotNode, LandParcel } from "@/types/plant";

export interface SiteMapProps {
  parcels?: LandParcel[];
  nodes?: IotNode[];
  selectedParcelId?: number | null;
  onSelectParcel?: (parcel: LandParcel) => void;
  className?: string;
}

/**
 * Leaflet reads `window` as soon as it is imported, which throws during server
 * rendering. Loading the map lazily keeps it out of the server bundle.
 */
const LeafletMap = lazy(() =>
  import("./SiteMapCanvas").then((module) => ({ default: module.SiteMapCanvas })),
);

/** Slippy map of restoration parcels and the sensor fleet. */
export function SiteMap(props: SiteMapProps) {
  return (
    <Suspense
      fallback={
        <div className={props.className} style={{ minHeight: 320 }} aria-busy="true">
          <div className="flex h-full w-full items-center justify-center rounded-xl bg-muted/40 text-sm text-muted-foreground">
            <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
            Loading map…
          </div>
        </div>
      }
    >
      <LeafletMap {...props} />
    </Suspense>
  );
}

/** Green through amber to grey as restoration potential falls. */
export function potentialColor(potential: number | null): string {
  if (potential === null) return "#94a3b8";
  if (potential >= 0.6) return "#15803d";
  if (potential >= 0.35) return "#65a30d";
  if (potential >= 0.15) return "#d97706";
  return "#94a3b8";
}
