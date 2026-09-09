import { useState, useMemo, useEffect, useCallback } from "react";
import {
  Activity, AlertTriangle, ArrowUpRight, BrainCircuit, BusFront, CloudSun,
  GitBranch, LayoutDashboard, MapPin, Route,
  SlidersHorizontal, TrendingUp, Users, X, Bell, ChevronDown, Search,
  CheckCircle2, Zap, Navigation2, Star, Clock, RefreshCw, WifiOff,
  Footprints, Building2, Home, Loader2, Flame, BedDouble, ArrowRight,
} from "lucide-react";
import {
  LineChart, Line, BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import { api } from "./api";

// ---------------------------------------------------------------------------
// Palette
// ---------------------------------------------------------------------------
const C = {
  bg: "#020509",
  panel: "rgba(6,22,28,0.62)",
  panelBorder: "rgba(45,212,191,0.35)",
  cyan: "#22e8f5",
  teal: "#2dd4bf",
  dim: "#8fb3ba",
  text: "#e7fdff",
  low: "#2dd4bf",
  medium: "#f5c542",
  high: "#ff9f45",
  critical: "#ff3d6e",
};
function riskColor(level) { return C[level] || C.dim; }

// Default event to load on first render. The backend has no "list events"
// endpoint, so this can be overridden from the event switcher in the top bar.
const DEFAULT_EVENT_ID = Number(import.meta.env.VITE_DEFAULT_EVENT_ID) || 1;

// Auto-refresh interval for live data (ms)
const REFRESH_INTERVAL_MS = 20000;

function riskLevel(pct) {
  if (pct >= 100) return "critical";
  if (pct >= 85) return "high";
  if (pct >= 60) return "medium";
  return "low";
}

// Backend risk levels are SAFE / WARNING / HIGH / CRITICAL — map them onto
// the low / medium / high / critical scale used throughout the UI.
function mapRiskLevel(level) {
  switch ((level || "").toUpperCase()) {
    case "SAFE": return "low";
    case "WARNING": return "medium";
    case "HIGH": return "high";
    case "CRITICAL": return "critical";
    default: return "low";
  }
}

// Same thresholds the backend's risk_service.py uses, so client-side
// projected scores (e.g. post-intervention) land on the same scale.
function scoreToRiskLevel(score) {
  if (score <= 30) return "low";
  if (score <= 60) return "medium";
  if (score <= 80) return "high";
  return "critical";
}

// pick the recommended gate: lowest load_percentage, i.e. least congested
function recommendedGate(zones) {
  return [...zones].sort((a, b) => a.load_percentage - b.load_percentage)[0];
}

// The backend has no venue-map coordinates for zones, so we lay them out on
// a fixed ring around the venue and cycle through it for any zone count.
const ZONE_LAYOUT = [
  { x: 18, y: 72 }, { x: 36, y: 84 }, { x: 50, y: 88 }, { x: 64, y: 84 },
  { x: 82, y: 72 }, { x: 88, y: 50 }, { x: 82, y: 28 }, { x: 64, y: 16 },
  { x: 50, y: 12 }, { x: 36, y: 16 }, { x: 18, y: 28 }, { x: 12, y: 50 },
];

// ---------------------------------------------------------------------------
// Transform raw backend payloads into the flat shape every page consumes
// ---------------------------------------------------------------------------
function buildZones(risks, state) {
  if (!risks?.zones) return [];
  const stateZones = state?.zones || {};
  let i = 0;
  return risks.zones
    .filter((z) => z.status !== "INSUFFICIENT_DATA")
    .map((z) => {
      const sZone = stateZones[String(z.zone_id)] || {};
      const pos = ZONE_LAYOUT[i % ZONE_LAYOUT.length];
      i += 1;
      const breachEta = z.prediction?.breach_eta ?? null;
      const queueMinutes = breachEta != null && breachEta > 0
        ? Math.max(1, Math.round(Math.min(breachEta, 45)))
        : 0;
      return {
        zone_id: String(z.zone_id),
        access_point_name: z.zone_name,
        capacity: z.capacity,
        current_count: z.current_count,
        load_percentage: z.current_load_percentage,
        arrival_rate: sZone.arrival_rate ?? 0,
        departure_rate: sZone.departure_rate ?? 0,
        risk_level: mapRiskLevel(z.risk_level),
        risk_score: z.risk_score,
        breach_eta: breachEta,
        hotspot: Boolean(z.hotspot),
        predictions: z.prediction?.predictions ?? null,
        reason_signals: z.reason_signals ?? [],
        queue_minutes: queueMinutes,
        map_position: pos,
      };
    });
}

function buildTransport(state) {
  const t = state?.transport || {};
  return Object.values(t).map((n) => {
    const load = n.load_percentage != null
      ? Math.round(n.load_percentage)
      : (n.capacity ? Math.round(((n.current_load || 0) / n.capacity) * 100) : 0);
    return {
      id: String(n.transport_node_id),
      name: n.node_name,
      node_type: n.node_type,
      load,
      status: n.status,
    };
  });
}

// ---------------------------------------------------------------------------
// Live data hook — pulls event state, risk scoring, and interventions from
// the FastAPI backend and keeps them fresh on an interval.
// ---------------------------------------------------------------------------
// Fetches the event list once (not polled — the list of events itself
// rarely changes mid-demo) so the top bar can offer a real dropdown instead
// of a raw numeric ID field.
function useEventList() {
  const [events, setEvents] = useState([]);
  useEffect(() => {
    let cancelled = false;
    api.getEvents()
      .then((res) => { if (!cancelled) setEvents(res?.events || []); })
      .catch(() => { if (!cancelled) setEvents([]); });
    return () => { cancelled = true; };
  }, []);
  return events;
}

function useEventData(eventId) {
  const [state, setState] = useState(null);
  const [risks, setRisks] = useState(null);
  const [interventions, setInterventions] = useState(null);
  const [accommodation, setAccommodation] = useState(null);
  const [appliedActions, setAppliedActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const load = useCallback(async () => {
    try {
      const [stateRes, risksRes] = await Promise.all([
        api.getState(eventId),
        api.getRisks(eventId),
      ]);
      setState(stateRes);
      setRisks(risksRes);

      // Interventions can legitimately be unavailable (e.g. no zone has
      // usable capacity/crowd data yet) — don't fail the whole page for it.
      try {
        setInterventions(await api.getInterventions(eventId));
      } catch {
        setInterventions(null);
      }

      // Accommodation covers the whole destination, not just this event —
      // treat it the same way: don't fail the page if it's unavailable.
      try {
        setAccommodation(await api.getAccommodation());
      } catch {
        setAccommodation(null);
      }

      try {
        const applied = await api.getAppliedInterventions(eventId);
        setAppliedActions(applied.applied_actions || []);
      } catch {
        setAppliedActions([]);
      }

      setError(null);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [eventId]);

  useEffect(() => {
    setLoading(true);
    setState(null);
    setRisks(null);
    setInterventions(null);
    setAccommodation(null);
    setAppliedActions([]);
    load();
    const id = setInterval(load, REFRESH_INTERVAL_MS);
    return () => clearInterval(id);
  }, [load]);

  return {
    state, risks, interventions, accommodation, appliedActions,
    loading, error, refresh: load, lastUpdated,
  };
}

// ---------------------------------------------------------------------------
// Animated cyberpunk city background
// ---------------------------------------------------------------------------
function seededRandom(seed) { let s = seed; return () => { s = (s * 9301 + 49297) % 233280; return s / 233280; }; }

function CityBackground() {
  const rand = seededRandom(42);
  const buildings = useMemo(() => {
    const arr = []; let x = 0; let i = 0;
    while (x < 1600) {
      const w = 40 + rand() * 70; const h = 90 + rand() * 260; const layer = i % 3;
      arr.push({ x, w, h, layer, seed: i }); x += w + 4 + rand() * 10; i++;
    }
    return arr;
  }, []);
  const windows = useMemo(() => {
    const arr = [];
    buildings.forEach((b, bi) => {
      const cols = Math.max(1, Math.floor(b.w / 14)); const rows = Math.max(2, Math.floor(b.h / 18));
      for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
        if (rand() > 0.55) continue;
        const hueRoll = rand();
        const color = hueRoll > 0.75 ? "#ff5fd6" : hueRoll > 0.45 ? "#22e8f5" : "#ffd166";
        arr.push({ x: b.x + 6 + c * 14, y: r * 17 + 8, bh: b.h, color, delay: rand() * 6, dur: 2 + rand() * 4, id: `${bi}-${r}-${c}` });
      }
    });
    return arr;
  }, [buildings]);
  const signs = useMemo(() => {
    const picks = [];
    buildings.forEach((b, i) => { if (i % 5 === 0 && b.h > 150) picks.push({ x: b.x + b.w * 0.15, y: 30 + rand() * 40, w: b.w * 0.7, h: 10 + rand() * 14, color: i % 2 === 0 ? "#ff2fb0" : "#22e8f5", delay: rand() * 3 }); });
    return picks;
  }, [buildings]);
  const cars = useMemo(() => Array.from({ length: 14 }, (_, i) => ({ id: i, lane: i % 2, y: i % 2 === 0 ? 3 : 13, delay: (i * 0.9) % 8, dur: 3.5 + (i % 4) * 0.6, color: i % 3 === 0 ? "#ff5fd6" : "#7cf6ff" })), []);

  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 0, overflow: "hidden", background: "linear-gradient(180deg,#050914 0%, #060c1c 45%, #030509 100%)" }}>
      <style>{`
        @keyframes flicker { 0%,100% { opacity: 0.15; } 45% { opacity: 0.15; } 50% { opacity: 0.95; } 55% { opacity: 0.2; } 60% { opacity: 0.9; } 90% { opacity: 0.9; } }
        @keyframes drift { 0% { transform: translateX(0); } 100% { transform: translateX(-800px); } }
        @keyframes carL { 0% { transform: translateX(-10%); opacity: 0; } 8% { opacity: 1; } 92% { opacity: 1; } 100% { transform: translateX(110%); opacity: 0; } }
        @keyframes carR { 0% { transform: translateX(110%); opacity: 0; } 8% { opacity: 1; } 92% { opacity: 1; } 100% { transform: translateX(-10%); opacity: 0; } }
        @keyframes billboardPulse { 0%,100% { opacity: 0.55; filter: brightness(0.9); } 50% { opacity: 1; filter: brightness(1.3); } }
        @keyframes blimpDrift { 0% { transform: translateX(-10vw); } 100% { transform: translateX(60vw); } }
      `}</style>
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse at 50% 30%, rgba(34,232,245,0.06), transparent 60%)" }} />
      <div style={{ position: "absolute", top: "8%", left: 0, animation: "blimpDrift 40s linear infinite", opacity: 0.5 }}>
        <div style={{ width: 46, height: 14, borderRadius: 10, background: "rgba(120,200,255,0.25)", border: "1px solid rgba(120,200,255,0.4)", boxShadow: "0 0 12px rgba(120,200,255,0.4)" }} />
      </div>
      {[0, 1].map((copy) => (
        <div key={copy} style={{ position: "absolute", bottom: 46, left: 0, width: 1600, height: 360, animation: "drift 90s linear infinite", animationDelay: copy === 1 ? "-45s" : "0s", transform: copy === 1 ? "translateX(800px)" : undefined }}>
          <svg width={1600} height={360} style={{ position: "absolute", bottom: 0, left: 0, overflow: "visible" }}>
            {buildings.map((b) => { const shade = b.layer === 0 ? "#0a1220" : b.layer === 1 ? "#0d1830" : "#111f38"; return <rect key={b.seed} x={b.x} y={360 - b.h} width={b.w} height={b.h} fill={shade} stroke="rgba(34,232,245,0.06)" />; })}
            {windows.map((w) => (<rect key={w.id} x={w.x} y={360 - w.bh + w.y} width={7} height={9} fill={w.color} style={{ animation: `flicker ${w.dur}s ease-in-out infinite`, animationDelay: `${w.delay}s`, filter: `drop-shadow(0 0 3px ${w.color})` }} />))}
            {signs.map((s, i) => (<rect key={i} x={s.x} y={360 - (s.y + s.h)} width={s.w} height={s.h} rx={2} fill={s.color} opacity={0.7} style={{ animation: "billboardPulse 2.6s ease-in-out infinite", animationDelay: `${s.delay}s`, filter: `drop-shadow(0 0 8px ${s.color})` }} />))}
          </svg>
        </div>
      ))}
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 46, background: "linear-gradient(180deg, #060a12, #010305)", borderTop: "1px solid rgba(34,232,245,0.08)" }}>
        {cars.map((c) => (<div key={c.id} style={{ position: "absolute", top: c.y, left: 0, width: "18%", height: 3, borderRadius: 3, background: `linear-gradient(${c.lane === 0 ? "90deg" : "270deg"}, transparent, ${c.color}, transparent)`, boxShadow: `0 0 8px ${c.color}`, animation: `${c.lane === 0 ? "carL" : "carR"} ${c.dur}s linear infinite`, animationDelay: `${c.delay}s` }} />))}
        <div style={{ position: "absolute", top: 20, left: 0, right: 0, height: 26, background: "linear-gradient(180deg, rgba(34,232,245,0.05), transparent)" }} />
      </div>
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse at 50% 40%, rgba(2,5,9,0.35), rgba(2,5,9,0.82) 75%)" }} />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Hologram shell primitives
// ---------------------------------------------------------------------------
function corner(pos) {
  const base = { position: "absolute", width: 12, height: 12, borderColor: C.cyan, opacity: 0.8 };
  const styles = {
    tl: { ...base, top: -1, left: -1, borderTop: "2px solid", borderLeft: "2px solid" },
    tr: { ...base, top: -1, right: -1, borderTop: "2px solid", borderRight: "2px solid" },
    bl: { ...base, bottom: -1, left: -1, borderBottom: "2px solid", borderLeft: "2px solid" },
    br: { ...base, bottom: -1, right: -1, borderBottom: "2px solid", borderRight: "2px solid" },
  };
  return styles[pos];
}
function HoloPanel({ children, style }) {
  return (
    <div style={{ position: "relative", background: C.panel, border: `1px solid ${C.panelBorder}`, borderRadius: 4, backdropFilter: "blur(10px)", boxShadow: "0 0 22px rgba(34,232,245,0.08), inset 0 0 30px rgba(34,232,245,0.03)", padding: 20, ...style }}>
      <span style={corner("tl")} /><span style={corner("tr")} /><span style={corner("bl")} /><span style={corner("br")} />
      {children}
    </div>
  );
}
function HoloLabel({ children }) { return <p style={{ fontSize: 10, letterSpacing: 2, color: C.teal, textTransform: "uppercase", opacity: 0.9 }}>{children}</p>; }
function HoloTitle({ children, size = 14 }) { return <h2 style={{ fontSize: size, fontWeight: 600, color: C.text, textShadow: "0 0 12px rgba(34,232,245,0.35)", letterSpacing: 0.5 }}>{children}</h2>; }
function RiskPill({ level }) {
  const col = riskColor(level);
  return <span style={{ fontSize: 9, fontWeight: 700, padding: "2px 8px", borderRadius: 20, letterSpacing: 1, color: col, border: `1px solid ${col}`, boxShadow: `0 0 8px ${col}55`, textTransform: "uppercase" }}>{level}</span>;
}
function StatCard({ icon: Icon, title, value, label }) {
  return (
    <HoloPanel>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ width: 34, height: 34, borderRadius: 8, background: "rgba(34,232,245,0.1)", border: `1px solid ${C.panelBorder}`, display: "flex", alignItems: "center", justifyContent: "center" }}><Icon size={16} color={C.cyan} /></div>
        <ArrowUpRight size={14} color={C.dim} />
      </div>
      <HoloLabel>{title}</HoloLabel>
      <h2 style={{ fontSize: 24, fontWeight: 700, color: C.text, marginTop: 4, textShadow: "0 0 10px rgba(34,232,245,0.3)" }}>{value}</h2>
      <p style={{ fontSize: 10, color: C.dim, marginTop: 2 }}>{label}</p>
    </HoloPanel>
  );
}
function PageHeader({ eyebrow, title, subtitle }) {
  return (
    <div style={{ marginBottom: 26 }}>
      <HoloLabel>{eyebrow}</HoloLabel>
      <h1 style={{ fontSize: 26, fontWeight: 700, color: C.text, marginTop: 6, textShadow: "0 0 18px rgba(34,232,245,0.4)", letterSpacing: 0.5 }}>{title}</h1>
      {subtitle && <p style={{ fontSize: 12.5, color: C.dim, marginTop: 6 }}>{subtitle}</p>}
    </div>
  );
}
function Row({ label, value, color }) {
  return <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, padding: "6px 0", borderBottom: "1px solid rgba(45,212,191,0.12)" }}><span style={{ color: C.dim }}>{label}</span><span style={{ color: color || C.text, fontWeight: 700 }}>{value}</span></div>;
}
function MiniMetric({ label, value }) {
  return <div style={{ background: "rgba(0,0,0,0.3)", borderRadius: 4, padding: "6px 8px", border: "1px solid rgba(45,212,191,0.15)" }}><p style={{ fontSize: 8.5, color: C.dim, letterSpacing: 1 }}>{label.toUpperCase()}</p><p style={{ fontSize: 13, fontWeight: 700, color: C.text }}>{value}</p></div>;
}
function EmptyPanel({ message }) {
  return (
    <HoloPanel style={{ maxWidth: 520 }}>
      <p style={{ fontSize: 13, color: C.dim, lineHeight: 1.6 }}>{message}</p>
    </HoloPanel>
  );
}

