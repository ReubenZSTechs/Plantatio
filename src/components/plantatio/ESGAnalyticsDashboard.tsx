import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Camera, Upload, Loader2, ScanSearch, Layers, 
  Target, Leaf, ShieldCheck, Cloud, TreePine 
} from "lucide-react";
import { toast } from "sonner";

const API_BASE = "http://localhost:8000/api";

export interface EuroSatData {
  imagePath: string;
  className: string;
  labels: {
    vegetationDensity: string;
    canopyCover: number;
    estBiomass: number;
    carbonEq: number;
    restorationQuality: string;
    confidence: number;
  };
}

export function ESGAnalyticsDashboard() {
  const [preFile, setPreFile] = useState<File | null>(null);
  const [currentFile, setCurrentFile] = useState<File | null>(null);
  const [prePreview, setPrePreview] = useState<string>("");
  const [currentPreview, setCurrentPreview] = useState<string>("");
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisData, setAnalysisData] = useState<EuroSatData | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, type: "pre" | "current") => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        if (type === "pre") {
          setPreFile(file);
          setPrePreview(reader.result as string);
        } else {
          setCurrentFile(file);
          setCurrentPreview(reader.result as string);
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUploadAndAnalyze = async () => {
    if (!preFile || !currentFile) {
      toast.error("Wajib mengunggah kedua berkas citra satelit (Pre-Restoration & Current State)");
      return;
    }

    setIsAnalyzing(true);
    const formData = new FormData();
    formData.append("pre_restoration", preFile);
    formData.append("current_state", currentFile);

    try {
      const response = await fetch(`${API_BASE}/b2b/satellite/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error();
      const result = await response.json();
      
      setAnalysisData(result);
      toast.success("Analisis komparatif selesai");
    } catch {
      toast.error("Gagal memproses analisis citra satelit");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6 text-left max-w-5xl mx-auto p-2">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">ESG Analytics</h1>
        <p className="text-sm text-muted-foreground">EuroSAT LULC Classification and Vegetation Analytics Pipeline.</p>
      </div>

      {/* Upload Section */}
      <Card className="p-5 border-primary/20 bg-muted/10 space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <Label className="text-xs font-bold">Pre-Restoration Image (T-0)</Label>
            <input type="file" accept="image/*" capture="environment" id="pre-sat" className="hidden" onChange={(e) => handleFileChange(e, "pre")} />
            <Label htmlFor="pre-sat" className="cursor-pointer relative aspect-video rounded-xl bg-slate-900 overflow-hidden border-2 border-dashed border-muted flex flex-col items-center justify-center text-white group">
              {prePreview ? (
                <img src={prePreview} className="h-full w-full object-cover" alt="Pre" />
              ) : (
                <div className="text-center text-xs text-muted-foreground space-y-1 p-4">
                  <Camera className="mx-auto h-5 w-5 opacity-50" />
                  <p>Ambil / Unggah Foto Baseline</p>
                </div>
              )}
            </Label>
          </div>

          <div className="space-y-1.5">
            <Label className="text-xs font-bold">Current State Image (T-1)</Label>
            <input type="file" accept="image/*" capture="environment" id="curr-sat" className="hidden" onChange={(e) => handleFileChange(e, "current")} />
            <Label htmlFor="curr-sat" className="cursor-pointer relative aspect-video rounded-xl bg-slate-900 overflow-hidden border-2 border-dashed border-emerald-500/20 flex flex-col items-center justify-center text-white group">
              {currentPreview ? (
                <img src={currentPreview} className="h-full w-full object-cover" alt="Current" />
              ) : (
                <div className="text-center text-xs text-muted-foreground space-y-1 p-4">
                  <Upload className="mx-auto h-5 w-5 opacity-50" />
                  <p>Ambil / Unggah Foto Terkini</p>
                </div>
              )}
            </Label>
          </div>
        </div>

        <Button className="w-full bg-emerald-700 hover:bg-emerald-800 text-white" onClick={handleUploadAndAnalyze} disabled={isAnalyzing}>
          {isAnalyzing ? (
            <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Memproses Data Spektral...</>
          ) : (
            <>Jalankan Audit Citra Satelit</>
          )}
        </Button>
      </Card>

      {/* ML Report Output */}
      {analysisData && (
        <Card className="overflow-hidden border-primary/10 shadow-sm">
          <div className="border-b bg-muted/40 px-5 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center gap-3">
              <ScanSearch className="h-5 w-5 text-primary" />
              <div>
                <h3 className="text-sm font-bold">ML Classification Result</h3>
                <p className="text-[10px] text-muted-foreground font-mono truncate max-w-md">
                  Path: {analysisData.imagePath}
                </p>
              </div>
            </div>
            <Badge className="bg-emerald-600 text-xs py-1 px-3">
              Class: {analysisData.className}
            </Badge>
          </div>

          <div className="p-4 bg-muted/10 border-b grid grid-cols-2 gap-4">
            <div className="p-3 bg-background border rounded-xl">
              <p className="text-[10px] text-muted-foreground uppercase font-bold">Vegetation Density</p>
              <p className="text-lg font-bold text-primary mt-0.5 capitalize">{analysisData.labels.vegetationDensity}</p>
            </div>
            <div className="p-3 bg-background border rounded-xl">
              <p className="text-[10px] text-muted-foreground uppercase font-bold">Restoration Quality</p>
              <p className="text-lg font-bold text-primary mt-0.5 capitalize">{analysisData.labels.restorationQuality}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 divide-x divide-y md:divide-y-0">
            <div className="p-4 space-y-1 bg-background">
               <p className="text-[10px] text-muted-foreground uppercase font-bold flex items-center gap-1"><Leaf className="h-3 w-3" /> Canopy Cover</p>
               <p className="text-xl font-bold">{(analysisData.labels.canopyCover * 100).toFixed(0)}%</p>
               <Progress value={analysisData.labels.canopyCover * 100} className="h-1 mt-1" />
            </div>
            <div className="p-4 space-y-1 bg-background">
               <p className="text-[10px] text-muted-foreground uppercase font-bold flex items-center gap-1"><TreePine className="h-3 w-3" /> Est. Biomass</p>
               <p className="text-xl font-bold">{analysisData.labels.estBiomass}</p>
               <Progress value={analysisData.labels.estBiomass * 100} className="h-1 mt-1" />
            </div>
            <div className="p-4 space-y-1 bg-background">
               <p className="text-[10px] text-muted-foreground uppercase font-bold flex items-center gap-1"><Cloud className="h-3 w-3" /> Carbon Equivalent</p>
               <p className="text-xl font-bold">{analysisData.labels.carbonEq}</p>
               <Progress value={analysisData.labels.carbonEq * 100} className="h-1 mt-1" />
            </div>
            <div className="p-4 space-y-1 bg-emerald-50/40 dark:bg-emerald-950/10">
               <p className="text-[10px] text-emerald-700 dark:text-emerald-400 uppercase font-bold flex items-center gap-1"><ShieldCheck className="h-3 w-3" /> ML Confidence</p>
               <p className="text-xl font-bold text-emerald-700 dark:text-emerald-400">{(analysisData.labels.confidence * 100).toFixed(0)}%</p>
               <div className="flex items-center gap-1 mt-1 text-[9px] text-muted-foreground">
                 <Target className="h-2.5 w-2.5" /> Overlapping Accuracy Profile
               </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}