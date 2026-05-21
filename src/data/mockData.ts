// Mock data for the PLANTATIO prototype.
// In production these payloads come from the FastAPI backend (see /mnt/documents/plantatio/main.py)
// which orchestrates: LLM (cognitive assistant), InfluxDB (sensor logs),
// GraphRAG (plant knowledge graph), and MQTT (IoT node telemetry).

export const plantProfile = {
  id: "plt_001",
  name: "Monstera Deliciosa",
  nickname: "Monty",
  species: "Monstera deliciosa",
  daysPlanted: 142,
  health: 87,
  image:
    "https://images.unsplash.com/photo-1614594975525-e45190c55d0b?w=600&q=80&auto=format&fit=crop",
  probe: {
    moisture: 62,
    nutrients: 78,
    light: 54,
    temperature: 23.4,
  },
  timeline: [
    { date: "2025-05-08", event: "Watered", note: "Auto-triggered by probe" },
    { date: "2025-05-04", event: "Fertilized", note: "NPK 10-10-10, 2g" },
    { date: "2025-04-28", event: "Repotted", note: "12cm → 16cm" },
    { date: "2025-04-12", event: "Pruned", note: "Removed 2 yellow leaves" },
    { date: "2025-01-21", event: "Planted", note: "Seedling, indoor" },
  ],
};

export const weatherAlert = {
  city: "Jakarta",
  tempC: 28,
  condition: "Sunny",
  humidity: 41,
  forecast: [
    { day: "Tue", tempC: 29, icon: "sun" },
    { day: "Wed", tempC: 33, icon: "sun" },
    { day: "Thu", tempC: 36, icon: "sun" },
    { day: "Fri", tempC: 31, icon: "cloud" },
    { day: "Sat", tempC: 27, icon: "rain" },
  ],
  alert: {
    level: "warning",
    title: "Heatwave incoming in 48h",
    body: "",
  },
};

export const chatHistory = [
  {
    role: "assistant",
    text: "Hi! I'm your Plantatio cognitive assistant. Upload a photo and I'll help diagnose any issues.",
  },
  { role: "user", text: "My monstera has yellow spots. What's wrong?" },
  {
    role: "assistant",
    text: "Based on the image, this looks like early-stage overwatering combined with low light. I'd recommend reducing watering to once every 9 days and moving 1m closer to indirect sunlight.",
    tags: ["Diagnosis: Overwatering", "Confidence: 92%"],
  },
];

export const esgSummary = {
  totalTrees: 184_320,
  survivalRate: 91.4,
  carbonTons: 2_146,
  hectares: 412,
  projection: [
    { month: "Jan", projected: 120, actual: 110 },
    { month: "Feb", projected: 240, actual: 235 },
    { month: "Mar", projected: 410, actual: 402 },
    { month: "Apr", projected: 640, actual: 651 },
    { month: "May", projected: 920, actual: 905 },
    { month: "Jun", projected: 1240, actual: 1218 },
    { month: "Jul", projected: 1600, actual: 1582 },
    { month: "Aug", projected: 1980, actual: 1955 },
    { month: "Sep", projected: 2380, actual: 2146 },
  ],
  speciesMix: [
    { name: "Cork Oak", value: 38 },
    { name: "Stone Pine", value: 27 },
    { name: "Holm Oak", value: 21 },
    { name: "Eucalyptus", value: 14 },
  ],
};

export const iotNodes = [
  { id: "N-014", zone: "Alpha-3", battery: 92, moisture: 38, status: "ok", lat: 38.72, lng: -9.14 },
  { id: "N-015", zone: "Alpha-3", battery: 78, moisture: 24, status: "warn", lat: 38.73, lng: -9.13 },
  { id: "N-022", zone: "Beta-1", battery: 14, moisture: 11, status: "critical", lat: 38.74, lng: -9.16 },
  { id: "N-031", zone: "Beta-2", battery: 88, moisture: 47, status: "ok", lat: 38.71, lng: -9.12 },
  { id: "N-040", zone: "Gamma-1", battery: 61, moisture: 19, status: "warn", lat: 38.75, lng: -9.15 },
  { id: "N-052", zone: "Gamma-2", battery: 96, moisture: 51, status: "ok", lat: 38.7, lng: -9.17 },
  { id: "N-061", zone: "Delta-1", battery: 44, moisture: 33, status: "ok", lat: 38.76, lng: -9.11 },
  { id: "N-072", zone: "Delta-2", battery: 9, moisture: 8, status: "critical", lat: 38.77, lng: -9.18 },
];

export const aiTacticalLogs = [
  { time: "14:02", action: "Irrigation valve V-7 opened (Beta-1, 8min)", severity: "info" },
  { time: "13:48", action: "Heatwave model triggered: shade nets queued for Gamma zones", severity: "warn" },
  { time: "13:22", action: "Node N-022 flagged for maintenance dispatch", severity: "critical" },
  { time: "12:55", action: "Carbon ledger synced to registry (Verra API)", severity: "info" },
  { time: "12:10", action: "Weather macro pull: 36°C peak Thu, soil permeability 0.41", severity: "info" },
];

export const macroData = {
  soilPermeability: 0.41,
  soilPh: 6.8,
  windKmh: 22,
  incomingWeather: "Heatwave 48h",
  satellitePass: "16:40 UTC",
};
