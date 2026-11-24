import { useCallback, useEffect, useState } from "react";
import { RefreshCw, ShieldCheck, Clock, Repeat } from "lucide-react";
import { API_BASE, authenticatedFetch } from "../services/authService";
import "./SLARetryComparisonDashboard.css";

interface RetryProfile {
  profile: string;
  max_attempts: number;
  initial_delay: number;
  backoff_factor: number;
  total_wait_seconds: number;
}

interface ComparisonResponse {
  profiles_compared: number;
  profiles: RetryProfile[];
}

export default function SLARetryComparisonDashboard() {
  const [data, setData] = useState<ComparisonResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadComparison = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await authenticatedFetch(
        `${API_BASE}/api/v1/sla/retry-comparison/`
      );

      if (!response.ok) {
        throw new Error(`Request failed (${response.status})`);
      }

      const result: ComparisonResponse = await response.json();
      setData(result);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to load retry comparison"
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadComparison();
  }, [loadComparison]);

  if (loading && !data) {
    return <section className="sla-retry-comparison"><p>Loading retry comparison...</p></section>;
  }

  return (
    <section className="sla-retry-comparison">
      <div className="sla-retry-comparison-header">
        <div>
          <h2>SLA Retry Profile Comparison</h2>
          <p>Compare retry attempts and backoff timing policies</p>
        </div>
        <button
          type="button"
          className="sla-retry-comparison-refresh"
          onClick={() => void loadComparison()}
          disabled={loading}
        >
          <RefreshCw size={16} className={loading ? "is-spinning" : ""} />
          Refresh
        </button>
      </div>

      {error && <div className="sla-retry-comparison-error">{error}</div>}

      {data && (
        <>
          <div className="sla-retry-comparison-summary">
            <ShieldCheck size={20} />
            <span>{data.profiles_compared} retry profiles available for comparison</span>
          </div>

          <div className="sla-retry-comparison-grid">
            {data.profiles.map((profile) => (
              <article
                className={`sla-retry-profile-card profile-${profile.profile}`}
                key={profile.profile}
              >
                <h3>{profile.profile.toUpperCase()}</h3>
                <p className="sla-retry-profile-description">
                  {profile.profile === "fast"
                    ? "Short retry window"
                    : profile.profile === "standard"
                      ? "Balanced retry policy"
                      : "Longer recovery window"}
                </p>

                <div className="sla-retry-profile-metric">
                  <Repeat size={17} />
                  <span>Maximum attempts</span>
                  <strong>{profile.max_attempts}</strong>
                </div>

                <div className="sla-retry-profile-metric">
                  <Clock size={17} />
                  <span>Initial delay</span>
                  <strong>{profile.initial_delay}s</strong>
                </div>

                <div className="sla-retry-profile-metric">
                  <span>×</span>
                  <span>Backoff factor</span>
                  <strong>{profile.backoff_factor}</strong>
                </div>

                <div className="sla-retry-profile-total">
                  <span>Total waiting time</span>
                  <strong>{profile.total_wait_seconds}s</strong>
                </div>
              </article>
            ))}
          </div>
        </>
      )}
    </section>
  );
}
