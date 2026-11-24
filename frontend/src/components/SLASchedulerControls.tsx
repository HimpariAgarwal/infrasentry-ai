import { useCallback, useEffect, useState } from "react";
import { Activity, Pause, Play, RefreshCw, Square, Zap } from "lucide-react";
import { API_BASE, authenticatedFetch } from "../services/authService";
import "./SLASchedulerControls.css";

interface SchedulerStatus {
  running: boolean;
  paused: boolean;
  job_configured: boolean;
  job_id: string;
  interval_seconds: number;
  next_run_time: string | null;
}

const ENDPOINT = `${API_BASE}/api/v1/sla`;

export default function SLASchedulerControls() {
  const [status, setStatus] = useState<SchedulerStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadStatus = useCallback(async () => {
    try {
      const response = await authenticatedFetch(`${ENDPOINT}/scheduler-status`);
      if (!response.ok) throw new Error(`Status request failed: ${response.status}`);
      setStatus(await response.json());
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load scheduler status");
    }
  }, []);

  const performAction = async (action: string) => {
    setLoading(true);
    setMessage("");
    setError("");

    try {
      const response = await authenticatedFetch(
        `${ENDPOINT}/scheduler/${action}`,
        { method: "POST" }
      );

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.detail || `Action failed: ${response.status}`);
      }

      setMessage(data.message || `Scheduler ${action} request successful`);
      await loadStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Scheduler action failed");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadStatus();
    const timer = window.setInterval(() => void loadStatus(), 15000);
    return () => window.clearInterval(timer);
  }, [loadStatus]);

  const stateLabel = !status
    ? "Unknown"
    : !status.running
      ? "Stopped"
      : status.paused
        ? "Paused"
        : "Running";

  return (
    <section className="sla-controls">
      <div className="sla-controls-header">
        <div>
          <h2><Activity size={21} /> SLA Scheduler Controls</h2>
          <p>Manage automated SLA alert generation</p>
        </div>
        <button
          className="sla-control-refresh"
          onClick={() => void loadStatus()}
          disabled={loading}
          title="Refresh status"
        >
          <RefreshCw size={17} />
        </button>
      </div>

      <div className="sla-control-status">
        <span className={`sla-control-indicator ${status?.running && !status.paused ? "active" : ""}`} />
        <span>Scheduler Status</span>
        <strong>{stateLabel}</strong>
      </div>

      <div className="sla-control-grid">
        <button disabled={loading || !status || status.running} onClick={() => void performAction("start")}>
          <Play size={17} /> Start
        </button>

        <button disabled={loading || !status?.running || status.paused} onClick={() => void performAction("pause")}>
          <Pause size={17} /> Pause
        </button>

        <button disabled={loading || !status?.running || !status.paused} onClick={() => void performAction("resume")}>
          <Play size={17} /> Resume
        </button>

        <button disabled={loading || !status?.running} onClick={() => void performAction("stop")}>
          <Square size={17} /> Stop
        </button>

        <button disabled={loading || !status?.running || status.paused} onClick={() => void performAction("trigger")}>
          <Zap size={17} /> Run Now
        </button>
      </div>

      <div className="sla-control-details">
        <div>
          <span>Job ID</span>
          <strong>{status?.job_id || "—"}</strong>
        </div>
        <div>
          <span>Interval</span>
          <strong>{status ? `${status.interval_seconds}s` : "—"}</strong>
        </div>
        <div>
          <span>Next Run</span>
          <strong>{status?.next_run_time ? new Date(status.next_run_time).toLocaleString() : "Not scheduled"}</strong>
        </div>
      </div>

      {loading && <p className="sla-control-info">Processing scheduler action...</p>}
      {message && <p className="sla-control-success">{message}</p>}
      {error && <p className="sla-control-error">{error}</p>}
    </section>
  );
}
