// ================================================
// PlantDetailPage.tsx
// ================================================

import { useCallback, useEffect, useState, type ReactNode } from "react";
import { Link } from "@tanstack/react-router";
import {
  ArrowLeft,
  Sprout,
  Droplets,
  Leaf,
  Sun,
  Thermometer,
  Bot,
  Loader2,
  AlertTriangle,
  QrCode,
  ScanLine,
  X,
  Check,
  Wifi,
  Flower2,
  Mountain,
  FlaskConical,
  Package,
  Cpu,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";

import { api, ApiError, API_BASE_URL } from "@/lib/api";
import { Route } from "@/routes/garden.$plantId";
import { ChatPanel } from "./ChatPanel";

// ─── Local TypeScript Interfaces ──────────────────────────────────────────────
export type ScanCategory = "sensor" | "seed" | "soil" | "fertilizer" | "other";

export interface ScannedItem {
  category: ScanCategory;
  id: string;
  name: string;
  brand?: string;
  sensorId?: string;
  seedVariety?: string;
  germinationDays?: number;
  soilType?: string;
  phLevel?: number;
  npkRatio?: string;
  applicationFrequency?: string;
  description?: string;
  scannedAt: string;
}

interface TimelineEvent {
  date: string;
  event: string;
  note: string;
}

interface ProbeData {
  moisture: number;
  nutrients: number;
  light: number;
  temperature: number;
}

interface Plant {
  id: number;
  nickname: string;
  species: string;
  image: string;
  health: number;
  daysPlanted: number;
  probe: ProbeData;
  timeline: TimelineEvent[];
  scannedItems?: ScannedItem[];
}

interface GaugeProps {
  icon: ReactNode;
  label: string;
  value: number;
  unit: string;
  max?: number;
  warn?: boolean;
}

// ─── MOCK DATA & CONFIGS UNTUK SCANNER ────────────────────────────────────────
const CATEGORY_CONFIG: Record<ScanCategory, { label: string; icon: ReactNode; color: string }> = {
  sensor: {
    label: "Sensor",
    icon: <Cpu className="h-4 w-4" />,
    color: "text-blue-500 bg-blue-50 border-blue-200",
  },
  seed: {
    label: "Bibit",
    icon: <Flower2 className="h-4 w-4" />,
    color: "text-emerald-600 bg-emerald-50 border-emerald-200",
  },
  soil: {
    label: "Tanah",
    icon: <Mountain className="h-4 w-4" />,
    color: "text-amber-600 bg-amber-50 border-amber-200",
  },
  fertilizer: {
    label: "Pupuk",
    icon: <FlaskConical className="h-4 w-4" />,
    color: "text-purple-600 bg-purple-50 border-purple-200",
  },
  other: {
    label: "Lainnya",
    icon: <Package className="h-4 w-4" />,
    color: "text-slate-600 bg-slate-50 border-slate-200",
  },
};

const MOCK_PRODUCTS: Record<ScanCategory, ScannedItem[]> = {
  sensor: [
    { category: "sensor", id: "PRB", name: "Smart Probe Gen 2", brand: "Plantatio", scannedAt: "" },
  ],
  seed: [
    {
      category: "seed",
      id: "SEED-001",
      name: "Tomat Cherry",
      brand: "GrowKing",
      seedVariety: "Cherry Roma",
      germinationDays: 7,
      scannedAt: "",
    },
  ],
  soil: [
    {
      category: "soil",
      id: "SOIL-001",
      name: "Premium Potting Mix",
      brand: "BioBest",
      soilType: "Perlite blend",
      phLevel: 6.5,
      scannedAt: "",
    },
  ],
  fertilizer: [
    {
      category: "fertilizer",
      id: "FERT-001",
      name: "GrowMax NPK",
      brand: "NutriPlant",
      npkRatio: "20-10-10",
      applicationFrequency: "Setiap 2 minggu",
      scannedAt: "",
    },
  ],
  other: [
    {
      category: "other",
      id: "OTH-001",
      name: "Pestisida Organik",
      brand: "GreenShield",
      description: "Pengendalian hama ramah lingkungan",
      scannedAt: "",
    },
  ],
};

// ─── Gauge & ChatBubble Components ───────────────────────────────────────────
function Gauge({ icon, label, value, unit, max = 100, warn = false }: GaugeProps) {
  return (
    <div className={`rounded-lg border bg-card p-3 ${warn ? "border-amber-400/60" : ""}`}>
      <div className="mb-1 flex items-center gap-1.5 text-xs text-muted-foreground">
        {icon}
        {label}
        {warn && <AlertTriangle className="ml-auto h-3 w-3 text-amber-400" />}
      </div>
      <div className="mb-1.5 text-lg font-semibold">
        {value}
        {unit}
      </div>
      <Progress value={(value / max) * 100} className="h-1.5" />
    </div>
  );
}

// ─── Chatbot Component ────────────────────────────────────────────────────────

// ─── OmniScannerModal Component ───────────────────────────────────────────────
function OmniScannerModal({
  plantName,
  onScanComplete,
  onClose,
}: {
  plantName: string;
  onScanComplete: (item: ScannedItem) => void;
  onClose: () => void;
}) {
  const [step, setStep] = useState<"select" | "scan" | "processing" | "result">("select");
  const [category, setCategory] = useState<ScanCategory>("sensor");
  const [result, setResult] = useState<ScannedItem | null>(null);

  const scanCategories: {
    id: ScanCategory;
    label: string;
    desc: string;
    icon: ReactNode;
    color: string;
  }[] = [
    {
      id: "sensor",
      label: "Sensor",
      desc: "Smart probe IoT",
      icon: <Cpu className="h-5 w-5" />,
      color: "text-blue-600 bg-blue-50 border-blue-200",
    },
    {
      id: "seed",
      label: "Bibit",
      desc: "Benih & varietas",
      icon: <Flower2 className="h-5 w-5" />,
      color: "text-emerald-600 bg-emerald-50 border-emerald-200",
    },
    {
      id: "soil",
      label: "Tanah",
      desc: "Media tanam",
      icon: <Mountain className="h-5 w-5" />,
      color: "text-amber-600 bg-amber-50 border-amber-200",
    },
    {
      id: "fertilizer",
      label: "Pupuk",
      desc: "Nutrisi & NPK",
      icon: <FlaskConical className="h-5 w-5" />,
      color: "text-purple-600 bg-purple-50 border-purple-200",
    },
    {
      id: "other",
      label: "Lainnya",
      desc: "Pestisida, alat...",
      icon: <Package className="h-5 w-5" />,
      color: "text-slate-600 bg-slate-50 border-slate-200",
    },
  ];

  const handleSimulateScan = () => {
    setStep("processing");
    setTimeout(() => {
      const pool = MOCK_PRODUCTS[category];
      const mock = { ...pool[0] };
      if (category === "sensor") {
        mock.id = `PRB-${Math.floor(1000 + Math.random() * 9000)}`;
        mock.sensorId = mock.id;
      }
      mock.scannedAt = new Date().toISOString();
      setResult(mock);
      setStep("result");
    }, 1800);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 backdrop-blur-sm sm:items-center p-4">
      <div className="w-full max-w-sm rounded-3xl bg-background shadow-2xl">
        {step === "select" && (
          <div className="space-y-0">
            <div className="flex items-center justify-between border-b px-5 py-4">
              <div>
                <h2 className="font-semibold">Scan to AI Context</h2>
                <p className="text-xs text-muted-foreground">Tambahkan data ke {plantName}</p>
              </div>
              <Button size="icon" variant="ghost" className="h-7 w-7" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="grid grid-cols-1 divide-y p-2">
              {scanCategories.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => {
                    setCategory(cat.id);
                    setStep("scan");
                  }}
                  className="flex items-center gap-3 rounded-xl px-3 py-3 text-left transition-colors hover:bg-secondary/50"
                >
                  <div
                    className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border ${cat.color}`}
                  >
                    {cat.icon}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{cat.label}</p>
                    <p className="text-xs text-muted-foreground">{cat.desc}</p>
                  </div>
                </button>
              ))}
            </div>
            <div className="border-t px-5 py-3">
              <Button variant="ghost" className="w-full" onClick={onClose}>
                Cancel
              </Button>
            </div>
          </div>
        )}

        {step === "scan" && (
          <div className="space-y-5 p-6 text-center">
            <div className="flex items-center gap-2">
              <Button
                size="icon"
                variant="ghost"
                className="h-7 w-7"
                onClick={() => setStep("select")}
              >
                <ArrowLeft className="h-4 w-4" />
              </Button>
              <h2 className="font-semibold">
                Scan {scanCategories.find((c) => c.id === category)?.label}
              </h2>
            </div>
            <div className="relative mx-auto flex h-44 w-44 items-center justify-center overflow-hidden rounded-2xl border-2 border-dashed border-primary bg-secondary/20">
              <div className="absolute left-0 top-0 h-0.5 w-full bg-primary/70 animate-[scan_2s_ease-in-out_infinite]" />
              <ScanLine className="h-12 w-12 text-primary/20" />
            </div>
            <Button className="w-full" onClick={handleSimulateScan}>
              <QrCode className="mr-2 h-4 w-4" /> Simulasi Scan
            </Button>
            <Button variant="ghost" className="w-full" onClick={onClose}>
              Cancel
            </Button>
            <style>{`@keyframes scan { 0%, 100% { top: 5%; } 50% { top: 90%; } }`}</style>
          </div>
        )}

        {step === "processing" && (
          <div className="py-16 text-center space-y-4 px-6">
            <Loader2 className="mx-auto h-10 w-10 animate-spin text-primary" />
            <p className="font-medium">Memproses Context...</p>
          </div>
        )}

        {step === "result" && result && (
          <div className="space-y-0">
            <div className="flex items-center gap-2 border-b px-5 py-4">
              <div
                className={`flex h-9 w-9 items-center justify-center rounded-xl border ${CATEGORY_CONFIG[result.category].color}`}
              >
                {CATEGORY_CONFIG[result.category].icon}
              </div>
              <div>
                <p className="font-semibold">{result.name}</p>
                <p className="text-xs text-muted-foreground">{result.brand}</p>
              </div>
            </div>
            <div className="p-5">
              <p className="rounded-lg bg-secondary/50 px-3 py-2 text-xs text-muted-foreground border border-border">
                ✅ Info ini akan otomatis ditambahkan ke "Otak AI" untuk saran perawatan yang lebih
                akurat.
              </p>
            </div>
            <div className="flex gap-2 border-t px-5 py-4">
              <Button
                className="flex-1 bg-emerald-600 hover:bg-emerald-700"
                onClick={() => onScanComplete(result)}
              >
                <Check className="mr-1.5 h-4 w-4" /> Sinkronkan ke AI
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────
export function PlantDetailPage() {
  const [localPlant, setLocalPlant] = useState<Plant | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [loading, setLoading] = useState(true);

  // Read the plant from the route. This was hardcoded to 1, so every card in
  // the garden opened the same plant.
  const { plantId: plantIdParam } = Route.useParams();
  const plantId = Number(plantIdParam);

  const [loadError, setLoadError] = useState<string | null>(null);

  const reloadPlant = useCallback(() => {
    if (!Number.isFinite(plantId)) {
      setLoadError("That plant id is not valid.");
      setLoading(false);
      return;
    }

    setLoading(true);
    api
      .getPlant(plantId)
      .then((data) => {
        setLocalPlant(data);
        setLoadError(null);
      })
      .catch((error: unknown) => {
        setLoadError(error instanceof ApiError ? error.message : "Could not load this plant.");
      })
      .finally(() => setLoading(false));
  }, [plantId]);

  useEffect(() => {
    reloadPlant();
  }, [reloadPlant]);

  const handleScanComplete = async (item: ScannedItem) => {
    if (!localPlant) return;

    try {
      // ✅ Menyimpan Scan (POST) ke API Backend
      const response = await fetch(`${API_BASE_URL}/plants/${localPlant.id}/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(item),
      });

      if (!response.ok) throw new Error("Could not save the scan");

      const updatedPlant = await response.json();
      setLocalPlant(updatedPlant); // Mengganti dengan data terbaru dari server
      toast.success(`Context AI diperbarui dengan ${item.name}!`);
    } catch (e) {
      toast.error("Could not sync to the server.");
    } finally {
      setIsScanning(false);
    }
  };

  if (loadError) {
    return (
      <div className="flex min-h-screen items-center justify-center px-4">
        <div className="max-w-sm text-center">
          <p className="text-sm font-medium">{loadError}</p>
          <Link
            to="/garden"
            className="mt-4 inline-flex items-center justify-center rounded-md border px-4 py-2 text-sm transition-colors hover:bg-accent"
          >
            Back to my garden
          </Link>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!localPlant) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 p-8 text-center">
        <Sprout className="h-12 w-12 text-muted-foreground/40" />
        <p className="text-lg font-semibold">Plant not found</p>
        <Button asChild variant="outline">
          <Link to="/garden">
            <ArrowLeft className="mr-1.5 h-4 w-4" /> Back to garden
          </Link>
        </Button>
      </div>
    );
  }

  const healthBadgeColor =
    localPlant.health >= 80
      ? "bg-emerald-500"
      : localPlant.health >= 50
        ? "bg-amber-400"
        : "bg-red-400";
  const activeSensor = localPlant.scannedItems?.find((item) => item.category === "sensor");

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-10 border-b bg-card/80 backdrop-blur">
        <div className="mx-auto flex max-w-md items-center justify-between px-4 py-3">
          <Link
            to="/garden"
            className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" /> Garden
          </Link>
          <div className="flex items-center gap-1.5 font-semibold">
            <Sprout className="h-5 w-5 text-primary" /> {localPlant.nickname}
          </div>
          <Badge className={`${healthBadgeColor} border-0 text-xs text-white`}>
            {localPlant.health}%
          </Badge>
        </div>
      </header>

      <main className="mx-auto max-w-md space-y-5 px-4 py-5">
        <div
          className="relative h-52 w-full overflow-hidden rounded-2xl bg-cover bg-center"
          style={{ backgroundImage: `url(${localPlant.image})` }}
        >
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent" />
          <div className="absolute bottom-4 left-4">
            <p className="text-[10px] uppercase tracking-widest text-white/60">
              {localPlant.species}
            </p>
            <h1 className="text-2xl font-bold text-white">{localPlant.nickname}</h1>
            <div className="mt-1 flex items-center gap-1.5 text-xs text-white/70">
              <Sprout className="h-3.5 w-3.5" /> Day {localPlant.daysPlanted} since planted
            </div>
          </div>
        </div>

        <Button
          variant="outline"
          className="w-full gap-2 border-primary/30 text-primary hover:bg-primary/10 transition-all shadow-sm"
          onClick={() => setIsScanning(true)}
        >
          <QrCode className="h-4 w-4" /> Scan QR to AI Context
        </Button>

        <Card className="overflow-hidden">
          <div className="flex flex-col border-b px-4 py-3 bg-muted/20">
            <div className="flex items-center justify-between">
              <p className="text-sm font-semibold">Live Telemetry</p>
              <Badge
                variant="outline"
                className="text-[10px] bg-emerald-50 text-emerald-600 border-emerald-200 dark:bg-emerald-950/30"
              >
                <Wifi className="mr-1 h-3 w-3 animate-pulse" /> MQTT
              </Badge>
            </div>

            {activeSensor ? (
              <div className="mt-3 flex items-center gap-3 rounded-lg border bg-background p-2 shadow-sm">
                <div className="flex h-9 w-9 items-center justify-center rounded-md bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400">
                  <Cpu className="h-5 w-5" />
                </div>
                <div className="flex-1">
                  <p className="text-xs font-bold leading-none">{activeSensor.name}</p>
                  <p className="text-[10px] text-muted-foreground mt-1 font-mono">
                    ID: {activeSensor.sensorId}
                  </p>
                </div>
                <Badge
                  variant="secondary"
                  className="text-[9px] bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                >
                  Connected
                </Badge>
              </div>
            ) : (
              <div className="mt-3 flex items-center gap-3 rounded-lg border border-dashed p-3 text-muted-foreground bg-secondary/10">
                <Cpu className="h-5 w-5 opacity-50" />
                <div>
                  <p className="text-xs font-medium">Belum ada sensor</p>
                  <p className="text-[10px] opacity-70">
                    Gunakan tombol Scan QR untuk menghubungkan perangkat.
                  </p>
                </div>
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3 p-4">
            <Gauge
              icon={<Droplets className="h-4 w-4" />}
              label="Moisture"
              value={localPlant.probe.moisture}
              unit="%"
              warn={localPlant.probe.moisture < 30}
            />
            <Gauge
              icon={<Leaf className="h-4 w-4" />}
              label="Nutrients"
              value={localPlant.probe.nutrients}
              unit="%"
              warn={localPlant.probe.nutrients < 30}
            />
            <Gauge
              icon={<Sun className="h-4 w-4" />}
              label="Light"
              value={localPlant.probe.light}
              unit="%"
              warn={localPlant.probe.light < 20}
            />
            <Gauge
              icon={<Thermometer className="h-4 w-4" />}
              label="Temp"
              value={localPlant.probe.temperature}
              unit="°C"
              max={40}
              warn={localPlant.probe.temperature > 35}
            />
          </div>
        </Card>

        <Card>
          <div className="border-b px-4 py-3">
            <p className="text-sm font-semibold">Care history</p>
          </div>
          <ol className="px-4 py-3">
            {localPlant.timeline.map((t, i) => (
              <li key={i} className="flex gap-3 py-2 text-sm">
                <div className="flex flex-col items-center gap-1">
                  <div className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-primary" />
                  {i < localPlant.timeline.length - 1 && (
                    <div className="w-px flex-1 bg-border" style={{ minHeight: 16 }} />
                  )}
                </div>
                <div className="flex-1 pb-1">
                  <div className="flex justify-between">
                    <span className="font-medium">{t.event}</span>
                    <span className="text-xs text-muted-foreground">{t.date}</span>
                  </div>
                  <div className="text-xs text-muted-foreground">{t.note}</div>
                </div>
              </li>
            ))}
          </ol>
        </Card>

        <div>
          <div className="mb-2 flex items-center gap-1.5 px-1">
            <Bot className="h-4 w-4 text-primary" />
            <h2 className="text-sm font-semibold">AI Plant Assistant</h2>
            <span className="text-xs text-muted-foreground">— Context Synced</span>
          </div>
          <ChatPanel
            scope="plant"
            plantId={localPlant.id}
            title={`Assistant for ${localPlant.nickname}`}
            subtitle="Knows this plant's readings and care history"
            greeting={`Ask me about ${localPlant.nickname}. I can also classify a leaf photo for disease — tap the camera.`}
            suggestions={[
              "Does it need watering now?",
              "How are the nutrients looking?",
              "Any care tips for this week?",
            ]}
            enableLeafScan
            onDiagnosed={reloadPlant}
            className="h-[560px]"
          />
        </div>
      </main>

      {isScanning && (
        <OmniScannerModal
          plantName={localPlant.nickname}
          onScanComplete={handleScanComplete}
          onClose={() => setIsScanning(false)}
        />
      )}
    </div>
  );
}
