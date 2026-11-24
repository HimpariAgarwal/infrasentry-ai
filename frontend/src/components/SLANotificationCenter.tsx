import { useCallback, useEffect, useRef, useState } from "react";
import { Bell, BellRing, CheckCheck, RefreshCw, ShieldAlert, X } from "lucide-react";
import { API_BASE, authenticatedFetch } from "../services/authService";
import "./SLANotificationCenter.css";

interface SLAAlert {
  id?: string | number;
  incident_id?: string | number;
  severity?: string;
  escalation_level?: string;
  message?: string;
  description?: string;
  status?: string;
  created_at?: string;
  [key: string]: unknown;
}

export default function SLANotificationCenter() {
  const [alerts, setAlerts] = useState<SLAAlert[]>([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [permission, setPermission] = useState<NotificationPermission>(
    typeof Notification === "undefined" ? "denied" : Notification.permission
  );
  const [readIds, setReadIds] = useState<string[]>(() => {
    try {
      return JSON.parse(sessionStorage.getItem("sla-read-alerts") || "[]");
    } catch {
      return [];
    }
  });
  const initialized = useRef(false);
  const knownIds = useRef<Set<string>>(new Set());

  const getId = (alert: SLAAlert, index: number) =>
    String(alert.id ?? `${alert.incident_id ?? "incident"}-${alert.created_at ?? index}`);

  const loadAlerts = useCallback(async () => {
    setLoading(true);
    try {
      const response = await authenticatedFetch(`${API_BASE}/api/v1/sla/alerts`);
      if (!response.ok) throw new Error(`Request failed: ${response.status}`);

      const data = await response.json();
      const items: SLAAlert[] = Array.isArray(data)
        ? data
        : Array.isArray(data.alerts)
          ? data.alerts
          : [];

      const active = items.filter(
        (item) => String(item.status ?? "active").toLowerCase() !== "resolved"
      );

      if (initialized.current && typeof Notification !== "undefined" &&
          Notification.permission === "granted") {
        active.forEach((alert, index) => {
          const id = getId(alert, index);
          if (!knownIds.current.has(id)) {
            new Notification("InfraSentry AI — SLA Alert", {
              body: alert.message || alert.description ||
                `Incident ${alert.incident_id ?? id} has an SLA alert.`,
              tag: `sla-${id}`,
            });
          }
        });
      }

      knownIds.current = new Set(active.map(getId));
      initialized.current = true;
      setAlerts(active);
    } catch (error) {
      console.error("SLA notifications:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadAlerts();
    const timer = window.setInterval(() => void loadAlerts(), 30000);
    return () => window.clearInterval(timer);
  }, [loadAlerts]);

  const enableNotifications = async () => {
    if (typeof Notification === "undefined") return;
    const result = await Notification.requestPermission();
    setPermission(result);
  };

  const markAllRead = () => {
    const ids = alerts.map(getId);
    const updated = Array.from(new Set([...readIds, ...ids]));
    setReadIds(updated);
    sessionStorage.setItem("sla-read-alerts", JSON.stringify(updated));
  };

  const unreadCount = alerts.filter(
    (alert, index) => !readIds.includes(getId(alert, index))
  ).length;

  return (
    <div className="sla-notification-root">
      <button
        className="sla-notification-trigger"
        onClick={() => setOpen((value) => !value)}
        title="SLA notifications"
        aria-label="Open SLA notifications"
      >
        {unreadCount > 0 ? <BellRing size={20} /> : <Bell size={20} />}
        {unreadCount > 0 && <span className="sla-notification-count">{unreadCount}</span>}
      </button>

      {open && (
        <section className="sla-notification-panel">
          <div className="sla-notification-heading">
            <div>
              <strong>SLA Notifications</strong>
              <small>{alerts.length} active alerts</small>
            </div>
            <button onClick={() => setOpen(false)} aria-label="Close">
              <X size={18} />
            </button>
          </div>

          <div className="sla-notification-actions">
            <button onClick={() => void loadAlerts()} disabled={loading}>
              <RefreshCw size={14} /> Refresh
            </button>
            <button onClick={markAllRead}>
              <CheckCheck size={14} /> Mark all read
            </button>
          </div>

          {permission !== "granted" && typeof Notification !== "undefined" && (
            <button className="sla-enable-browser" onClick={() => void enableNotifications()}>
              <BellRing size={15} />
              {permission === "denied" ? "Browser notifications blocked" : "Enable browser notifications"}
            </button>
          )}

          <div className="sla-notification-list">
            {alerts.length === 0 ? (
              <p className="sla-notification-empty">No active SLA alerts.</p>
            ) : alerts.map((alert, index) => {
              const id = getId(alert, index);
              const isRead = readIds.includes(id);
              return (
                <article className={`sla-notification-item ${isRead ? "read" : "unread"}`} key={id}>
                  <ShieldAlert size={18} />
                  <div>
                    <strong>{alert.escalation_level || alert.severity || "SLA Alert"}</strong>
                    <p>{alert.message || alert.description || `Incident ${alert.incident_id ?? id}`}</p>
                    <small>Incident: {String(alert.incident_id ?? "N/A")}</small>
                  </div>
                </article>
              );
            })}
          </div>
        </section>
      )}
    </div>
  );
}
