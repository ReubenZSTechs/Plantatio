import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Info, Loader2, TreeDeciduous } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { LandParcel } from "@/types/plant";
import { SiteMap, potentialColor } from "./SiteMap";

const POTENTIAL_FILTERS = [
  { label: "All sites", value: 0 },
  { label: "Promising", value: 0.35 },
  { label: "High potential", value: 0.6 },
];

/**
 * Restoration candidates across the monitored site.
 *
 * Potential measures how much a parcel could gain, not what it is worth now:
 * degraded pasture ranks above mature forest, which is already at capacity.
 */
export function GreenLandsView() {
  const [minPotential, setMinPotential] = useState(0);
  const [selected, setSelected] = useState<LandParcel | null>(null);

  const parcels = useQuery({
    queryKey: ["land-parcels", minPotential],
    queryFn: () => api.listLandParcels({ minPotential: minPotential || undefined }),
  });

  const nodes = useQuery({ queryKey: ["devices"], queryFn: api.listDevices });
  const legend = useQuery({
    queryKey: ["land-cover-classes"],
    queryFn: api.getLandCoverClasses,
  });

  const totals = useMemo(() => {
    const rows = parcels.data ?? [];
    return {
      count: rows.length,
      hectares: rows.reduce((sum, p) => sum + (p.areaHectares ?? 0), 0),
      best: rows[0] ?? null,
    };
  }, [parcels.data]);

  const active = selected ?? totals.best;

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Green Lands</h1>
          <p className="text-sm text-muted-foreground">
            Candidate parcels ranked by how much restoration they could support.
          </p>
        </div>

        <div className="flex gap-1.5" role="group" aria-label="Filter by potential">
          {POTENTIAL_FILTERS.map((filter) => (
            <button
              key={filter.label}
              type="button"
              onClick={() => setMinPotential(filter.value)}
              aria-pressed={minPotential === filter.value}
              className={cn(
                "rounded-full border px-3 py-1 text-xs transition-colors",
                minPotential === filter.value
                  ? "border-primary bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-secondary",
              )}
            >
              {filter.label}
            </button>
          ))}
        </div>
      </header>

      <div className="grid gap-3 sm:grid-cols-3">
        <SummaryTile label="Candidate parcels" value={String(totals.count)} />
        <SummaryTile label="Total area" value={`${totals.hectares.toFixed(1)} ha`} />
        <SummaryTile
          label="Best opportunity"
          value={totals.best?.name ?? "—"}
          hint={
            totals.best
              ? `${((totals.best.restorationPotential ?? 0) * 100).toFixed(0)}% potential`
              : undefined
          }
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1.5fr)_minmax(0,1fr)]">
        <Card className="overflow-hidden p-0">
          {parcels.isLoading ? (
            <div className="flex h-[420px] items-center justify-center text-sm text-muted-foreground">
              <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
              Loading site map…
            </div>
          ) : parcels.isError ? (
            <div className="flex h-[420px] items-center justify-center px-6 text-center text-sm text-muted-foreground">
              Could not load parcels. Check that the API is running.
            </div>
          ) : (
            <SiteMap
              className="h-[420px]"
              parcels={parcels.data ?? []}
              nodes={nodes.data ?? []}
              selectedParcelId={active?.id ?? null}
              onSelectParcel={setSelected}
            />
          )}
        </Card>

        <div className="space-y-4">
          <Card className="divide-y p-0">
            <h2 className="px-4 py-3 text-sm font-semibold">Ranked candidates</h2>

            {(parcels.data ?? []).length === 0 && !parcels.isLoading && (
              <p className="px-4 py-6 text-center text-sm text-muted-foreground">
                No parcels match this filter.
              </p>
            )}

            <ul>
              {(parcels.data ?? []).map((parcel) => (
                <li key={parcel.id}>
                  <button
                    type="button"
                    onClick={() => setSelected(parcel)}
                    aria-current={active?.id === parcel.id}
                    className={cn(
                      "flex w-full items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-secondary/50",
                      active?.id === parcel.id && "bg-secondary/60",
                    )}
                  >
                    <span
                      className="h-8 w-1.5 shrink-0 rounded-full"
                      style={{ background: potentialColor(parcel.restorationPotential) }}
                      aria-hidden="true"
                    />
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-medium">{parcel.name}</span>
                      <span className="block truncate text-xs text-muted-foreground">
                        {parcel.landCoverClass} · {parcel.areaHectares} ha
                      </span>
                    </span>
                    <span className="text-sm font-semibold tabular-nums">
                      {((parcel.restorationPotential ?? 0) * 100).toFixed(0)}%
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </Card>

          {active && <ParcelDetail parcel={active} />}
        </div>
      </div>

      {legend.data && legend.data.length > 0 && (
        <Card className="p-4">
          <h2 className="flex items-center gap-1.5 text-sm font-semibold">
            Land-cover reference
            <Info className="h-3.5 w-3.5 text-muted-foreground" aria-hidden="true" />
          </h2>
          <p className="mt-1 text-xs text-muted-foreground">
            Headroom is how much restoration each cover type can absorb. Reference tile counts come
            from a labelled EuroSAT sample used to illustrate the classes — they are synthetic
            examples, not measurements of this site.
          </p>

          <ul className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {legend.data.map((entry) => (
              <li key={entry.name} className="rounded-lg border p-2.5">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-medium">{entry.name}</span>
                  <Badge variant="secondary" className="text-[10px]">
                    {(entry.headroom * 100).toFixed(0)}%
                  </Badge>
                </div>
                <p className="mt-1 text-[11px] leading-snug text-muted-foreground">
                  {entry.description}
                </p>
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}

function SummaryTile({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <Card className="p-4">
      <p className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
        {label}
      </p>
      <p className="mt-1 truncate text-xl font-semibold">{value}</p>
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
    </Card>
  );
}

function ParcelDetail({ parcel }: { parcel: LandParcel }) {
  const metrics = [
    { label: "Canopy cover", value: parcel.canopyCover },
    { label: "Est. biomass", value: parcel.estBiomass },
    { label: "Carbon equivalent", value: parcel.carbonEq },
  ];

  return (
    <Card className="space-y-3 p-4">
      <div className="flex items-start gap-2">
        <TreeDeciduous className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
        <div className="min-w-0">
          <h2 className="truncate text-sm font-semibold">{parcel.name}</h2>
          <p className="text-xs text-muted-foreground">
            {parcel.zone} · {parcel.areaHectares} ha
          </p>
        </div>
      </div>

      {parcel.rationale && (
        <p className="rounded-lg bg-secondary/50 p-2.5 text-xs text-muted-foreground">
          {parcel.rationale}
        </p>
      )}

      <dl className="space-y-2.5">
        {metrics.map((metric) => (
          <div key={metric.label}>
            <div className="flex items-center justify-between text-xs">
              <dt className="text-muted-foreground">{metric.label}</dt>
              <dd className="font-medium tabular-nums">
                {metric.value === null ? "—" : `${(metric.value * 100).toFixed(0)}%`}
              </dd>
            </div>
            <Progress value={(metric.value ?? 0) * 100} className="mt-1 h-1" />
          </div>
        ))}
      </dl>

      {parcel.analyzedAt ? (
        <p className="text-[11px] text-muted-foreground">
          Last analysed {new Date(parcel.analyzedAt).toLocaleDateString()}
        </p>
      ) : (
        <p className="text-[11px] text-muted-foreground">
          Not yet analysed from imagery; values are the seeded baseline.
        </p>
      )}
    </Card>
  );
}
