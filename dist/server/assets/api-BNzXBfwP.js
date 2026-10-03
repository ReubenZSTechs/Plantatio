const API_BASE_URL = "http://localhost:8000/api";
class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
  status;
}
async function request(path, init) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, init);
  } catch {
    throw new ApiError("Could not reach the Plantatio API. Check that the backend is running.", 0);
  }
  if (!response.ok) {
    throw new ApiError(await readErrorMessage(response), response.status);
  }
  if (response.status === 204) {
    return void 0;
  }
  return await response.json();
}
async function readErrorMessage(response) {
  try {
    const body = await response.json();
    if (typeof body?.detail === "string") return body.detail;
    if (Array.isArray(body?.detail) && body.detail[0]?.msg) return body.detail[0].msg;
  } catch {
  }
  return `Request failed (${response.status})`;
}
function json(path, method, body) {
  return request(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
}
const api = {
  // ── Plants ────────────────────────────────────────────────────────────────
  listPlants: () => request("/plants"),
  getPlant: (plantId) => request(`/plants/${plantId}`),
  createPlant: (plant) => json("/plants", "POST", plant),
  deletePlant: (plantId) => request(`/plants/${plantId}`, { method: "DELETE" }),
  scanItem: (plantId, item) => json(`/plants/${plantId}/scan`, "POST", item),
  // ── Assistant ─────────────────────────────────────────────────────────────
  /**
   * Send a conversation to the agent.
   *
   * The API expects the full message list; sending `{ text }` returns 422.
   */
  chat: (scope, messages, plantId) => {
    const path = scope === "plant" && plantId !== void 0 ? `/plants/${plantId}/chat` : `/${scope}/chat`;
    return json(path, "POST", { messages, scope, plantId });
  },
  /** Classify a leaf photograph. Returns 503 while no model is trained. */
  diagnosePlant: (plantId, image) => {
    const form = new FormData();
    form.append("image", image);
    return request(`/plants/${plantId}/diagnose`, {
      method: "POST",
      body: form
    });
  },
  // ── Weather ───────────────────────────────────────────────────────────────
  getWeatherMacro: () => request("/v1/weather/macro"),
  getWeatherAlert: () => request("/v1/weather/alert"),
  // ── Devices ───────────────────────────────────────────────────────────────
  listDevices: () => request("/b2b/devices"),
  createDevice: (node) => json("/b2b/devices", "POST", node),
  diagnoseDevice: (nodeId) => request(`/b2b/devices/${nodeId}/diagnose`, { method: "POST" }),
  orderProbes: () => request("/b2b/procurement", { method: "POST" }),
  requestMaintenance: () => request("/b2b/maintenance", { method: "POST" }),
  getTacticalLogs: () => request("/b2b/agents/log"),
  // ── Land and satellite ────────────────────────────────────────────────────
  listLandParcels: (params) => {
    const query = new URLSearchParams();
    if (params?.minPotential) query.set("min_potential", String(params.minPotential));
    if (params?.landCoverClass) query.set("land_cover_class", params.landCoverClass);
    const suffix = query.toString() ? `?${query}` : "";
    return request(`/b2b/land-parcels${suffix}`);
  },
  getLandCoverClasses: () => request("/b2b/land-cover-classes"),
  analyzeSatellite: (preRestoration, currentState) => {
    const form = new FormData();
    form.append("pre_restoration", preRestoration);
    form.append("current_state", currentState);
    return request("/b2b/satellite/analyze", {
      method: "POST",
      body: form
    });
  }
};
export {
  API_BASE_URL as A,
  api as a,
  ApiError as b
};
