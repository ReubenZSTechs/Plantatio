// ================================================
// PlantGardenPage.tsx — Simplified Add + Omni Scanner (With Image Upload)
// ================================================

import { useState, ReactNode } from "react";
import { Link } from "@tanstack/react-router";
import {
  ArrowLeft,
  Sprout,
  Droplets,
  Leaf,
  Bot,
  QrCode,
  ScanLine,
  Loader2,
  Wifi,
  Plus,
  X,
  Check,
  Pencil,
  Trash2,
  FlaskConical,
  Mountain,
  Flower2,
  Cpu,
  Package,
  Camera, // <-- Ditambahkan ikon Camera
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

// ─── 1. INTERFACES ────────────────────────────────────────────────────────────

export type ScanCategory = "sensor" | "seed" | "soil" | "fertilizer" | "other";

export interface ProbeData {
  moisture: number;
  nutrients: number;
  light: number;
  temperature: number;
}

export interface ScannedItem {
  category: ScanCategory;
  id: string;
  name: string;
  brand?: string;
  // sensor
  sensorId?: string;
  // seed
  seedVariety?: string;
  germinationDays?: number;
  // soil
  soilType?: string;
  phLevel?: number;
  // fertilizer
  npkRatio?: string;
  applicationFrequency?: string;
  // other
  description?: string;
  scannedAt: string;
}

export interface TimelineEvent {
  date: string;
  event: string;
  note: string;
  scanCategory?: ScanCategory;
}

export interface Plant {
  id: number;
  nickname: string;
  species: string;
  image: string;
  health: number;
  daysPlanted: number;
  probe: ProbeData;
  timeline: TimelineEvent[];
  scannedItems: ScannedItem[];
}

export type PlantFormData = Pick<Plant, "nickname" | "species" | "image"> & { id?: number };

// ─── 2. SEED DATA ─────────────────────────────────────────────────────────────

const SEED_PLANTS: Plant[] = [
  {
    id: 1,
    nickname: "Tomato",
    species: "Solanum lycopersicum",
    image: "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=600&q=80",
    health: 85.0,
    daysPlanted: 14,
    probe: { moisture: 45.0, nutrients: 60.0, light: 80.0, temperature: 26.0 },
    scannedItems: [],
    timeline: [
      { date: "10 Oct", event: "Ditanam", note: "Bibit dipindahkan ke pot" },
      { date: "12 Oct", event: "Disiram", note: "Penyiraman pertama" },
    ],
  },
];

// ─── 3. HELPERS ───────────────────────────────────────────────────────────────

function healthColor(v: number) {
  if (v >= 80) return "bg-emerald-500";
  if (v >= 50) return "bg-amber-400";
  return "bg-red-400";
}

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

// ─── 4. GAUGE ─────────────────────────────────────────────────────────────────

function Gauge({
  icon,
  label,
  value,
  unit,
  max = 100,
}: {
  icon: ReactNode;
  label: string;
  value: number;
  unit: string;
  max?: number;
}) {
  return (
    <div className="rounded-lg border bg-card p-3 text-left">
      <div className="mb-1 flex items-center gap-1.5 text-xs text-muted-foreground">
        {icon} {label}
      </div>
      <div className="mb-1.5 text-lg font-semibold">
        {value}
        {unit}
      </div>
      <Progress value={(value / max) * 100} className="h-1.5" />
    </div>
  );
}

// ─── 5. SCANNED ITEM BADGE ────────────────────────────────────────────────────

// ─── 6. SCANNED ITEMS SECTION ────────────────────────────────────────────────

function ScannedItemsSection({ items }: { items: ScannedItem[] }) {
  if (items.length === 0) return null;

  const sensor = items.find((i) => i.category === "sensor");
  const seed = items.find((i) => i.category === "seed");
  const soil = items.find((i) => i.category === "soil");
  const fertilizer = items.find((i) => i.category === "fertilizer");

  return (
    <div className="space-y-1.5 rounded-xl border bg-secondary/30 p-3">
      <p className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
        Scanned items
      </p>

      {sensor && (
        <div className="flex items-center justify-between text-xs">
          <span className="flex items-center gap-1.5 text-muted-foreground">
            <Wifi className="h-3 w-3 text-blue-500 animate-pulse" /> Sensor
          </span>
          <span className="font-medium">
            {sensor.sensorId} · {sensor.name}
          </span>
        </div>
      )}

      {seed && (
        <div className="flex items-center justify-between text-xs">
          <span className="flex items-center gap-1.5 text-muted-foreground">
            <Flower2 className="h-3 w-3 text-emerald-500" /> Bibit
          </span>
          <span className="font-medium">
            {seed.name}
            {seed.seedVariety ? ` · ${seed.seedVariety}` : ""}
          </span>
        </div>
      )}

      {soil && (
        <div className="flex items-center justify-between text-xs">
          <span className="flex items-center gap-1.5 text-muted-foreground">
            <Mountain className="h-3 w-3 text-amber-500" /> Tanah
          </span>
          <span className="font-medium">
            {soil.name}
            {soil.phLevel ? ` · pH ${soil.phLevel}` : ""}
          </span>
        </div>
      )}

      {fertilizer && (
        <div className="flex items-center justify-between text-xs">
          <span className="flex items-center gap-1.5 text-muted-foreground">
            <FlaskConical className="h-3 w-3 text-purple-500" /> Pupuk
          </span>
          <span className="font-medium">
            {fertilizer.name}
            {fertilizer.npkRatio ? ` · NPK ${fertilizer.npkRatio}` : ""}
          </span>
        </div>
      )}
    </div>
  );
}

// ─── 7. PLANT CARD ────────────────────────────────────────────────────────────

function PlantCard({
  plant,
  onEdit,
  onDelete,
  onScan,
}: {
  plant: Plant;
  onEdit: (p: Plant) => void;
  onDelete: (id: number) => void;
  onScan: (p: Plant) => void;
}) {
  const activeSensor = plant.scannedItems.find((i) => i.category === "sensor");

  return (
    <Card className="overflow-hidden transition-shadow hover:shadow-md">
      <Link to="/garden/$plantId" params={{ plantId: String(plant.id) }} className="block w-full">
        <div
          className="relative h-40 w-full bg-cover bg-center"
          style={{ backgroundImage: `url(${plant.image})` }}
        >
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
          <div className="absolute bottom-3 left-4 right-4 flex items-end justify-between text-white">
            <div>
              <div className="mb-0.5 flex items-center gap-1">
                <Wifi
                  className={`h-2.5 w-2.5 ${activeSensor ? "text-emerald-400 animate-pulse" : "text-slate-400"}`}
                />
                <p className="text-[9px] uppercase tracking-widest">
                  {activeSensor ? `Sensor ${activeSensor.sensorId}` : "No Sensor"}
                </p>
              </div>
              <h3 className="text-base font-semibold">{plant.nickname}</h3>
            </div>
            <div className="flex flex-col items-end gap-1">
              <Badge className={`${healthColor(plant.health)} border-0 text-white`}>
                {plant.health}%
              </Badge>
              {plant.scannedItems.length > 0 && (
                <div className="flex gap-0.5">
                  {plant.scannedItems.slice(0, 4).map((item, i) => (
                    <span
                      key={i}
                      className="flex h-4 w-4 items-center justify-center rounded-full bg-white/20 text-[8px] text-white"
                      title={CATEGORY_CONFIG[item.category].label}
                    >
                      {item.category === "sensor"
                        ? "📡"
                        : item.category === "seed"
                          ? "🌱"
                          : item.category === "soil"
                            ? "🪨"
                            : item.category === "fertilizer"
                              ? "🧪"
                              : "📦"}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </Link>

      <div className="space-y-3 p-4">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">Day {plant.daysPlanted}</span>
          <div className="flex gap-1">
            <Button
              size="icon"
              variant="outline"
              className="h-7 w-7 border-emerald-500 text-emerald-600"
              onClick={() => onScan(plant)}
              title="Scan Item"
            >
              <QrCode className="h-3.5 w-3.5" />
            </Button>

            <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => onEdit(plant)}>
              <Pencil className="h-3.5 w-3.5" />
            </Button>
            <Button
              size="icon"
              variant="ghost"
              className="h-7 w-7 text-destructive"
              onClick={() => onDelete(plant.id)}
            >
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>

        <ScannedItemsSection items={plant.scannedItems} />

        <div className={`grid grid-cols-2 gap-2 ${!activeSensor && "opacity-50 grayscale"}`}>
          <Gauge
            icon={<Droplets className="h-3 w-3" />}
            label="Moisture"
            value={plant.probe.moisture}
            unit="%"
          />
          <Gauge
            icon={<Leaf className="h-3 w-3" />}
            label="Nutrients"
            value={plant.probe.nutrients}
            unit="%"
          />
        </div>

        <Button
          asChild
          className="w-full gap-2 bg-primary/10 text-primary hover:bg-primary/20"
          variant="secondary"
        >
          <Link to="/garden/$plantId" params={{ plantId: String(plant.id) }}>
            <Bot className="h-4 w-4" /> Chat with AI
          </Link>
        </Button>
      </div>
    </Card>
  );
}

// ─── 8. ADD PLANT FORM MODAL ──────────────────────────────────────────────────

function AddPlantModal({
  onSave,
  onClose,
}: {
  onSave: (form: PlantFormData) => void;
  onClose: () => void;
}) {
  const [form, setForm] = useState<PlantFormData>({ nickname: "", species: "", image: "" });

  const set = <K extends keyof PlantFormData>(key: K, val: PlantFormData[K]) =>
    setForm((f) => ({ ...f, [key]: val }));

  // Fungsi untuk menangani input file dari kamera / galeri
  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        set("image", reader.result as string); // Stored as a base64 preview
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = () => {
    if (!form.nickname.trim()) {
      toast.error("Give the plant a name");
      return;
    }
    onSave(form);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="relative w-full max-w-sm rounded-3xl bg-background shadow-2xl">
        <div className="flex items-center justify-between border-b px-5 py-4">
          <h2 className="font-semibold">Add plant</h2>
          <Button size="icon" variant="ghost" className="h-7 w-7" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="space-y-4 px-5 py-4">
          {/* UPLOAD FOTO SECTION */}
          <div className="space-y-2">
            <Label>Foto Tanaman</Label>

            {/* Input file disembunyikan, kita trigger lewat klik pada Label */}
            <input
              type="file"
              accept="image/*"
              capture="environment" // Fitur untuk menyarankan kamera belakang di HP
              id="upload-add"
              className="hidden"
              onChange={handleImageUpload}
            />

            <Label
              htmlFor="upload-add"
              className="cursor-pointer flex h-36 w-full flex-col items-center justify-center overflow-hidden rounded-2xl border-2 border-dashed border-primary/30 bg-secondary/30 transition-colors hover:bg-secondary/50"
            >
              {form.image ? (
                <div
                  className="h-full w-full bg-cover bg-center"
                  style={{ backgroundImage: `url(${form.image})` }}
                />
              ) : (
                <div className="flex flex-col items-center gap-2 text-muted-foreground/60">
                  <Camera className="h-8 w-8 text-primary/40" />
                  <span className="text-xs font-medium text-primary/60">Kamera / Unggah Foto</span>
                </div>
              )}
            </Label>
          </div>

          <div className="space-y-1">
            <Label htmlFor="nickname">Nama tanaman *</Label>
            <Input
              id="nickname"
              value={form.nickname}
              onChange={(e) => set("nickname", e.target.value)}
              placeholder="e.g. Tomato Cherry"
            />
          </div>

          <div className="space-y-1">
            <Label htmlFor="species">Jenis / spesies</Label>
            <Input
              id="species"
              value={form.species}
              onChange={(e) => set("species", e.target.value)}
              placeholder="e.g. Solanum lycopersicum"
            />
          </div>

          <p className="rounded-lg bg-emerald-50 px-3 py-2 text-[10px] text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-400 leading-relaxed">
            💡 Scan sensor, pupuk, tanah, atau bibit nanti menggunakan tombol QR pada kartu tanaman.
          </p>
        </div>

        <div className="flex gap-2 border-t px-5 py-4">
          <Button variant="outline" className="flex-1" onClick={onClose}>
            Cancel
          </Button>
          <Button className="flex-1" onClick={handleSubmit}>
            <Check className="mr-1.5 h-4 w-4" /> Tambah
          </Button>
        </div>
      </div>
    </div>
  );
}

// ─── 9. EDIT PLANT MODAL ──────────────────────────────────────────────────────

function EditPlantModal({
  plant,
  onSave,
  onClose,
}: {
  plant: Plant;
  onSave: (form: PlantFormData) => void;
  onClose: () => void;
}) {
  const [form, setForm] = useState<PlantFormData>({
    id: plant.id,
    nickname: plant.nickname,
    species: plant.species,
    image: plant.image,
  });

  const set = <K extends keyof PlantFormData>(key: K, val: PlantFormData[K]) =>
    setForm((f) => ({ ...f, [key]: val }));

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => set("image", reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = () => {
    if (!form.nickname.trim()) {
      toast.error("Give the plant a name");
      return;
    }
    onSave(form);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="relative w-full max-w-sm rounded-3xl bg-background shadow-2xl">
        <div className="flex items-center justify-between border-b px-5 py-4">
          <h2 className="font-semibold">Edit tanaman</h2>
          <Button size="icon" variant="ghost" className="h-7 w-7" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="space-y-4 px-5 py-4">
          {/* UPLOAD FOTO SECTION */}
          <div className="space-y-2">
            <Label>Foto Tanaman</Label>
            <input
              type="file"
              accept="image/*"
              capture="environment"
              id="upload-edit"
              className="hidden"
              onChange={handleImageUpload}
            />
            <Label
              htmlFor="upload-edit"
              className="cursor-pointer flex h-36 w-full flex-col items-center justify-center overflow-hidden rounded-2xl border-2 border-dashed border-primary/30 bg-secondary/30 transition-colors hover:bg-secondary/50"
            >
              {form.image ? (
                <div
                  className="relative h-full w-full bg-cover bg-center group"
                  style={{ backgroundImage: `url(${form.image})` }}
                >
                  <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <Camera className="h-8 w-8 text-white" />
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-2 text-muted-foreground/60">
                  <Camera className="h-8 w-8 text-primary/40" />
                  <span className="text-xs font-medium text-primary/60">Kamera / Unggah Foto</span>
                </div>
              )}
            </Label>
          </div>

          <div className="space-y-1">
            <Label>Nama tanaman *</Label>
            <Input value={form.nickname} onChange={(e) => set("nickname", e.target.value)} />
          </div>
          <div className="space-y-1">
            <Label>Jenis / spesies</Label>
            <Input value={form.species} onChange={(e) => set("species", e.target.value)} />
          </div>
        </div>

        <div className="flex gap-2 border-t px-5 py-4">
          <Button variant="outline" className="flex-1" onClick={onClose}>
            Cancel
          </Button>
          <Button className="flex-1" onClick={handleSubmit}>
            <Check className="mr-1.5 h-4 w-4" /> Save
          </Button>
        </div>
      </div>
    </div>
  );
}

// ─── 10. OMNI SCANNER MODAL ───────────────────────────────────────────────────

// Mock product database per category
const MOCK_PRODUCTS: Record<ScanCategory, ScannedItem[]> = {
  sensor: [
    {
      category: "sensor",
      id: `PRB-${Math.floor(1000 + Math.random() * 9000)}`,
      name: "Smart Probe Gen 2",
      brand: "Plantatio",
      sensorId: `PRB-${Math.floor(1000 + Math.random() * 9000)}`,
      scannedAt: "",
    },
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
    {
      category: "seed",
      id: "SEED-002",
      name: "Basil Genovese",
      brand: "HerbLab",
      seedVariety: "Genovese",
      germinationDays: 5,
      scannedAt: "",
    },
    {
      category: "seed",
      id: "SEED-003",
      name: "Cabe Rawit",
      brand: "Nusantara Seeds",
      seedVariety: "Rawit Hijau",
      germinationDays: 10,
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
    {
      category: "soil",
      id: "SOIL-002",
      name: "Cocopeat Pro",
      brand: "TropicGrow",
      soilType: "Cocopeat",
      phLevel: 5.8,
      scannedAt: "",
    },
    {
      category: "soil",
      id: "SOIL-003",
      name: "Vermicompost Blend",
      brand: "EarthWorm Co.",
      soilType: "Organic compost",
      phLevel: 7.0,
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
    {
      category: "fertilizer",
      id: "FERT-002",
      name: "BloomBooster",
      brand: "FloraFeed",
      npkRatio: "10-30-20",
      applicationFrequency: "Sekali seminggu",
      scannedAt: "",
    },
    {
      category: "fertilizer",
      id: "FERT-003",
      name: "Organic Liquid",
      brand: "BioNatur",
      npkRatio: "5-3-4",
      applicationFrequency: "3x seminggu",
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
    {
      category: "other",
      id: "OTH-002",
      name: "Pot Hidroponik 5L",
      brand: "HydroKit",
      description: "Pot dengan sistem drainase aktif",
      scannedAt: "",
    },
  ],
};

function OmniScannerModal({
  plant,
  onScanComplete,
  onClose,
}: {
  plant: Plant;
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
      color: "text-blue-600 bg-blue-50 border-blue-200 dark:bg-blue-950/30",
    },
    {
      id: "seed",
      label: "Bibit",
      desc: "Benih & varietas",
      icon: <Flower2 className="h-5 w-5" />,
      color: "text-emerald-600 bg-emerald-50 border-emerald-200 dark:bg-emerald-950/30",
    },
    {
      id: "soil",
      label: "Tanah",
      desc: "Media tanam",
      icon: <Mountain className="h-5 w-5" />,
      color: "text-amber-600 bg-amber-50 border-amber-200 dark:bg-amber-950/30",
    },
    {
      id: "fertilizer",
      label: "Pupuk",
      desc: "Nutrisi & NPK",
      icon: <FlaskConical className="h-5 w-5" />,
      color: "text-purple-600 bg-purple-50 border-purple-200 dark:bg-purple-950/30",
    },
    {
      id: "other",
      label: "Lainnya",
      desc: "Pestisida, alat...",
      icon: <Package className="h-5 w-5" />,
      color: "text-slate-600 bg-slate-50 border-slate-200 dark:bg-slate-800/50",
    },
  ];

  const handleSimulateScan = () => {
    setStep("processing");
    setTimeout(() => {
      const pool = MOCK_PRODUCTS[category];
      const mock = { ...pool[Math.floor(Math.random() * pool.length)] };
      // generate unique IDs for sensor
      if (category === "sensor") {
        const id = `PRB-${Math.floor(1000 + Math.random() * 9000)}`;
        mock.id = id;
        mock.sensorId = id;
      }
      mock.scannedAt = new Date().toLocaleDateString("id-ID", { day: "numeric", month: "short" });
      setResult(mock);
      setStep("result");
    }, 1800);
  };

  const handleConfirm = () => {
    if (result) onScanComplete(result);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 backdrop-blur-sm sm:items-center p-4">
      <div className="w-full max-w-sm rounded-3xl bg-background shadow-2xl">
        {/* STEP: select category */}
        {step === "select" && (
          <div className="space-y-0">
            <div className="flex items-center justify-between border-b px-5 py-4">
              <div>
                <h2 className="font-semibold">Scan ke {plant.nickname}</h2>
                <p className="text-xs text-muted-foreground">Pilih jenis item yang akan discan</p>
              </div>
              <Button size="icon" variant="ghost" className="h-7 w-7" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="grid grid-cols-1 divide-y p-2">
              {scanCategories.map((cat) => {
                const alreadyScanned = plant.scannedItems.some((i) => i.category === cat.id);
                return (
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
                    {alreadyScanned && (
                      <Badge
                        variant="outline"
                        className="text-[9px] text-emerald-600 border-emerald-300"
                      >
                        <Check className="mr-0.5 h-2.5 w-2.5" /> Sudah
                      </Badge>
                    )}
                  </button>
                );
              })}
            </div>
            <div className="border-t px-5 py-3">
              <Button variant="ghost" className="w-full" onClick={onClose}>
                Cancel
              </Button>
            </div>
          </div>
        )}

        {/* STEP: scanning */}
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

            <p className="text-sm text-muted-foreground">
              Arahkan kamera ke barcode / QR pada kemasan{" "}
              {scanCategories.find((c) => c.id === category)?.label.toLowerCase()}
            </p>

            <Button className="w-full" onClick={handleSimulateScan}>
              <QrCode className="mr-2 h-4 w-4" /> Simulasi Scan
            </Button>
            <Button variant="ghost" className="w-full" onClick={onClose}>
              Cancel
            </Button>
            <style>{`@keyframes scan { 0%, 100% { top: 5%; } 50% { top: 90%; } }`}</style>
          </div>
        )}

        {/* STEP: processing */}
        {step === "processing" && (
          <div className="py-16 text-center space-y-4 px-6">
            <Loader2 className="mx-auto h-10 w-10 animate-spin text-primary" />
            <p className="font-medium">Memproses data produk...</p>
            <p className="text-xs text-muted-foreground">Mengambil info dari database</p>
          </div>
        )}

        {/* STEP: result */}
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
                <p className="text-xs text-muted-foreground">
                  {result.brand} · {CATEGORY_CONFIG[result.category].label}
                </p>
              </div>
            </div>

            {/* detail per category */}
            <div className="space-y-2 px-5 py-4">
              {result.category === "sensor" && (
                <div className="rounded-xl bg-blue-50 dark:bg-blue-950/30 p-3 space-y-1">
                  <p className="text-xs font-medium text-blue-700 dark:text-blue-300">ID Sensor</p>
                  <p className="font-mono text-sm font-bold text-blue-800 dark:text-blue-200">
                    {result.sensorId}
                  </p>
                  <p className="text-xs text-blue-600 dark:text-blue-400">
                    Akan dihubungkan via MQTT broker
                  </p>
                </div>
              )}
              {result.category === "seed" && (
                <div className="rounded-xl bg-emerald-50 dark:bg-emerald-950/30 p-3 space-y-1.5">
                  <div className="flex justify-between text-xs">
                    <span className="text-emerald-600">Varietas</span>
                    <span className="font-medium text-emerald-800 dark:text-emerald-200">
                      {result.seedVariety}
                    </span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-emerald-600">Estimasi tumbuh</span>
                    <span className="font-medium text-emerald-800 dark:text-emerald-200">
                      {result.germinationDays} hari
                    </span>
                  </div>
                </div>
              )}
              {result.category === "soil" && (
                <div className="rounded-xl bg-amber-50 dark:bg-amber-950/30 p-3 space-y-1.5">
                  <div className="flex justify-between text-xs">
                    <span className="text-amber-600">Tipe media</span>
                    <span className="font-medium text-amber-800 dark:text-amber-200">
                      {result.soilType}
                    </span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-amber-600">Tingkat pH</span>
                    <span className="font-medium text-amber-800 dark:text-amber-200">
                      {result.phLevel}
                    </span>
                  </div>
                </div>
              )}
              {result.category === "fertilizer" && (
                <div className="rounded-xl bg-purple-50 dark:bg-purple-950/30 p-3 space-y-1.5">
                  <div className="flex justify-between text-xs">
                    <span className="text-purple-600">Rasio NPK</span>
                    <span className="font-mono font-bold text-purple-800 dark:text-purple-200">
                      {result.npkRatio}
                    </span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-purple-600">Frekuensi</span>
                    <span className="font-medium text-purple-800 dark:text-purple-200">
                      {result.applicationFrequency}
                    </span>
                  </div>
                </div>
              )}
              {result.category === "other" && (
                <div className="rounded-xl bg-slate-50 dark:bg-slate-800/50 p-3">
                  <p className="text-xs text-slate-600 dark:text-slate-400">{result.description}</p>
                </div>
              )}

              <p className="rounded-lg bg-secondary/50 px-3 py-2 text-xs text-muted-foreground">
                ✅ Info ini akan ditambahkan ke konteks AI chatbot untuk saran perawatan yang lebih
                akurat.
              </p>
            </div>

            <div className="flex gap-2 border-t px-5 py-4">
              <Button variant="outline" className="flex-1" onClick={() => setStep("select")}>
                Scan Lagi
              </Button>
              <Button
                className="flex-1 bg-emerald-600 hover:bg-emerald-700"
                onClick={handleConfirm}
              >
                <Check className="mr-1.5 h-4 w-4" /> Tambahkan
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── 11. MAIN PAGE ────────────────────────────────────────────────────────────

export function PlantGardenPage() {
  const [plants, setPlants] = useState<Plant[]>(SEED_PLANTS);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingPlant, setEditingPlant] = useState<Plant | null>(null);
  const [scanningPlant, setScanningPlant] = useState<Plant | null>(null);

  // ── Add plant ──
  const handleAddPlant = (form: PlantFormData) => {
    const today = new Date().toLocaleDateString("id-ID", { day: "numeric", month: "short" });
    const newPlant: Plant = {
      id: Date.now(),
      nickname: form.nickname,
      species: form.species,
      image: form.image,
      health: 100,
      daysPlanted: 0,
      probe: { moisture: 50, nutrients: 50, light: 60, temperature: 24 },
      scannedItems: [],
      timeline: [
        {
          date: today,
          event: "Terdaftar",
          note: "Plant added",
        },
      ],
    };
    setPlants((prev) => [newPlant, ...prev]);
    toast.success(`${form.nickname} ditambahkan ke kebun 🌿`);
    setShowAddForm(false);
  };

  // ── Edit plant ──
  const handleEditPlant = (form: PlantFormData) => {
    setPlants((prev) =>
      prev.map((p) =>
        p.id === form.id
          ? { ...p, nickname: form.nickname, species: form.species, image: form.image }
          : p,
      ),
    );
    toast.success("Plant updated");
    setEditingPlant(null);
  };

  // ── Scan complete ──
  const handleScanComplete = (item: ScannedItem) => {
    if (!scanningPlant) return;

    setPlants((prev) =>
      prev.map((p) => {
        if (p.id !== scanningPlant.id) return p;

        // Remove existing item of same category, then add new one
        const filteredItems = p.scannedItems.filter((i) => i.category !== item.category);
        const newItems = [...filteredItems, item];

        // If sensor scanned, update probe data with simulated live data
        const updatedProbe =
          item.category === "sensor"
            ? {
                moisture: 65 + Math.floor(Math.random() * 20),
                nutrients: 60 + Math.floor(Math.random() * 25),
                light: 55 + Math.floor(Math.random() * 30),
                temperature: 22 + Math.floor(Math.random() * 6),
              }
            : p.probe;

        const today = new Date().toLocaleDateString("id-ID", { day: "numeric", month: "short" });
        const eventLabel = {
          sensor: "Sensor dipasang",
          seed: "Bibit didaftarkan",
          soil: "Media tanam dicatat",
          fertilizer: "Pupuk diterapkan",
          other: "Item ditambahkan",
        }[item.category];

        const noteText =
          item.category === "sensor"
            ? `${item.sensorId} via MQTT`
            : item.category === "soil"
              ? `${item.name} pH ${item.phLevel}`
              : item.category === "fertilizer"
                ? `${item.name} NPK ${item.npkRatio}`
                : item.name;

        return {
          ...p,
          probe: updatedProbe,
          scannedItems: newItems,
          timeline: [
            { date: today, event: eventLabel, note: noteText, scanCategory: item.category },
            ...p.timeline,
          ],
        };
      }),
    );

    const label = CATEGORY_CONFIG[item.category].label;
    toast.success(`${label} "${item.name}" ditambahkan ke ${scanningPlant.nickname}`);
    setScanningPlant(null);
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-10 border-b bg-card/80 backdrop-blur px-4 py-3">
        <div className="mx-auto flex max-w-2xl items-center justify-between">
          <Link to="/" className="flex items-center gap-1 text-sm text-muted-foreground">
            <ArrowLeft className="h-4 w-4" /> Back
          </Link>
          <div className="flex items-center gap-2 font-bold">
            <Sprout className="h-5 w-5 text-primary" /> My Garden
          </div>
          <Badge variant="outline">{plants.length} Units</Badge>
        </div>
      </header>

      <main className="mx-auto max-w-2xl space-y-6 p-4">
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-2xl font-bold">Plant Collection</h1>
            <p className="text-sm text-muted-foreground">Live Telemetry</p>
          </div>
          <Button
            onClick={() => setShowAddForm(true)}
            size="sm"
            className="bg-emerald-600 hover:bg-emerald-700"
          >
            <Plus className="mr-2 h-4 w-4" /> Add Plant
          </Button>
        </div>

        {plants.length === 0 && (
          <div className="flex flex-col items-center justify-center space-y-3 rounded-2xl border border-dashed py-16 text-center">
            <Sprout className="h-10 w-10 text-muted-foreground/40" />
            <div>
              <p className="font-medium text-muted-foreground">Belum ada tanaman</p>
              <p className="text-sm text-muted-foreground/60">Add plant pertama kamu</p>
            </div>
            <Button variant="outline" onClick={() => setShowAddForm(true)}>
              <Plus className="mr-1.5 h-4 w-4" /> Add plant
            </Button>
          </div>
        )}

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {plants.map((p) => (
            <PlantCard
              key={p.id}
              plant={p}
              onEdit={(plant) => setEditingPlant(plant)}
              onDelete={(id) => {
                setPlants((prev) => prev.filter((x) => x.id !== id));
                toast.success("Plant removed");
              }}
              onScan={(plant) => setScanningPlant(plant)}
            />
          ))}
        </div>
      </main>

      {/* Modals */}
      {showAddForm && (
        <AddPlantModal onSave={handleAddPlant} onClose={() => setShowAddForm(false)} />
      )}

      {editingPlant && (
        <EditPlantModal
          plant={editingPlant}
          onSave={handleEditPlant}
          onClose={() => setEditingPlant(null)}
        />
      )}

      {scanningPlant && (
        <OmniScannerModal
          plant={scanningPlant}
          onScanComplete={handleScanComplete}
          onClose={() => setScanningPlant(null)}
        />
      )}
    </div>
  );
}
