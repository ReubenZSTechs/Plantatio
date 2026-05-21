import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Battery, BatteryLow, Cpu, Wrench, ShoppingCart, Plus, MapPin, X, Check, Loader2 } from "lucide-react";
import { toast } from "sonner";

const API_BASE = "http://localhost:8000/api/b2b";

const statusVariant: Record<string, string> = {
  ok: "bg-emerald-500/15 text-emerald-600 border-emerald-500/30",
  warn: "bg-amber-500/15 text-amber-600 border-amber-500/30",
  critical: "bg-destructive/15 text-destructive border-destructive/30",
};

export interface IotNode {
  id: string;
  zone: string;
  battery: number;
  moisture: number;
  status: string;
  latitude: number;
  longitude: number;
}

export function DeviceManager() {
  const [devices, setDevices] = useState<IotNode[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  // Form State untuk sensor baru
  const [zone, setZone] = useState("");
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");

  // GET: Fetch devices
  const fetchDevices = () => {
    fetch(`${API_BASE}/devices`)
      .then((res) => res.json())
      .then((data) => setDevices(data))
      .catch(() => toast.error("Gagal memuat perangkat dari server."))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    fetchDevices();
  }, []);

  // POST: Tambah Sensor
  const handleAddDevice = async () => {
    if (!zone || !latitude || !longitude) {
      toast.error("Zona dan titik koordinat wajib diisi");
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/devices`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          zone,
          latitude: parseFloat(latitude),
          longitude: parseFloat(longitude),
        }),
      });

      if (!res.ok) throw new Error();
      toast.success("Sensor baru berhasil didaftarkan");
      fetchDevices(); // Refresh data
      setShowAddModal(false);
      setZone(""); setLatitude(""); setLongitude("");
    } catch {
      toast.error("Gagal menambahkan sensor");
    }
  };

  // POST: Fitur Mock Procurement dkk
  const handleDiagnose = async (id: string) => {
    await fetch(`${API_BASE}/devices/${id}/diagnose`, { method: "POST" });
    toast.info(`Ping diagnostic dikirim ke ${id}`);
  };

  const handleOrder = async () => {
    await fetch(`${API_BASE}/procurement`, { method: "POST" });
    toast.success("Cart updated · 10 probes ditambahkan");
  };

  const handleMaintenance = async () => {
    await fetch(`${API_BASE}/maintenance`, { method: "POST" });
    toast.success("Maintenance ticket #M-2419 created");
  };

  // HTML5 Geolocation API
  const handleGetLocation = () => {
    if ("geolocation" in navigator) {
      toast.info("Mencari sinyal GPS...");
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLatitude(position.coords.latitude.toFixed(6));
          setLongitude(position.coords.longitude.toFixed(6));
          toast.success("Koordinat didapatkan");
        },
        () => toast.error("Gagal mendapatkan lokasi GPS. Pastikan izin lokasi aktif.")
      );
    } else {
      toast.error("Browser Anda tidak mendukung GPS.");
    }
  };

  return (
    <div className="space-y-6 p-4 md:p-8 max-w-5xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Device Manager</h1>
          <p className="text-sm text-muted-foreground">Manajemen sensor lapangan, baterai, dan pengadaan barang.</p>
        </div>
        <Button className="bg-primary" onClick={() => setShowAddModal(true)}>
          <Plus className="mr-2 h-4 w-4" /> Register Sensor Baru
        </Button>
      </div>

      <Card className="overflow-hidden">
        {isLoading ? (
          <div className="flex justify-center p-8"><Loader2 className="h-6 w-6 animate-spin text-primary" /></div>
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Node ID</TableHead>
                  <TableHead>Zone & Koordinat</TableHead>
                  <TableHead>Battery</TableHead>
                  <TableHead>Moisture</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {devices.length === 0 ? (
                  <TableRow><TableCell colSpan={6} className="text-center py-6 text-muted-foreground">Belum ada sensor terdaftar</TableCell></TableRow>
                ) : (
                  devices.map((n) => (
                    <TableRow key={n.id}>
                      <TableCell className="font-mono text-xs font-bold text-primary/80">{n.id}</TableCell>
                      <TableCell>
                        <p className="font-medium">{n.zone}</p>
                        <p className="text-[10px] text-muted-foreground flex items-center gap-1 mt-0.5">
                           <MapPin className="h-3 w-3" /> {n.latitude}, {n.longitude}
                        </p>
                      </TableCell>
                      <TableCell>
                        <span className="flex items-center gap-1.5 font-medium">
                          {n.battery < 20 ? <BatteryLow className="h-4 w-4 text-destructive animate-pulse" /> : <Battery className="h-4 w-4 text-emerald-500" />}
                          {n.battery}%
                        </span>
                      </TableCell>
                      <TableCell>{n.moisture}%</TableCell>
                      <TableCell>
                        <Badge variant="outline" className={statusVariant[n.status]}>{n.status.toUpperCase()}</Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button size="sm" variant="ghost" onClick={() => handleDiagnose(n.id)}>Diagnose</Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        )}
      </Card>

      <div>
        <h2 className="mb-3 text-lg font-semibold">Procurement & Maintenance</h2>
        <div className="grid gap-4 md:grid-cols-2">
          <Card className="p-5 flex flex-col justify-between">
            <div>
              <Cpu className="mb-3 h-6 w-6 text-primary" />
              <div className="font-semibold">Order Smart Probes</div>
              <p className="mt-1 text-sm text-muted-foreground">Plantatio Probe v3 — soil moisture, NPK, temperature, LoRa mesh.</p>
            </div>
            <div className="mt-4 flex items-center justify-between border-t pt-4">
              <span className="text-sm font-medium">€89 / unit · MOQ 10</span>
              <Button size="sm" onClick={handleOrder}>
                <ShoppingCart className="mr-2 h-4 w-4" /> Add to order
              </Button>
            </div>
          </Card>
          <Card className="p-5 flex flex-col justify-between">
            <div>
              <Wrench className="mb-3 h-6 w-6 text-amber-500" />
              <div className="font-semibold">Request On-Site Maintenance</div>
              <p className="mt-1 text-sm text-muted-foreground">Dispatch a certified field technician for failing nodes.</p>
            </div>
            <div className="mt-4 flex items-center justify-between border-t pt-4">
              <span className="text-sm font-medium text-amber-600">2 critical nodes flagged</span>
              <Button size="sm" variant="outline" className="border-amber-200 text-amber-700 hover:bg-amber-50" onClick={handleMaintenance}>
                <Wrench className="mr-2 h-4 w-4" /> Dispatch
              </Button>
            </div>
          </Card>
        </div>
      </div>

      {/* Modal Add Sensor */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-sm rounded-2xl bg-background shadow-2xl">
            <div className="flex items-center justify-between border-b px-5 py-4">
              <h2 className="font-semibold">Register Node Sensor</h2>
              <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => setShowAddModal(false)}><X className="h-4 w-4" /></Button>
            </div>
            <div className="p-5 space-y-4">
              <div className="space-y-1.5">
                <Label>Nama Zona / Penempatan</Label>
                <Input placeholder="e.g. Sektor C - Barat" value={zone} onChange={e => setZone(e.target.value)} />
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label>Latitude</Label>
                  <Input type="number" placeholder="-6.200" value={latitude} onChange={e => setLatitude(e.target.value)} />
                </div>
                <div className="space-y-1.5">
                  <Label>Longitude</Label>
                  <Input type="number" placeholder="106.816" value={longitude} onChange={e => setLongitude(e.target.value)} />
                </div>
              </div>
              
              <Button type="button" variant="secondary" className="w-full gap-2 text-xs h-8 bg-blue-50 text-blue-600 hover:bg-blue-100 dark:bg-blue-900/30 dark:text-blue-400" onClick={handleGetLocation}>
                <MapPin className="h-3.5 w-3.5" /> Gunakan GPS Saat Ini
              </Button>
            </div>
            <div className="flex gap-2 border-t px-5 py-4">
              <Button variant="outline" className="flex-1" onClick={() => setShowAddModal(false)}>Batal</Button>
              <Button className="flex-1" onClick={handleAddDevice}><Check className="mr-2 h-4 w-4" /> Simpan Node</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}