// ---------------------------------------------------------------------------
// EventFlow AI — API client
//
// Thin wrapper around fetch() for talking to the FastAPI backend.
// Base URL is read from VITE_API_BASE_URL (see .env.example); it falls
// back to localhost:8000, which is FastAPI's default with `uvicorn app.main:app`.
// ---------------------------------------------------------------------------

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch (err) {
    throw new Error(
      `Could not reach the backend at ${API_BASE}. Is it running? (${err.message})`
    );
  }

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // response wasn't JSON — keep statusText
    }
    throw new Error(detail || `Request failed with status ${res.status}`);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  // List every event (id, name, venue, status) so the UI can offer a picker
  // instead of a raw numeric ID field.
  getEvents: () => request(`/api/events`),

  // Unified current state for an event: event, venue, zones, transport, conditions, incidents
  getState: (eventId) => request(`/api/events/${eventId}/state`),

  // Raw ML horizon predictions (10/20/30 min) per zone
  getPredictions: (eventId) => request(`/api/events/${eventId}/predictions`),

  // Per-zone risk scoring, built on top of predictions + live state
  getRisks: (eventId) => request(`/api/events/${eventId}/risks`),

  // Root-cause breakdown for one zone
  getCauses: (eventId, zoneId) => request(`/api/events/${eventId}/causes/${zoneId}`),

  // Ranked interventions (+ simulated baseline/impact) for the current highest-load zone
  getInterventions: (eventId) => request(`/api/events/${eventId}/interventions`),

  // What-if simulation for a specific zone + intervention
  runSimulation: (eventId, { zoneId, interventionId, durationMinutes = 30 }) =>
    request(
      `/api/events/${eventId}/simulation?zone_id=${zoneId}&intervention_id=${interventionId}&duration_minutes=${durationMinutes}`,
      { method: "POST" }
    ),

  // Record that the organizer applied a recommended intervention ("Apply" stage)
  applyIntervention: (eventId, { interventionId, approvedBy, actionDetails }) =>
    request(`/api/events/${eventId}/interventions/apply`, {
      method: "POST",
      body: JSON.stringify({
        intervention_id: interventionId,
        approved_by: approvedBy ?? null,
        action_details: actionDetails ?? null,
      }),
    }),

  // History of applied interventions for this event
  getAppliedInterventions: (eventId) => request(`/api/events/${eventId}/interventions/applied`),

  // Destination-wide accommodation availability + pressure (not event-scoped)
  getAccommodation: () => request(`/api/accommodation`),
};

export default api;
