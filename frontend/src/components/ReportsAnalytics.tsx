import type { CSSProperties } from "react";
import "./ReportsAnalytics.css";

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

type Props = {
  reports: Report[];
};

function ReportsAnalytics({ reports }: Props) {
  const total = reports.length;

  const submitted = reports.filter(r => r.status === "submitted").length;
  const underReview = reports.filter(r => r.status === "under_review").length;
  const resolved = reports.filter(r => r.status === "resolved").length;

  const averageSeverity = total
    ? reports.reduce((sum, r) => sum + Number(r.severity || 0), 0) / total
    : 0;

  const highSeverity = reports.filter(r => r.severity >= 4).length;

  const damageTypes = Object.entries(
    reports.reduce<Record<string, number>>((acc, report) => {
      const type = report.damage_type || "Unknown";
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {})
  ).sort((a, b) => b[1] - a[1]);

  const severityCounts = [1, 2, 3, 4, 5].map(level => ({
    level,
    count: reports.filter(r => Number(r.severity) === level).length,
  }));

  const lastSevenDays = Array.from({ length: 7 }, (_, index) => {
    const date = new Date();
    date.setHours(0, 0, 0, 0);
    date.setDate(date.getDate() - (6 - index));

    const key = date.toLocaleDateString();

    return {
      label: date.toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
      }),
      count: reports.filter(report => {
        if (!report.created_at) return false;
        return new Date(report.created_at).toLocaleDateString() === key;
      }).length,
    };
  });

  const maxDaily = Math.max(1, ...lastSevenDays.map(day => day.count));
  const maxDamage = Math.max(1, ...damageTypes.map(item => item[1]));
  const maxSeverity = Math.max(1, ...severityCounts.map(item => item.count));

  return (
    <div className="reports-analytics">
      <div className="ra-intro">
        <div>
          <h2>Reports Intelligence</h2>
          <p>Analysis of road damage reports recorded in InfraSentry.</p>
        </div>
        <span className="ra-live">LIVE DATA</span>
      </div>

      <section className="ra-kpi-grid">
        <div className="ra-kpi">
          <span>Total Reports</span>
          <strong>{total}</strong>
          <small>All recorded reports</small>
        </div>
        <div className="ra-kpi">
          <span>High Severity</span>
          <strong>{highSeverity}</strong>
          <small>Severity level 4 and 5</small>
        </div>
        <div className="ra-kpi">
          <span>Average Severity</span>
          <strong>{averageSeverity.toFixed(2)} / 5</strong>
          <small>Across all reports</small>
        </div>
        <div className="ra-kpi">
          <span>Resolution Rate</span>
          <strong>{total ? ((resolved / total) * 100).toFixed(1) : "0.0"}%</strong>
          <small>{resolved} resolved reports</small>
        </div>
      </section>

      <section className="ra-grid">
        <div className="ra-panel">
          <h3>Report Status Overview</h3>
          <p className="ra-subtitle">Current progress of all reports</p>

          {[
            { label: "Submitted", value: submitted, color: "#3985ed" },
            { label: "Under Review", value: underReview, color: "#e6a23c" },
            { label: "Resolved", value: resolved, color: "#27a477" },
          ].map(item => (
            <div className="ra-status" key={item.label}>
              <div className="ra-status-label">
                <span>{item.label}</span>
                <strong>{item.value}</strong>
              </div>
              <div className="ra-track">
                <div
                  className="ra-fill"
                  style={{
                    width: `${total ? (item.value / total) * 100 : 0}%`,
                    background: item.color,
                  }}
                />
              </div>
            </div>
          ))}
        </div>

        <div className="ra-panel">
          <h3>Severity Distribution</h3>
          <p className="ra-subtitle">Number of reports at each severity level</p>

          <div className="ra-bars">
            {severityCounts.map(item => (
              <div className="ra-bar-column" key={item.level}>
                <strong>{item.count}</strong>
                <div className="ra-bar-track">
                  <div
                    className="ra-bar"
                    style={{
                      height: `${(item.count / maxSeverity) * 100}%`,
                      background: item.level >= 4
                        ? "#dc5555"
                        : item.level === 3
                          ? "#e6a23c"
                          : "#27a477",
                    }}
                  />
                </div>
                <span>Level {item.level}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="ra-panel">
          <h3>Damage Type Distribution</h3>
          <p className="ra-subtitle">Most frequently reported damage types</p>

          {damageTypes.length === 0 ? (
            <p className="ra-empty">No damage reports available yet.</p>
          ) : (
            damageTypes.slice(0, 7).map(([name, count]) => (
              <div className="ra-damage-row" key={name}>
                <div className="ra-status-label">
                  <span>{name}</span>
                  <strong>{count}</strong>
                </div>
                <div className="ra-track">
                  <div
                    className="ra-fill ra-damage-fill"
                    style={{ width: `${(count / maxDamage) * 100}%` }}
                  />
                </div>
              </div>
            ))
          )}
        </div>

        <div className="ra-panel">
          <h3>Last 7 Days</h3>
          <p className="ra-subtitle">Reports created per day</p>

          <div className="ra-bars ra-week-bars">
            {lastSevenDays.map(day => (
              <div className="ra-bar-column" key={day.label}>
                <strong>{day.count}</strong>
                <div className="ra-bar-track">
                  <div
                    className="ra-bar ra-week-bar"
                    style={{
                      height: `${(day.count / maxDaily) * 100}%`,
                    } as CSSProperties}
                  />
                </div>
                <span>{day.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <div className="ra-footer">
        Analytics calculated from {total} report records currently loaded from the API.
      </div>
    </div>
  );
}

export default ReportsAnalytics;
