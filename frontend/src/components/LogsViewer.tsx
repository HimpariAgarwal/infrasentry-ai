import { useCallback, useEffect, useState } from "react";
import { Download, RefreshCw, Search, Trash2, FileText } from "lucide-react";
import "./LogsViewer.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
}

export default function LogsViewer() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [search, setSearch] = useState("");
  const [level, setLevel] = useState("ALL");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ search, level, limit: "500" });
      const response = await fetch(`${API_BASE}/api/v1/logs?${params}`);
      if (!response.ok) throw new Error(`API error ${response.status}`);
      const result = await response.json();
      setLogs(result.logs || []);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load logs");
    } finally {
      setLoading(false);
    }
  }, [search, level]);

  useEffect(() => {
    fetchLogs();
    const timer = window.setInterval(fetchLogs, 10000);
    return () => window.clearInterval(timer);
  }, [fetchLogs]);

  const clearLogs = async () => {
    if (!window.confirm("Are you sure you want to clear all API logs?")) return;
    try {
      const response = await fetch(`${API_BASE}/api/v1/logs`, { method: "DELETE" });
      if (!response.ok) throw new Error("Could not clear logs");
      await fetchLogs();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Clear failed");
    }
  };

  const downloadLogs = () => {
    window.open(`${API_BASE}/api/v1/logs/export`, "_blank");
  };

  return (
    <section className="logs-page">
      <div className="logs-header">
        <div>
          <h2><FileText size={22} /> API Logs Viewer</h2>
          <p>Backend request activity and diagnostic events</p>
        </div>
        <div className="logs-actions">
          <button onClick={fetchLogs}><RefreshCw size={15} /> Refresh</button>
          <button onClick={downloadLogs}><Download size={15} /> Export CSV</button>
          <button onClick={clearLogs}><Trash2 size={15} /> Clear</button>
        </div>
      </div>

      <div className="logs-toolbar">
        <div className="logs-search">
          <Search size={17} />
          <input
            value={search}
            onChange={event => setSearch(event.target.value)}
            placeholder="Search endpoint, method or status..."
          />
        </div>
        <select value={level} onChange={event => setLevel(event.target.value)}>
          <option value="ALL">All levels</option>
          <option value="INFO">INFO</option>
          <option value="ERROR">ERROR</option>
          <option value="WARNING">WARNING</option>
        </select>
      </div>

      {error && <div className="logs-error">{error}</div>}

      <div className="logs-summary">
        <strong>{logs.length}</strong>
        <span>Matching log entries</span>
        <span>{loading ? "Refreshing..." : "Auto-refresh: 10 seconds"}</span>
      </div>

      <div className="logs-table-wrap">
        <table className="logs-table">
          <thead>
            <tr><th>Timestamp</th><th>Level</th><th>Event</th></tr>
          </thead>
          <tbody>
            {logs.map((log, index) => (
              <tr key={`${log.timestamp}-${index}`}>
                <td>{log.timestamp}</td>
                <td><span className={`log-level ${log.level.toLowerCase()}`}>{log.level}</span></td>
                <td>{log.message}</td>
              </tr>
            ))}
            {logs.length === 0 && (
              <tr><td colSpan={3} className="logs-empty">No log entries found.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
