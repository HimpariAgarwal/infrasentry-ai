import SLASchedulerAnalytics from "./components/SLASchedulerAnalytics";
import SLANotificationCenter from "./components/SLANotificationCenter";
import SLAAlertsDashboard from "./components/SLAAlertsDashboard";
import SLADashboard from "./components/SLADashboard";
import IncidentAnalytics from "./components/IncidentAnalytics";
import { ShieldCheck } from "lucide-react";
import IncidentDashboard from "./components/IncidentDashboard";
import NotificationCenter from "./components/NotificationCenter";
import SecurityAlerts from "./components/SecurityAlerts";
import { ShieldAlert } from "lucide-react";
import SecurityDashboard from "./components/SecurityDashboard";
import { authenticatedFetch } from "./services/apiClient";
import { verifySession, clearToken } from "./services/authService";
import Login from "./components/Login";
import LogsViewer from "./components/LogsViewer";
import SystemHealth from "./components/SystemHealth";
import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  FilePlus2,
  LayoutDashboard,
  History as HistoryIcon,
  RefreshCw,
  Search,
  Trash2,
  Upload,
  XCircle,
  FileText
} from "lucide-react";

import ImageUpload from "./ImageUpload";
import DetectionPanel from "./components/DetectionPanel";
import BenchmarkAnalytics from "./components/BenchmarkAnalytics";
import DetectionHistory from "./components/DetectionHistory";
import ModelHealth from "./components/ModelHealth";
import ReportsAnalytics from "./components/ReportsAnalytics";
import RoadDamageMap from "./components/RoadDamageMap";
import PerformanceDashboard from "./components/PerformanceDashboard";
import "./App.css";

const API = "http://127.0.0.1:8000";

