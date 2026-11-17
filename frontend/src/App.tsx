
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
  Plus,
  ArrowLeft,
  Send,
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

type ReportForm = {
  damage_type: string;
  description: string;
  latitude: string;
  longitude: string;
  severity: string;
};

const initialForm: ReportForm = {
  damage_type: "",
  description: "",
  latitude: "",
  longitude: "",
  severity: "3",
};

function App() {
  const [reports, setReports] = useState<Report[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  const [updatingId, setUpdatingId] = useState("");
  const [deletingId, setDeletingId] = useState("");

  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState<ReportForm>(initialForm);

  async function loadDashboard() {
    setLoading(true);
    setError("");

    try {
      const [analyticsResponse, reportsResponse] = await Promise.all([
        fetch(`${API}/analytics/summary`),
        fetch(`${API}/reports`),
      ]);

      if (!analyticsResponse.ok || !reportsResponse.ok) {
        throw new Error("Unable to load dashboard data.");
      }

      const analyticsData = await analyticsResponse.json();
      const reportsData = await reportsResponse.json();

      let reportList: Report[] = [];

      if (Array.isArray(reportsData)) {
        reportList = reportsData;
      } else if (Array.isArray(reportsData?.reports)) {
        reportList = reportsData.reports;
      } else if (Array.isArray(reportsData?.items)) {
        reportList = reportsData.items;
      } else {
        throw new Error("Unexpected reports API response.");
      }

      setReports(reportList);
      setAnalytics(analyticsData);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to load data."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

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

  function handleFormChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) {
    const { name, value } = e.target;
    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  async function submitReport(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    setError("");
    setSuccess("");

    const latitude = Number(form.latitude);
    const longitude = Number(form.longitude);
    const severity = Number(form.severity);

    if (
      !Number.isFinite(latitude) ||
      latitude < -90 ||
      latitude > 90
    ) {
      setError("Latitude must be a number between -90 and 90.");
      return;
    }

    if (
      !Number.isFinite(longitude) ||
      longitude < -180 ||
      longitude > 180
    ) {
      setError("Longitude must be a number between -180 and 180.");
      return;
    }

    if (!Number.isInteger(severity) || severity < 1 || severity > 5) {
      setError("Please select a severity between 1 and 5.");
      return;
    }

    setSubmitting(true);

    try {
      const response = await fetch(`${API}/reports`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          damage_type: form.damage_type,
          description: form.description,
          latitude,
          longitude,
          severity,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const message =
          errorData?.detail
            ? typeof errorData.detail === "string"
              ? errorData.detail
              : JSON.stringify(errorData.detail)
            : "Could not create report.";

        throw new Error(message);
      }

      setForm(initialForm);
      setShowForm(false);
      setSuccess("New road damage report submitted successfully!");

      await loadDashboard();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Report submission failed."
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function updateStatus(
    id: string,
    newStatus: Report["status"]
  ) {
    setUpdatingId(id);
    setError("");
    setSuccess("");

    try {
      const response = await fetch(`${API}/reports/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!response.ok) {
        throw new Error("Failed to update report status.");
      }

      await loadDashboard();
      setSuccess("Report status updated successfully.");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Status update failed."
      );
    } finally {
      setUpdatingId("");
    }
  }

  async function deleteReport(id: string) {
    if (!window.confirm("Are you sure you want to delete this report?")) {
      return;
    }

    setDeletingId(id);
    setError("");
    setSuccess("");

    try {
      const response = await fetch(`${API}/reports/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to delete report.");
      }

      await loadDashboard();
      setSuccess("Report deleted successfully.");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Delete failed."
      );
    } finally {
      setDeletingId("");
    }
  }

  function getSeverityLabel(severity: number) {
    if (severity >= 4) return "High";
    if (severity === 3) return "Medium";
    return "Low";
  }

  function formatDate(date: string) {
    if (!date) return "N/A";

    const parsedDate = new Date(date);

    if (Number.isNaN(parsedDate.getTime())) return "N/A";

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
          <button
            className={`nav-item ${!showForm ? "active" : ""}`}
            onClick={() => setShowForm(false)}
          >
            <Activity size={19} />
            Dashboard
          </button>

          <button
            className={`nav-item ${showForm ? "active" : ""}`}
            onClick={() => setShowForm(true)}
          >
            <FileText size={19} />
            New Report
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="system-status">
            <span className="status-dot"></span>
            System Monitoring
          </div>
          <p>InfraSentry AI v1.0</p>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">INFRASTRUCTURE MONITORING</p>
            <h1>{showForm ? "Submit Damage Report" : "Report Management"}</h1>
            <p className="subtitle">
              {showForm
                ? "Provide details about a road damage incident."
                : "Monitor, manage and prioritize road damage reports."}
            </p>
          </div>

          {!showForm && (
            <button
              className="refresh-btn"
              onClick={loadDashboard}
              disabled={loading}
            >
              <RefreshCw size={16} />
              Refresh
            </button>
          )}
        </header>

        {error && (
          <div className="error-message">
            <AlertTriangle size={18} />
            {error}
          </div>
        )}

        {success && (
          <div className="success-message">
            <CheckCircle size={18} />
            {success}
          </div>
        )}

        {showForm ? (
          <section className="form-section">
            <div className="form-heading">
              <div>
                <h2>New Road Damage Report</h2>
                <p>Enter accurate details so the issue can be assessed.</p>
              </div>
              <button
                className="back-btn"
                onClick={() => {
                  setShowForm(false);
                  setError("");
                  setSuccess("");
                }}
              >
                <ArrowLeft size={16} />
                Back to Dashboard
              </button>
            </div>

            <form className="report-form" onSubmit={submitReport}>
              <div className="form-group">
                <label htmlFor="damage_type">Damage Type *</label>
                <select
                  id="damage_type"
                  name="damage_type"
                  value={form.damage_type}
                  onChange={handleFormChange}
                  required
                >
                  <option value="">Select damage type</option>
                  <option value="Pothole">Pothole</option>
                  <option value="Crack">Road Crack</option>
                  <option value="Alligator Crack">Alligator Crack</option>
                  <option value="Surface Damage">Surface Damage</option>
                  <option value="Road Collapse">Road Collapse</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="description">Description *</label>
                <textarea
                  id="description"
                  name="description"
                  placeholder="Describe the road damage, its size, and any visible risks..."
                  value={form.description}
                  onChange={handleFormChange}
                  minLength={10}
                  maxLength={500}
                  rows={5}
                  required
                />
                <small>{form.description.length}/500 characters</small>
              </div>

              <div className="form-divider">
                <MapPin size={18} />
                <div>
                  <strong>Location Details</strong>
                  <p>Enter the GPS coordinates of the damaged road.</p>
                </div>
              </div>

              <div className="form-grid">
                <div className="form-group">
                  <label htmlFor="latitude">Latitude *</label>
                  <input
                    id="latitude"
                    name="latitude"
                    type="number"
                    step="any"
                    min="-90"
                    max="90"
                    placeholder="Example: 28.6139"
                    value={form.latitude}
                    onChange={handleFormChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="longitude">Longitude *</label>
                  <input
                    id="longitude"
                    name="longitude"
                    type="number"
                    step="any"
                    min="-180"
                    max="180"
                    placeholder="Example: 77.2090"
                    value={form.longitude}
                    onChange={handleFormChange}
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="severity">Damage Severity *</label>
                <select
                  id="severity"
                  name="severity"
                  value={form.severity}
                  onChange={handleFormChange}
                  required
                >
                  <option value="1">1 - Very Low</option>
                  <option value="2">2 - Low</option>
                  <option value="3">3 - Medium</option>
                  <option value="4">4 - High</option>
                  <option value="5">5 - Critical</option>
                </select>
                <small>
                  Select severity based on the visible condition and risk.
                </small>
              </div>

              <div className="form-note">
                <AlertTriangle size={17} />
                <span>
                  Please verify the location and description before submitting.
                  Incorrect coordinates can affect report tracking.
                </span>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={() => {
                    setForm(initialForm);
                    setShowForm(false);
                    setError("");
                  }}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="submit-btn"
                  disabled={submitting}
                >
                  <Send size={16} />
                  {submitting ? "Submitting..." : "Submit Report"}
                </button>
              </div>
            </form>
          </section>
        ) : loading && !analytics ? (
          <div className="loading">Loading dashboard...</div>
        ) : analytics ? (
          <>
            <section className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon blue"><FileText /></div>
                <p>Total Reports</p>
                <h2>{analytics.total_reports ?? 0}</h2>
              </div>

              <div className="stat-card">
                <div className="stat-icon orange"><Clock /></div>
                <p>Submitted</p>
                <h2>{analytics.status_summary?.submitted ?? 0}</h2>
              </div>

              <div className="stat-card">
                <div className="stat-icon purple"><Activity /></div>
                <p>Under Review</p>
                <h2>{analytics.status_summary?.under_review ?? 0}</h2>
              </div>

              <div className="stat-card">
                <div className="stat-icon green"><CheckCircle /></div>
                <p>Resolved</p>
                <h2>{analytics.status_summary?.resolved ?? 0}</h2>
              </div>

              <div className="stat-card">
                <div className="stat-icon red"><AlertTriangle /></div>
                <p>High Severity</p>
                <h2>{highSeverity}</h2>
              </div>
            </section>

            <section className="management-section">
              <div className="section-heading">
                <div>
                  <h2>All Damage Reports</h2>
                  <p>Manage and track reported infrastructure issues.</p>
                </div>

                <button
                  className="add-report-btn"
                  onClick={() => {
                    setShowForm(true);
                    setError("");
                    setSuccess("");
                  }}
                >
                  <Plus size={17} />
                  New Report
                </button>
              </div>

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
                  onChange={(e) => setSeverityFilter(e.target.value)}
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
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <option value="all">All Statuses</option>
                  <option value="submitted">Submitted</option>
                  <option value="under_review">Under Review</option>
                  <option value="resolved">Resolved</option>
                </select>
              </div>

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
                            <strong>{report.damage_type || "Unknown"}</strong>
                            <span>{report.description || "No description"}</span>
                            <small>ID: {report.id?.slice(0, 8) || "N/A"}</small>
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
                          <span className={`severity-badge severity-${report.severity}`}>
                            {getSeverityLabel(report.severity)} ({report.severity}/5)
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
                            <option value="submitted">Submitted</option>
                            <option value="under_review">Under Review</option>
                            <option value="resolved">Resolved</option>
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
