import { useCallback, useEffect, useState } from "react";
import { authenticatedFetch } from "../services/apiClient";
import "./ReadinessStatus.css";

interface ReadinessData {
  service: string;
  ready: boolean;
  status: "healthy" | "degraded";
  timestamp: string;
  checks: {
    total: number;
    healthy: number;
    degraded: number;
  };
}

export default function ReadinessStatus() {
  const [data, setData] = useState<ReadinessData | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState("");

  const fetchReadiness = useCallback(async () => {
    try {
      const response = await authenticatedFetch("/api/v1/readiness");
      if (!response.ok) {
        throw new Error(`Readiness API returned ${response.status}`);
      }

      const result = (await response.json()) as ReadinessData;
      setData(result);
      setError("");
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to fetch readiness");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const initial = window.setTimeout(() => void fetchReadiness(), 0);
    const interval = window.setInterval(() => void fetchReadiness(), 15000);

    return () => {
      window.clearTimeout(initial);
      window.clearInterval(interval);
    };
  }, [fetchReadiness]);

  const ready = data?.ready === true;

  return (
    <section className="readiness-panel" aria-live="polite">
      <div className="readiness-heading">
        <div>
          <h3>Live System Readiness</h3>
          <p>Backend readiness monitor</p>
        </div>
        <span className={`readiness-pill ${ready ? "is-ready" : "is-degraded"}`}>
          {loading ? "Checking..." : ready ? "READY" : "DEGRADED"}
        </span>
      </div>

      {error && (
        <div className="readiness-error" role="alert">
          {error}
        </div>
      )}

      {data && (
        <>
          <div className="readiness-status">
            <span className={`readiness-indicator ${ready ? "is-ready" : "is-degraded"}`} />
            <div>
              <strong>{ready ? "System is ready" : "System needs attention"}</strong>
              <p>{data.service} · {data.status}</p>
            </div>
          </div>

          <div className="readiness-metrics">
            <div><strong>{data.checks.total}</strong><span>Total checks</span></div>
            <div><strong>{data.checks.healthy}</strong><span>Healthy</span></div>
            <div><strong>{data.checks.degraded}</strong><span>Degraded</span></div>
          </div>

          <p className="readiness-meta">
            API timestamp: {data.timestamp ? new Date(data.timestamp).toLocaleString() : "Unavailable"}
          </p>
        </>
      )}

      <div className="readiness-footer">
        <span>{lastUpdated ? `Last refreshed: ${lastUpdated}` : "Waiting for API..."}</span>
        <button type="button" onClick={() => void fetchReadiness()} disabled={loading}>
          Refresh
        </button>
      </div>
    </section>
  );
}
