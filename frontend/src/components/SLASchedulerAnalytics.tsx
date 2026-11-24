import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  CheckCircle,
  Clock,
  RefreshCw,
  Server,
  XCircle,
} from "lucide-react";
import { API_BASE, authenticatedFetch } from "../services/authService";
import "./SLASchedulerAnalytics.css";

interface SchedulerMetrics {
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  average_duration_ms: number;
  last_run: string | null;
  last_status: string;
  history: {
    timestamp: string;
    status: string;
    duration_ms: number;
    message?: string | null;
  }[];
  retained_history: number;
}

interface SchedulerStatus {
  running: boolean;
  interval_seconds: number;
  next_run_time?: string | null;
}

export default function SLASchedulerAnalytics() {
  const [metrics, setMetrics] = useState<SchedulerMetrics | null>(null);
  const [scheduler, setScheduler] = useState<SchedulerStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadData = useCallback(async () => {
    try {
      const [metricsResponse, statusResponse] = await Promise.all([
        authenticatedFetch(`${API_BASE}/api/v1/sla/scheduler-analytics`),
        authenticatedFetch(`${API_BASE}/api/v1/sla/scheduler-status`),
      ]);

      if (!metricsResponse.ok || !statusResponse.ok) {
        throw new Error("Unable to load scheduler analytics.");
      }

      const [metricsData, statusData] = await Promise.all([
        metricsResponse.json(),
        statusResponse.json(),
      ]);

      setMetrics(metricsData);
      setScheduler(statusData);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analytics unavailable.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
    const timer = window.setInterval(() => void loadData(), 30000);
    return () => window.clearInterval(timer);
  }, [loadData]);

  const successRate = metrics && metrics.total_runs > 0
    ? (metrics.successful_runs / metrics.total_runs) * 100
    : 0;

  return (
    <section className="sla-analytics-page">
      <div className="sla-analytics-header">
        <div>
          <h2>SLA Scheduler Analytics</h2>
          <p>Background escalation job performance and reliability</p>
        </div>
        <button onClick={() => void loadData()} disabled={loading}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {error && <div className="sla-analytics-error">{error}</div>}

      <div className="sla-analytics-status">
        <span className={scheduler?.running ? "online" : "offline"} />
        Scheduler {scheduler?.running ? "Running" : "Stopped"}
        <small>Interval: {scheduler?.interval_seconds ?? 60}s</small>
      </div>

      {loading && !metrics ? (
        <p className="sla-analytics-loading">Loading analytics...</p>
      ) : metrics ? (
        <>
          <div className="sla-analytics-kpis">
            <article>
              <Activity size={21} />
              <span>Total executions</span>
              <strong>{metrics.total_runs}</strong>
            </article>
            <article>
              <CheckCircle size={21} />
              <span>Successful</span>
              <strong>{metrics.successful_runs}</strong>
            </article>
            <article>
              <XCircle size={21} />
              <span>Failed</span>
              <strong>{metrics.failed_runs}</strong>
            </article>
            <article>
              <Clock size={21} />
              <span>Average duration</span>
              <strong>{Number(metrics.average_duration_ms).toFixed(2)} ms</strong>
            </article>
          </div>

          <div className="sla-analytics-card">
            <div className="sla-analytics-card-heading">
              <h3>Execution Reliability</h3>
              <strong>{successRate.toFixed(1)}%</strong>
            </div>
            <div className="sla-analytics-progress">
              <div style={{ width: `${successRate}%` }} />
            </div>
            <p>
              {metrics.successful_runs} successful out of {metrics.total_runs} executions
            </p>
          </div>

          <div className="sla-analytics-card">
            <h3>Scheduler Information</h3>
            <div className="sla-analytics-info">
              <span><Server size={15} /> Last status</span>
              <strong>{metrics.last_status}</strong>
            </div>
            <div className="sla-analytics-info">
              <span>Last execution</span>
              <strong>
                {metrics.last_run
                  ? new Date(metrics.last_run).toLocaleString()
                  : "No executions yet"}
              </strong>
            </div>
            <div className="sla-analytics-info">
              <span>Next scheduled run</span>
              <strong>
                {scheduler?.next_run_time
                  ? new Date(scheduler.next_run_time).toLocaleString()
                  : "Not available"}
              </strong>
            </div>
          </div>

          <div className="sla-analytics-card">
            <h3>Recent Execution History</h3>
            {metrics.history.length === 0 ? (
              <p className="sla-analytics-empty">No scheduler executions recorded yet.</p>
            ) : (
              <div className="sla-analytics-table-wrap">
                <table className="sla-analytics-table">
                  <thead>
                    <tr>
                      <th>Timestamp</th>
                      <th>Status</th>
                      <th>Duration</th>
                      <th>Message</th>
                    </tr>
                  </thead>
                  <tbody>
                    {metrics.history.slice().reverse().map((item, index) => (
                      <tr key={`${item.timestamp}-${index}`}>
                        <td>{new Date(item.timestamp).toLocaleString()}</td>
                        <td>
                          <span className={`sla-run-status ${item.status}`}>
                            {item.status}
                          </span>
                        </td>
                        <td>{Number(item.duration_ms).toFixed(2)} ms</td>
                        <td>{item.message || "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <small>Retained records: {metrics.retained_history}/100</small>
          </div>
        </>
      ) : (
        <p className="sla-analytics-empty">Analytics data is unavailable.</p>
      )}
    </section>
  );
}
