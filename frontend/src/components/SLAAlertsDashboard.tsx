import { useCallback, useEffect, useState } from "react";
import { AlertTriangle, CheckCircle, RefreshCw, ShieldAlert } from "lucide-react";
import { API_BASE, authenticatedFetch } from "../services/authService";
import "./SLAAlertsDashboard.css";

type SLAAlert = {
  id: string;
  incident_id: string;
  incident_title: string;
  severity: string;
  status: string;
  target_hours: number;
  elapsed_hours: number;
  overdue_hours: number;
  escalation_level: string;
  escalation_message: string;
  created_at: string;
};

type Filter = "all" | "active" | "resolved";

export default function SLAAlertsDashboard() {
  const [alerts, setAlerts] = useState<SLAAlert[]>([]);
  const [filter, setFilter] = useState<Filter>("all");
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadAlerts = useCallback(async () => {
    try {
      setError("");
      const response = await authenticatedFetch(
        `${API_BASE}/api/v1/sla/alerts`,
      );
      if (!response.ok) throw new Error(`API error: ${response.status}`);
      const data = await response.json();
      setAlerts(Array.isArray(data.alerts) ? data.alerts : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load SLA alerts");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAlerts();
    const timer = window.setInterval(loadAlerts, 30000);
    return () => window.clearInterval(timer);
  }, [loadAlerts]);

  const generateAlerts = async () => {
    try {
      setGenerating(true);
      setMessage("");
      const response = await authenticatedFetch(
        `${API_BASE}/api/v1/sla/alerts/generate`,
        { method: "POST" },
      );
      if (!response.ok) throw new Error(`Generation failed: ${response.status}`);
      const data = await response.json();
      setMessage(`${data.generated ?? 0} new SLA alert(s) generated.`);
      await loadAlerts();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Alert generation failed");
    } finally {
      setGenerating(false);
    }
  };

  const resolveAlert = async (id: string) => {
    try {
      const response = await authenticatedFetch(
        `${API_BASE}/api/v1/sla/alerts/${encodeURIComponent(id)}/resolve`,
        { method: "PATCH" },
      );
      if (!response.ok) throw new Error(`Resolve failed: ${response.status}`);
      setMessage("SLA alert resolved successfully.");
      await loadAlerts();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to resolve alert");
    }
  };

  const active = alerts.filter((a) => a.status === "active");
  const resolved = alerts.filter((a) => a.status === "resolved");
  const critical = active.filter((a) => a.escalation_level === "critical").length;

  const visibleAlerts = alerts.filter((alert) => {
    if (filter === "active") return alert.status === "active";
    if (filter === "resolved") return alert.status === "resolved";
    return true;
  });

  const formatDate = (value: string) => {
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? "Unknown" : date.toLocaleString();
  };

  return (
    <section className="sla-alerts-page">
      <div className="sla-alerts-header">
        <div>
          <h2><ShieldAlert size={25} /> SLA Breach Alerts</h2>
          <p>Monitor overdue incidents and escalation activity.</p>
        </div>
        <div className="sla-alert-actions">
          <button onClick={loadAlerts} disabled={loading}>
            <RefreshCw size={16} /> Refresh
          </button>
          <button onClick={generateAlerts} disabled={generating}>
            <AlertTriangle size={16} />
            {generating ? "Generating..." : "Generate Alerts"}
          </button>
        </div>
      </div>

      {message && <div className="sla-alert-message">{message}</div>}
      {error && <div className="sla-alert-error">{error}</div>}

      <div className="sla-alert-kpis">
        <div className="sla-alert-kpi">
          <span>Active Alerts</span>
          <strong>{active.length}</strong>
        </div>
        <div className="sla-alert-kpi critical">
          <span>Critical Escalations</span>
          <strong>{critical}</strong>
        </div>
        <div className="sla-alert-kpi">
          <span>Resolved Alerts</span>
          <strong>{resolved.length}</strong>
        </div>
        <div className="sla-alert-kpi">
          <span>Total Alerts</span>
          <strong>{alerts.length}</strong>
        </div>
      </div>

      <div className="sla-alert-toolbar">
        <h3>Alert History</h3>
        <div className="sla-alert-filters">
          {(["all", "active", "resolved"] as Filter[]).map((item) => (
            <button
              key={item}
              className={filter === item ? "selected" : ""}
              onClick={() => setFilter(item)}
            >
              {item.replace("_", " ").toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="sla-alert-empty">Loading SLA alerts...</div>
      ) : visibleAlerts.length === 0 ? (
        <div className="sla-alert-empty">
          <CheckCircle size={32} />
          <h3>No alerts found</h3>
          <p>No alerts match the selected filter.</p>
        </div>
      ) : (
        <div className="sla-alert-list">
          {visibleAlerts.map((alert) => (
            <article className="sla-alert-card" key={alert.id}>
              <div className="sla-alert-card-top">
                <div>
                  <span className={`sla-level ${alert.escalation_level}`}>
                    {alert.escalation_level} escalation
                  </span>
                  <span className={`sla-status ${alert.status}`}>
                    {alert.status}
                  </span>
                </div>
                <small>{formatDate(alert.created_at)}</small>
              </div>

              <h3>{alert.incident_title}</h3>
              <p className="sla-alert-incident-id">
                Incident ID: {alert.incident_id}
              </p>
              <p>{alert.escalation_message}</p>

              <div className="sla-alert-details">
                <span>Severity: <b>{alert.severity}</b></span>
                <span>Target: <b>{alert.target_hours}h</b></span>
                <span>Elapsed: <b>{alert.elapsed_hours}h</b></span>
                <span>Overdue: <b>{alert.overdue_hours}h</b></span>
              </div>

              {alert.status === "active" && (
                <button
                  className="sla-resolve-button"
                  onClick={() => resolveAlert(alert.id)}
                >
                  <CheckCircle size={16} /> Resolve Alert
                </button>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
