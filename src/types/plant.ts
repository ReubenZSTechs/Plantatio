/**
 * Shared domain types.
 *
 * These were previously redeclared in three components with conflicting
 * shapes, so the same `Plant` meant different things depending on the file.
 */

export type ScanCategory = "sensor" | "seed" | "soil" | "fertilizer" | "other";

export interface ProbeData {
  moisture: number;
  nutrients: number;
  light: number;
  temperature: number;
}

export interface TimelineEvent {
  id?: number;
  plantId?: number;
  date: string;
  event: string;
  note: string;
  scanCategory?: ScanCategory;
}

export interface ScannedItem {
  id: string;
  plantId?: number;
  category: ScanCategory;
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

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

/** What the agent retrieved on the way to an answer. */
export interface GraphProvenance {
  subQuestions: string[];
  retrievedFacts: string[];
  recordCount: number;
  graphAvailable: boolean;
}

export interface ChatReply {
  role: "assistant";
  text: string;
  tags?: string[];
  provenance?: GraphProvenance;
}

export interface DiagnosisPrediction {
  classId: number;
  className: string;
  label: string;
  confidence: number;
}

export interface Diagnosis {
  plantId?: number;
  predictions: DiagnosisPrediction[];
  topClass: string;
  label: string;
  confidence: number;
  isDefective: boolean;
  healthScore: number;
  summary: string;
}

export interface IotNode {
  id: string;
  zone: string;
  battery: number;
  moisture: number;
  status: "ok" | "warn" | "critical";
  latitude: number;
  longitude: number;
}

export interface TacticalLog {
  id: number;
  time: string;
  action: string;
  severity: "info" | "warn" | "critical";
}

export interface ForecastDay {
  day: string;
  icon: string;
  tempC: number;
}

export interface WeatherMacro {
  city: string;
  tempC: number;
  condition: string;
  humidity: number;
  forecast: ForecastDay[];
}

export interface WeatherAlert {
  title: string;
  body: string;
}

export interface RestorationDelta {
  canopyCoverChange: number | null;
  biomassChange: number | null;
  carbonChange: number | null;
}

export interface SatelliteLabels {
  vegetationDensity: string | null;
  canopyCover: number | null;
  estBiomass: number | null;
  carbonEq: number | null;
  restorationQuality: string | null;
  confidence: number | null;
  restorationDelta: RestorationDelta | null;
}

export interface SatelliteAnalysis {
  imagePath: string;
  className: string;
  labels: SatelliteLabels;
}

export interface GeoJsonPolygon {
  type: "Polygon";
  coordinates: number[][][];
}

export interface LandParcel {
  id: number;
  name: string;
  zone: string | null;
  geometry: GeoJsonPolygon;
  centroidLatitude: number;
  centroidLongitude: number;
  areaHectares: number | null;
  landCoverClass: string | null;
  vegetationDensity: string | null;
  canopyCover: number | null;
  estBiomass: number | null;
  carbonEq: number | null;
  restorationQuality: string | null;
  confidence: number | null;
  restorationPotential: number | null;
  rationale: string | null;
  analyzedAt: string | null;
}

export interface LandCoverClass {
  name: string;
  headroom: number;
  description: string;
  referenceTiles: number;
}
