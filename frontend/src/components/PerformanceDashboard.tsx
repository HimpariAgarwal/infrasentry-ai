import { useEffect, useState } from "react";
import type { PerformanceMetric } from "../services/performanceMonitor";

function PerformanceDashboard() {
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    const loadMetrics = () => {
      setMetrics([...(window.__infrasentryPerformance ?? [])]);
    };

    loadMetrics();

    const handleMetric = () => loadMetrics();

    window.addEventListener("infrasentry:performance", handleMetric);
    return () => {
      window.removeEventListener("infrasentry:performance", handleMetric);
    };
  }, []);

  const apiMetrics = metrics.filter(
    (metric) => metric.type === "api-request" || metric.type === "api-error"
  );

  const successful = apiMetrics.filter((metric) => metric.success);
  const failed = apiMetrics.filter((metric) => !metric.success);

  const average = apiMetrics.length
    ? apiMetrics.reduce((sum, metric) => sum + metric.durationMs, 0) /
      apiMetrics.length
    : 0;

  const slowest = [...apiMetrics].sort(
    (a, b) => b.durationMs - a.durationMs
  ).slice(0, 5);

  const pageLoads = metrics.filter((metric) => metric.type === "page-load");

  const visibleMetrics = metrics.filter((metric) => {
    if (filter === "api") {
      return metric.type === "api-request" || metric.type === "api-error";
    }
    if (filter === "errors") return !metric.success;
    if (filter === "page") return metric.type === "page-load";
    return true;
  }).slice().reverse();

  const cardStyle = {
    background: "var(--card-bg, #ffffff)",
    border: "1px solid var(--border-color, #e5e7eb)",
    borderRadius: "12px",
    padding: "20px",
    minWidth: 0,
  };

  const muted = { color: "var(--text-secondary, #64748b)" };

  return (
    <div style={{ display: "grid", gap: "22px" }}>
      <div>
        <h2 style={{ margin: 0 }}>Performance Monitoring</h2>
        <p style={muted}>
          Live frontend and API performance metrics collected in this browser session.
        </p>
      </div>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))",
        gap: "14px"
      }}>
        <div style={cardStyle}>
          <p style={muted}>Total API Requests</p>
          <h2>{apiMetrics.length}</h2>
        </div>
        <div style={cardStyle}>
          <p style={muted}>Successful Requests</p>
          <h2 style={{ color: "#16a34a" }}>{successful.length}</h2>
        </div>
        <div style={cardStyle}>
          <p style={muted}>Failed Requests</p>
          <h2 style={{ color: "#dc2626" }}>{failed.length}</h2>
        </div>
        <div style={cardStyle}>
          <p style={muted}>Average API Duration</p>
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
          <p style={muted}>No API requests recorded yet. Visit Detection History or Model Health to generate metrics.</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
              <thead>
                <tr>
                  <th style={{ padding: "10px" }}>Request</th>
                  <th style={{ padding: "10px" }}>Duration</th>
                  <th style={{ padding: "10px" }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {slowest.map((metric, index) => (
                  <tr key={`${metric.timestamp}-${index}`}>
                    <td style={{ padding: "10px", overflowWrap: "anywhere" }}>{metric.name}</td>
                    <td style={{ padding: "10px" }}>{metric.durationMs.toFixed(2)} ms</td>
                    <td style={{ padding: "10px", color: metric.success ? "#16a34a" : "#dc2626" }}>
                      {metric.status ?? (metric.success ? "Success" : "Failed")}
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
          gap: "12px"
        }}>
          <h3>Recent Performance Events</h3>
          <select
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
            style={{ padding: "9px", borderRadius: "8px" }}
          >
            <option value="all">All Events</option>
            <option value="api">API Requests</option>
            <option value="errors">Failed Events</option>
            <option value="page">Page Loads</option>
          </select>
        </div>

        {visibleMetrics.length === 0 ? (
          <p style={muted}>No performance events match this filter.</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
              <thead>
                <tr>
                  <th style={{ padding: "10px" }}>Type</th>
                  <th style={{ padding: "10px" }}>Name</th>
                  <th style={{ padding: "10px" }}>Duration</th>
                  <th style={{ padding: "10px" }}>Result</th>
                  <th style={{ padding: "10px" }}>Time</th>
                </tr>
              </thead>
              <tbody>
                {visibleMetrics.map((metric, index) => (
                  <tr key={`${metric.timestamp}-${index}`}>
                    <td style={{ padding: "10px" }}>{metric.type}</td>
                    <td style={{ padding: "10px", overflowWrap: "anywhere" }}>{metric.name}</td>
                    <td style={{ padding: "10px" }}>{metric.durationMs.toFixed(2)} ms</td>
                    <td style={{ padding: "10px", color: metric.success ? "#16a34a" : "#dc2626" }}>
                      {metric.success ? "Success" : "Failed"}
                    </td>
                    <td style={{ padding: "10px", whiteSpace: "nowrap" }}>
                      {new Date(metric.timestamp).toLocaleTimeString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <p style={{ ...muted, fontSize: "12px" }}>
        Metrics are collected locally in browser memory (maximum 200 events).
        They reset when the page is reloaded. This dashboard measures observed
        request timing, not backend server processing time alone.
      </p>
    </div>
  );
}

export default PerformanceDashboard;
