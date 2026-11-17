
import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Trash2,
  RefreshCw,
  Search,
  Shield,
  MapPin,
  FileText,
} from "lucide-react";
import "./App.css";

const API = "http://127.0.0.1:8000";

type Report = {
  id: string;
  damage_type: string;
  description: string;
  latitude: number;
  longitude: number;
  severity: number;
  status: "submitted" | "under_review" | "resolved";
  created_at: string;
};

type Analytics = {
  total_reports: number;
  status_summary: {
    submitted: number;
    under_review: number;
    resolved: number;
  };
  severity_summary: Record<string, number>;
  average_severity: number;
  recent_reports: Report[];
};

function App() {
  const [reports, setReports] = useState<Report[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [updatingId, setUpdatingId] = useState("");
  const [deletingId, setDeletingId] = useState("");

  // Load reports and analytics
  async function loadDashboard() {
    setLoading(true);
    setError("");

    try {
      const [analyticsResponse, reportsResponse] = await Promise.all([
        fetch(`${API}/analytics/summary`),
        fetch(`${API}/reports`),
      ]);

      if (!analyticsResponse.ok) {
        throw new Error("Failed to load analytics.");
      }

      if (!reportsResponse.ok) {
        throw new Error("Failed to load reports.");
      }

      const analyticsData = await analyticsResponse.json();
      const reportsData = await reportsResponse.json();

      // Handle both array and object API responses
      let reportList: Report[] = [];

      if (Array.isArray(reportsData)) {
        reportList = reportsData;
      } else if (Array.isArray(reportsData?.reports)) {
        reportList = reportsData.reports;
      } else if (Array.isArray(reportsData?.items)) {
        reportList = reportsData.items;
      } else {
        throw new Error(
          "Unexpected reports API response. Check /reports in your browser."
        );
      }

      setReports(reportList);
      setAnalytics(analyticsData);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong while loading data."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  // Search and filter reports
  const filteredReports = useMemo(() => {
    return reports.filter((report) => {
      const searchText = search.toLowerCase();

      const matchesSearch =
        (report.damage_type || "").toLowerCase().includes(searchText) ||
        (report.description || "").toLowerCase().includes(searchText) ||
        (report.id || "").toLowerCase().includes(searchText);

      const matchesSeverity =
        severityFilter === "all" ||
        String(report.severity) === severityFilter;

      const matchesStatus =
        statusFilter === "all" ||
        report.status === statusFilter;

      return matchesSearch && matchesSeverity && matchesStatus;
    });
  }, [reports, search, severityFilter, statusFilter]);

  // Update report status
  async function updateStatus(
    id: string,
    newStatus: Report["status"]
  ) {
    setUpdatingId(id);
    setError("");

    try {
      const response = await fetch(`${API}/reports/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          status: newStatus,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to update report status.");
      }

      await loadDashboard();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Status update failed."
      );
    } finally {
      setUpdatingId("");
    }
  }

  // Delete report
  async function deleteReport(id: string) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this report?"
    );

    if (!confirmed) return;

    setDeletingId(id);
    setError("");

    try {
      const response = await fetch(`${API}/reports/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to delete report.");
      }

      await loadDashboard();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Delete failed."
      );
    } finally {
      setDeletingId("");
    }
  }

  // Severity label
  function getSeverityLabel(severity: number) {
    if (severity >= 4) return "High";
    if (severity === 3) return "Medium";
    return "Low";
  }

  // Format date
  function formatDate(date: string) {
    if (!date) return "N/A";

    const parsedDate = new Date(date);

    if (Number.isNaN(parsedDate.getTime())) {
      return "N/A";
    }

    return parsedDate.toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  }

  const highSeverity =
    (analytics?.severity_summary?.["4"] || 0) +
    (analytics?.severity_summary?.["5"] || 0);

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Shield size={25} />
          </div>

          <div>
            <h2>InfraSentry</h2>
            <span>AI Infrastructure Intelligence</span>
          </div>
        </div>

        <nav className="navigation">
          <div className="nav-item active">
            <Activity size={19} />
            Dashboard
          </div>

          <div className="nav-item">
            <FileText size={19} />
            Reports
          </div>
        </nav>

        <div className="sidebar-bottom">
          <div className="system-status">
            <span className="status-dot"></span>
            System Monitoring
          </div>

          <p>InfraSentry AI v1.0</p>
        </div>
      </aside>

      {/* Main content */}
      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">INFRASTRUCTURE MONITORING</p>
            <h1>Report Management</h1>
            <p className="subtitle">
              Monitor, manage and prioritize road damage reports.
            </p>
          </div>

          <button
            className="refresh-btn"
            onClick={loadDashboard}
            disabled={loading}
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        </header>

        {/* Error message */}
        {error && (
          <div className="error-message">
            <AlertTriangle size={18} />
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && !analytics ? (
          <div className="loading">
            Loading dashboard...
          </div>
        ) : analytics ? (
          <>
            {/* Statistics */}
            <section className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon blue">
                  <FileText />
                </div>
                <p>Total Reports</p>
                <h2>{analytics.total_reports ?? 0}</h2>
              </div>

              <div className="stat-card">
                <div className="stat-icon orange">
                  <Clock />
                </div>
                <p>Submitted</p>
                <h2>
                  {analytics.status_summary?.submitted ?? 0}
                </h2>
              </div>

              <div className="stat-card">
                <div className="stat-icon purple">
                  <Activity />
                </div>
                <p>Under Review</p>
                <h2>
                  {analytics.status_summary?.under_review ?? 0}
                </h2>
              </div>

              <div className="stat-card">
                <div className="stat-icon green">
                  <CheckCircle />
                </div>
                <p>Resolved</p>
                <h2>
                  {analytics.status_summary?.resolved ?? 0}
                </h2>
              </div>

              <div className="stat-card">
                <div className="stat-icon red">
                  <AlertTriangle />
                </div>
                <p>High Severity</p>
                <h2>{highSeverity}</h2>
              </div>
            </section>

            {/* Report management */}
            <section className="management-section">
              <div className="section-heading">
                <div>
                  <h2>All Damage Reports</h2>
                  <p>
                    Manage and track reported infrastructure issues.
                  </p>
                </div>

                <span className="report-count">
                  {filteredReports.length} Reports
                </span>
              </div>

              {/* Search and filters */}
              <div className="filter-toolbar">
                <div className="search-box">
                  <Search size={18} />

                  <input
                    type="text"
                    placeholder="Search reports..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                </div>

                <select
                  value={severityFilter}
                  onChange={(e) =>
                    setSeverityFilter(e.target.value)
                  }
                >
                  <option value="all">All Severities</option>
                  <option value="1">Severity 1</option>
                  <option value="2">Severity 2</option>
                  <option value="3">Severity 3</option>
                  <option value="4">Severity 4</option>
                  <option value="5">Severity 5</option>
                </select>

                <select
                  value={statusFilter}
                  onChange={(e) =>
                    setStatusFilter(e.target.value)
                  }
                >
                  <option value="all">All Statuses</option>
                  <option value="submitted">Submitted</option>
                  <option value="under_review">Under Review</option>
                  <option value="resolved">Resolved</option>
                </select>
              </div>

              {/* Reports table */}
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>REPORT</th>
                      <th>LOCATION</th>
                      <th>SEVERITY</th>
                      <th>DATE</th>
                      <th>STATUS</th>
                      <th>ACTIONS</th>
                    </tr>
                  </thead>

                  <tbody>
                    {filteredReports.map((report) => (
                      <tr key={report.id}>
                        <td>
                          <div className="report-name">
                            <strong>
                              {report.damage_type || "Unknown"}
                            </strong>

                            <span>
                              {report.description || "No description"}
                            </span>

                            <small>
                              ID: {report.id?.slice(0, 8) || "N/A"}
                            </small>
                          </div>
                        </td>

                        <td>
                          <div className="location">
                            <MapPin size={15} />

                            <span>
                              {Number(report.latitude).toFixed(4)},{" "}
                              {Number(report.longitude).toFixed(4)}
                            </span>
                          </div>
                        </td>

                        <td>
                          <span
                            className={`severity-badge severity-${report.severity}`}
                          >
                            {getSeverityLabel(report.severity)} (
                            {report.severity}/5)
                          </span>
                        </td>

                        <td>{formatDate(report.created_at)}</td>

                        <td>
                          <select
                            className={`status-select status-${report.status}`}
                            value={report.status}
                            disabled={updatingId === report.id}
                            onChange={(e) =>
                              updateStatus(
                                report.id,
                                e.target.value as Report["status"]
                              )
                            }
                          >
                            <option value="submitted">
                              Submitted
                            </option>

                            <option value="under_review">
                              Under Review
                            </option>

                            <option value="resolved">
                              Resolved
                            </option>
                          </select>
                        </td>

                        <td>
                          <button
                            className="delete-btn"
                            onClick={() => deleteReport(report.id)}
                            disabled={
                              deletingId === report.id ||
                              updatingId === report.id
                            }
                            title="Delete report"
                          >
                            <Trash2 size={17} />
                          </button>
                        </td>
                      </tr>
                    ))}

                    {filteredReports.length === 0 && (
                      <tr>
                        <td colSpan={6} className="empty-state">
                          No reports found. Try changing your filters.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </section>

            <footer className="footer">
              InfraSentry AI · Intelligent Infrastructure Monitoring
            </footer>
          </>
        ) : (
          <div className="loading">
            Analytics data is unavailable. Please refresh.
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
