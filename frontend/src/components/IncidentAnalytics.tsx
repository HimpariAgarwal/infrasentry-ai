import { useCallback, useEffect, useState } from "react";
import {
  Activity, AlertTriangle, CheckCircle, Clock, RefreshCw
} from "lucide-react";
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, PieChart, Pie, Cell
} from "recharts";
import { authenticatedFetch, API_BASE } from "../services/authService";
import "./IncidentAnalytics.css";

interface Analytics {
  total_incidents: number;
  open_incidents: number;
  investigating_incidents: number;
  resolved_incidents: number;
  resolution_rate: number;
  severity_distribution: Record<string, number>;
  status_distribution: Record<string, number>;
  daily_trend: { date: string; count: number }[];
  last_7_days_count: number;
  generated_at: string;
}

const COLORS = ["#ef4444", "#f59e0b", "#3b82f6", "#22c55e"];

export default function IncidentAnalytics() {
  const [data, setData] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadAnalytics = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await authenticatedFetch(
        `${API_BASE}/api/v1/incidents/analytics`
      );

      if (!response.ok) throw new Error("Unable to load incident analytics.");

      setData(await response.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAnalytics();
  }, [loadAnalytics]);

  const severityData = data
    ? Object.entries(data.severity_distribution).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  const statusData = data
    ? Object.entries(data.status_distribution).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  return (
    <section className="incident-analytics">
      <div className="incident-analytics-header">
        <div>
          <h2><Activity size={23} /> Incident Analytics</h2>
          <p>Security incident performance and trends.</p>
        </div>
        <button onClick={loadAnalytics} disabled={loading}>
          <RefreshCw size={16} /> Refresh
        </button>
      </div>

      {error && <p className="incident-analytics-error">{error}</p>}
      {loading && <p>Loading analytics...</p>}

      {data && (
        <>
          <div className="incident-analytics-kpis">
            <div><Activity /><span>Total Incidents</span><strong>{data.total_incidents}</strong></div>
            <div><AlertTriangle /><span>Open Incidents</span><strong>{data.open_incidents}</strong></div>
            <div><Clock /><span>Investigating</span><strong>{data.investigating_incidents}</strong></div>
            <div><CheckCircle /><span>Resolved</span><strong>{data.resolved_incidents}</strong></div>
          </div>

          <div className="incident-resolution">
            <div>
              <span>Resolution Rate</span>
              <strong>{data.resolution_rate}%</strong>
            </div>
            <div className="resolution-track">
              <div style={{ width: `${Math.min(100, data.resolution_rate)}%` }} />
            </div>
            <small>{data.last_7_days_count} incidents in the last 7 days</small>
          </div>

          <div className="incident-analytics-grid">
            <div className="incident-chart-card">
              <h3>7-Day Incident Trend</h3>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={data.daily_trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3b82f6" radius={[5, 5, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="incident-chart-card">
              <h3>Severity Distribution</h3>
              {severityData.length > 0 ? (
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie
                      data={severityData}
                      dataKey="value"
                      nameKey="name"
                      outerRadius={95}
                      label
                    >
                      {severityData.map((item, index) => (
                        <Cell
                          key={item.name}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : <p>No severity data available.</p>}
            </div>

            <div className="incident-chart-card">
              <h3>Status Distribution</h3>
              {statusData.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={statusData}
                      dataKey="value"
                      nameKey="name"
                      outerRadius={85}
                      label
                    >
                      {statusData.map((item, index) => (
                        <Cell
                          key={item.name}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : <p>No status data available.</p>}
            </div>
          </div>

          <p className="incident-analytics-updated">
            Last generated: {new Date(data.generated_at).toLocaleString()}
          </p>
        </>
      )}
    </section>
  );
}
