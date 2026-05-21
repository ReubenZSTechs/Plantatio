import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Wind, Droplet, Satellite, CloudRain, Activity, Loader2 } from "lucide-react";
import { toast } from "sonner";

// Menggunakan tipe data yang ditarik dari API
import { IotNode } from "./DeviceManager"; // Pastikan path import ini sesuai

const API_BASE = "http://localhost:8000/api";

const statusColor: Record<string, string> = {
  ok: "bg-emerald-500",
  warn: "bg-amber-500",
  critical: "bg-destructive",
};

export function MacroDataMap() {
  const [nodes, setNodes] = useState<IotNode[]>([]);
  const [tacticalLogs, setTacticalLogs] = useState<any[]>([]);
  const [weatherData, setWeatherData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Fetch semua data dari API secara bersamaan
    Promise.all([
      fetch(`${API_BASE}/b2b/devices`).then((res) => res.json()),
      fetch(`${API_BASE}/v1/weather/macro`).then((res) => res.json()),
      fetch(`${API_BASE}/b2b/agents/log`).then((res) => res.json()),
    ])
      .then(([devicesData, weatherRes, logsData]) => {
        setNodes(devicesData);
        setWeatherData(weatherRes);
        setTacticalLogs(logsData);
      })
      .catch(() => toast.error("Gagal sinkronisasi data dari server"))
      .finally(() => setIsLoading(false));
  }, []);

  // ─── LOGIKA PEMETAAN KOORDINAT (GPS -> CSS %) ───
  // Mencari batas Latitude & Longitude dari semua sensor untuk membuat bounding box
  const minLat = Math.min(...nodes.map((n) => n.latitude));
  const maxLat = Math.max(...nodes.map((n) => n.latitude));
  const minLng = Math.min(...nodes.map((n) => n.longitude));
  const maxLng = Math.max(...nodes.map((n) => n.longitude));

  const getMapPosition = (lat: number, lng: number) => {
    // Jika hanya ada 1 node, taruh di tengah
    if (nodes.length <= 1) return { top: "50%", left: "50%" };

    const latRange = maxLat - minLat || 1; // Mencegah division by zero
    const lngRange = maxLng - minLng || 1;

    // Normalisasi koordinat ke skala 10% - 90% pada kotak map
    // (Latitude dibalik karena pada peta, Latitude tinggi/utara ada di atas (Y lebih kecil))
    const top = 10 + ((maxLat - lat) / latRange) * 80;
    const left = 10 + ((lng - minLng) / lngRange) * 80;

    return { top: `${top}%`, left: `${left}%` };
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Macro Data & Field Map</h1>
        <p className="text-sm text-muted-foreground">Live IoT mesh telemetry overlaid on environmental macro data.</p>
      </div>

      {isLoading ? (
        <div className="flex h-64 items-center justify-center rounded-xl border border-dashed">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <Card className="overflow-hidden lg:col-span-2">
            <div className="relative h-[420px] bg-[oklch(0.95_0.03_140)] dark:bg-slate-900 overflow-hidden">
              {/* Stylized topo grid */}
              <svg className="absolute inset-0 h-full w-full opacity-40 dark:opacity-20" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <pattern id="g" width="40" height="40" patternUnits="userSpaceOnUse">
                    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" strokeWidth="0.5" />
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#g)" />
              </svg>
              {/* Fake terrain blobs */}
              <div className="absolute left-[10%] top-[15%] h-40 w-56 rounded-full bg-emerald-500/10 blur-2xl" />
              <div className="absolute right-[8%] bottom-[10%] h-52 w-72 rounded-full bg-blue-500/10 blur-3xl" />

              {/* RENDER SENSOR NODES SESUAI TITIK GPS (LAT/LNG) */}
              {nodes.map((n) => {
                const pos = getMapPosition(n.latitude, n.longitude);
                return (
                  <div
                    key={n.id}
                    className="group absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all duration-500 hover:z-10"
                    style={pos}
                  >
                    <span className={`relative block h-3.5 w-3.5 rounded-full ${statusColor[n.status]} ring-4 ring-background shadow-md`}>
                      <span className={`absolute inset-0 animate-ping rounded-full ${statusColor[n.status]} opacity-60`} />
                    </span>
                    {/* Tooltip Koordinat */}
                    <div className="pointer-events-none absolute left-5 top-0 hidden w-max rounded-md bg-foreground px-3 py-2 text-xs text-background group-hover:block shadow-xl z-20">
                      <p className="font-bold">{n.id} · {n.zone}</p>
                      <p className="text-muted-foreground mt-0.5">Moisture: {n.moisture}% | Battery: {n.battery}%</p>
                      <p className="text-[9px] opacity-60 font-mono mt-1">{n.latitude}, {n.longitude}</p>
                    </div>
                  </div>
                );
              })}

              <div className="absolute bottom-3 left-3 flex gap-3 rounded-lg bg-card/95 px-3 py-2 text-xs shadow-md backdrop-blur">
                <Legend color="bg-emerald-500" label="Healthy" />
                <Legend color="bg-amber-500" label="Warning" />
                <Legend color="bg-destructive" label="Critical" />
              </div>
            </div>
          </Card>

          <div className="space-y-4">
            <Card className="p-5">
              <div className="mb-3 flex items-center justify-between">
                <div className="text-sm font-semibold">Macro Environment</div>
                <Badge variant="secondary" className="text-[10px]">{weatherData?.city || "Unknown"}</Badge>
              </div>
              <div className="space-y-2 text-sm">
                <Row icon={<Activity className="h-4 w-4" />} label="Temperature" value={`${weatherData?.tempC || 0}°C`} />
                <Row icon={<Droplet className="h-4 w-4" />} label="Humidity" value={`${weatherData?.humidity || 0}%`} />
                <Row icon={<CloudRain className="h-4 w-4" />} label="Condition" value={weatherData?.condition || "-"} />
                {/* Simulasi Data Pertanian (Bisa ditambahkan ke Endpoint Weather nanti) */}
                <Row icon={<Wind className="h-4 w-4" />} label="Wind Speed" value="12 km/h" />
                <Row icon={<Satellite className="h-4 w-4" />} label="Satellite Pass" value="14:00 WIB" />
              </div>
            </Card>

            <Card className="p-5 flex-1 max-h-[180px] overflow-y-auto">
              <div className="mb-3 flex items-center justify-between sticky top-0 bg-card z-10 pb-2">
                <div className="text-sm font-semibold">AI Tactical Decisions</div>
                <Badge variant="outline" className="text-[10px] text-blue-500 border-blue-200 bg-blue-50 dark:bg-blue-900/20">LIVE STREAM</Badge>
              </div>
              <ol className="space-y-3">
                {tacticalLogs.map((l, i) => (
                  <li key={i} className="flex gap-3 text-sm">
                    <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${
                      l.severity === "critical" ? "bg-destructive" : l.severity === "warn" ? "bg-warning" : "bg-primary"
                    }`} />
                    <div className="flex-1">
                      <div className="text-xs text-muted-foreground">{l.time}</div>
                      <div className="font-medium text-sm leading-tight mt-0.5">{l.action}</div>
                    </div>
                  </li>
                ))}
              </ol>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}

function Legend({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-1.5">
      <span className={`h-2 w-2 rounded-full ${color}`} />
      <span>{label}</span>
    </div>
  );
}

function Row({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center justify-between border-b py-2.5 last:border-0 last:pb-0">
      <span className="flex items-center gap-2 text-muted-foreground">
        {icon}
        {label}
      </span>
      <span className="font-medium">{value}</span>
    </div>
  );
}