// ---------------------------------------------------------------------------
// Venue map (shared by both organizer + attendee, with an optional highlight)
// ---------------------------------------------------------------------------
function VenueMap({ zones, venueName, onSelect, selectedId, highlightId }) {
  const selectedZone = zones.find((z) => z.zone_id === selectedId);
  return (
    <div style={{ position: "relative", width: "100%", height: "100%", minHeight: 380, borderRadius: 4, overflow: "hidden", background: "rgba(1,3,6,0.7)", border: `1px solid ${C.panelBorder}` }}>
      <div style={{ position: "absolute", inset: 0, opacity: 0.15, backgroundImage: `linear-gradient(${C.cyan} 1px, transparent 1px), linear-gradient(90deg, ${C.cyan} 1px, transparent 1px)`, backgroundSize: "36px 36px" }} />
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(circle at 50% 55%, rgba(34,232,245,0.06), transparent 60%)" }} />
      <div style={{ position: "absolute", top: 14, left: 16, zIndex: 20 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}><MapPin size={13} color={C.cyan} /><span style={{ fontSize: 11, fontWeight: 700, color: C.text }}>{(venueName || "VENUE").toUpperCase()}</span></div>
        <p style={{ fontSize: 9, color: C.dim, marginTop: 2 }}>LIVE CROWD DENSITY // SCAN ACTIVE</p>
      </div>
      <div style={{ position: "absolute", left: "50%", top: "53%", transform: "translate(-50%,-50%)", width: "70%", height: "54%" }}>
        <div style={{ position: "absolute", inset: 0, borderRadius: "50%", border: "1.5px solid rgba(34,232,245,0.5)", boxShadow: "0 0 40px rgba(34,232,245,0.15) inset" }} />
        <div style={{ position: "absolute", inset: "8%", borderRadius: "50%", border: "1px solid rgba(45,212,191,0.35)" }} />
        <div style={{ position: "absolute", left: "50%", top: "50%", transform: "translate(-50%,-50%)", width: "38%", height: "30%", borderRadius: "45%", background: "rgba(45,212,191,0.08)", border: "1px solid rgba(45,212,191,0.4)", boxShadow: "0 0 30px rgba(45,212,191,0.15)" }} />
      </div>
      {zones.map((zone) => {
        const col = riskColor(zone.risk_level);
        const isHighlight = zone.zone_id === highlightId;
        const shortLabel = zone.access_point_name.length > 8
          ? zone.access_point_name.replace(/[^A-Za-z0-9]/g, "").slice(0, 3).toUpperCase()
          : zone.access_point_name.replace("Gate ", "G");
        return (
          <button key={zone.zone_id} onClick={() => onSelect && onSelect(zone.zone_id)} style={{ position: "absolute", left: `${zone.map_position.x}%`, top: `${zone.map_position.y}%`, transform: "translate(-50%,-50%)", background: "none", border: "none", cursor: onSelect ? "pointer" : "default" }}>
            <span style={{ position: "absolute", inset: -6, borderRadius: "50%", background: isHighlight ? C.cyan : col, opacity: 0.25, animation: "holoPing 1.8s infinite" }} />
            <span style={{ position: "relative", display: "flex", alignItems: "center", justifyContent: "center", width: isHighlight ? 40 : 34, height: isHighlight ? 40 : 34, borderRadius: "50%", background: "#020509", border: `2px solid ${isHighlight ? C.cyan : col}`, boxShadow: `0 0 14px ${isHighlight ? C.cyan : col}` }}>
              <span style={{ fontSize: 10, fontWeight: 800, color: isHighlight ? C.cyan : col }}>{shortLabel}</span>
            </span>
            {isHighlight && <Star size={12} color={C.cyan} style={{ position: "absolute", top: -14, left: "50%", transform: "translateX(-50%)" }} />}
          </button>
        );
      })}
      {selectedZone && (
        <div style={{ position: "absolute", bottom: 14, left: 14, right: 14, zIndex: 40, maxWidth: 300 }}>
          <HoloPanel style={{ padding: 14 }}>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <div><HoloLabel>Selected zone</HoloLabel><p style={{ fontSize: 13, fontWeight: 700, color: C.text, marginTop: 4 }}>{selectedZone.access_point_name}</p></div>
              <X size={15} color={C.dim} style={{ cursor: "pointer" }} onClick={() => onSelect(null)} />
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginTop: 10 }}>
              <MiniMetric label="Count" value={selectedZone.current_count} />
              <MiniMetric label="Capacity" value={selectedZone.capacity} />
              <MiniMetric label="Load" value={`${selectedZone.load_percentage}%`} />
              <MiniMetric label="ETA to breach" value={selectedZone.breach_eta != null ? `${Math.round(selectedZone.breach_eta)}m` : "—"} />
            </div>
          </HoloPanel>
        </div>
      )}
    </div>
  );
}

