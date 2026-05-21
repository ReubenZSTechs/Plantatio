import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  BrainCircuit, Zap, Database, TrendingUp, 
  CheckCircle2, Play, RefreshCw, CloudSun, Radio, Thermometer 
} from "lucide-react";
import { Progress } from "@/components/ui/progress";

export function MLPredictionManager() {
  // 1. Definisi Model Sederhana untuk Tahap Awal
  const models = [
    {
      id: "M-LR-01",
      name: "Water Demand Regression",
      algorithm: "Linear Regression",
      status: "Active",
      accuracy: 85.5,
      dataSource: "Moisture Sensor + Weather API",
      insight: "Memprediksi volume air (liter) yang dibutuhkan besok."
    },
    {
      id: "M-RF-02",
      name: "Pathogen Classifier",
      algorithm: "Random Forest",
      status: "Active",
      accuracy: 92.1,
      dataSource: "Humidity + Temp Sensors",
      insight: "Klasifikasi risiko penyakit: Low, Medium, High."
    },
    {
      id: "M-TS-03",
      name: "Growth Time-Series",
      algorithm: "Simple Moving Average",
      status: "Training",
      accuracy: 76.4,
      dataSource: "Camera/Image Processing API",
      insight: "Estimasi tinggi tanaman berdasarkan tren mingguan."
    }
  ];

  // 2. Simulasi Data dari API & Sensor
  const externalData = [
    { label: "Weather API", value: "28°C", sub: "Cloudy / 65% Hum", icon: <CloudSun className="text-sky-500" /> },
    { label: "MQTT Signal", value: "-65 dBm", sub: "Node A-04 (Strong)", icon: <Radio className="text-emerald-500" /> },
    { label: "Soil Probe", value: "450 mV", sub: "Nutrient Voltage", icon: <Thermometer className="text-amber-500" /> },
  ];

  return (
    <div className="space-y-6 text-left">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">ML Prediction Manager</h2>
        <p className="text-sm text-muted-foreground">Analisis data sensor dan prediksi model secara real-time.</p>
      </div>

      {/* RAW DATA FEED DARI API & SENSOR */}
      <div className="grid gap-4 md:grid-cols-3">
        {externalData.map((data, idx) => (
          <Card key={idx} className="p-4 flex items-center gap-4 bg-muted/30 border-none">
            <div className="p-3 bg-background rounded-xl shadow-sm">{data.icon}</div>
            <div>
              <p className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider">{data.label}</p>
              <p className="text-lg font-bold">{data.value}</p>
              <p className="text-[10px] opacity-70">{data.sub}</p>
            </div>
          </Card>
        ))}
      </div>

      {/* MODEL MANAGEMENT */}
      <div className="grid gap-4 md:grid-cols-3">
        {models.map((model) => (
          <Card key={model.id} className="p-5 space-y-4 shadow-sm border-primary/10 relative overflow-hidden">
            <div className="flex items-start justify-between">
              <div className="rounded-full bg-primary/10 p-2 text-primary">
                <BrainCircuit className="h-5 w-5" />
              </div>
              <Badge variant={model.status === "Active" ? "default" : "secondary"}>
                {model.status}
              </Badge>
            </div>
            
            <div>
              <h3 className="font-bold leading-tight">{model.name}</h3>
              <p className="text-[10px] font-mono text-primary uppercase">{model.algorithm}</p>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-xs font-medium">
                <span>Validation Accuracy</span>
                <span>{model.accuracy}%</span>
              </div>
              <Progress value={model.accuracy} className="h-1" />
            </div>

            <p className="text-xs text-muted-foreground italic leading-relaxed">"{model.insight}"</p>

            <div className="flex gap-2 pt-2">
              <Button size="sm" className="w-full gap-1.5" variant="outline">
                <RefreshCw className="h-3.5 w-3.5" /> Retrain
              </Button>
              <Button size="sm" className="w-full gap-1.5 bg-primary">
                <Play className="h-3.5 w-3.5" /> Predict
              </Button>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {/* ML Inference Pipeline */}
        <Card className="p-6 space-y-4 bg-card">
          <div className="flex items-center gap-2 font-bold">
            <Zap className="h-5 w-5 text-amber-500" />
            Active Signal Processing
          </div>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center justify-between border-b border-border/50 pb-2 last:border-0">
                <div className="flex items-center gap-3">
                  <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                  <div>
                    <p className="text-sm font-medium">Telemetry Node #{i}</p>
                    <p className="text-[10px] text-muted-foreground font-mono">Raw: 0.42v | Map: 68%</p>
                  </div>
                </div>
                <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              </div>
            ))}
          </div>
        </Card>

        {/* Aggregated Forecast */}
        <Card className="p-6 bg-emerald-600 text-white space-y-4">
          <div className="flex items-center gap-2 font-bold">
            <TrendingUp className="h-5 w-5" />
            Smart Irrigation Forecast
          </div>
          <div className="space-y-2">
             <div className="text-4xl font-bold">-25%</div>
             <p className="text-sm opacity-90 leading-relaxed">
               Potensi penghematan air dalam 7 hari ke depan karena prediksi curah hujan tinggi dari Weather API.
             </p>
             <div className="flex gap-2 pt-2">
                <Badge className="bg-white/20 text-white border-0">High Precision</Badge>
                <Badge className="bg-white/20 text-white border-0">API Synced</Badge>
             </div>
          </div>
        </Card>
      </div>
    </div>
  );
}