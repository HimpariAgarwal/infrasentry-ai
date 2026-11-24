import { useCallback, useEffect, useState } from "react";
import { Clock3, RefreshCw, ShieldCheck, Zap } from "lucide-react";
import { API_BASE, authenticatedFetch } from "../services/authService";
import "./SLARetryProfilesDashboard.css";

interface RetryProfile {
  name: string;
  max_attempts: number;
  initial_delay: number;
  backoff_factor: number;
}

interface ProfilesResponse {
  profiles: RetryProfile[];
  total: number;
}

const PROFILE_DESCRIPTIONS: Record<string, string> = {
  fast: "Short delays for quick recovery attempts.",
  standard: "Balanced retry behaviour for normal operations.",
  conservative: "Longer delays to reduce pressure during repeated failures.",
};

export default function SLARetryProfilesDashboard() {
  const [profiles, setProfiles] = useState<RetryProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadProfiles = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await authenticatedFetch(
        `${API_BASE}/api/v1/sla/retry-profiles`
      );

      if (!response.ok) {
        throw new Error(`Unable to load retry profiles (${response.status})`);
      }

      const data: ProfilesResponse = await response.json();

      if (!Array.isArray(data.profiles)) {
        throw new Error("Invalid retry profiles response.");
      }

      setProfiles(data.profiles);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Could not load retry profiles."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadProfiles();
  }, [loadProfiles]);

  return (
    <section className="sla-retry-profiles">
      <div className="sla-retry-profiles-header">
        <div>
          <h2>SLA Retry Profiles</h2>
          <p>Configured retry strategies for SLA operations</p>
        </div>

        <button
          type="button"
          className="sla-retry-profiles-refresh"
          onClick={() => void loadProfiles()}
          disabled={loading}
        >
          <RefreshCw size={16} className={loading ? "sla-spinning" : ""} />
          Refresh
        </button>
      </div>

      {loading && (
        <div className="sla-retry-profiles-state" role="status">
          Loading retry profiles...
        </div>
      )}

      {!loading && error && (
        <div className="sla-retry-profiles-error" role="alert">
          <span>{error}</span>
          <button type="button" onClick={() => void loadProfiles()}>
            Try again
          </button>
        </div>
      )}

      {!loading && !error && (
        <>
          <div className="sla-retry-profiles-summary">
            <ShieldCheck size={18} />
            <span>{profiles.length} retry profiles available</span>
          </div>

          {profiles.length === 0 ? (
            <div className="sla-retry-profiles-state">
              No retry profiles are configured.
            </div>
          ) : (
            <div className="sla-retry-profiles-grid">
              {profiles.map((profile) => (
                <article
                  className="sla-retry-profile-card"
                  key={profile.name}
                >
                  <div className="sla-retry-profile-title">
                    <div className="sla-retry-profile-icon">
                      {profile.name === "fast" ? (
                        <Zap size={19} />
                      ) : (
                        <Clock3 size={19} />
                      )}
                    </div>
                    <div>
                      <h3>{profile.name}</h3>
                      <span className="sla-retry-profile-label">
                        Retry strategy
                      </span>
                    </div>
                  </div>

                  <p className="sla-retry-profile-description">
                    {PROFILE_DESCRIPTIONS[profile.name] ??
                      "Configured retry strategy."}
                  </p>

                  <div className="sla-retry-profile-metrics">
                    <div>
                      <span>Max attempts</span>
                      <strong>{profile.max_attempts}</strong>
                    </div>
                    <div>
                      <span>Initial delay</span>
                      <strong>{profile.initial_delay}s</strong>
                    </div>
                    <div>
                      <span>Backoff factor</span>
                      <strong>{profile.backoff_factor}x</strong>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </>
      )}
    </section>
  );
}
