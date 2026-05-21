import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Cloud, CloudRain, Sun, AlertTriangle } from "lucide-react";

const iconFor = (k: string) =>
  k === "rain" ? <CloudRain className="h-4 w-4" /> : k === "cloud" ? <Cloud className="h-4 w-4" /> : <Sun className="h-4 w-4" />;

interface ForecastItem {
  day: string;
  icon: string;
  tempC: number;
}

interface WeatherData {
  city: string;
  tempC: number;
  condition: string;
  humidity: number;
  forecast: ForecastItem[];
}

interface AlertData {
  title: string;
  body: string;
}

export function WeatherSyncWidget() {
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [alert, setAlert] = useState<AlertData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Mengambil data dari kedua API secara bersamaan
        const [weatherRes, alertRes] = await Promise.all([
          fetch("http://localhost:8000/api/v1/weather/macro"),
          fetch("http://localhost:8000/api/v1/weather/alert")
        ]);

        if (!weatherRes.ok || !alertRes.ok) {
          throw new Error("Gagal mengambil data dari server");
        }

        const weatherData = await weatherRes.json();
        const alertData = await alertRes.json();

        setWeather(weatherData);
        setAlert(alertData);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading || !weather) {
    return (
      <Card className="flex h-[280px] items-center justify-center">
        <div className="text-sm text-muted-foreground">Memuat data...</div>
      </Card>
    );
  }

  return (
    <Card className="overflow-hidden">
      <div
        className="p-5 text-primary-foreground"
        style={{ background: "var(--gradient-hero)" }}
      >
        <div className="flex items-center justify-between">
          <div>
            <div className="text-xs uppercase tracking-wide opacity-80">{weather.city}</div>
            <div className="text-4xl font-semibold">{weather.tempC}°</div>
            <div className="text-sm opacity-90">{weather.condition} · {weather.humidity}% humidity</div>
          </div>
          <Sun className="h-12 w-12 opacity-90" />
        </div>
        <div className="mt-4 grid grid-cols-5 gap-2">
          {weather.forecast.map((d) => (
            <div key={d.day} className="rounded-lg bg-white/15 p-2 text-center text-xs backdrop-blur-sm">
              <div className="opacity-80">{d.day}</div>
              <div className="my-1 flex justify-center">{iconFor(d.icon)}</div>
              <div className="font-medium">{d.tempC}°</div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Tampilkan bagian alert hanya jika data alert berhasil diambil dari API */}
      {alert && (
        <div className="flex gap-3 border-l-4 border-warning bg-warning/10 p-4">
          <AlertTriangle className="h-5 w-5 shrink-0 text-warning" />
          <div className="text-sm">
            <div className="font-semibold">{alert.title}</div>
            <div className="text-xs text-muted-foreground">{alert.body}</div>
          </div>
        </div>
      )}
    </Card>
  );
}