// ===========================================================================
// ORGANIZER PAGES
// ===========================================================================
// The end-to-end decision loop this platform runs, made visible so it reads
// as one connected system rather than a set of separate dashboards.
const DECISION_LOOP_STAGES = [
  { id: "monitor", label: "Monitor", hint: "Live state" },
  { id: "predict", label: "Predict", hint: "10/20/30m horizon" },
  { id: "detect", label: "Detect Risk", hint: "Zone risk score" },
  { id: "explain", label: "Explain", hint: "Root causes" },
  { id: "recommend", label: "Recommend", hint: "Ranked actions" },
  { id: "simulate", label: "Simulate", hint: "Before / after" },
  { id: "apply", label: "Apply", hint: "Organizer decision" },
  { id: "guide", label: "Guide", hint: "Attendee update" },
];
function DecisionLoop({ hasApplied }) {
  return (
    <HoloPanel style={{ marginBottom: 16 }}>
      <HoloLabel>How this dashboard works</HoloLabel>
      <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap", gap: 4, marginTop: 10 }}>
        {DECISION_LOOP_STAGES.map((stage, i) => {
          const dim = stage.id === "apply" && !hasApplied;
          return (
            <div key={stage.id} style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <div style={{ textAlign: "center", padding: "6px 9px", borderRadius: 4, background: dim ? "rgba(255,255,255,0.03)" : "rgba(34,232,245,0.08)", border: `1px solid ${dim ? "rgba(255,255,255,0.1)" : C.panelBorder}` }}>
                <p style={{ fontSize: 10, fontWeight: 700, color: dim ? C.dim : C.text }}>{stage.label}</p>
                <p style={{ fontSize: 8, color: C.dim, marginTop: 1 }}>{stage.hint}</p>
              </div>
              {i < DECISION_LOOP_STAGES.length - 1 && <ArrowRight size={11} color={C.dim} style={{ opacity: 0.5 }} />}
            </div>
          );
        })}
      </div>
    </HoloPanel>
  );
}

function OverviewPage({ zones, venue, eventInfo, incidents, appliedActions }) {
  const [selectedId, setSelectedId] = useState(zones[0]?.zone_id ?? null);
  const totalCount = zones.reduce((s, z) => s + (z.current_count || 0), 0);
  const totalCap = zones.reduce((s, z) => s + (z.capacity || 0), 0);
  const critical = zones.filter((z) => z.risk_level === "critical");
  const hotspots = zones.filter((z) => z.hotspot);
  const activeIncident = incidents?.[0];
  const criticalZone = critical[0];

  return (
    <div style={{ padding: 28 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 26, flexWrap: "wrap", gap: 12 }}>
        <div>
          <HoloLabel>Operations Dashboard</HoloLabel>
          <h1 style={{ fontSize: 26, fontWeight: 700, color: C.text, marginTop: 6, textShadow: "0 0 18px rgba(34,232,245,0.4)" }}>Event Overview</h1>
          <p style={{ fontSize: 12, color: C.dim, marginTop: 6 }}>{venue?.venue_name || "Venue"} · {eventInfo?.event_name || "Event"}</p>
        </div>
        <div style={{ textAlign: "right" }}>
          <HoloLabel>Event Status</HoloLabel>
          <div style={{ display: "flex", justifyContent: "flex-end", alignItems: "center", gap: 6, marginTop: 4 }}>
            <span style={{ width: 7, height: 7, borderRadius: "50%", background: criticalZone ? C.critical : C.teal, boxShadow: `0 0 8px ${criticalZone ? C.critical : C.teal}` }} />
            <span style={{ fontSize: 12, color: criticalZone ? C.critical : C.teal, fontWeight: 700, textTransform: "uppercase" }}>{criticalZone ? "critical" : (eventInfo?.status || "live")}</span>
          </div>
        </div>
      </div>
      <DecisionLoop hasApplied={appliedActions?.length > 0} />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", gap: 14 }}>
        <StatCard icon={Users} title="Live Attendance" value={totalCount.toLocaleString()} label="current venue count" />
        <StatCard icon={Activity} title="Venue Capacity" value={totalCap > 0 ? `${Math.round((totalCount / totalCap) * 100)}%` : "—"} label="current occupancy" />
        <StatCard icon={AlertTriangle} title="Active Alerts" value={String(critical.length).padStart(2, "0")} label="critical-risk zones" />
        <StatCard icon={Flame} title="Hotspots" value={String(hotspots.length).padStart(2, "0")} label="predicted to exceed 90% load" />
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 14, marginTop: 16 }}>
        <HoloPanel>
          <HoloTitle>Venue Intelligence</HoloTitle>
          <p style={{ fontSize: 11, color: C.dim, marginTop: 2 }}>Live crowd distribution across the venue</p>
          <div style={{ height: 400, marginTop: 14 }}><VenueMap zones={zones} venueName={venue?.venue_name} onSelect={setSelectedId} selectedId={selectedId} /></div>
        </HoloPanel>
        <HoloPanel>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <div><HoloTitle>Active Incident</HoloTitle><p style={{ fontSize: 11, color: C.dim, marginTop: 2 }}>System-reported status</p></div>
            <TrendingUp size={16} color={C.cyan} />
          </div>
          {activeIncident ? (
            <div style={{ marginTop: 18, padding: 14, borderRadius: 4, background: "rgba(255,61,110,0.08)", border: `1px solid ${C.critical}55` }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}><AlertTriangle size={14} color={C.critical} /><span style={{ fontSize: 10, fontWeight: 800, color: C.critical, letterSpacing: 1 }}>{(activeIncident.severity || "ACTIVE").toUpperCase()}</span></div>
              <p style={{ fontSize: 13, color: C.text, marginTop: 10, fontWeight: 600 }}>{activeIncident.incident_type || "Incident"}</p>
              <p style={{ fontSize: 11, color: C.dim, marginTop: 6, lineHeight: 1.5 }}>{activeIncident.description || "No further details reported."}</p>
            </div>
          ) : criticalZone ? (
            <div style={{ marginTop: 18, padding: 14, borderRadius: 4, background: "rgba(255,61,110,0.08)", border: `1px solid ${C.critical}55` }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}><AlertTriangle size={14} color={C.critical} /><span style={{ fontSize: 10, fontWeight: 800, color: C.critical, letterSpacing: 1 }}>HIGH SEVERITY</span></div>
              <p style={{ fontSize: 13, color: C.text, marginTop: 10, fontWeight: 600 }}>{criticalZone.access_point_name} congestion detected</p>
              <p style={{ fontSize: 11, color: C.dim, marginTop: 6, lineHeight: 1.5 }}>Arrival plaza load exceeds operating threshold.</p>
              <p style={{ fontSize: 10, color: C.dim, marginTop: 10, opacity: 0.7 }}>Zone: {criticalZone.zone_id}</p>
            </div>
          ) : <p style={{ fontSize: 12, color: C.dim, marginTop: 16 }}>No active incidents.</p>}
        </HoloPanel>
      </div>
    </div>
  );
}

function CrowdTooltip({ active, payload }) {
  if (!active || !payload || !payload.length) return null;

  const name = payload[0].payload.name;
  const load = payload[0].payload.load;
  const level = riskLevel(load);

  return (
    <div
      style={{
        background: "#020509",
        border: `1px solid ${C.panelBorder}`,
        borderRadius: 6,
        padding: "9px 12px",
        boxShadow: "0 4px 18px rgba(0,0,0,0.45)",
      }}
    >
      <div
        style={{
          fontWeight: 700,
          color: C.text,
          marginBottom: 5,
        }}
      >
        {name}
      </div>

      <div style={{ color: C.muted }}>
        Load:{" "}
        <span style={{ color: C.text, fontWeight: 700 }}>
          {load.toFixed(1)}%
        </span>
      </div>

      <div style={{ color: C.muted }}>
        Status:{" "}
        <span
          style={{
            color: riskColor(level),
            fontWeight: 700,
          }}
        >
          {level.toUpperCase()}
        </span>
      </div>
    </div>
  );
}

