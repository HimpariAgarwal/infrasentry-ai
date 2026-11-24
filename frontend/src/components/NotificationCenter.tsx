import { useCallback, useEffect, useState } from "react";
import {
  Bell, CheckCheck, RefreshCw, ShieldAlert, X
} from "lucide-react";
import {
  getStoredNotifications,
  syncSecurityNotifications,
  markNotificationRead,
  markAllNotificationsRead,
  type SecurityNotification,
} from "../services/notificationService";
import "./NotificationCenter.css";

export default function NotificationCenter() {
  const [notifications, setNotifications] = useState<SecurityNotification[]>(
    getStoredNotifications
  );
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const unreadCount = notifications.filter(item => !item.read).length;

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const result = await syncSecurityNotifications();
      setNotifications(result);
    } catch (error) {
      console.error("Notification refresh failed:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const interval = window.setInterval(refresh, 30000);
    return () => window.clearInterval(interval);
  }, [refresh]);

  const markRead = (id: string) => {
    setNotifications(markNotificationRead(id));
  };

  const markAllRead = () => {
    setNotifications(markAllNotificationsRead());
  };

  return (
    <div className="notification-center">
      <button
        className="notification-bell"
        onClick={() => setOpen(previous => !previous)}
        aria-label="Toggle notifications"
      >
        <Bell size={20} />
        {unreadCount > 0 && (
          <span className="notification-count">
            {unreadCount > 99 ? "99+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="notification-panel">
          <div className="notification-panel-header">
            <h3><ShieldAlert size={18} /> Notifications</h3>
            <div>
              <button onClick={refresh} disabled={loading} title="Refresh">
                <RefreshCw size={16} />
              </button>
              <button onClick={markAllRead} title="Mark all read">
                <CheckCheck size={16} />
              </button>
              <button onClick={() => setOpen(false)} title="Close">
                <X size={16} />
              </button>
            </div>
          </div>

          <div className="notification-list">
            {notifications.length === 0 ? (
              <p className="notification-empty">No notifications available.</p>
            ) : notifications.map(item => (
              <article
                key={item.id}
                className={`notification-item ${item.read ? "read" : "unread"}`}
                onClick={() => markRead(item.id)}
              >
                <div className="notification-item-top">
                  <strong>{item.type.replaceAll("_", " ")}</strong>
                  <span>{item.severity}</span>
                </div>
                <p>{item.message}</p>
                <small>{new Date(item.timestamp).toLocaleString()}</small>
              </article>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
