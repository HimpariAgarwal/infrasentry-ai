import ReadinessStatus from "./ReadinessStatus";
import { authenticatedFetch } from "../services/apiClient";
import { useCallback, useEffect, useState } from "react";
import {
  Activity, AlertTriangle, CheckCircle, Clock,
  Database, RefreshCw, ShieldAlert, Trash2
} from "lucide-react";
import "./SystemHealth.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface HealthData {
  status: string;
  timestamp: string;
  uptime_seconds: number;
  system: {
    platform: string;
    platform_release: string;
    architecture: string;
    processor: string;
    cpu_percent: number;
    cpu_count: number;
    memory: { total_mb: number; used_mb: number; available_mb: number; percent: number };
    disk: { total_gb: number; used_gb: number; free_gb: number; percent: number };
  };
  database: { connected: boolean; status: string; error?: string };
}

interface HealthEvent {
  id: string;
  time: string;
  level: "warning" | "critical" | "success";
  message: string;
}

interface DiagnosticCheck {
  name: string;
  status: string;
  details: Record<string, string | number>;
}

interface DiagnosticsData {
  service: string;
  status: string;
  timestamp: string;
  runtime: {
    python_version: string;
    platform: string;
  };
  checks: DiagnosticCheck[];
  summary: {
    total: number;
    healthy: number;
    degraded: number;
  };
}