function CrowdPage({ zones }) {
  const sorted = [...zones].sort((a, b) => b.load_percentage - a.load_percentage);
  const chartData = zones.map((z) => ({ name: z.access_point_name, load: z.load_percentage }));
  return (
    <div style={{ padding: 28 }}>
      <PageHeader eyebrow="EventFlow AI" title="Crowd & Hotspots" subtitle="Zone-by-zone occupancy, ranked by current load" />
      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 14 }}>
        <HoloPanel>
          <HoloTitle>Load by access point</HoloTitle>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={chartData} barCategoryGap="25%" style={{ marginTop: 14 }}>
              <CartesianGrid stroke="rgba(45,212,191,0.12)" vertical={false} />
              <XAxis dataKey="name" stroke={C.dim} fontSize={11} />
              <YAxis stroke={C.dim} fontSize={11} />
              <Tooltip
                cursor={false}
                content={<CrowdTooltip />}
              />
              <Bar
                dataKey="load"
                radius={[5, 5, 0, 0]}
                barSize={28}
                maxBarSize={32}
              >
                {chartData.map((d, i) => (
                  <Cell
                    key={`cell-${i}`}
                    fill={["#2DD4BF", "#26B8AC", "#229E9A", "#1F8587"][i % 4]}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </HoloPanel>
        <HoloPanel>
          <HoloTitle>Hotspot ranking</HoloTitle>
          <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 10 }}>
            {sorted.map((z) => (
              <div key={z.zone_id} style={{ padding: 10, borderRadius: 4, background: "rgba(0,0,0,0.3)", border: "1px solid rgba(45,212,191,0.15)" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}><span style={{ fontSize: 12, color: C.text, fontWeight: 600 }}>{z.access_point_name}</span><RiskPill level={z.risk_level} /></div>
                <div style={{ height: 4, borderRadius: 4, background: "rgba(255,255,255,0.08)", marginTop: 8, overflow: "hidden" }}><div style={{ height: "100%", width: `${Math.min(100, z.load_percentage)}%`, background: riskColor(z.risk_level), boxShadow: `0 0 6px ${riskColor(z.risk_level)}` }} /></div>
                <p style={{ fontSize: 10, color: C.dim, marginTop: 6 }}>{z.current_count}/{z.capacity} · {z.load_percentage}% load</p>
              </div>
            ))}
          </div>
        </HoloPanel>
      </div>
    </div>
  );
}

const HORIZONS = [10, 20, 30];
function PredictionPage({ zones }) {
  const projection = useMemo(() => {
    const rows = [{ t: "Now" }];
    zones.forEach((z) => { rows[0][z.access_point_name] = z.load_percentage; });
    HORIZONS.forEach((h) => {
      const row = { t: `+${h}m` };
      zones.forEach((z) => {
        const p = z.predictions?.[String(h)];
        row[z.access_point_name] = p ? p.load_percentage : null;
      });
      rows.push(row);
    });
    return rows;
  }, [zones]);
  const colors = [C.cyan, "#8b7bff", C.critical, C.medium, C.teal, "#ff8fd6"];
  return (
    <div style={{ padding: 28 }}>
      <PageHeader eyebrow="EventFlow AI" title="Prediction + Risk" subtitle="ML-projected load per gate (10 / 20 / 30 minute horizons)" />
      <HoloPanel style={{ marginBottom: 14 }}>
        <HoloTitle>Projected load (%)</HoloTitle>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={projection} style={{ marginTop: 14 }}>
            <CartesianGrid stroke="rgba(45,212,191,0.12)" vertical={false} />
            <XAxis dataKey="t" stroke={C.dim} fontSize={11} />
            <YAxis stroke={C.dim} fontSize={11} />
            <Tooltip contentStyle={{ background: "#020509", border: `1px solid ${C.panelBorder}`, fontSize: 11, color: C.text }} />
            {zones.map((z, i) => <Line key={z.zone_id} type="monotone" dataKey={z.access_point_name} stroke={colors[i % colors.length]} strokeWidth={2} dot={false} connectNulls />)}
          </LineChart>
        </ResponsiveContainer>
      </HoloPanel>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(170px,1fr))", gap: 14 }}>
        {zones.map((z) => {
          const source = z.predictions?.["10"]?.prediction_source;
          return (
            <HoloPanel key={z.zone_id}>
              <div style={{ display: "flex", justifyContent: "space-between" }}><span style={{ fontSize: 12, fontWeight: 700, color: C.text }}>{z.access_point_name}</span><RiskPill level={z.risk_level} /></div>
              <p style={{ fontSize: 24, fontWeight: 700, color: C.text, marginTop: 10 }}>{z.risk_score}<span style={{ fontSize: 11, color: C.dim, fontWeight: 400 }}> /100</span></p>
              <p style={{ fontSize: 10, color: C.dim }}>risk score</p>
              <p style={{ fontSize: 10, color: C.dim, marginTop: 10 }}>{z.breach_eta != null ? `Breach ETA: ${Math.round(z.breach_eta)} min` : "No breach projected"}</p>
              {source && <p style={{ fontSize: 9, color: C.dim, marginTop: 4, opacity: 0.7 }}>Source: {source === "ML" ? "ML model" : "baseline rate"}</p>}
            </HoloPanel>
          );
        })}
      </div>
    </div>
  );
}

function RootCausePage({ interventionsData, zones }) {
  if (!interventionsData) {
    return (
      <div style={{ padding: 28 }}>
        <PageHeader eyebrow="EventFlow AI" title="Root Cause" subtitle="Explaining why the highest-load zone is under pressure" />
        <EmptyPanel message="Root-cause analysis isn't available right now — no zone currently has enough live crowd data." />
      </div>
    );
  }
  const { affected_zone, risk, root_causes } = interventionsData;
  const zoneDetail = zones.find((z) => z.zone_id === String(affected_zone.zone_id));
  return (
    <div style={{ padding: 28 }}>
      <PageHeader eyebrow="EventFlow AI" title="Root Cause" subtitle="Explaining why the highest-load zone is under pressure" />
      <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: 14 }}>
        <HoloPanel>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}><GitBranch size={15} color={C.cyan} /><span style={{ fontSize: 13, fontWeight: 700, color: C.text }}>{affected_zone.zone_name}</span></div>
          <div style={{ marginTop: 10 }}><RiskPill level={mapRiskLevel(risk.risk_level)} /></div>
          {zoneDetail && (
            <>
              <div style={{ marginTop: 12 }}><HoloLabel>Occupancy</HoloLabel><p style={{ fontSize: 18, fontWeight: 700, color: C.text }}>{zoneDetail.current_count?.toLocaleString()} / {zoneDetail.capacity?.toLocaleString()}</p></div>
              <div style={{ marginTop: 10 }}><HoloLabel>Load</HoloLabel><p style={{ fontSize: 18, fontWeight: 700, color: C.text }}>{zoneDetail.load_percentage}%</p></div>
            </>
          )}
          <div style={{ marginTop: 10 }}><HoloLabel>Risk score</HoloLabel><p style={{ fontSize: 18, fontWeight: 700, color: C.text }}>{risk.risk_score} / 100</p></div>
        </HoloPanel>
        <HoloPanel>
          <HoloTitle>Contributing factors</HoloTitle>
          <div style={{ marginTop: 14, display: "flex", flexDirection: "column", gap: 14 }}>
            {root_causes.length === 0 && <p style={{ fontSize: 12, color: C.dim }}>No single factor dominates — risk is currently balanced across signals.</p>}
            {root_causes.map((c, i) => (
              <div key={c.factor} style={{ display: "flex", gap: 10 }}>
                <span style={{ fontSize: 11, color: C.dim, width: 18 }}>{String(i + 1).padStart(2, "0")}</span>
                <div>
                  <p style={{ fontSize: 13, color: C.text }}>{c.cause}</p>
                  <p style={{ fontSize: 11, color: C.dim, marginTop: 2 }}>{c.factor.replace(/_/g, " ")} · severity {(c.severity * 100).toFixed(0)}%</p>
                </div>
              </div>
            ))}
          </div>
        </HoloPanel>
      </div>
    </div>
  );
}

