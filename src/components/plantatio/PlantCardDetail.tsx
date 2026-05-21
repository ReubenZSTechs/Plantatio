// ================================================
// PlantGardenPage.tsx
// ================================================

import { useState, useEffect, ReactNode } from "react";
import { Link } from "@tanstack/react-router";
import {
  ArrowLeft, Sprout, Droplets, Leaf, Sun, Thermometer,
  Pencil, Trash2, X, Check, ChevronDown, ChevronUp, Bot, QrCode, ScanLine, Loader2, 
  Wifi, Box, FlaskConical, Mountain
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";

const API_BASE = "http://localhost:8000/api";

// ─── 1. INTERFACES ──────────────────────────────────────────────────────────
export type ScanCategory = "sensor" | "seed" | "soil" | "fertilizer";

export interface ProbeData {
  moisture: number;
  nutrients: number;
  light: number;
  temperature: number;
}

export interface TimelineEvent {
  date: string;
  event: string;
  note: string;
  type?: ScanCategory;
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
  sensorId?: string;
}

// ─── 2. HELPERS ──────────────────────────────────────────────────────────────
function healthColor(v: number) {
  if (v >= 80) return "bg-emerald-500";
  if (v >= 50) return "bg-amber-400";
  return "bg-red-400";
}

// ─── 3. SUB-COMPONENTS ───────────────────────────────────────────────────────
function Gauge({ icon, label, value, unit, max = 100 }: { icon: ReactNode; label: string; value: number; unit: string; max?: number }) {
  return (
    <div className="rounded-lg border bg-card p-3 text-left">
      <div className="mb-1 flex items-center gap-1.5 text-xs text-muted-foreground">
        {icon} {label}
      </div>
      <div className="mb-1.5 text-lg font-semibold">{value}{unit}</div>
      <Progress value={(value / max) * 100} className="h-1.5" />
    </div>
  );
}

function PlantCard({ plant, onEdit, onDelete, onWater }: { plant: Plant; onEdit: (p: Plant) => void; onDelete: (id: number) => void; onWater: (id: number) => void }) {
  return (
    <Card className="overflow-hidden transition-shadow hover:shadow-md text-left">
      <Link to="/garden/$plantId" params={{ plantId: String(plant.id) }} state={{ plant } as any} className="block w-full">
        <div className="relative h-40 w-full bg-cover bg-center" style={{ backgroundImage: `url(${plant.image})` }}>
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
          <div className="absolute bottom-3 left-4 right-4 flex items-end justify-between text-white">
            <div>
              <div className="flex items-center gap-1 mb-0.5">
                 <Wifi className={`h-2.5 w-2.5 ${plant.sensorId ? 'text-emerald-400 animate-pulse' : 'text-slate-400'}`} />
                 <p className="text-[9px] uppercase tracking-widest">{plant.sensorId ? `Sensor ${plant.sensorId}` : 'Offline'}</p>
              </div>
              <h3 className="text-base font-semibold">{plant.nickname}</h3>
            </div>
            <Badge className={`${healthColor(plant.health)} border-0 text-white`}>{plant.health}%</Badge>
          </div>
        </div>
      </Link>

      <div className="p-4 space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-xs text-muted-foreground">Hari ke-{plant.daysPlanted}</span>
          <div className="flex gap-1">
            <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => onWater(plant.id)}><Droplets className="h-3.5 w-3.5 text-blue-500" /></Button>
            <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => onEdit(plant)}><Pencil className="h-3.5 w-3.5" /></Button>
            <Button size="icon" variant="ghost" className="h-7 w-7 text-destructive" onClick={() => onDelete(plant.id)}><Trash2 className="h-3.5 w-3.5" /></Button>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <Gauge icon={<Droplets className="h-3 w-3" />} label="Moisture" value={plant.probe.moisture} unit="%" />
          <Gauge icon={<Leaf className="h-3 w-3" />} label="Nutrients" value={plant.probe.nutrients} unit="%" />
        </div>
        <Button asChild className="w-full gap-2 bg-primary/10 text-primary hover:bg-primary/20" variant="secondary">
          <Link to="/garden/$plantId" params={{ plantId: String(plant.id) }} state={{ plant } as any}>
            <Bot className="h-4 w-4" /> Tanya Plantatio AI
          </Link>
        </Button>
      </div>
    </Card>
  );
}

