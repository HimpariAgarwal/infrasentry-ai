import { useCallback, useEffect, useState } from "react";
import { Activity, AlertTriangle, RefreshCw, ShieldAlert } from "lucide-react";
import { authenticatedFetch, API_BASE } from "../services/authService";
import "./SecurityDashboard.css";

interface SecurityEvent {
  timestamp: string;
  event: string;
  path: string;
  ip_address: string;
  reason: string;
}

interface AuditResponse {
  total: number;
  events: SecurityEvent[];
}

export default function SecurityDashboard() {
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("all");

  const loadEvents = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const params = new URLSearchParams({
        limit: "200",
        event: filter,
      });

      const response = await authenticatedFetch(
        `${API_BASE}/api/v1/security/audit?${params}`,
      );

      if (!response.ok) throw new Error("Unable to load security events.");

      const data: AuditResponse = await response.json();
      setEvents(data.events);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed.");
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  const failures = events.filter(
    (item) => item.event === "authentication_failed",
  ).length;

  return (
    <section className="security-dashboard">
      <div className="security-heading">
        <div>
          <h2><ShieldAlert size={23} /> Security Audit</h2>
          <p>Monitor authentication and API security events.</p>
        </div>

        <button onClick={loadEvents} disabled={loading}>
          <RefreshCw size={16} /> Refresh
        </button>
      </div>

      <div className="security-stats">
        <div className="security-stat">
          <Activity size={22} />
          <span>Total Events</span>
          <strong>{total}</strong>
        </div>

        <div className="security-stat">
          <AlertTriangle size={22} />
          <span>Authentication Failures</span>
          <strong>{failures}</strong>
        </div>
      </div>

      <div className="security-toolbar">
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="all">All Events</option>
          <option value="authentication_failed">Authentication Failed</option>
          <option value="authentication_unavailable">Configuration Errors</option>
        </select>
      </div>

      {error && <p className="security-error">{error}</p>}
      {loading && <p>Loading security events...</p>}

      {!loading && !error && (
        <div className="security-table-wrap">
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Event</th>
                <th>API Path</th>
                <th>IP Address</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              {events.length === 0 ? (
                <tr>
                  <td colSpan={5}>No security events found.</td>
                </tr>
              ) : events.map((item, index) => (
                <tr key={`${item.timestamp}-${index}`}>
                  <td>{new Date(item.timestamp).toLocaleString()}</td>
                  <td>{item.event}</td>
                  <td>{item.path}</td>
                  <td>{item.ip_address}</td>
                  <td>{item.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