function InterventionsPage({ eventId, interventionsData, appliedActions, onApplied }) {
  const [applying, setApplying] = useState(false);
  const [applyError, setApplyError] = useState(null);

  if (!interventionsData || !interventionsData.recommended_intervention) {
    return (
      <div style={{ padding: 28 }}>
        <PageHeader eyebrow="EventFlow AI" title="Interventions" subtitle="AI-recommended actions for the current highest-risk zone" />
        <EmptyPanel message="No interventions are configured for this event, or no zone currently has enough live data to recommend one." />
      </div>
    );
  }
  const rec = interventionsData.recommended_intervention;
  const zoneName = interventionsData.affected_zone.zone_name;
  const postLevel = scoreToRiskLevel(rec.estimated_post_risk);
  const alreadyApplied = appliedActions?.some((a) => a.intervention_id === rec.intervention_id);

  const handleApply = async () => {
    setApplying(true);
    setApplyError(null);
    try {
      await api.applyIntervention(eventId, { interventionId: rec.intervention_id, approvedBy: "Organizer" });
      await onApplied();
    } catch (err) {
      setApplyError(err.message);
    } finally {
      setApplying(false);
    }
  };

  return (
    <div style={{ padding: 28 }}>
      <PageHeader eyebrow="EventFlow AI" title="Interventions" subtitle="AI-recommended actions for the current highest-risk zone" />
      <HoloPanel style={{ maxWidth: 560 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}><Zap size={15} color={C.cyan} /><span style={{ fontSize: 11, fontWeight: 800, color: C.cyan, letterSpacing: 1.5 }}>AI RECOMMENDATION — {zoneName}</span></div>
        <p style={{ fontSize: 13, fontWeight: 700, color: C.text }}>{rec.intervention_name}</p>
        <p style={{ fontSize: 13, color: C.text, lineHeight: 1.6, marginTop: 6 }}>{rec.description || "No description provided."}</p>
        {rec.reason && <p style={{ fontSize: 11, color: C.dim, marginTop: 10 }}>{rec.reason}</p>}
        <p style={{ fontSize: 11, color: C.dim, marginTop: 12 }}>
          Expected risk change: <span style={{ color: riskColor(mapRiskLevel(interventionsData.current_risk_level)) }}>{interventionsData.current_risk_level}</span>
          {" "}→{" "}
          <span style={{ color: riskColor(postLevel) }}>{postLevel.toUpperCase()}</span>
          {" "}({rec.estimated_post_risk} / 100)
        </p>
        <p style={{ fontSize: 11, color: C.dim, marginTop: 4 }}>Effectiveness score: {Math.round(rec.effectiveness_score * 100)}%</p>
        <button onClick={handleApply} disabled={alreadyApplied || applying} style={{ marginTop: 18, display: "inline-flex", alignItems: "center", gap: 8, padding: "10px 18px", borderRadius: 4, fontSize: 12, fontWeight: 700, border: `1px solid ${alreadyApplied ? C.teal : C.cyan}`, background: alreadyApplied ? "rgba(45,212,191,0.08)" : "rgba(34,232,245,0.1)", color: alreadyApplied ? C.teal : C.cyan, cursor: alreadyApplied || applying ? "default" : "pointer", boxShadow: `0 0 14px ${alreadyApplied ? C.teal : C.cyan}44`, opacity: applying ? 0.6 : 1 }}>
          {alreadyApplied ? <><CheckCircle2 size={14} /> Intervention applied</> : applying ? <><Loader2 size={14} style={{ animation: "spin 1s linear infinite" }} /> Applying…</> : "Apply intervention"}
        </button>
        {applyError && <p style={{ fontSize: 11, color: C.critical, marginTop: 8 }}>{applyError}</p>}
      </HoloPanel>
      {appliedActions?.length > 0 && (
        <HoloPanel style={{ maxWidth: 560, marginTop: 14 }}>
          <HoloTitle size={12}>Applied history — this event</HoloTitle>
          <div style={{ marginTop: 10, display: "flex", flexDirection: "column", gap: 8 }}>
            {appliedActions.slice(0, 5).map((a) => (
              <div key={a.action_id} style={{ display: "flex", justifyContent: "space-between", fontSize: 11, padding: "6px 0", borderBottom: "1px solid rgba(45,212,191,0.12)" }}>
                <span style={{ color: C.dim, display: "flex", alignItems: "center", gap: 6 }}><CheckCircle2 size={11} color={C.teal} /> Intervention #{a.intervention_id}</span>
                <span style={{ color: C.text }}>{new Date(a.applied_at).toLocaleTimeString()}</span>
              </div>
            ))}
          </div>
        </HoloPanel>
      )}
      {interventionsData.interventions.length > 1 && (
        <HoloPanel style={{ maxWidth: 560, marginTop: 14 }}>
          <HoloTitle size={12}>Other ranked options</HoloTitle>
          <div style={{ marginTop: 10, display: "flex", flexDirection: "column", gap: 8 }}>
            {interventionsData.interventions.slice(1).map((iv) => (
              <div key={iv.intervention_id} style={{ display: "flex", justifyContent: "space-between", fontSize: 11, padding: "6px 0", borderBottom: "1px solid rgba(45,212,191,0.12)" }}>
                <span style={{ color: C.dim }}>#{iv.rank} {iv.intervention_name}</span>
                <span style={{ color: C.text }}>{Math.round(iv.effectiveness_score * 100)}% effective</span>
              </div>
            ))}
          </div>
        </HoloPanel>
      )}
    </div>
  );
}

const SIMULATION_DURATIONS = [10, 20, 30, 45, 60];

function SimulationPage({ eventId, interventionsData, appliedActions }) {
  const rec = interventionsData?.recommended_intervention;
  const options = interventionsData?.interventions || [];
  const zoneId = interventionsData?.affected_zone?.zone_id;
  const zoneName = interventionsData?.affected_zone?.zone_name;

  const [interventionId, setInterventionId] = useState(rec?.intervention_id ?? null);
  const [duration, setDuration] = useState(30);
  const [live, setLive] = useState(null); // result of a user-run simulation
  const [running, setRunning] = useState(false);
  const [runError, setRunError] = useState(null);

  // Re-anchor to the current top-risk zone's recommendation whenever the
  // underlying data changes (new poll, or a different event selected).
  useEffect(() => {
    setInterventionId(rec?.intervention_id ?? null);
    setLive(null);
    setRunError(null);
  }, [rec?.intervention_id, zoneId]);

  const runLive = useCallback(async (ivId, mins) => {
    if (!zoneId || !ivId) return;
    setRunning(true);
    setRunError(null);
    try {
      const res = await api.runSimulation(eventId, { zoneId, interventionId: ivId, durationMinutes: mins });
      setLive(res);
    } catch (err) {
      setRunError(err.message);
    } finally {
      setRunning(false);
    }
  }, [eventId, zoneId]);

  if (!interventionsData || !rec) {
    return (
      <div style={{ padding: 28 }}>
        <PageHeader eyebrow="EventFlow AI" title="What-if Simulation" subtitle="Comparing current state vs. a simulated intervention" />
        <EmptyPanel message="No simulation is available right now — no zone currently has both an intervention and enough live data." />
      </div>
    );
  }

  // Show the live, user-run result once one exists; otherwise fall back to
  // the bundled baseline comparison for the top-ranked intervention so the
  // page never opens empty.
  const baseline = live ? live.simulation.baseline : rec.baseline;
  const result = live ? live.simulation.intervention : rec.intervention_result;
  const impact = live ? live.simulation.impact : rec.impact;
  const interventionName = live ? live.intervention.intervention_name : rec.intervention_name;

  return (
    <div style={{ padding: 28 }}>
      <PageHeader eyebrow="EventFlow AI" title="What-if Simulation" subtitle={`Test any ranked intervention at ${zoneName} before applying it`} />
      {options.length > 0 && (
        <HoloPanel style={{ maxWidth: 560, marginBottom: 14 }}>
          <HoloLabel>Choose what to test</HoloLabel>
          <div style={{ display: "flex", gap: 10, marginTop: 10, flexWrap: "wrap" }}>
            <select
              value={interventionId ?? ""}
              onChange={(e) => setInterventionId(parseInt(e.target.value, 10))}
              style={{ flex: 1, minWidth: 200, background: "rgba(0,0,0,0.4)", border: `1px solid ${C.panelBorder}`, borderRadius: 4, color: C.text, fontSize: 12, padding: "8px 8px" }}
            >
              {options.map((o) => (
                <option key={o.intervention_id} value={o.intervention_id} style={{ background: C.bg }}>
                  #{o.rank} {o.intervention_name}
                </option>
              ))}
            </select>
            <select
              value={duration}
              onChange={(e) => setDuration(parseInt(e.target.value, 10))}
              style={{ background: "rgba(0,0,0,0.4)", border: `1px solid ${C.panelBorder}`, borderRadius: 4, color: C.text, fontSize: 12, padding: "8px 8px" }}
            >
              {SIMULATION_DURATIONS.map((m) => <option key={m} value={m} style={{ background: C.bg }}>{m} min</option>)}
            </select>
            <button
              onClick={() => runLive(interventionId, duration)}
              disabled={running || !interventionId}
              style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "8px 16px", borderRadius: 4, fontSize: 12, fontWeight: 700, border: `1px solid ${C.cyan}`, background: "rgba(34,232,245,0.1)", color: C.cyan, cursor: running ? "default" : "pointer", opacity: running ? 0.6 : 1 }}
            >
              {running ? <><Loader2 size={13} style={{ animation: "spin 1s linear infinite" }} /> Simulating…</> : "Run simulation"}
            </button>
          </div>
          {runError && <p style={{ fontSize: 11, color: C.critical, marginTop: 8 }}>{runError}</p>}
          {!live && <p style={{ fontSize: 10.5, color: C.dim, marginTop: 8 }}>Showing the pre-computed comparison for the top-ranked option below — pick a different intervention or duration and run it to test something else.</p>}
        </HoloPanel>
      )}
      <p style={{ fontSize: 12, color: C.dim, marginBottom: 10 }}>
        Comparing current state vs. <span style={{ color: C.text, fontWeight: 600 }}>"{interventionName}"</span>
        {live ? ` over ${live.simulation.duration_minutes} min` : ""}
      </p>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, maxWidth: 560 }}>
        <HoloPanel>
          <HoloLabel>Baseline (no action)</HoloLabel>
          <div style={{ marginTop: 8 }}>
            <Row label="Projected load" value={`${baseline.projected_load_percentage}%`} />
            <Row label="Projected count" value={Math.round(baseline.projected_count).toLocaleString()} />
            <Row label="Over capacity" value={baseline.over_capacity ? "Yes" : "No"} color={baseline.over_capacity ? C.critical : C.teal} />
          </div>
        </HoloPanel>
        <HoloPanel>
          <HoloLabel>With intervention</HoloLabel>
          <div style={{ marginTop: 8 }}>
            <Row label="Projected load" value={`${result.projected_load_percentage}%`} />
            <Row label="Projected count" value={Math.round(result.projected_count).toLocaleString()} />
            <Row label="Over capacity" value={result.over_capacity ? "Yes" : "No"} color={result.over_capacity ? C.critical : C.teal} />
          </div>
        </HoloPanel>
      </div>
      <p style={{ fontSize: 13, color: C.teal, marginTop: 16, display: "flex", alignItems: "center", gap: 8 }}>
        <TrendingUp size={15} /> Predicted congestion reduction: {impact.improvement_percentage}% ({impact.crowd_reduction} fewer people, {impact.load_reduction_percentage_points} pts lower load)
      </p>
      {!live && rec.simulation_outcome && <p style={{ fontSize: 11, color: C.dim, marginTop: 8 }}>{rec.simulation_outcome}</p>}
      {appliedActions?.some((a) => a.intervention_id === (live ? live.intervention.intervention_id : rec.intervention_id)) && <p style={{ fontSize: 11, color: C.cyan, marginTop: 10 }}>This intervention has already been applied via Interventions.</p>}
    </div>
  );
}