type Report = {
  id: string;
  damage_type: string;
  description: string;
  latitude: number;
  longitude: number;
  severity: number;
  status: string;
  created_at: string | null;
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

type ReportForm = {
  damage_type: string;
  description: string;
  latitude: string;
  longitude: string;
  severity: string;
};

const emptyForm: ReportForm = {
  damage_type: "Pothole",
  description: "",
  latitude: "",
  longitude: "",
  severity: "3"
};

function App() {
  useEffect(() => {
    const handleSessionExpired = () => {
      clearToken();
      setIsAuthenticated(false);
      setError("Your session expired. Please sign in again.");
    };

    window.addEventListener("infrasentry:session-expired", handleSessionExpired);

    return () => {
      window.removeEventListener("infrasentry:session-expired", handleSessionExpired);
    };
  }, []);

  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authChecking, setAuthChecking] = useState(true);

  useEffect(() => {
    let active = true;

    verifySession().then((valid) => {
      if (active) {
        setIsAuthenticated(valid);
        setAuthChecking(false);
      }
    });

    return () => {
      active = false;
    };
  }, []);

  const handleLogout = () => {
    clearToken();
    setIsAuthenticated(false);
  };

  const [reports, setReports] = useState<Report[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [severityFilter, setSeverityFilter] = useState("all");

  const [activePage, setActivePage] = useState<string>("dashboard");

  const [form, setForm] = useState<ReportForm>(emptyForm);
  const [submitting, setSubmitting] = useState(false);

  // --------------------------------
  // FETCH REPORTS
  // --------------------------------

  async function fetchReports() {
    try {
      const response = await authenticatedFetch(`${API}/reports`);

      if (!response.ok) {
        throw new Error("Could not fetch reports.");
      }

      const data = await response.json();

      const list = Array.isArray(data)
        ? data
        : Array.isArray(data?.reports)
          ? data.reports
          : Array.isArray(data?.items)
            ? data.items
            : null;

      if (!list) {
        throw new Error("Unexpected reports API response.");
      }

      setReports(list);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load reports."
      );
    }
  }

  // --------------------------------
  // FETCH ANALYTICS
  // --------------------------------

  async function fetchAnalytics() {
    try {
      const response = await authenticatedFetch(`${API}/analytics/summary`);

      if (!response.ok) {
        throw new Error("Could not fetch analytics.");
      }

      const data = await response.json();
      setAnalytics(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load analytics."
      );
    }
  }

  // --------------------------------
  // INITIAL LOAD
  // --------------------------------

  async function loadDashboard() {
    setLoading(true);
    setError("");

    await Promise.all([
      fetchReports(),
      fetchAnalytics(),
    ]);

    setLoading(false);
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  // --------------------------------
  // CREATE NEW REPORT
  // --------------------------------

  async function submitReport(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setError("");
    setSuccess("");

    const latitude = Number(form.latitude);
    const longitude = Number(form.longitude);
    const severity = Number(form.severity);

    if (
      form.latitude.trim() === "" ||
      form.longitude.trim() === "" ||
      !Number.isFinite(latitude) ||
      !Number.isFinite(longitude) ||
      latitude < -90 ||
      latitude > 90 ||
      longitude < -180 ||
      longitude > 180
    ) {
      setError("Please enter valid latitude and longitude.");
      return;
    }

    if (!Number.isInteger(severity) || severity < 1 || severity > 5) {
      setError("Severity must be between 1 and 5.");
      return;
    }

    if (
      form.description.trim().length < 10 ||
      form.description.trim().length > 500
    ) {
      setError("Description must contain 10 to 500 characters.");
      return;
    }

    setSubmitting(true);

    try {
      const response = await authenticatedFetch(`${API}/reports`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
},
        body: JSON.stringify({
          damage_type: form.damage_type,
          description: form.description.trim(),
          latitude,
          longitude,
          severity
})
});

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Report submission failed.");
      }

      setSuccess("Road damage report submitted successfully!");
      setForm(emptyForm);

      await loadDashboard();
      setActivePage("dashboard");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Could not submit report."
      );
    } finally {
      setSubmitting(false);
    }
  }

  // --------------------------------
  // UPDATE REPORT STATUS
  // --------------------------------

  async function updateStatus(id: string, status: string) {
    setError("");
    setSuccess("");

    try {
      const response = await authenticatedFetch(`${API}/reports/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json"
},
        body: JSON.stringify({ status })
});

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Status update failed.");
      }

      setSuccess("Report status updated successfully.");
      await loadDashboard();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Status update failed."
      );
    }
  }

  // --------------------------------
  // DELETE REPORT
  // --------------------------------

  async function deleteReport(id: string) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this report?"
    );

    if (!confirmed) return;

    setError("");
    setSuccess("");

    try {
      const response = await authenticatedFetch(`${API}/reports/${id}`, {
        method: "DELETE"
});

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Delete failed.");
      }

      setSuccess("Report deleted successfully.");
      await loadDashboard();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Could not delete report."
      );
    }
  }

  // --------------------------------
  // FILTER REPORTS
  // --------------------------------

  const filteredReports = reports.filter((report) => {
    const searchText = search.toLowerCase();

    const matchesSearch =
      report.damage_type.toLowerCase().includes(searchText) ||
      report.description.toLowerCase().includes(searchText) ||
      report.id.toLowerCase().includes(searchText);

    const matchesStatus =
      statusFilter === "all" || report.status === statusFilter;

    const matchesSeverity =
      severityFilter === "all" ||
      report.severity === Number(severityFilter);

    return matchesSearch && matchesStatus && matchesSeverity;
  });

  // --------------------------------
  // EXPORT FILTERED REPORTS TO CSV
  // --------------------------------

  function exportReports() {
    if (filteredReports.length === 0) {
      setError("No reports available to export.");
      return;
    }

    const headers = [
      "Report ID",
      "Damage Type",
      "Description",
      "Latitude",
      "Longitude",
      "Severity",
      "Status",
      "Created At",
    ];

    const escapeCSV = (value: unknown) =>
      `"${String(value ?? "").replace(/"/g, '""')}"`;

    const rows = filteredReports.map((report) => [
      report.id,
      report.damage_type,
      report.description,
      report.latitude,
      report.longitude,
      report.severity,
      report.status,
      report.created_at ?? "",
    ]);

    const csv = [
      headers.map(escapeCSV).join(","),
      ...rows.map((row) => row.map(escapeCSV).join(",")),
    ].join("\r\n");

    const blob = new Blob(["\uFEFF", csv], {
      type: "text/csv;charset=utf-8;"
});

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = `infrasentry-reports-${new Date()
      .toISOString()
      .slice(0, 10)}.csv`;

    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);

    setSuccess(`${filteredReports.length} reports exported successfully.`);
    setError("");
  }

  // --------------------------------
  // HELPERS
  // --------------------------------

  function severityColor(severity: number) {
    if (severity >= 4) return "#dc4444";
    if (severity === 3) return "#e59a26";
    return "#269b69";
  }

  function formatDate(date: string | null) {
    if (!date) return "N/A";

    return new Date(date).toLocaleString();
  }

  // --------------------------------
  // DASHBOARD UI
  // --------------------------------

  return (
    authChecking ? (
      <div style={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
        Checking secure session...
      </div>
    ) : !isAuthenticated ? (
      <Login onLogin={() => setIsAuthenticated(true)} />
    ) : (
    <div className="app-container">

      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Activity size={23} />
          </div>

          <div>
            <h2>InfraSentry</h2>
            <span>AI INTELLIGENCE</span>
          </div>
        </div>

        <div className="sidebar-label">MAIN MENU</div>

        <button
          className={`nav-item ${
            activePage === "dashboard" ? "active" : ""
          }`}
          onClick={() => setActivePage("dashboard")}
        >
          <LayoutDashboard size={18} />
          Dashboard
        </button>

        <button
          className={`nav-item ${
            activePage === "new-report" ? "active" : ""
          }`}
          onClick={() => setActivePage("new-report")}
        >
          <FilePlus2 size={18} />
          New Report
        </button>

        <button
          className={`nav-item ${
            activePage === "image-upload" ? "active" : ""
          }`}
          onClick={() => setActivePage("image-upload")}
        >
          <Upload size={18} />
          Image Upload
        </button>

        <button
          className={`nav-item ${
            activePage === "ai-analytics" ? "active" : ""
          }`}
          onClick={() => setActivePage("ai-analytics")}
        >
          <Activity size={18} />
          AI Analytics
        </button>
        <button
          className={`nav-item ${
            activePage === "detection-history" ? "active" : ""
          }`}
          onClick={() => setActivePage("detection-history")}
        >
          <HistoryIcon size={18} />
          Detection History
        </button>

        <button
          className={`nav-item ${
            activePage === "model-health" ? "active" : ""
          }`}
          onClick={() => setActivePage("model-health")}
        >
          <Activity size={18} />
          Model Health
        </button>

        <button
          className={`nav-item ${
            activePage === "reports-analytics" ? "active" : ""
          }`}
          onClick={() => setActivePage("reports-analytics")}
        >
          <Activity size={18} />
          Reports Analytics
        </button>

        <button
          className={`nav-item ${
            activePage === "road-map" ? "active" : ""
          }`}
          onClick={() => setActivePage("road-map")}
        >
          <Activity size={18} />
          Damage Map
        </button>

        <button
          className={`nav-item ${
            activePage === "performance" ? "active" : ""
          }`}
          onClick={() => setActivePage("performance")}
        >
          <Activity size={18} />
          Performance Monitor
        </button>

        <button className="nav-item" onClick={() => setActivePage("system-health")}><Activity size={18} /> <span>System Health</span></button>
<button className="nav-item" onClick={() => setActivePage("logs")}><FileText size={18} /> <span>API Logs</span></button>

        <button className="nav-item" onClick={() => setActivePage("security")}>
          <ShieldAlert size={18} /> <span>Security Audit</span>
        </button>

        <button className="nav-item" onClick={() => setActivePage("security-alerts")}>
          <ShieldAlert size={18} /> <span>Security Alerts</span>
        </button>

        <button className="nav-item" onClick={() => setActivePage("incidents")}>
          <ShieldCheck size={18} /> <span>Incidents</span>
        </button>

        <button className="nav-item" onClick={() => setActivePage("incident-analytics")}>
          <Activity size={18} /> <span>Incident Analytics</span>
        </button>

        <button className="nav-item" onClick={() => setActivePage("sla")}>
          <Clock size={18} /> <span>SLA Monitoring</span>
        </button>

        <button
          type="button"
          onClick={() => setActivePage("sla-alerts")}
          style={{
            display: "flex", alignItems: "center", gap: "10px",
            width: "100%", padding: "11px 14px", marginBottom: "6px",
            border: "none", borderRadius: "8px", cursor: "pointer",
            textAlign: "left", color: "inherit",
            background: activePage === "sla-alerts" ? "rgba(100,116,139,.25)" : "transparent"
          }}
        >
          <span>??</span> SLA Alerts
        </button>


        <button
          className="sidebar-nav-item"
          onClick={() => setActivePage("sla-analytics")}
        >
          <span>??</span>
          <span>SLA Analytics</span>
        </button>

<div className="sidebar-bottom">
          <div className="system-status">
            <span className="status-dot"></span>
            System Active
          </div>

          <p>InfraSentry AI v1.0</p>
        </div>
      </aside>

      <main className="main-content">
{ activePage === "system-health" && <SystemHealth />
 }


        <SLANotificationCenter />
      <NotificationCenter />
        <header className="top-header">
          <div>
            <h1>
              {activePage === "dashboard"
                ? "Infrastructure Dashboard"
                : activePage === "new-report"
                  ? "Create New Report"
                  : activePage === "ai-analytics"
                  ? "AI Performance Analytics"
                  : activePage === "detection-history"
                    ? "Detection History"
                    : activePage === "model-health"
                      ? "AI Model Health"
                      : activePage === "reports-analytics"
                        ? "Reports Analytics"
                        : activePage === "performance"
                        ? "Performance Monitoring"
: activePage === "road-map"
                          ? "Road Damage Map"
                          : "Image Upload"}
            </h1>

            <p>
              Monitor, analyze and manage road infrastructure damage.
            </p>
          </div>

          <button
            className="refresh-button"
            onClick={() => activePage === "detection-history" ? window.dispatchEvent(new Event("infrasentry-history-refresh")) : loadDashboard()}
            disabled={loading}
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        <button type="button" onClick={handleLogout} className="auth-logout-button">Sign out</button>
</header>

        {error && (
          <div className="error-message">
            <XCircle size={17} />
            {error}
            <button onClick={() => setError("")}>Ã—</button>
          </div>
        )}

        {success && (
          <div className="success-message">
            <CheckCircle size={17} />
            {success}
            <button onClick={() => setSuccess("")}>Ã—</button>
          </div>
        )}

        {/* DETECTION HISTORY PAGE */}
        {activePage === "detection-history" && <DetectionHistory />}

        {/* MODEL HEALTH PAGE */}
        {activePage === "model-health" && <ModelHealth />}

        {/* REPORTS ANALYTICS PAGE */}
        {activePage === "reports-analytics" && (
          <ReportsAnalytics reports={reports} />
        )}

        {/* ROAD DAMAGE MAP PAGE */}
        {activePage === "road-map" && (
          <RoadDamageMap reports={reports} />
        )}

        {/* PERFORMANCE MONITORING PAGE */}
        {activePage === "performance" && <PerformanceDashboard />}

        {/* DASHBOARD PAGE */}

        {activePage === "dashboard" && (
          <>
            <div className="welcome-banner">
              <div>
                <span className="banner-tag">
                  INFRASTRUCTURE INTELLIGENCE PLATFORM
                </span>

                <h2>Road Damage Monitoring System</h2>

                <p>
                  Track road damage reports and monitor infrastructure
                  conditions through intelligent analytics.
                </p>
              </div>

              <Activity size={60} />
            </div>

            {loading ? (
              <div className="loading">
                Loading dashboard...
              </div>
            ) : (
              <>
                <section className="stats-grid">

                  <div className="stat-card">
                    <div className="stat-icon blue">
                      <Activity size={21} />
                    </div>

                    <p>Total Reports</p>

                    <h2>{analytics?.total_reports ?? reports.length}</h2>
                  </div>

                  <div className="stat-card">
                    <div className="stat-icon orange">
                      <Clock size={21} />
                    </div>

                    <p>Under Review</p>

                    <h2>
                      {analytics?.status_summary?.under_review ?? 0}
                    </h2>
                  </div>

                  <div className="stat-card">
                    <div className="stat-icon green">
                      <CheckCircle size={21} />
                    </div>

                    <p>Resolved</p>

                    <h2>
                      {analytics?.status_summary?.resolved ?? 0}
                    </h2>
                  </div>

                  <div className="stat-card">
                    <div className="stat-icon red">
                      <AlertTriangle size={21} />
                    </div>

                    <p>High Severity</p>

                    <h2>
                      {(analytics?.severity_summary?.["4"] ?? 0) +
                        (analytics?.severity_summary?.["5"] ?? 0)}
                    </h2>
                  </div>

                </section>

                <section className="analytics-grid">

                  <div className="panel">
                    <h3>Severity Distribution</h3>

                    <p className="panel-subtitle">
                      Reports grouped by damage severity
                    </p>

                    <div className="severity-chart">
                      {[1, 2, 3, 4, 5].map((level) => {
                        const count =
                          analytics?.severity_summary?.[
                            String(level)
                          ] ?? 0;

                        const maximum = Math.max(
                          1,
                          ...Object.values(analytics?.severity_summary ?? {})
                        );

                        return (
                          <div
                            className="severity-column"
                            key={level}
                          >
                            <span>{count}</span>

                            <div className="bar-background">
                              <div
                                className="severity-bar"
                                style={{
                                  height: `${(count / maximum) * 100}%`,
                                  background: severityColor(level)
}}
                              />
                            </div>

                            <span>Level {level}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  <div className="panel">
                    <h3>Report Status</h3>

                    <p className="panel-subtitle">
                      Current report progress
                    </p>

                    {[
                      {
                        label: "Submitted",
                        value:
                          analytics?.status_summary?.submitted ?? 0,
                        color: "#3b82f6"
},
                      {
                        label: "Under Review",
                        value:
                          analytics?.status_summary?.under_review ?? 0,
                        color: "#e59a26"
},
                      {
                        label: "Resolved",
                        value:
                          analytics?.status_summary?.resolved ?? 0,
                        color: "#269b69"
},
                    ].map((item) => {
                      const total = analytics?.total_reports ?? 0;

                      const percentage =
                        total > 0
                          ? (item.value / total) * 100
                          : 0;

                      return (
                        <div
                          className="status-row"
                          key={item.label}
                        >
                          <div className="status-info">
                            <span>{item.label}</span>
                            <strong>{item.value}</strong>
                          </div>

                          <div className="status-track">
                            <div
                              className="status-fill"
                              style={{
                                width: `${percentage}%`,
                                background: item.color
}}
                            />
                          </div>
                        </div>
                      );
                    })}

                    <div className="average-severity">
                      <span>Average Severity</span>
                      <strong>
                        {analytics?.average_severity ?? 0} / 5
                      </strong>
                    </div>
                  </div>

                </section>

                <section className="panel reports-panel">

                  <div className="reports-heading">
                    <div>
                      <h3>Road Damage Reports</h3>

                      <p className="panel-subtitle">
                        Search, filter and manage reports
                      </p>
                    </div>

                    <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
                      <button
                        className="add-report-btn"
                        onClick={exportReports}
                        disabled={filteredReports.length === 0}
                      >
                        Export CSV
                      </button>

                      <button
                        className="add-report-btn"
                        onClick={() => setActivePage("new-report")}
                      >
                        + New Report
                      </button>
                    </div>
                  </div>

                  <div className="filters">

                    <div className="search-box">
                      <Search size={17} />

                      <input
                        type="text"
                        placeholder="Search reports..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                      />
                    </div>

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

                  </div>

                  <div className="table-wrapper">
                    <table>
                      <thead>
                        <tr>
                          <th>Damage Type</th>
                          <th>Severity</th>
                          <th>Location</th>
                          <th>Date</th>
                          <th>Status</th>
                          <th>Actions</th>
                        </tr>
                      </thead>

                      <tbody>
                        {filteredReports.length === 0 ? (
                          <tr>
                            <td colSpan={6} className="empty-state">
                              No reports found.
                            </td>
                          </tr>
                        ) : (
                          filteredReports.map((report) => (
                            <tr key={report.id}>
                              <td>
                                <strong>{report.damage_type}</strong>

                                <small className="report-description">
                                  {report.description}
                                </small>
                              </td>

                              <td>
                                <span
                                  className="severity-badge"
                                  style={{
                                    color: severityColor(report.severity)
}}
                                >
                                  {report.severity}/5
                                </span>
                              </td>

                              <td>
                                {report.latitude.toFixed(4)},
                                {" "}
                                {report.longitude.toFixed(4)}
                              </td>

                              <td>{formatDate(report.created_at)}</td>

                              <td>
                                <select
                                  className="status-select"
                                  value={report.status}
                                  onChange={(e) =>
                                    updateStatus(
                                      report.id,
                                      e.target.value
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
                                  title="Delete report"
                                  onClick={() =>
                                    deleteReport(report.id)
                                  }
                                >
                                  <Trash2 size={16} />
                                </button>
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>

                  <p className="report-count">
                    Showing {filteredReports.length} of {reports.length} reports
                  </p>

                </section>
              </>
            )}
          </>
        )}

        {/* NEW REPORT PAGE */}

        {activePage === "new-report" && (
          <section className="form-section">

            <div className="form-heading">
              <h2>Submit Road Damage Report</h2>

              <p>
                Enter the damage details and its geographical location.
              </p>
            </div>

            <form
              className="report-form"
              onSubmit={submitReport}
            >

              <div className="form-group">
                <label>Damage Type *</label>

                <select
                  value={form.damage_type}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      damage_type: e.target.value
})
                  }
                >
                  <option>Pothole</option>
                  <option>Crack</option>
                  <option>Alligator Crack</option>
                  <option>Surface Damage</option>
                  <option>Road Collapse</option>
                  <option>Other</option>
                </select>
              </div>

              <div className="form-group">
                <label>Description *</label>

                <textarea
                  placeholder="Describe the road damage..."
                  minLength={10}
                  maxLength={500}
                  value={form.description}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      description: e.target.value
})
                  }
                  required
                />
              </div>

              <div className="form-grid">

                <div className="form-group">
                  <label>Latitude *</label>

                  <input
                    type="number"
                    step="any"
                    min="-90"
                    max="90"
                    placeholder="28.6139"
                    value={form.latitude}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        latitude: e.target.value
})
                    }
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Longitude *</label>

                  <input
                    type="number"
                    step="any"
                    min="-180"
                    max="180"
                    placeholder="77.2090"
                    value={form.longitude}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        longitude: e.target.value
})
                    }
                    required
                  />
                </div>

              </div>

              <div className="form-group">
                <label>Severity Level *</label>

                <select
                  value={form.severity}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      severity: e.target.value
})
                  }
                >
                  <option value="1">1 - Very Low</option>
                  <option value="2">2 - Low</option>
                  <option value="3">3 - Moderate</option>
                  <option value="4">4 - High</option>
                  <option value="5">5 - Critical</option>
                </select>
              </div>

              <div className="form-note">
                <AlertTriangle size={17} />

                Please ensure the geographical coordinates are accurate.
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={() => setActivePage("dashboard")}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="submit-btn"
                  disabled={submitting}
                >
                  {submitting
                    ? "Submitting..."
                    : "Submit Report"}
                </button>
              </div>

            </form>
          </section>
        )}

        {/* IMAGE UPLOAD PAGE */}

        {activePage === "image-upload" && (
          <><ImageUpload /><DetectionPanel /></>
        )}

        {activePage === "ai-analytics" && (
          <BenchmarkAnalytics />
        )}
        {activePage === "security" && <SecurityDashboard />}

        {activePage === "security-alerts" && <SecurityAlerts />}

        {activePage === "incidents" && <IncidentDashboard />}

        {activePage === "incident-analytics" && <IncidentAnalytics />}

        {activePage === "sla" && <SLADashboard />}

        
      {activePage === "sla-alerts" && <SLAAlertsDashboard />}

<footer className="footer">
          <p>
            Â© 2026 InfraSentry AI. Infrastructure Intelligence Platform.
          </p>
        
      {activePage === "sla-analytics" && <SLASchedulerAnalytics />}

      </footer>

      </main>
    
{activePage === "logs" && <LogsViewer />}
</div>
    )
  );
}

export default App;