export default function SystemHealth() {
  const [data, setData] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState("");
  const [events, setEvents] = useState<HealthEvent[]>([]);
  const [diagnostics, setDiagnostics] = useState<DiagnosticsData | null>(null);
  const [diagnosticsError, setDiagnosticsError] = useState("");

  const fetchDiagnostics = useCallback(async () => {
    try {
      const response = await authenticatedFetch(
        `${API_BASE}/api/v1/system-diagnostics`
      );

      if (!response.ok) {
        throw new Error(`Diagnostics API error: ${response.status}`);
      }

      const result: DiagnosticsData = await response.json();
      setDiagnostics(result);
      setDiagnosticsError("");
    } catch (err) {
      setDiagnosticsError(
        err instanceof Error
          ? err.message
          : "Diagnostics service unavailable"
      );
    }
  }, []);

  const fetchHealth = useCallback(async () => {
    try {
      const response = await authenticatedFetch(`${API_BASE}/api/v1/system-health`);
      if (!response.ok) throw new Error(`API error: ${response.status}`);

      const result: HealthData = await response.json();
      setData(result);
      setError("");
      setLastUpdated(new Date().toLocaleTimeString());

      const alerts: HealthEvent[] = [];
      if (result.system.cpu_percent >= 80) {
        alerts.push({ id: "cpu", time: new Date().toLocaleTimeString(), level: result.system.cpu_percent >= 95 ? "critical" : "warning", message: `High CPU usage: ${result.system.cpu_percent}%` });
      }
      if (result.system.memory.percent >= 85) {
        alerts.push({ id: "memory", time: new Date().toLocaleTimeString(), level: result.system.memory.percent >= 95 ? "critical" : "warning", message: `High memory usage: ${result.system.memory.percent}%` });
      }
      if (result.system.disk.percent >= 90) {
        alerts.push({ id: "disk", time: new Date().toLocaleTimeString(), level: "critical", message: `Critical disk usage: ${result.system.disk.percent}%` });
      }
      if (!result.database.connected) {
        alerts.push({ id: "database", time: new Date().toLocaleTimeString(), level: "critical", message: "Database connection unavailable" });
      }
      if (alerts.length === 0) {
        alerts.push({ id: "healthy", time: new Date().toLocaleTimeString(), level: "success", message: "System health check passed" });
      }

      setEvents(previous => {
        const additions = alerts.filter(alert =>
          !previous.length ||
          previous[0].message !== alert.message ||
          previous[0].level !== alert.level
        );
        return [...additions, ...previous].slice(0, 20);
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Backend connection failed");
      setEvents(previous => [{
        id: "api-error",
        time: new Date().toLocaleTimeString(),
        level: "critical" as const,
        message: "Backend health endpoint unavailable"
      }, ...previous].slice(0, 20));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const initialFetch = window.setTimeout(() => {
      void fetchHealth();
      void fetchDiagnostics();
    }, 0);

    const timer = window.setInterval(() => {
      void fetchHealth();
      void fetchDiagnostics();
    }, 15000);

    return () => {
      window.clearTimeout(initialFetch);
      window.clearInterval(timer);
    };
  }, [fetchHealth, fetchDiagnostics]);


  const exportHealthEvents = () => {
    const headers = ["Time", "Severity", "Event"];
    const rows = events.map(event => [
      event.time,
      event.level.toUpperCase(),
      event.message
    ]);

    const csv = [headers, ...rows]
      .map(row => row.map(value =>
        `"${String(value).replace(/"/g, '""')}"`
      ).join(","))
      .join("\r\n");

    const blob = new Blob(["\uFEFF" + csv], {
      type: "text/csv;charset=utf-8;"
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `infrasentry-health-events-${new Date().toISOString().replace(/[:.]/g, "-")}.csv`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  const alerts = data ? [
    ...(data.system.cpu_percent >= 80 ? [`CPU usage is high (${data.system.cpu_percent}%)`] : []),
    ...(data.system.memory.percent >= 85 ? [`Memory usage is high (${data.system.memory.percent}%)`] : []),
    ...(data.system.disk.percent >= 90 ? [`Disk usage is critical (${data.system.disk.percent}%)`] : []),
    ...(!data.database.connected ? ["Database is disconnected"] : [])
  ] : [];

  if (loading && !data) {
    return <div className="health-message"><RefreshCw className="health-spin" /> Loading system health...</div>;
  }

  if (!data) {
    return <div className="health-message health-error"><AlertTriangle /> {error}<button onClick={fetchHealth}>Retry</button></div>;
  }

  return (
    <section className="system-health-page">
      <ReadinessStatus />
      <div className="health-topbar">
        <div>
          <h2>System Health Monitor</h2>
          <p>Infrastructure monitoring and resource alerts</p>
        </div>
        <button className="health-refresh" onClick={fetchHealth}><RefreshCw size={16} /> Refresh</button>
      </div>

      {error && <div className="health-warning"><AlertTriangle size={16} /> {error}</div>}

      <div className="health-status-card">
        {data.status === "healthy" ? <CheckCircle color="#16a34a" size={26} /> : <AlertTriangle color="#d97706" size={26} />}
        <div>
          <strong>Backend {data.status.toUpperCase()}</strong>
          <p>Last updated: {lastUpdated}</p>
        </div>
        <span className={`health-status-badge ${data.status}`}>{data.status}</span>
      </div>

      {/* PROTECTED SYSTEM DIAGNOSTICS */}
      <div className="health-detail-card diagnostics-panel">
        <div className="diagnostics-heading">
          <div>
            <h3><Activity size={19} /> Protected System Diagnostics</h3>
            <p>Live diagnostics from the authenticated backend API</p>
          </div>

          <button
            type="button"
            onClick={fetchDiagnostics}
            disabled={Boolean(diagnosticsError && !diagnostics)}
          >
            <RefreshCw size={15} /> Refresh diagnostics
          </button>
        </div>

        {diagnosticsError && (
          <div className="health-warning">
            <AlertTriangle size={16} />
            {diagnosticsError}
          </div>
        )}

        {!diagnostics && !diagnosticsError && (
          <p>Loading protected diagnostics...</p>
        )}

        {diagnostics && (
          <>
            <div className="diagnostics-overview">
              <div>
                <span>Diagnostics status</span>
                <strong className={
                  diagnostics.status === "healthy"
                    ? "health-connected"
                    : "health-disconnected"
                }>
                  {diagnostics.status.toUpperCase()}
                </strong>
              </div>

              <div>
                <span>Total checks</span>
                <strong>{diagnostics.summary.total}</strong>
              </div>

              <div>
                <span>Healthy checks</span>
                <strong className="health-connected">
                  {diagnostics.summary.healthy}
                </strong>
              </div>

              <div>
                <span>Degraded checks</span>
                <strong className={
                  diagnostics.summary.degraded > 0
                    ? "health-disconnected"
                    : "health-connected"
                }>
                  {diagnostics.summary.degraded}
                </strong>
              </div>
            </div>

            <div className="diagnostics-runtime">
              <h4>Runtime Information</h4>
              <p>
                <span>Service</span>
                <strong>{diagnostics.service}</strong>
              </p>
              <p>
                <span>Python version</span>
                <strong>{diagnostics.runtime.python_version}</strong>
              </p>
              <p>
                <span>Platform</span>
                <strong>{diagnostics.runtime.platform}</strong>
              </p>
              <p>
                <span>Last diagnostics timestamp</span>
                <strong>
                  {new Date(diagnostics.timestamp).toLocaleString()}
                </strong>
              </p>
            </div>

            <div className="diagnostics-checks">
              <h4>Individual Checks</h4>

              {diagnostics.checks.map((check) => (
                <div className="diagnostics-check-row" key={check.name}>
                  <div>
                    <strong>{check.name.replace(/_/g, " ")}</strong>
                    <span className={
                      check.status === "healthy"
                        ? "health-connected"
                        : "health-disconnected"
                    }>
                      {check.status.toUpperCase()}
                    </span>
                  </div>

                  {typeof check.details.usage_percent === "number" && (
                    <p>
                      Disk usage: {check.details.usage_percent}%
                      {" ? "}
                      Warning threshold: {check.details.warning_threshold}%
                    </p>
                  )}

                  {typeof check.details.python_version === "string" && (
                    <p>
                      Python: {check.details.python_version}
                    </p>
                  )}

                  {typeof check.details.implementation === "string" && (
                    <p>
                      Implementation: {check.details.implementation}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      <div className="health-alert-summary">
        <div>
          <ShieldAlert size={22} />
          <strong>{alerts.length}</strong>
          <span>Active Alerts</span>
        </div>
        <p>{alerts.length ? "Attention required: check the alerts below." : "All monitored resources are within configured thresholds."}</p>
      </div>

      {alerts.length > 0 && (
        <div className="health-alert-list">
          {alerts.map((alert, index) => (
            <div className="health-alert-item" key={index}>
              <AlertTriangle size={17} />
              {alert}
            </div>
          ))}
        </div>
      )}

      <div className="health-grid">
        <div className="health-metric">
          <div className="health-metric-heading">CPU Usage <Activity size={19} /></div>
          <div className="health-metric-value">{data.system.cpu_percent}%</div>
          <div className="health-metric-detail">{data.system.cpu_count} logical cores</div>
          <div className="health-progress"><div style={{ width: `${Math.min(100, data.system.cpu_percent)}%` }} /></div>
        </div>
        <div className="health-metric">
          <div className="health-metric-heading">Memory Usage <Activity size={19} /></div>
          <div className="health-metric-value">{data.system.memory.percent}%</div>
          <div className="health-metric-detail">{data.system.memory.used_mb.toFixed(0)} / {data.system.memory.total_mb.toFixed(0)} MB</div>
          <div className="health-progress"><div style={{ width: `${Math.min(100, data.system.memory.percent)}%` }} /></div>
        </div>
        <div className="health-metric">
          <div className="health-metric-heading">Disk Usage <Activity size={19} /></div>
          <div className="health-metric-value">{data.system.disk.percent}%</div>
          <div className="health-metric-detail">{data.system.disk.used_gb} / {data.system.disk.total_gb} GB</div>
          <div className="health-progress"><div style={{ width: `${Math.min(100, data.system.disk.percent)}%` }} /></div>
        </div>
        <div className="health-metric">
          <div className="health-metric-heading">Backend Uptime <Clock size={19} /></div>
          <div className="health-metric-value">{formatUptime(data.uptime_seconds)}</div>
          <div className="health-metric-detail">Since backend startup</div>
        </div>
      </div>

      <div className="health-details-grid">
        <div className="health-detail-card">
          <h3>System Information</h3>
          <p><span>Operating System</span><strong>{data.system.platform} {data.system.platform_release}</strong></p>
          <p><span>Architecture</span><strong>{data.system.architecture}</strong></p>
          <p><span>Processor</span><strong>{data.system.processor}</strong></p>
          <p><span>Available RAM</span><strong>{data.system.memory.available_mb.toFixed(0)} MB</strong></p>
          <p><span>Free Disk</span><strong>{data.system.disk.free_gb} GB</strong></p>
        </div>
        <div className="health-detail-card">
          <h3><Database size={18} /> Service Status</h3>
          <p><span>Backend API</span><strong className="health-connected">Connected</strong></p>
          <p><span>Database</span><strong className={data.database.connected ? "health-connected" : "health-disconnected"}>{data.database.status}</strong></p>
          <p><span>Monitoring</span><strong>Active</strong></p>
          <p><span>Refresh Interval</span><strong>15 seconds</strong></p>
        </div>
      </div>

      <div className="health-detail-card health-events-card">
        <div className="health-events-heading">
          <h3><Activity size={19} /> Health Event Log</h3>
          <div className="health-event-actions">
            <button onClick={exportHealthEvents} disabled={events.length === 0}>
              Export CSV
            </button>
            <button onClick={() => setEvents([])}>
              <Trash2 size={15} /> Clear Log
            </button>
          </div>
        </div>
        {events.length === 0 ? (
          <p>No health events recorded yet.</p>
        ) : events.map((event, index) => (
          <div className="health-event-row" key={`${event.id}-${index}-${event.time}`}>
            <span className={`health-event-dot ${event.level}`} />
            <span className="health-event-message">{event.message}</span>
            <span className="health-event-time">{event.time}</span>
          </div>
        ))}
        <p className="health-event-note">Latest 20 checks · Automatically updated every 15 seconds · Session-only history</p>
      </div>
    </section>
  );
}