function TransportPage({ transport }) {
  if (!transport.length) {
    return (
      <div style={{ padding: 28 }}>
        <PageHeader eyebrow="EventFlow AI" title="Transport" subtitle="Load across transit nodes feeding the venue" />
        <EmptyPanel message="No transport node data is available for this venue." />
      </div>
    );
  }
  return (
    <div style={{ padding: 28 }}>
      <PageHeader eyebrow="EventFlow AI" title="Transport" subtitle="Load across transit nodes feeding the venue" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 14 }}>
        {transport.map((n) => {
          const level = riskLevel(n.load);
          return (
            <HoloPanel key={n.id}>
              <div style={{ display: "flex", justifyContent: "space-between" }}><div style={{ display: "flex", alignItems: "center", gap: 8 }}><BusFront size={15} color={C.cyan} /><span style={{ fontSize: 12, color: C.text }}>{n.name}</span></div><RiskPill level={level} /></div>
              <div style={{ height: 4, borderRadius: 4, background: "rgba(255,255,255,0.08)", marginTop: 14, overflow: "hidden" }}><div style={{ height: "100%", width: `${Math.min(100, n.load)}%`, background: riskColor(level), boxShadow: `0 0 6px ${riskColor(level)}` }} /></div>
              <p style={{ fontSize: 10, color: C.dim, marginTop: 8 }}>{n.load}% of nominal capacity{n.status ? ` · ${n.status}` : ""}</p>
            </HoloPanel>
          );
        })}
      </div>
    </div>
  );
}

function ConditionsPage({ zones, conditions, incidents }) {
  const elevatedZones = zones.filter((z) => z.risk_level !== "low");
  return (
    <div style={{ padding: 28 }}>
      <PageHeader eyebrow="EventFlow AI" title="Conditions / Incidents" subtitle="Weather context and the current incident log" />
      <HoloPanel style={{ maxWidth: 320, marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}><CloudSun size={15} color={C.cyan} /><span style={{ fontSize: 12, color: C.text }}>Weather</span></div>
        {conditions ? (
          <>
            <p style={{ fontSize: 18, fontWeight: 700, color: C.text, marginTop: 8 }}>
              {conditions.weather_type || "Unknown"}{conditions.temperature != null ? `, ${conditions.temperature}°C` : ""}
            </p>
            {conditions.severity && <div style={{ marginTop: 6 }}><RiskPill level={mapRiskLevel(conditions.severity)} /></div>}
          </>
        ) : <p style={{ fontSize: 13, color: C.dim, marginTop: 8 }}>No weather data reported.</p>}
      </HoloPanel>
      <HoloTitle size={12}>Reported incidents</HoloTitle>
      <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 10, marginBottom: 20 }}>
        {(!incidents || incidents.length === 0) && <p style={{ color: C.dim, fontSize: 13 }}>No active incidents.</p>}
        {incidents?.map((inc) => (
          <HoloPanel key={inc.incident_id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: 14 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <AlertTriangle size={15} color={C.high} />
              <div><p style={{ fontSize: 12, color: C.text }}>{inc.incident_type}</p><p style={{ fontSize: 10, color: C.dim, marginTop: 2 }}>{inc.description}</p></div>
            </div>
            {inc.severity && <RiskPill level={mapRiskLevel(inc.severity)} />}
          </HoloPanel>
        ))}
      </div>
      <HoloTitle size={12}>Elevated-risk zones</HoloTitle>
      <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 10 }}>
        {elevatedZones.length === 0 && <p style={{ color: C.dim, fontSize: 13 }}>All zones nominal.</p>}
        {elevatedZones.map((z) => (
          <HoloPanel key={z.zone_id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: 14 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <AlertTriangle size={15} color={z.risk_level === "critical" ? C.critical : C.high} />
              <div><p style={{ fontSize: 12, color: C.text }}>{z.access_point_name} — elevated load</p><p style={{ fontSize: 10, color: C.dim, marginTop: 2 }}>{z.load_percentage}% load{z.breach_eta != null ? ` · breach in ${Math.round(z.breach_eta)}m` : ""}</p></div>
            </div>
            <RiskPill level={z.risk_level} />
          </HoloPanel>
        ))}
      </div>
    </div>
  );
}

function AccommodationPage({ accommodation }) {
  if (!accommodation || !accommodation.accommodation?.length) {
    return (
      <div style={{ padding: 28 }}>
        <PageHeader eyebrow="EventFlow AI" title="Accommodation" subtitle="Destination-wide lodging availability and pressure" />
        <EmptyPanel message="No accommodation data is available right now." />
      </div>
    );
  }
  const { accommodation: zones, recommended } = accommodation;
  return (
    <div style={{ padding: 28 }}>
      <PageHeader eyebrow="EventFlow AI" title="Accommodation" subtitle="Destination-wide lodging availability and pressure — helps distribute visitors beyond the venue itself" />
      {recommended?.length > 0 && (
        <HoloPanel style={{ marginBottom: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}><BedDouble size={15} color={C.cyan} /><span style={{ fontSize: 11, fontWeight: 800, color: C.cyan, letterSpacing: 1.5 }}>LEAST-PRESSURED, RECOMMEND FIRST</span></div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", gap: 10 }}>
            {recommended.map((a) => (
              <div key={a.accommodation_id} style={{ padding: 10, borderRadius: 4, background: "rgba(45,212,191,0.06)", border: "1px solid rgba(45,212,191,0.25)" }}>
                <p style={{ fontSize: 12, fontWeight: 700, color: C.text }}>{a.name}</p>
                <p style={{ fontSize: 10, color: C.dim, marginTop: 4 }}>{a.occupancy_percentage}% occupied · {a.available_units} units open</p>
              </div>
            ))}
          </div>
        </HoloPanel>
      )}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 14 }}>
        {zones.map((a) => {
          const level = mapRiskLevel(a.pressure_level);
          return (
            <HoloPanel key={a.accommodation_id}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}><BedDouble size={15} color={C.cyan} /><span style={{ fontSize: 12, color: C.text }}>{a.name}</span></div>
                <RiskPill level={level} />
              </div>
              <p style={{ fontSize: 10, color: C.dim, marginTop: 6 }}>{a.accommodation_type || "Lodging"}</p>
              <p style={{ fontSize: 20, fontWeight: 700, color: C.text, marginTop: 10 }}>{a.occupancy_percentage != null ? `${a.occupancy_percentage}%` : "—"}</p>
              <p style={{ fontSize: 10, color: C.dim }}>occupied</p>
              <div style={{ height: 4, borderRadius: 4, background: "rgba(255,255,255,0.08)", marginTop: 10, overflow: "hidden" }}><div style={{ height: "100%", width: `${Math.min(100, a.occupancy_percentage || 0)}%`, background: riskColor(level), boxShadow: `0 0 6px ${riskColor(level)}` }} /></div>
              <p style={{ fontSize: 10, color: C.dim, marginTop: 8 }}>{a.available_units ?? 0} units available{a.status ? ` · ${a.status}` : ""}</p>
            </HoloPanel>
          );
        })}
      </div>
    </div>
  );
}

