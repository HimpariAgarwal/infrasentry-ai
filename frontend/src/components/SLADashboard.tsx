import { useCallback, useEffect, useState } from "react";
import { Activity, AlertTriangle, CheckCircle, Clock, RefreshCw } from "lucide-react";
import { authenticatedFetch, API_BASE } from "../services/authService";
import "./SLADashboard.css";

interface SLAIncident {
  incident_id: string;
  severity: string;
  status: string;
  sla_hours: number;
  sla_deadline: string | null;
  sla_status: string;
  message: string;
}

interface SLAReport {
  total_incidents: number;
  resolved_incidents: number;
  overdue_incidents: number;
  within_sla: number;
  unknown_sla: number;
  sla_compliance_rate: number;
  severity_sla_hours: Record<string, number>;
  incidents: SLAIncident[];
  generated_at: string;
}

export default function SLADashboard() {
  const [report, setReport] = useState<SLAReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("all");

  const loadReport = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await authenticatedFetch(
        `${API_BASE}/api/v1/sla/report`
      );

      if (!response.ok) throw new Error("Unable to load SLA report.");

      setReport(await response.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadReport();
  }, [loadReport]);

  const incidents = report?.incidents.filter((item) =>
    filter === "all" ? true : item.sla_status === filter
  ) ?? [];

  return (
    <section className="sla-dashboard">
      <div className="sla-header">
        <div>
          <h2><Activity size={23} /> SLA Monitoring</h2>
          <p>Incident response deadline and compliance monitoring</p>
        </div>
        <button onClick={loadReport} disabled={loading}>
          <RefreshCw size={16} /> Refresh
        </button>
      </div>

      {error && <p className="sla-error">{error}</p>}
      {loading && <p>Loading SLA report...</p>}

      {report && (
        <>
          <div className="sla-kpis">
            <div>
              <Activity />
              <span>Total Incidents</span>
              <strong>{report.total_incidents}</strong>
            </div>
            <div>
              <AlertTriangle />
              <span>Overdue</span>
              <strong>{report.overdue_incidents}</strong>
            </div>
            <div>
              <CheckCircle />
              <span>Within SLA</span>
              <strong>{report.within_sla}</strong>
            </div>
            <div>
              <Clock />
              <span>Unknown SLA</span>
              <strong>{report.unknown_sla}</strong>
            </div>
          </div>

          <div className="sla-compliance">
            <div>
              <span>SLA Compliance Rate</span>
              <strong>{report.sla_compliance_rate}%</strong>
            </div>
            <div className="sla-progress">
              <div style={{
                width: `${Math.min(100, Math.max(0, report.sla_compliance_rate))}%`
              }} />
            </div>
          </div>

          <div className="sla-targets">
            <h3>Severity Response Targets</h3>
            <div className="sla-target-grid">
              {Object.entries(report.severity_sla_hours).map(([severity, hours]) => (
                <div key={severity}>
                  <span>{severity}</span>
                  <strong>{hours} hours</strong>
                </div>
              ))}
            </div>
          </div>

          <div className="sla-table-section">
            <div className="sla-table-header">
              <h3>Incident SLA Records</h3>
              <select value={filter} onChange={(event) => setFilter(event.target.value)}>
                <option value="all">All incidents</option>
                <option value="breached">Overdue</option>
                <option value="within_sla">Within SLA</option>
                <option value="unknown">Unknown</option>
              </select>
            </div>

            <div className="sla-table-wrap">
              <table className="sla-table">
                <thead>
                  <tr>
                    <th>Incident ID</th>
                    <th>Severity</th>
                    <th>Status</th>
                    <th>Target</th>
                    <th>Deadline</th>
                    <th>SLA Result</th>
                  </tr>
                </thead>
                <tbody>
                  {incidents.map((item, index) => (
                    <tr key={item.incident_id || index}>
                      <td>{item.incident_id || "N/A"}</td>
                      <td>{item.severity}</td>
                      <td>{item.status}</td>
                      <td>{item.sla_hours} hours</td>
                      <td>
                        {item.sla_deadline
                          ? new Date(item.sla_deadline).toLocaleString()
                          : "Unavailable"}
                      </td>
                      <td>
                        <span className={`sla-badge ${item.sla_status}`}>
                          {item.sla_status.replace("_", " ")}
                        </span>
                      </td>
                    </tr>
                  ))}
                  {incidents.length === 0 && (
                    <tr><td colSpan={6}>No matching incidents found.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <small className="sla-updated">
            Generated: {new Date(report.generated_at).toLocaleString()}
          </small>
        </>
      )}
    </section>
  );
}
