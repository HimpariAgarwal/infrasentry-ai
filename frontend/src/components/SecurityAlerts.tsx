import { useCallback, useEffect, useState } from "react";
import {
  AlertTriangle, CheckCircle, RefreshCw, ShieldAlert
} from "lucide-react";
import { authenticatedFetch, API_BASE } from "../services/authService";
import "./SecurityAlerts.css";

interface SecurityAlert {
  id: string;
  timestamp: string;
  type: string;
  severity: string;
  message: string;
  source: string;
  status: string;
  event_count?: number;
}

export default function SecurityAlerts() {
  const [alerts, setAlerts] = useState<SecurityAlert[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [severity, setSeverity] = useState("all");
  const [status, setStatus] = useState("all");

  const loadAlerts = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await authenticatedFetch(
        `${API_BASE}/api/v1/security/alerts`
      );

      if (!response.ok) throw new Error("Unable to load security alerts.");

      const data = await response.json();
      setAlerts(data.alerts || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAlerts();
  }, [loadAlerts]);

  const generateAlerts = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await authenticatedFetch(
        `${API_BASE}/api/v1/security/alerts/generate`,
        { method: "POST" }
      );

      if (!response.ok) throw new Error("Alert generation failed.");
      await loadAlerts();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed.");
    } finally {
      setLoading(false);
    }
  };

  const resolveAlert = async (id: string) => {
    try {
      const response = await authenticatedFetch(
        `${API_BASE}/api/v1/security/alerts/${encodeURIComponent(id)}/resolve`,
        { method: "PATCH" }
      );

      if (!response.ok) throw new Error("Unable to resolve alert.");
      await loadAlerts();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Resolve failed.");
    }
  };

  const filteredAlerts = alerts.filter((alert) => {
    const severityMatch =
      severity === "all" || alert.severity === severity;
    const statusMatch = status === "all" || alert.status === status;
    return severityMatch && statusMatch;
  });

  const activeCount = alerts.filter((a) => a.status === "active").length;
  const criticalCount = alerts.filter(
    (a) => a.severity === "critical" && a.status === "active"
  ).length;

  return (
    <section className="security-alerts-page">
      <div className="security-alerts-header">
        <div>
          <h2><ShieldAlert size={23} /> Security Alerts</h2>
          <p>Review suspicious activity and manage security alerts.</p>
        </div>

        <div className="security-alert-actions">
          <button onClick={generateAlerts} disabled={loading}>
            <AlertTriangle size={16} /> Generate Alerts
          </button>
          <button onClick={loadAlerts} disabled={loading}>
            <RefreshCw size={16} /> Refresh
          </button>
        </div>
      </div>

      <div className="security-alert-kpis">
        <div className="security-alert-kpi">
          <span>Total Alerts</span>
          <strong>{alerts.length}</strong>
        </div>
        <div className="security-alert-kpi">
          <span>Active Alerts</span>
          <strong>{activeCount}</strong>
        </div>
        <div className="security-alert-kpi">
          <span>Critical Alerts</span>
          <strong>{criticalCount}</strong>
        </div>
      </div>

      <div className="security-alert-filters">
        <select value={severity} onChange={(e) => setSeverity(e.target.value)}>
          <option value="all">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
        </select>

        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="all">All Statuses</option>
          <option value="active">Active</option>
          <option value="resolved">Resolved</option>
        </select>
      </div>

      {error && <p className="security-alert-error">{error}</p>}
      {loading && <p>Loading alerts...</p>}

      {!loading && (
        <div className="security-alert-list">
          {filteredAlerts.length === 0 ? (
            <div className="security-alert-empty">
              <CheckCircle size={28} />
              <p>No alerts match the selected filters.</p>
            </div>
          ) : filteredAlerts.map((alert) => (
            <article className="security-alert-card" key={alert.id}>
              <div className="security-alert-card-top">
                <div>
                  <span className={`alert-severity ${alert.severity}`}>
                    {alert.severity}
                  </span>
                  <strong>{alert.type.replaceAll("_", " ")}</strong>
                </div>
                <span className={`alert-status ${alert.status}`}>
                  {alert.status}
                </span>
              </div>

              <p>{alert.message}</p>

              <div className="security-alert-meta">
                <span>Source: {alert.source}</span>
                {alert.event_count !== undefined && (
                  <span>Events: {alert.event_count}</span>
                )}
                <span>{new Date(alert.timestamp).toLocaleString()}</span>
              </div>

              {alert.status === "active" && (
                <button
                  className="resolve-alert-button"
                  onClick={() => resolveAlert(alert.id)}
                >
                  <CheckCircle size={15} /> Resolve Alert
                </button>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