// ===========================================================================
// ATTENDEE PAGES  (Home, Live Map, Gate Status, My Route, Transport, Alerts)
// ===========================================================================
function AttendeeHomePage({ zones, eventInfo, venue }) {
  const rec = recommendedGate(zones);
  const critical = zones.filter((z) => z.risk_level === "critical" || z.risk_level === "high");
  return (
    <div style={{ padding: 28 }}>
      <PageHeader eyebrow={eventInfo?.event_name || "Event"} title={venue?.venue_name || "Venue"} subtitle={venue?.address || eventInfo?.status || ""} />
      <HoloPanel style={{ maxWidth: 480, marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}><Star size={16} color={C.cyan} /><span style={{ fontSize: 11, fontWeight: 800, letterSpacing: 1.5, color: C.cyan }}>RECOMMENDED FOR YOU</span></div>
        <p style={{ fontSize: 20, fontWeight: 700, color: C.text, marginTop: 10 }}>Use {rec.access_point_name}</p>
        <p style={{ fontSize: 12, color: C.dim, marginTop: 6 }}>{rec.load_percentage}% loaded{rec.queue_minutes > 0 ? ` · queue ~${rec.queue_minutes} min` : ""}</p>
      </HoloPanel>
      {critical.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: 10, maxWidth: 480 }}>
          {critical.map((z) => (
            <HoloPanel key={z.zone_id} style={{ padding: 14, display: "flex", alignItems: "center", gap: 10 }}>
              <AlertTriangle size={16} color={riskColor(z.risk_level)} />
              <p style={{ fontSize: 12.5, color: C.text }}>⚠️ {z.access_point_name} is crowded — avoid if possible</p>
            </HoloPanel>
          ))}
        </div>
      )}
    </div>
  );
}
function AttendeeMapPage({ zones, venue }) {
  const [selectedId, setSelectedId] = useState(null);
  const rec = recommendedGate(zones);
  return (
    <div style={{ padding: 28 }}>
      <PageHeader eyebrow="Live Map" title="Venue Map" subtitle="Gates, zones and your recommended route, updated live" />
      <HoloPanel><div style={{ height: 440 }}><VenueMap zones={zones} venueName={venue?.venue_name} onSelect={setSelectedId} selectedId={selectedId} highlightId={rec.zone_id} /></div></HoloPanel>
    </div>
  );
}
function AttendeeGateStatusPage({ zones }) {
  const rec = recommendedGate(zones);
  return (
    <div style={{ padding: 28 }}>
      <PageHeader eyebrow="Attendee" title="Gate Status" subtitle="Live occupancy and queue time at every gate" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 14 }}>
        {zones.map((z) => {
          const isRec = z.zone_id === rec.zone_id;
          return (
            <HoloPanel key={z.zone_id} style={isRec ? { border: `1px solid ${C.cyan}`, boxShadow: `0 0 22px ${C.cyan}33` } : {}}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: 13, fontWeight: 700, color: C.text, display: "flex", alignItems: "center", gap: 6 }}>{z.access_point_name} {isRec && <Star size={12} color={C.cyan} />}</span>
                <RiskPill level={z.risk_level} />
              </div>
              <p style={{ fontSize: 22, fontWeight: 700, color: C.text, marginTop: 10 }}>{z.load_percentage}%</p>
              <p style={{ fontSize: 10, color: C.dim }}>loaded</p>
              <p style={{ fontSize: 11, color: C.dim, marginTop: 8, display: "flex", alignItems: "center", gap: 5 }}><Clock size={11} /> {z.queue_minutes > 0 ? `Queue ~${z.queue_minutes} min` : "No queue"}</p>
              {isRec && <p style={{ fontSize: 10.5, color: C.cyan, marginTop: 8, fontWeight: 700 }}>RECOMMENDED</p>}
            </HoloPanel>
          );
        })}
      </div>
    </div>
  );
}
function AttendeeRoutePage({ zones }) {
  const rec = recommendedGate(zones);
  const worst = [...zones].sort((a, b) => b.load_percentage - a.load_percentage)[0];
  return (
    <div style={{ padding: 28 }}>
      <PageHeader eyebrow="My Route" title="Recommended Route" subtitle="Personalized guidance based on live gate conditions" />
      <HoloPanel style={{ maxWidth: 480 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}><Navigation2 size={16} color={C.cyan} /><span style={{ fontSize: 18, fontWeight: 700, color: C.text }}>Go to {rec.access_point_name}</span></div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginTop: 14 }}>
          <MiniMetric label="Load" value={`${rec.load_percentage}%`} />
          <MiniMetric label="Queue" value={rec.queue_minutes > 0 ? `${rec.queue_minutes} min` : "None"} />
        </div>
        <div style={{ marginTop: 14, padding: 12, borderRadius: 4, background: "rgba(0,0,0,0.3)", border: "1px solid rgba(45,212,191,0.15)" }}>
          <HoloLabel>Why this gate?</HoloLabel>
          <p style={{ fontSize: 12, color: C.text, marginTop: 6, lineHeight: 1.5 }}>
            {worst.zone_id !== rec.zone_id
              ? `${worst.access_point_name} has high crowd pressure${worst.queue_minutes > 0 ? ` and an estimated ${worst.queue_minutes}-minute queue` : ""}. ${rec.access_point_name} is currently the least congested option.`
              : `${rec.access_point_name} is currently the least congested gate at the venue.`}
          </p>
        </div>
        <div style={{ marginTop: 14, display: "flex", alignItems: "center", gap: 6 }}>
          <Footprints size={13} color={C.dim} />
          <p style={{ fontSize: 11, color: C.dim }}>Live guidance updates automatically as conditions change.</p>
        </div>
      </HoloPanel>
    </div>
  );
}
function AttendeeTransportPage({ transport }) {
  if (!transport.length) {
    return (
      <div style={{ padding: 28 }}>
        <PageHeader eyebrow="Attendee" title="Transport" subtitle="Status of transit options serving the venue" />
        <EmptyPanel message="No transport node data is available for this venue." />
      </div>
    );
  }
  return (
    <div style={{ padding: 28 }}>
      <PageHeader eyebrow="Attendee" title="Transport" subtitle="Status of transit options serving the venue" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 14 }}>
        {transport.map((n) => {
          const level = riskLevel(n.load);
          return (
            <HoloPanel key={n.id}>
              <div style={{ display: "flex", justifyContent: "space-between" }}><div style={{ display: "flex", alignItems: "center", gap: 8 }}><BusFront size={15} color={C.cyan} /><span style={{ fontSize: 12, color: C.text }}>{n.name}</span></div><RiskPill level={level} /></div>
              <p style={{ fontSize: 20, fontWeight: 700, color: C.text, marginTop: 10 }}>{n.load}%</p>
              <p style={{ fontSize: 10, color: C.dim }}>capacity{n.status ? ` · ${n.status}` : ""}</p>
            </HoloPanel>
          );
        })}
      </div>
    </div>
  );
}
function AttendeeStayPage({ accommodation }) {
  if (!accommodation || !accommodation.accommodation?.length) {
    return (
      <div style={{ padding: 28 }}>
        <PageHeader eyebrow="Attendee" title="Where to Stay" subtitle="Lodging options across the destination, ranked by availability" />
        <EmptyPanel message="No accommodation data is available right now." />
      </div>
    );
  }
  const { recommended, accommodation: zones } = accommodation;
  return (
    <div style={{ padding: 28 }}>
      <PageHeader eyebrow="Attendee" title="Where to Stay" subtitle="Lodging options across the destination, ranked by availability" />
      {recommended?.length > 0 && (
        <HoloPanel style={{ maxWidth: 480, marginBottom: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}><Star size={16} color={C.cyan} /><span style={{ fontSize: 11, fontWeight: 800, letterSpacing: 1.5, color: C.cyan }}>BEST AVAILABILITY RIGHT NOW</span></div>
          <p style={{ fontSize: 18, fontWeight: 700, color: C.text, marginTop: 10 }}>{recommended[0].name}</p>
          <p style={{ fontSize: 12, color: C.dim, marginTop: 4 }}>{recommended[0].occupancy_percentage}% occupied · {recommended[0].available_units} units open</p>
        </HoloPanel>
      )}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(200px,1fr))", gap: 14 }}>
        {zones.map((a) => {
          const level = mapRiskLevel(a.pressure_level);
          return (
            <HoloPanel key={a.accommodation_id}>
              <div style={{ display: "flex", justifyContent: "space-between" }}><span style={{ fontSize: 12, color: C.text }}>{a.name}</span><RiskPill level={level} /></div>
              <p style={{ fontSize: 18, fontWeight: 700, color: C.text, marginTop: 8 }}>{a.occupancy_percentage != null ? `${a.occupancy_percentage}%` : "—"}</p>
              <p style={{ fontSize: 10, color: C.dim }}>occupied · {a.available_units ?? 0} open</p>
            </HoloPanel>
          );
        })}
      </div>
    </div>
  );
}
function AttendeeAlertsPage({ zones, conditions }) {
  const rec = recommendedGate(zones);
  const alerts = [
    ...zones.filter((z) => z.risk_level === "critical" || z.risk_level === "high").map((z) => ({
      icon: AlertTriangle, color: riskColor(z.risk_level), text: `${z.access_point_name} is becoming crowded — avoid if possible`,
    })),
    { icon: Star, color: C.cyan, text: `${rec.access_point_name} is currently recommended` },
    ...(conditions?.severity && conditions.severity.toUpperCase() !== "LOW"
      ? [{ icon: CloudSun, color: C.medium, text: `Weather update: ${conditions.weather_type || "conditions changing"}${conditions.temperature != null ? `, ${conditions.temperature}°C` : ""}` }]
      : []),
  ];
  return (
    <div style={{ padding: 28 }}>
      <PageHeader eyebrow="Attendee" title="Alerts & Guidance" subtitle="Live notifications relevant to your visit" />
      <div style={{ display: "flex", flexDirection: "column", gap: 10, maxWidth: 480 }}>
        {alerts.map((a, i) => {
          const Icon = a.icon;
          return (
            <HoloPanel key={i} style={{ display: "flex", alignItems: "center", gap: 12, padding: 14 }}>
              <Icon size={16} color={a.color} />
              <p style={{ fontSize: 12.5, color: C.text }}>{a.text}</p>
            </HoloPanel>
          );
        })}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Shell
// ---------------------------------------------------------------------------
const NAV_ORGANIZER = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "crowd", label: "Crowd & Hotspots", icon: Users },
  { id: "prediction", label: "Prediction + Risk", icon: BrainCircuit },
  { id: "rootCause", label: "Root Cause", icon: GitBranch },
  { id: "interventions", label: "Interventions", icon: SlidersHorizontal },
  { id: "simulation", label: "What-if Simulation", icon: Route },
  { id: "transport", label: "Transport", icon: BusFront },
  { id: "accommodation", label: "Accommodation", icon: BedDouble },
  { id: "conditions", label: "Conditions / Incidents", icon: CloudSun },
];
const NAV_ATTENDEE = [
  { id: "home", label: "Event Home", icon: Home },
  { id: "liveMap", label: "Live Map", icon: MapPin },
  { id: "gateStatus", label: "Gate Status", icon: Building2 },
  { id: "myRoute", label: "My Route", icon: Navigation2 },
  { id: "attendeeTransport", label: "Transport", icon: BusFront },
  { id: "attendeeStay", label: "Where to Stay", icon: BedDouble },
  { id: "alerts", label: "Alerts / Guidance", icon: Bell },
];

function ModeToggle({ mode, setMode }) {
  return (
    <div style={{ display: "flex", gap: 4, padding: 3, borderRadius: 6, background: "rgba(0,0,0,0.35)", border: "1px solid rgba(45,212,191,0.2)", marginBottom: 18 }}>
      {[{ id: "organizer", label: "Organizer" }, { id: "attendee", label: "Attendee" }].map((m) => (
        <button key={m.id} onClick={() => setMode(m.id)} style={{ flex: 1, padding: "7px 0", borderRadius: 4, fontSize: 10.5, fontWeight: 700, letterSpacing: 1, cursor: "pointer", background: mode === m.id ? "rgba(34,232,245,0.15)" : "transparent", border: mode === m.id ? `1px solid ${C.cyan}` : "1px solid transparent", color: mode === m.id ? C.cyan : C.dim }}>
          {m.label.toUpperCase()}
        </button>
      ))}
    </div>
  );
}

