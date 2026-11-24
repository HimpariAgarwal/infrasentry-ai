import { useCallback, useEffect, useState } from "react";
import {
  AlertTriangle, RefreshCw, ShieldCheck, UserCheck
} from "lucide-react";
import { authenticatedFetch, API_BASE } from "../services/authService";
import "./IncidentDashboard.css";

interface Incident {
  id: string;
  title: string;
  description: string;
  severity: string;
  source: string;
  status: string;
  assigned_to: string | null;
  created_at: string;
  updated_at: string;
  notes: { text: string; timestamp: string }[];
}

export default function IncidentDashboard() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [assignees, setAssignees] = useState<Record<string, string>>({});
  const [notes, setNotes] = useState<Record<string, string>>({});

  const loadIncidents = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await authenticatedFetch(
        `${API_BASE}/api/v1/incidents?status=${filter}`
      );

      if (!response.ok) throw new Error("Unable to load incidents.");

      const data = await response.json();
      setIncidents(data.incidents || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed.");
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    loadIncidents();
  }, [loadIncidents]);

  const createFromAlerts = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await authenticatedFetch(
        `${API_BASE}/api/v1/incidents/from-alerts`,
        { method: "POST" }
      );

      if (!response.ok) throw new Error("Incident creation failed.");
      await loadIncidents();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed.");
    } finally {
      setLoading(false);
    }
  };

  const updateIncident = async (
    id: string,
    payload: { status?: string; assigned_to?: string; note?: string }
  ) => {
    try {
      const response = await authenticatedFetch(
        `${API_BASE}/api/v1/incidents/${encodeURIComponent(id)}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) throw new Error("Incident update failed.");
      await loadIncidents();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Update failed.");
    }
  };

  const openCount = incidents.filter(i => i.status === "open").length;
  const investigatingCount = incidents.filter(
    i => i.status === "investigating"
  ).length;
  const resolvedCount = incidents.filter(i => i.status === "resolved").length;

  return (
    <section className="incident-dashboard">
      <div className="incident-heading">
        <div>
          <h2><ShieldCheck size={23} /> Incident Management</h2>
          <p>Track, assign and resolve security incidents.</p>
        </div>

        <div className="incident-actions">
          <button onClick={createFromAlerts} disabled={loading}>
            <AlertTriangle size={16} /> Import Active Alerts
          </button>
          <button onClick={loadIncidents} disabled={loading}>
            <RefreshCw size={16} /> Refresh
          </button>
        </div>
      </div>

      <div className="incident-kpis">
        <div><span>Total</span><strong>{incidents.length}</strong></div>
        <div><span>Open</span><strong>{openCount}</strong></div>
        <div><span>Investigating</span><strong>{investigatingCount}</strong></div>
        <div><span>Resolved</span><strong>{resolvedCount}</strong></div>
      </div>

      <div className="incident-filter">
        <select value={filter} onChange={e => setFilter(e.target.value)}>
          <option value="all">All Incidents</option>
          <option value="open">Open</option>
          <option value="investigating">Investigating</option>
          <option value="resolved">Resolved</option>
        </select>
      </div>

      {error && <p className="incident-error">{error}</p>}
      {loading && <p>Loading incidents...</p>}

      {!loading && (
        <div className="incident-list">
          {incidents.length === 0 ? (
            <p className="incident-empty">No incidents found.</p>
          ) : incidents.map(incident => (
            <article className="incident-card" key={incident.id}>
              <div className="incident-card-heading">
                <div>
                  <span className={`incident-severity ${incident.severity}`}>
                    {incident.severity}
                  </span>
                  <h3>{incident.title}</h3>
                </div>
                <span className={`incident-status ${incident.status}`}>
                  {incident.status}
                </span>
              </div>

              <p>{incident.description}</p>

              <div className="incident-meta">
                <span>Source: {incident.source}</span>
                <span>Created: {new Date(incident.created_at).toLocaleString()}</span>
              </div>

              <div className="incident-controls">
                <select
                  value={incident.status}
                  onChange={e => updateIncident(incident.id, { status: e.target.value })}
                >
                  <option value="open">Open</option>
                  <option value="investigating">Investigating</option>
                  <option value="resolved">Resolved</option>
                </select>

                <input
                  value={assignees[incident.id] ?? incident.assigned_to ?? ""}
                  placeholder="Assign to..."
                  onChange={e => setAssignees(previous => ({
                    ...previous, [incident.id]: e.target.value
                  }))}
                />

                <button
                  onClick={() => updateIncident(incident.id, {
                    assigned_to: assignees[incident.id] || ""
                  })}
                >
                  <UserCheck size={15} /> Assign
                </button>
              </div>

              <div className="incident-note-controls">
                <input
                  value={notes[incident.id] || ""}
                  placeholder="Add investigation note..."
                  onChange={e => setNotes(previous => ({
                    ...previous, [incident.id]: e.target.value
                  }))}
                />
                <button
                  disabled={!notes[incident.id]?.trim()}
                  onClick={async () => {
                    const note = notes[incident.id].trim();
                    await updateIncident(incident.id, { note });
                    setNotes(previous => ({ ...previous, [incident.id]: "" }));
                  }}
                >
                  Add Note
                </button>
              </div>

              {incident.notes?.length > 0 && (
                <details className="incident-notes">
                  <summary>Investigation Notes ({incident.notes.length})</summary>
                  {incident.notes.map((note, index) => (
                    <p key={index}>
                      {note.text}
                      <small>{new Date(note.timestamp).toLocaleString()}</small>
                    </p>
                  ))}
                </details>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
