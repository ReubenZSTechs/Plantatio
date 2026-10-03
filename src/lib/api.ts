/**
 * Typed client for the Plantatio API.
 *
 * The base URL comes from VITE_API_BASE_URL. It used to be hardcoded as
 * `http://localhost:8000/api` in six separate components, which also meant the
 * deployed build called the visitor's own machine.
 */

import type {
  ChatMessage,
  ChatReply,
  Diagnosis,
  IotNode,
  LandCoverClass,
  LandParcel,
  Plant,
  SatelliteAnalysis,
  ScannedItem,
  TacticalLog,
  WeatherAlert,
  WeatherMacro,
} from "@/types/plant";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

/** Raised for any non-2xx response, carrying the server's own message. */
export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, init);
  } catch {
    throw new ApiError("Could not reach the Plantatio API. Check that the backend is running.", 0);
  }

  if (!response.ok) {
    throw new ApiError(await readErrorMessage(response), response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

/** Prefer FastAPI's `detail` field over an opaque status line. */
async function readErrorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body?.detail === "string") return body.detail;
    if (Array.isArray(body?.detail) && body.detail[0]?.msg) return body.detail[0].msg;
  } catch {
    // Fall through to the generic message below.
  }

  return `Request failed (${response.status})`;
}

function json<T>(path: string, method: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export const api = {
  // ── Plants ────────────────────────────────────────────────────────────────
  listPlants: () => request<Plant[]>("/plants"),

  getPlant: (plantId: number) => request<Plant>(`/plants/${plantId}`),

  createPlant: (plant: { nickname: string; species?: string; image?: string }) =>
    json<Plant>("/plants", "POST", plant),

  deletePlant: (plantId: number) =>
    request<{ message: string }>(`/plants/${plantId}`, { method: "DELETE" }),

  scanItem: (plantId: number, item: ScannedItem) =>
    json<Plant>(`/plants/${plantId}/scan`, "POST", item),

  // ── Assistant ─────────────────────────────────────────────────────────────
  /**
   * Send a conversation to the agent.
   *
   * The API expects the full message list; sending `{ text }` returns 422.
   */
  chat: (scope: "b2c" | "b2b" | "plant", messages: ChatMessage[], plantId?: number) => {
    const path =
      scope === "plant" && plantId !== undefined ? `/plants/${plantId}/chat` : `/${scope}/chat`;

    return json<ChatReply>(path, "POST", { messages, scope, plantId });
  },

  /** Classify a leaf photograph. Returns 503 while no model is trained. */
  diagnosePlant: (plantId: number, image: File) => {
    const form = new FormData();
    form.append("image", image);
    return request<Diagnosis>(`/plants/${plantId}/diagnose`, {
      method: "POST",
      body: form,
    });
  },

  // ── Weather ───────────────────────────────────────────────────────────────
  getWeatherMacro: () => request<WeatherMacro>("/v1/weather/macro"),
  getWeatherAlert: () => request<WeatherAlert>("/v1/weather/alert"),

  // ── Devices ───────────────────────────────────────────────────────────────
  listDevices: () => request<IotNode[]>("/b2b/devices"),

  createDevice: (node: { zone: string; latitude: number; longitude: number }) =>
    json<IotNode>("/b2b/devices", "POST", node),

  diagnoseDevice: (nodeId: string) =>
    request<{ message: string }>(`/b2b/devices/${nodeId}/diagnose`, { method: "POST" }),

  orderProbes: () => request<{ message: string }>("/b2b/procurement", { method: "POST" }),

  requestMaintenance: () => request<{ message: string }>("/b2b/maintenance", { method: "POST" }),

  getTacticalLogs: () => request<TacticalLog[]>("/b2b/agents/log"),

  // ── Land and satellite ────────────────────────────────────────────────────
  listLandParcels: (params?: { minPotential?: number; landCoverClass?: string }) => {
    const query = new URLSearchParams();
    if (params?.minPotential) query.set("min_potential", String(params.minPotential));
    if (params?.landCoverClass) query.set("land_cover_class", params.landCoverClass);
    const suffix = query.toString() ? `?${query}` : "";

    return request<LandParcel[]>(`/b2b/land-parcels${suffix}`);
  },

  getLandCoverClasses: () => request<LandCoverClass[]>("/b2b/land-cover-classes"),

  analyzeSatellite: (preRestoration: File, currentState: File) => {
    const form = new FormData();
    form.append("pre_restoration", preRestoration);
    form.append("current_state", currentState);

    return request<SatelliteAnalysis>("/b2b/satellite/analyze", {
      method: "POST",
      body: form,
    });
  },
};
