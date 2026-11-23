import { useEffect, useState } from "react";
import type { PerformanceMetric } from "../services/performanceMonitor";

declare global {
  interface Window {
    __infrasentryPerformance?: PerformanceMetric[];
  }
}

function PerformanceDashboard() {
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);
  const [filter, setFilter] = useState("all");

  const refreshMetrics = () => {
    setMetrics([...(window.__infrasentryPerformance ?? [])]);
  };

  useEffect(() => {
    refreshMetrics();

    const handleMetric = () => refreshMetrics();

    window.addEventListener("infrasentry:performance", handleMetric);

    return () => {
      window.removeEventListener("infrasentry:performance", handleMetric);
    };
  }, []);

  const apiMetrics = metrics.filter(
    (m) => m.type === "api-request" || m.type === "api-error"
  );

  const successful = apiMetrics.filter((m) => m.success);
  const failed = apiMetrics.filter((m) => !m.success);

  const average = apiMetrics.length
    ? apiMetrics.reduce((sum, m) => sum + m.durationMs, 0) / apiMetrics.length
    : 0;

  const pageLoads = metrics.filter((m) => m.type === "page-load");

  const filteredMetrics = metrics.filter((m) => {
    if (filter === "api") return m.type === "api-request" || m.type === "api-error";
    if (filter === "errors") return !m.success;
    if (filter === "page") return m.type === "page-load";
    return true;
  }).slice().reverse();

  const cardStyle: React.CSSProperties = {
    padding: "20px",
    borderRadius: "12px",
    border: "1px solid var(--border-color, #e5e7eb)",
    background: "var(--card-bg, #ffffff)",
    minWidth: 0,
  };

  const muted: React.CSSProperties = {
    color: "var(--text-secondary, #64748b)",
  };

  const exportCSV = () => {
    if (!metrics.length) {
      alert("No performance metrics available to export.");
      return;
    }

    const headers = [
      "Type",
      "Name",
      "Duration (ms)",
      "Timestamp",
      "Status",
      "Success",
      "Details",
    ];

    const escapeCSV = (value: unknown) =>
      `"${String(value ?? "").replace(/"/g, '""')}"`;

    const rows = metrics.map((m) => [
      m.type,
      m.name,
      m.durationMs,
      m.timestamp,
      m.status ?? "",
      m.success,
      m.details ?? "",
    ]);

    const csv = [
      headers.map(escapeCSV).join(","),
      ...rows.map((row) => row.map(escapeCSV).join(",")),
    ].join("\r\n");

    const blob = new Blob(["\uFEFF", csv], {
      type: "text/csv;charset=utf-8;",
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = `infrasentry-performance-${new Date()
      .toISOString()
      .replace(/[:.]/g, "-")}.csv`;

    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };

  const clearMetrics = () => {
    if (!window.confirm("Clear all performance metrics from this browser session?")) {
      return;
    }

    window.__infrasentryPerformance = [];
    refreshMetrics();
  };

  const slowest = [...apiMetrics]
    .sort((a, b) => b.durationMs - a.durationMs)
    .slice(0, 5);

  return (
    <div style={{ display: "grid", gap: "22px" }}>
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexWrap: "wrap",
        gap: "12px",
      }}>
        <div>
          <h2 style={{ margin: 0 }}>Performance Monitoring</h2>
          <p style={muted}>
            Application performance and API diagnostics.
          </p>
        </div>

        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
          <button onClick={refreshMetrics}>Refresh</button>
          <button onClick={exportCSV} disabled={!metrics.length}>
            Export CSV
          </button>
          <button onClick={clearMetrics} disabled={!metrics.length}>
            Clear Metrics
          </button>
        </div>
      </div>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(165px, 1fr))",
        gap: "14px",
      }}>
        <div style={cardStyle}>
          <p style={muted}>Total Events</p>
          <h2>{metrics.length}</h2>
        </div>
        <div style={cardStyle}>
          <p style={muted}>API Requests</p>
          <h2>{apiMetrics.length}</h2>
        </div>
        <div style={cardStyle}>
          <p style={muted}>Successful</p>
          <h2 style={{ color: "#16a34a" }}>{successful.length}</h2>
        </div>
        <div style={cardStyle}>
          <p style={muted}>Failed</p>
          <h2 style={{ color: "#dc2626" }}>{failed.length}</h2>
        </div>
        <div style={cardStyle}>
          <p style={muted}>Average API Time</p>
          <h2>{average.toFixed(2)} ms</h2>
        </div>
        <div style={cardStyle}>
          <p style={muted}>Page Load Samples</p>
          <h2>{pageLoads.length}</h2>
        </div>
      </div>

      <section style={cardStyle}>
        <h3>Slowest API Requests</h3>

        {slowest.length === 0 ? (
          <p style={muted}>No API request data recorded yet.</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", textAlign: "left", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={{ padding: "10px" }}>Request</th>
                  <th style={{ padding: "10px" }}>Duration</th>
                  <th style={{ padding: "10px" }}>Result</th>
                </tr>
              </thead>
              <tbody>
                {slowest.map((m, i) => (
                  <tr key={`${m.timestamp}-${i}`}>
                    <td style={{ padding: "10px", overflowWrap: "anywhere" }}>{m.name}</td>
                    <td style={{ padding: "10px" }}>{m.durationMs.toFixed(2)} ms</td>
                    <td style={{ padding: "10px", color: m.success ? "#16a34a" : "#dc2626" }}>
                      {m.status ?? (m.success ? "Success" : "Failed")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section style={cardStyle}>
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "12px",
        }}>
          <h3>Performance Event History</h3>

          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            style={{ padding: "9px", borderRadius: "8px" }}
          >
            <option value="all">All Events</option>
            <option value="api">API Requests</option>
            <option value="errors">Failed Events</option>
            <option value="page">Page Loads</option>
          </select>
        </div>

        {filteredMetrics.length === 0 ? (
          <p style={muted}>No events available for this filter.</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", textAlign: "left", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={{ padding: "10px" }}>Type</th>
                  <th style={{ padding: "10px" }}>Name</th>
                  <th style={{ padding: "10px" }}>Duration</th>
                  <th style={{ padding: "10px" }}>Result</th>
                  <th style={{ padding: "10px" }}>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {filteredMetrics.map((m, i) => (
                  <tr key={`${m.timestamp}-${i}`}>
                    <td style={{ padding: "10px" }}>{m.type}</td>
                    <td style={{ padding: "10px", overflowWrap: "anywhere" }}>{m.name}</td>
                    <td style={{ padding: "10px" }}>{m.durationMs.toFixed(2)} ms</td>
                    <td style={{ padding: "10px", color: m.success ? "#16a34a" : "#dc2626" }}>
                      {m.success ? "Success" : "Failed"}
                    </td>
                    <td style={{ padding: "10px", whiteSpace: "nowrap" }}>
                      {new Date(m.timestamp).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <p style={{ ...muted, fontSize: "12px" }}>
        Metrics are held in browser memory, with a maximum of 200 events.
        Export your report before reloading or clearing the session.
      </p>
    </div>
  );
}

export default PerformanceDashboard;