function SideBar({ mode, setMode, activePage, onNavigate, connected }) {
  const nav = mode === "organizer" ? NAV_ORGANIZER : NAV_ATTENDEE;
  return (
    <aside style={{ width: 230, minHeight: "100%", background: "rgba(2,5,9,0.75)", backdropFilter: "blur(8px)", borderRight: `1px solid ${C.panelBorder}`, padding: "22px 14px", display: "flex", flexDirection: "column" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "0 8px 20px" }}>
        <div style={{ width: 34, height: 34, borderRadius: 8, background: "rgba(34,232,245,0.1)", border: `1px solid ${C.cyan}`, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: `0 0 14px ${C.cyan}44` }}><Activity size={17} color={C.cyan} /></div>
        <div><p style={{ fontSize: 14, fontWeight: 800, color: C.text, letterSpacing: 0.5 }}>EVENTFLOW</p><p style={{ fontSize: 8.5, color: C.cyan, letterSpacing: 2 }}>AI ORGANIZER</p></div>
      </div>
      <ModeToggle mode={mode} setMode={(m) => { setMode(m); onNavigate(m === "organizer" ? "overview" : "home"); }} />
      <p style={{ fontSize: 9, color: C.dim, letterSpacing: 2, padding: "0 10px", marginBottom: 8 }}>{mode === "organizer" ? "OPERATIONS" : "ATTENDEE VIEW"}</p>
      <nav style={{ display: "flex", flexDirection: "column", gap: 3 }}>
        {nav.map((item) => {
          const Icon = item.icon; const active = activePage === item.id;
          return (
            <button key={item.id} onClick={() => onNavigate(item.id)} style={{ display: "flex", alignItems: "center", gap: 10, padding: "9px 10px", borderRadius: 4, fontSize: 12, textAlign: "left", background: active ? "rgba(34,232,245,0.1)" : "transparent", border: active ? `1px solid ${C.panelBorder}` : "1px solid transparent", color: active ? C.cyan : C.dim, cursor: "pointer", textShadow: active ? `0 0 8px ${C.cyan}66` : "none" }}>
              <Icon size={15} strokeWidth={1.8} /><span>{item.label}</span>
            </button>
          );
        })}
      </nav>
      <div style={{ marginTop: "auto", padding: "12px 10px", borderRadius: 4, background: "rgba(45,212,191,0.05)", border: "1px solid rgba(45,212,191,0.2)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ width: 6, height: 6, borderRadius: "50%", background: connected ? C.teal : C.critical, boxShadow: `0 0 8px ${connected ? C.teal : C.critical}` }} />
          <span style={{ fontSize: 10, color: C.text }}>{connected ? "BACKEND CONNECTED" : "BACKEND UNREACHABLE"}</span>
        </div>
        <p style={{ fontSize: 9, color: C.dim, marginTop: 4, marginLeft: 12 }}>Live FastAPI + PostgreSQL data</p>
      </div>
    </aside>
  );
}
function TopBar({ mode, venue, eventInfo, eventId, events, onEventIdChange, onRefresh, lastUpdated, connected }) {
  const [draftEventId, setDraftEventId] = useState(String(eventId));
  useEffect(() => { setDraftEventId(String(eventId)); }, [eventId]);
  const submitEventId = () => {
    const parsed = parseInt(draftEventId, 10);
    if (!Number.isNaN(parsed) && parsed > 0) onEventIdChange(parsed);
    else setDraftEventId(String(eventId));
  };
  const hasEventList = events && events.length > 0;
  return (
    <header style={{ height: 68, borderBottom: `1px solid ${C.panelBorder}`, padding: "0 26px", display: "flex", alignItems: "center", justifyContent: "space-between", background: "rgba(2,5,9,0.7)", backdropFilter: "blur(8px)" }}>
      <div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <MapPin size={14} color={C.cyan} />
          <span style={{ fontSize: 12, color: C.text }}>{venue?.venue_name || "No venue loaded"}</span>
          <ChevronDown size={12} color={C.dim} />
        </div>
        <p style={{ fontSize: 10, color: C.dim, marginTop: 2 }}>{eventInfo?.event_name || "—"}</p>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        {hasEventList ? (
          <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <span style={{ fontSize: 9, color: C.dim }}>EVENT</span>
            <select
              value={eventId}
              onChange={(e) => onEventIdChange(parseInt(e.target.value, 10))}
              style={{ maxWidth: 220, background: "rgba(0,0,0,0.4)", border: `1px solid ${C.panelBorder}`, borderRadius: 4, color: C.text, fontSize: 11, padding: "5px 6px" }}
            >
              {events.map((ev) => (
                <option key={ev.event_id} value={ev.event_id} style={{ background: C.bg }}>
                  #{ev.event_id} · {ev.event_name}{ev.venue_name ? ` (${ev.venue_name})` : ""}
                </option>
              ))}
            </select>
          </div>
        ) : (
          <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <span style={{ fontSize: 9, color: C.dim }}>EVENT ID</span>
            <input
              value={draftEventId}
              onChange={(e) => setDraftEventId(e.target.value)}
              onBlur={submitEventId}
              onKeyDown={(e) => { if (e.key === "Enter") submitEventId(); }}
              style={{ width: 44, background: "rgba(0,0,0,0.4)", border: `1px solid ${C.panelBorder}`, borderRadius: 4, color: C.text, fontSize: 11, padding: "4px 6px", textAlign: "center" }}
            />
          </div>
        )}
        <button onClick={onRefresh} title="Refresh now" style={{ background: "none", border: "none", cursor: "pointer", display: "flex", alignItems: "center" }}>
          <RefreshCw size={14} color={C.dim} />
        </button>
        <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 10, color: connected ? C.teal : C.critical, letterSpacing: 1 }}>
          {connected ? <span style={{ width: 6, height: 6, borderRadius: "50%", background: C.teal, boxShadow: `0 0 8px ${C.teal}` }} /> : <WifiOff size={11} />}
          {connected ? "LIVE" : "OFFLINE"}
        </div>
        <Search size={15} color={C.dim} />
        <div style={{ position: "relative" }}><Bell size={15} color={C.dim} /></div>
        <div style={{ width: 1, height: 24, background: "rgba(255,255,255,0.1)" }} />
        <div style={{ textAlign: "right" }}>
          <p style={{ fontSize: 11, color: C.text }}>{mode === "organizer" ? "Operations" : "Attendee"}</p>
          <p style={{ fontSize: 9, color: C.dim }}>{lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString()}` : "—"}</p>
        </div>
      </div>
    </header>
  );
}

function LoadingState() {
  return (
    <div style={{ padding: 60, display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
      <Loader2 size={26} color={C.cyan} style={{ animation: "spin 1s linear infinite" }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <p style={{ fontSize: 12, color: C.dim }}>Loading live event data from the backend…</p>
    </div>
  );
}
function ErrorState({ message, onRetry }) {
  return (
    <div style={{ padding: 60, display: "flex", flexDirection: "column", alignItems: "center", gap: 12, textAlign: "center" }}>
      <WifiOff size={26} color={C.critical} />
      <p style={{ fontSize: 13, color: C.text, maxWidth: 480 }}>{message}</p>
      <p style={{ fontSize: 11, color: C.dim, maxWidth: 480 }}>Confirm the FastAPI backend is running and reachable, and that VITE_API_BASE_URL points to it.</p>
      <button onClick={onRetry} style={{ marginTop: 8, display: "inline-flex", alignItems: "center", gap: 8, padding: "8px 16px", borderRadius: 4, fontSize: 12, fontWeight: 700, border: `1px solid ${C.cyan}`, background: "rgba(34,232,245,0.1)", color: C.cyan, cursor: "pointer" }}>
        <RefreshCw size={13} /> Retry
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// App
// ---------------------------------------------------------------------------
export default function App() {
  const [mode, setMode] = useState("organizer");
  const [activePage, setActivePage] = useState("overview");
  const [eventId, setEventId] = useState(DEFAULT_EVENT_ID);
  const events = useEventList();

  const {
    state, risks, interventions, accommodation, appliedActions,
    loading, error, refresh, lastUpdated,
  } = useEventData(eventId);

  const zones = useMemo(() => buildZones(risks, state), [risks, state]);
  const transport = useMemo(() => buildTransport(state), [state]);
  const venue = state?.venue || {};
  const eventInfo = state?.event || {};
  const conditions = state?.conditions || null;
  const incidents = state?.incidents || [];

  const handleRefresh = () => refresh();
  const handleEventIdChange = (id) => setEventId(id);

  const organizerPages = {
    overview: <OverviewPage zones={zones} venue={venue} eventInfo={eventInfo} incidents={incidents} appliedActions={appliedActions} />,
    crowd: <CrowdPage zones={zones} />,
    prediction: <PredictionPage zones={zones} />,
    rootCause: <RootCausePage interventionsData={interventions} zones={zones} />,
    interventions: <InterventionsPage eventId={eventId} interventionsData={interventions} appliedActions={appliedActions} onApplied={refresh} />,
    simulation: <SimulationPage eventId={eventId} interventionsData={interventions} appliedActions={appliedActions} />,
    transport: <TransportPage transport={transport} />,
    accommodation: <AccommodationPage accommodation={accommodation} />,
    conditions: <ConditionsPage zones={zones} conditions={conditions} incidents={incidents} />,
  };
  const attendeePages = {
    home: <AttendeeHomePage zones={zones} eventInfo={eventInfo} venue={venue} />,
    liveMap: <AttendeeMapPage zones={zones} venue={venue} />,
    gateStatus: <AttendeeGateStatusPage zones={zones} />,
    myRoute: <AttendeeRoutePage zones={zones} />,
    attendeeTransport: <AttendeeTransportPage transport={transport} />,
    attendeeStay: <AttendeeStayPage accommodation={accommodation} />,
    alerts: <AttendeeAlertsPage zones={zones} conditions={conditions} />,
  };
  const pages = mode === "organizer" ? organizerPages : attendeePages;

  let content;
  if (loading && !state) {
    content = <LoadingState />;
  } else if (error) {
    content = <ErrorState message={error} onRetry={handleRefresh} />;
  } else if (zones.length === 0) {
    content = (
      <div style={{ padding: 28 }}>
        <EmptyPanel message={`No zones with live crowd data were found for event ${eventId}. Check the event ID, or confirm crowd_state rows exist for it.`} />
      </div>
    );
  } else {
    content = pages[activePage];
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", color: C.text, fontFamily: "'Inter', system-ui, sans-serif", position: "relative", overflow: "hidden" }}>
      <style>{`
        @keyframes holoPing { 0% { transform: scale(1); opacity: 0.35; } 70% { transform: scale(1.8); opacity: 0; } 100% { opacity: 0; } }
        @keyframes scan { 0% { transform: translateY(-100%); } 100% { transform: translateY(100%); } }
      `}</style>
      <CityBackground />
      <div style={{ position: "fixed", left: 0, right: 0, height: 2, background: "linear-gradient(90deg, transparent, rgba(34,232,245,0.5), transparent)", animation: "scan 6s linear infinite", zIndex: 1, pointerEvents: "none" }} />
      <div style={{ position: "relative", zIndex: 2, display: "flex", width: "100%" }}>
        <SideBar mode={mode} setMode={setMode} activePage={activePage} onNavigate={setActivePage} connected={!error} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <TopBar mode={mode} venue={venue} eventInfo={eventInfo} eventId={eventId} events={events} onEventIdChange={handleEventIdChange} onRefresh={handleRefresh} lastUpdated={lastUpdated} connected={!error} />
          {content}
        </div>
      </div>
    </div>
  );
}