// ─── 4. OMNI SCANNER MODAL ───────────────────────────────────────────────────
function OmniScannerModal({ onScanComplete, onClose }: { onScanComplete: (category: ScanCategory, data: any) => void; onClose: () => void }) {
  const [category, setCategory] = useState<ScanCategory>("sensor");
  const [step, setStep] = useState<"select" | "scan" | "processing">("select");

  const categories = [
    { id: "sensor", label: "Sensor", icon: <Wifi className="h-4 w-4" /> },
    { id: "seed", label: "Bibit", icon: <Sprout className="h-4 w-4" /> },
    { id: "soil", label: "Tanah", icon: <Mountain className="h-4 w-4" /> },
    { id: "fertilizer", label: "Pupuk", icon: <FlaskConical className="h-4 w-4" /> },
  ];

  const handleSimulateScan = () => {
    setStep("processing");
    setTimeout(() => {
      const mockData = { id: `DEV-${Math.floor(1000 + Math.random() * 9000)}`, name: "Premium Pack" };
      onScanComplete(category, mockData);
    }, 1500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-md">
      <div className="w-full max-w-sm rounded-3xl bg-background p-6 shadow-2xl space-y-6">
        {step === "select" ? (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-center">Pilih Objek Scan</h2>
            <div className="grid grid-cols-2 gap-3">
              {categories.map((cat) => (
                <button key={cat.id} onClick={() => { setCategory(cat.id as ScanCategory); setStep("scan"); }} className="flex flex-col items-center gap-2 rounded-2xl bg-secondary/50 p-4 hover:bg-primary/10 hover:text-primary transition-all">
                  {cat.icon} <span className="text-xs font-bold">{cat.label}</span>
                </button>
              ))}
            </div>
          </div>
        ) : step === "scan" ? (
          <div className="space-y-6 text-center">
            <h2 className="text-xl font-bold uppercase">Scan {category}</h2>
            <div className="relative mx-auto h-40 w-40 border-2 border-dashed border-primary rounded-xl overflow-hidden flex items-center justify-center bg-secondary/20">
               <div className="absolute top-0 left-0 w-full h-1 bg-primary animate-[scan_2s_infinite]" />
               <QrCode className="h-10 w-10 text-primary/20" />
            </div>
            <Button className="w-full" onClick={handleSimulateScan}>Mulai Pindai</Button>
          </div>
        ) : (
          <div className="py-12 text-center space-y-4">
            <Loader2 className="mx-auto h-12 w-12 animate-spin text-primary" />
            <p className="font-medium">Memproses Data...</p>
          </div>
        )}
        <Button variant="ghost" className="w-full" onClick={onClose}>Batal</Button>
        <style>{`@keyframes scan { 0%, 100% { top: 10%; } 50% { top: 90%; } }`}</style>
      </div>
    </div>
  );
}

// ─── 5. MAIN PAGE ────────────────────────────────────────────────────────────
export function PlantGardenPage() {
  const [plants, setPlants] = useState<Plant[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isScanning, setIsScanning] = useState(false);

  // GET: Ambil daftar tanaman saat halaman dimuat
  const fetchPlants = () => {
    fetch(`${API_BASE}/plants`)
      .then(res => res.json())
      .then(data => setPlants(data))
      .catch(err => toast.error("Gagal memuat tanaman dari server."))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    fetchPlants();
  }, []);

  // POST: Tambah tanaman ke backend dari hasil scan OmniScanner
  const handleOmniScan = async (category: ScanCategory, data: any) => {
    if (category === "sensor" || category === "seed") {
      try {
        const response = await fetch(`${API_BASE}/plants`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            nickname: category === "seed" ? "Tanaman Baru (Bibit)" : "Smart Plant",
            species: category === "seed" ? "Hasil Scan" : "Unknown",
            image: "https://images.unsplash.com/photo-1545239351-ef35f43d514b?w=600&q=80"
          }),
        });
        
        if (!response.ok) throw new Error("Gagal membuat tanaman");
        
        // Refresh daftar setelah sukses
        fetchPlants();
        toast.success("Tanaman baru berhasil ditambahkan!");
      } catch (err) {
        toast.error("Gagal sinkronisasi dengan server.");
      }
    } else {
      // Jika scan tanah/pupuk dari luar, beri tahu user masuk ke detail dulu
      toast.info(`Buka detail tanaman dulu untuk menerapkan ${category}.`);
    }
    setIsScanning(false);
  };

  // DELETE: Hapus dari backend
  const handleDelete = async (id: number) => {
    try {
      await fetch(`${API_BASE}/plants/${id}`, { method: "DELETE" });
      setPlants(plants.filter(x => x.id !== id));
      toast.success("Tanaman dihapus");
    } catch {
      toast.error("Gagal menghapus");
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-10 border-b bg-card/80 backdrop-blur px-4 py-3">
        <div className="max-w-2xl mx-auto flex justify-between items-center">
           <Link to="/" className="text-sm text-muted-foreground flex items-center gap-1"><ArrowLeft className="h-4 w-4"/> Dashboard</Link>
           <div className="font-bold flex items-center gap-2"><Sprout className="h-5 w-5 text-primary"/> MY GARDEN</div>
           <Badge variant="secondary">{plants.length} Unit</Badge>
        </div>
      </header>

      <main className="max-w-2xl mx-auto p-4 space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Koleksi Tanaman</h1>
          <Button onClick={() => setIsScanning(true)} className="bg-emerald-600 hover:bg-emerald-700 text-white">
            <QrCode className="mr-2 h-4 w-4" /> Scan Sesuatu
          </Button>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : plants.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground border-2 border-dashed rounded-xl">
             <Sprout className="mx-auto h-12 w-12 mb-3 opacity-20" />
             <p>Belum ada tanaman di kebun Anda.</p>
             <p className="text-sm">Gunakan tombol Scan untuk memulai!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {plants.map(p => (
              <PlantCard 
                key={p.id} 
                plant={p} 
                onEdit={() => toast.info("Fitur Edit segera hadir")} 
                onDelete={handleDelete} 
                onWater={() => toast.success(`${p.nickname} disiram!`)} 
              />
            ))}
          </div>
        )}
      </main>

      {isScanning && <OmniScannerModal onScanComplete={handleOmniScan} onClose={() => setIsScanning(false)} />}
    </div>
  );
}