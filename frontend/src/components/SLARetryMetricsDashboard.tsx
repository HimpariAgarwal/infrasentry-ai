import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  CheckCircle,
  Clock,
  RefreshCw,
  XCircle,
} from "lucide-react";
import { API_BASE, authenticatedFetch } from "../services/authService";
import {
  exportRetryMetricsCSV,
  exportRetryMetricsPDF,
} from "../services/slaRetryReportService";
import "./SLARetryMetricsDashboard.css";

interface RetryRun {
  timestamp: string;
  status: string;
  attempts: number;
  duration_seconds: number;
  error: string | null;
}

interface RetryMetrics {
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  total_attempts: number;
  average_duration_seconds: number;
  last_run: RetryRun | null;
  history: RetryRun[];
}

const EMPTY_METRICS: RetryMetrics = {
  total_runs: 0,
  successful_runs: 0,
  failed_runs: 0,
  total_attempts: 0,
  average_duration_seconds: 0,
  last_run: null,
  history: [],
};

export default function SLARetryMetricsDashboard() {
  const [metrics, setMetrics] = useState<RetryMetrics>(EMPTY_METRICS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadMetrics = useCallback(async () => {
    try {
      const response = await authenticatedFetch(
        `${API_BASE}/api/v1/sla/retry-metrics`
      );

      if (!response.ok) {
        throw new Error(`Request failed (${response.status})`);
      }

      const data = await response.json();
      setMetrics({
        ...EMPTY_METRICS,
        ...data,
        history: Array.isArray(data.history) ? data.history : [],
      });
      setError("");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to load retry metrics"
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadMetrics();
    const timer = window.setInterval(() => {
      void loadMetrics();
    }, 30000);

    return () => window.clearInterval(timer);
  }, [loadMetrics]);

  const successRate =
    metrics.total_runs > 0
      ? ((metrics.successful_runs / metrics.total_runs) * 100).toFixed(1)
      : "0.0";

  return (
    <section className="sla-retry-dashboard">
      <div className="sla-retry-header">
        <div>
          <h2>SLA Retry Monitoring</h2>
          <p>Execution reliability and retry statistics</p>
        </div>
        <button
          className="sla-retry-export"
          onClick={() => exportRetryMetricsCSV(metrics)}
          disabled={loading || metrics.total_runs === 0}
        >
          Export CSV
        </button>
        <button
          className="sla-retry-export"
          onClick={() => exportRetryMetricsPDF(metrics)}
          disabled={loading || metrics.total_runs === 0}
        >
          Export PDF
        </button>
        <button
          className="sla-retry-refresh"
          onClick={() => void loadMetrics()}
          disabled={loading}
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="sla-retry-error" role="alert">
          {error}
        </div>
      )}

      <div className="sla-retry-kpis">
        <article className="sla-retry-card">
          <Activity size={21} />
          <span>Total Runs</span>
          <strong>{metrics.total_runs}</strong>
        </article>

        <article className="sla-retry-card">
          <CheckCircle size={21} />
          <span>Successful</span>
          <strong>{metrics.successful_runs}</strong>
        </article>

        <article className="sla-retry-card">
          <XCircle size={21} />
          <span>Failed</span>
          <strong>{metrics.failed_runs}</strong>
        </article>

        <article className="sla-retry-card">
          <Clock size={21} />
          <span>Avg Duration</span>
          <strong>{metrics.average_duration_seconds.toFixed(2)}s</strong>
        </article>
      </div>

      <div className="sla-retry-summary">
        <div>
          <span>Success Rate</span>
          <strong>{successRate}%</strong>
        </div>
        <div>
          <span>Total Attempts</span>
          <strong>{metrics.total_attempts}</strong>
        </div>
        <div>
          <span>Last Run</span>
          <strong>
            {metrics.last_run
              ? new Date(metrics.last_run.timestamp).toLocaleString()
              : "No runs yet"}
          </strong>
        </div>
      </div>

      <div className="sla-retry-history">
        <h3>Recent Retry History</h3>

        {loading && metrics.history.length === 0 ? (
          <p>Loading retry metrics...</p>
        ) : metrics.history.length === 0 ? (
          <p>No retry execution records available.</p>
        ) : (
          <div className="sla-retry-table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Status</th>
                  <th>Attempts</th>
                  <th>Duration</th>
                  <th>Error</th>
                </tr>
              </thead>
              <tbody>
                {[...metrics.history].reverse().map((run, index) => (
                  <tr key={`${run.timestamp}-${index}`}>
                    <td>{new Date(run.timestamp).toLocaleString()}</td>
                    <td>
                      <span
                        className={`sla-retry-status ${
                          run.status === "success" ? "success" : "failed"
                        }`}
                      >
                        {run.status}
                      </span>
                    </td>
                    <td>{run.attempts}</td>
                    <td>{run.duration_seconds.toFixed(2)}s</td>
                    <td>{run.error || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
