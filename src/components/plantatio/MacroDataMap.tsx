import { useQuery } from "@tanstack/react-query";
import { Activity, Droplets, Loader2, Thermometer, Wind } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { api } from "@/lib/api";
import { SiteMap } from "./SiteMap";

const SEVERITY_STYLES: Record<string, string> = {
  critical: "bg-destructive/15 text-destructive",
  warn: "bg-warning/15 text-warning-foreground",
  info: "bg-secondary text-secondary-foreground",
};

/**
 * Field overview: sensors on a real map, with current conditions beside them.
 *
 * The previous map normalised each coordinate axis independently into CSS
 * percentages over an SVG grid, so distances and shapes were meaningless.
 */
export function MacroDataMap() {
  const nodes = useQuery({ queryKey: ["devices"], queryFn: api.listDevices });
  const parcels = useQuery({
    queryKey: ["land-parcels", 0],
    queryFn: () => api.listLandParcels(),
  });
  const weather = useQuery({ queryKey: ["weather-macro"], queryFn: api.getWeatherMacro });
  const logs = useQuery({ queryKey: ["tactical-logs"], queryFn: api.getTacticalLogs });

  const online = (nodes.data ?? []).filter((node) => node.status === "ok").length;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">Site Map</h1>
        <p className="text-sm text-muted-foreground">
          Sensor fleet and restoration parcels across the monitored area.
        </p>
      </header>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
        <Card className="overflow-hidden p-0">
          {nodes.isLoading ? (
            <div className="flex h-[420px] items-center justify-center text-sm text-muted-foreground">
              <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
              Loading map…
            </div>
          ) : nodes.isError ? (
            <div className="flex h-[420px] items-center justify-center px-6 text-center text-sm text-muted-foreground">
              Could not load the sensor fleet. Check that the API is running.
            </div>
          ) : (
            <SiteMap className="h-[420px]" nodes={nodes.data ?? []} parcels={parcels.data ?? []} />
          )}
        </Card>

        <div className="space-y-4">
          <Card className="p-4">
            <h2 className="text-sm font-semibold">Conditions</h2>

            {weather.isLoading ? (
              <p className="mt-3 text-xs text-muted-foreground">Loading…</p>
            ) : weather.isError ? (
              <p className="mt-3 text-xs text-muted-foreground">Unavailable.</p>
            ) : (
              <dl className="mt-3 space-y-2.5 text-sm">
                <Reading
                  icon={<Thermometer className="h-3.5 w-3.5" />}
                  label={weather.data!.city}
                  value={`${weather.data!.tempC}°C`}
                />
                <Reading
                  icon={<Droplets className="h-3.5 w-3.5" />}
                  label="Humidity"
                  value={`${weather.data!.humidity}%`}
                />
                <Reading
                  icon={<Wind className="h-3.5 w-3.5" />}
                  label="Condition"
                  value={weather.data!.condition}
                />
                <Reading
                  icon={<Activity className="h-3.5 w-3.5" />}
                  label="Nodes online"
                  value={`${online} / ${nodes.data?.length ?? 0}`}
                />
              </dl>
            )}
          </Card>

          <Card className="p-4">
            <h2 className="text-sm font-semibold">Recent activity</h2>

            {(logs.data ?? []).length === 0 ? (
              <p className="mt-3 text-xs text-muted-foreground">No activity recorded yet.</p>
            ) : (
              <ul className="mt-3 space-y-2">
                {(logs.data ?? []).map((log) => (
                  <li key={log.id} className="flex items-start gap-2 text-xs">
                    <Badge
                      variant="secondary"
                      className={SEVERITY_STYLES[log.severity] ?? SEVERITY_STYLES.info}
                    >
                      {log.time}
                    </Badge>
                    <span className="min-w-0 flex-1 text-muted-foreground">{log.action}</span>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}

function Reading({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <dt className="flex min-w-0 items-center gap-1.5 text-muted-foreground">
        <span aria-hidden="true">{icon}</span>
        <span className="truncate text-xs">{label}</span>
      </dt>
      <dd className="shrink-0 text-sm font-medium">{value}</dd>
    </div>
  );
}
