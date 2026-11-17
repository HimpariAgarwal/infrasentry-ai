
import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock3,
  FileText,
  MapPin,
  RefreshCw,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

type Report = {
  id: string;
  damage_type: string;
  description: string;
  latitude: number;
  longitude: number;
  severity: number;
  status: string;
  created_at: string;
};

type Analytics = {
  total_reports: number;
  status_summary: Record<string, number>;
  severity_summary: Record<string, number>;
  average_severity: number;
  recent_reports: Report[];
};

function App() {
  const [data, setData] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/analytics/summary`);

      if (!response.ok) {
        throw new Error("Unable to fetch analytics data.");
      }

      const result: Analytics = await response.json();
      setData(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const severityLabels = ["1", "2", "3", "4", "5"];

  const statusLabels = [
    { key: "submitted", label: "Submitted" },
    { key: "under_review", label: "Under Review" },
    { key: "resolved", label: "Resolved" },
  ];

  const getHighSeverity = () => {
    if (!data) return 0;

    return (
      (data.severity_summary["4"] || 0) +
      (data.severity_summary["5"] || 0)
    );
  };

  const getDate = (date: string) => {
    return new Date(date).toLocaleString();
  };

  if (loading && !data) {
    return (
      <div className="loading-screen">
        <Activity size={36} />
        <h2>Loading InfraSentry AI...</h2>
        <p>Connecting to infrastructure intelligence server</p>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="error-screen">
        <AlertTriangle size={42} />
        <h2>Connection failed</h2>
        <p>{error}</p>
        <button onClick={fetchAnalytics}>
          <RefreshCw size={17} /> Retry
        </button>
      </div>
    );
  }

  if (!data) return null;

  const cards = [
    {
      title: "Total Reports",
      value: data.total_reports,
      icon: FileText,
      className: "blue",
    },
    {
      title: "Under Review",
      value: data.status_summary.under_review || 0,
      icon: Clock3,
      className: "orange",
    },
    {
      title: "Resolved",
      value: data.status_summary.resolved || 0,
      icon: CheckCircle2,
      className: "green",
    },
    {
      title: "High Severity",
      value: getHighSeverity(),
      icon: AlertTriangle,
      className: "red",
    },
  ];

  const maxSeverity = Math.max(
    1,
    ...severityLabels.map(
      (level) => data.severity_summary[level] || 0
    )
  );

  const maxStatus = Math.max(
    1,
    ...statusLabels.map(
      (item) => data.status_summary[item.key] || 0
    )
  );

  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <ShieldCheck size={25} />
          </div>
          <div>
            <h2>InfraSentry</h2>
            <span>AI Intelligence</span>
          </div>
        </div>

        <div className="sidebar-label">MAIN MENU</div>

        <div className="nav-item active">
          <Activity size={19} />
          Dashboard
        </div>

        <div className="sidebar-footer">
          <div className="online-dot"></div>
          System Connected
          <span>API</span>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="breadcrumb">Workspace / Overview</p>
            <h1>Infrastructure Dashboard</h1>
            <p className="subtitle">
              Monitor road damage reports and infrastructure health.
            </p>
          </div>

          <button
            className="refresh-button"
            onClick={fetchAnalytics}
            disabled={loading}
          >
            <RefreshCw
              size={17}
              className={loading ? "spinning" : ""}
            />
            Refresh Data
          </button>
        </header>

        {error && (
          <div className="inline-error">
            {error} Please refresh to try again.
          </div>
        )}

        <section className="welcome-banner">
          <div>
            <span className="banner-tag">AI-POWERED MONITORING</span>
            <h2>Infrastructure Intelligence Center</h2>
            <p>
              Track, analyze and manage road damage reports
              from one centralized dashboard.
            </p>
          </div>
          <div className="banner-icon">
            <TrendingUp size={58} />
          </div>
        </section>

        <section className="stats-grid">
          {cards.map((card) => {
            const Icon = card.icon;

            return (
              <div className="stat-card" key={card.title}>
                <div className={`stat-icon ${card.className}`}>
                  <Icon size={22} />
                </div>

                <p>{card.title}</p>
                <h2>{card.value}</h2>
                <span>Live database value</span>
              </div>
            );
          })}
        </section>

        <section className="charts-grid">
          <div className="panel">
            <div className="panel-heading">
              <div>
                <h3>Severity Distribution</h3>
                <p>Reports grouped by damage severity</p>
              </div>
              <AlertTriangle size={21} />
            </div>

            <div className="bar-chart">
              {severityLabels.map((level) => {
                const count =
                  data.severity_summary[level] || 0;

                return (
                  <div className="bar-column" key={level}>
                    <span className="bar-value">{count}</span>

                    <div className="bar-track">
                      <div
                        className={`bar-fill severity-${level}`}
                        style={{
                          height: `${(count / maxSeverity) * 100}%`,
                        }}
                      />
                    </div>

                    <span className="bar-label">
                      Level {level}
                    </span>
                  </div>
                );
              })}
            </div>

            <p className="chart-note">
              Severity 1 = Low damage · Severity 5 = Critical damage
            </p>
          </div>

          <div className="panel">
            <div className="panel-heading">
              <div>
                <h3>Report Status</h3>
                <p>Current report progress</p>
              </div>
              <Activity size={21} />
            </div>

            <div className="status-chart">
              {statusLabels.map((item) => {
                const count =
                  data.status_summary[item.key] || 0;

                return (
                  <div className="status-row" key={item.key}>
                    <div className="status-info">
                      <span>{item.label}</span>
                      <strong>{count}</strong>
                    </div>

                    <div className="status-track">
                      <div
                        className={`status-fill ${item.key}`}
                        style={{
                          width: `${(count / maxStatus) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="average-box">
              <span>Average Damage Severity</span>
              <strong>
                {data.average_severity.toFixed(2)}
                <small> / 5</small>
              </strong>
            </div>
          </div>
        </section>

        <section className="panel recent-panel">
          <div className="panel-heading">
            <div>
              <h3>Recent Damage Reports</h3>
              <p>Latest five reports from your database</p>
            </div>
            <FileText size={21} />
          </div>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Damage Type</th>
                  <th>Location</th>
                  <th>Severity</th>
                  <th>Status</th>
                  <th>Reported At</th>
                </tr>
              </thead>

              <tbody>
                {data.recent_reports.length > 0 ? (
                  data.recent_reports.map((report) => (
                    <tr key={report.id}>
                      <td>
                        <strong>{report.damage_type}</strong>
                        <small>{report.description}</small>
                      </td>

                      <td>
                        <span className="location-cell">
                          <MapPin size={14} />
                          {report.latitude.toFixed(3)},{" "}
                          {report.longitude.toFixed(3)}
                        </span>
                      </td>

                      <td>
                        <span
                          className={`severity-badge level-${report.severity}`}
                        >
                          Level {report.severity}
                        </span>
                      </td>

                      <td>
                        <span
                          className={`status-badge ${report.status}`}
                        >
                          {report.status.replace("_", " ")}
                        </span>
                      </td>

                      <td className="date-cell">
                        {getDate(report.created_at)}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="empty-state">
                      No reports found. Submit your first
                      damage report to see it here.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <footer className="dashboard-footer">
          <span>
            <ShieldCheck size={16} />
            InfraSentry AI · Infrastructure Intelligence Platform
          </span>
          <span>Powered by FastAPI + PostgreSQL</span>
        </footer>
      </main>
    </div>
  );
}

export default App;
