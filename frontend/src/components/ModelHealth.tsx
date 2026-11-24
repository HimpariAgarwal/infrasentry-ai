import { authenticatedFetch } from "../services/apiClient";
import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  CheckCircle,
  XCircle,
  RefreshCw,
  Clock,
  Server,
} from "lucide-react";
import "./ModelHealth.css";

const API = "http://127.0.0.1:8000";

type HealthState = "checking" | "online" | "offline";

function ModelHealth() {
  const [status, setStatus] = useState<HealthState>("checking");
  const [modelInfo, setModelInfo] = useState<Record<string, unknown> | null>(null);
  const [responseTime, setResponseTime] = useState<number | null>(null);
  const [lastChecked, setLastChecked] = useState<string>("Not checked yet");
  const [error, setError] = useState("");

  const checkHealth = useCallback(async () => {
    setStatus("checking");
    setError("");

    const start = performance.now();

    try {
      const response = await authenticatedFetch(`${API}/api/v1/model-info`, {
        signal: AbortSignal.timeout(10000),
      });

      const elapsed = Math.round(performance.now() - start);

      if (!response.ok) {
        throw new Error(`API returned HTTP ${response.status}`);
      }

      const data: unknown = await response.json();

      setModelInfo(
        data && typeof data === "object"
          ? data as Record<string, unknown>
          : { response: data }
      );

      setResponseTime(elapsed);
      setStatus("online");
    } catch (err) {
      setStatus("offline");
      setModelInfo(null);
      setResponseTime(null);
      setError(
        err instanceof Error ? err.message : "Unable to connect to backend."
      );
    } finally {
      setLastChecked(new Date().toLocaleString());
    }
  }, []);

  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  return (
    <div className="model-health-page">
      <div className="health-heading">
        <div>
          <span className="health-eyebrow">SYSTEM MONITORING</span>
          <h2>AI Model Health</h2>
          <p>Monitor backend connectivity and AI model information.</p>
        </div>

        <button className="health-refresh" onClick={checkHealth}>
          <RefreshCw size={16} />
          Check Again
        </button>
      </div>

      <div className="health-grid">
        <div className="health-card">
          <div className="health-card-top">
            <span>Backend Status</span>
            <Server size={20} />
          </div>

          <div className={`health-status ${status}`}>
            {status === "online" ? (
              <CheckCircle size={25} />
            ) : status === "offline" ? (
              <XCircle size={25} />
            ) : (
              <RefreshCw size={25} className="health-spin" />
            )}

            <strong>
              {status === "online"
                ? "Connected"
                : status === "offline"
                  ? "Offline"
                  : "Checking..."}
            </strong>
          </div>

          <p className="health-muted">FastAPI model information endpoint</p>
        </div>

        <div className="health-card">
          <div className="health-card-top">
            <span>API Response Time</span>
            <Activity size={20} />
          </div>

          <div className="health-metric">
            {responseTime !== null ? `${responseTime} ms` : "--"}
          </div>

          <p className="health-muted">Measured during latest health check</p>
        </div>

        <div className="health-card">
          <div className="health-card-top">
            <span>Last Checked</span>
            <Clock size={20} />
          </div>

          <div className="health-last-checked">{lastChecked}</div>
          <p className="health-muted">Local system time</p>
        </div>
      </div>

      {error && (
        <div className="health-error">
          <XCircle size={18} />
          <div>
            <strong>Connection failed</strong>
            <p>{error}</p>
            <p>Ensure the FastAPI backend is running on port 8000.</p>
          </div>
        </div>
      )}

      <section className="health-details">
        <div className="health-details-heading">
          <div>
            <h3>Model Information</h3>
            <p>Actual response from the backend API</p>
          </div>
          <Activity size={21} />
        </div>

        {status === "checking" && (
          <p className="health-empty">Checking model information...</p>
        )}

        {status === "offline" && (
          <p className="health-empty">Model information is unavailable.</p>
        )}

        {status === "online" && modelInfo && (
          <div className="health-info-list">
            {Object.entries(modelInfo).map(([key, value]) => (
              <div className="health-info-row" key={key}>
                <span>{key.replaceAll("_", " ")}</span>
                <strong>
                  {typeof value === "object"
                    ? JSON.stringify(value)
                    : String(value ?? "N/A")}
                </strong>
              </div>
            ))}
          </div>
        )}
      </section>

      <div className="health-note">
        <Activity size={17} />
        <span>
          This monitor checks API availability. It does not measure model
          accuracy or guarantee correct damage detection.
        </span>
      </div>
    </div>
  );
}

export default ModelHealth;
