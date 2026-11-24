import { API_BASE, authenticatedFetch } from "./authService";

export interface SecurityNotification {
  id: string;
  timestamp: string;
  type: string;
  severity: string;
  message: string;
  source: string;
  status: string;
  read: boolean;
}

const STORAGE_KEY = "infrasentry_notifications";

export function getStoredNotifications(): SecurityNotification[] {
  try {
    return JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "[]");
  } catch {
    return [];
  }
}

function saveNotifications(items: SecurityNotification[]) {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(items.slice(0, 100)));
}

export async function syncSecurityNotifications() {
  const response = await authenticatedFetch(
    `${API_BASE}/api/v1/security/alerts`
  );

  if (!response.ok) throw new Error("Notification sync failed.");

  const data = await response.json();
  const stored = getStoredNotifications();
  const readIds = new Set(stored.filter(item => item.read).map(item => item.id));

  const notifications = (data.alerts || []).map((alert: SecurityNotification) => ({
    ...alert,
    read: readIds.has(alert.id),
  }));

  saveNotifications(notifications);
  return notifications;
}

export function markNotificationRead(id: string) {
  const notifications = getStoredNotifications().map(item =>
    item.id === id ? { ...item, read: true } : item
  );
  saveNotifications(notifications);
  return notifications;
}

export function markAllNotificationsRead() {
  const notifications = getStoredNotifications().map(item => ({
    ...item,
    read: true,
  }));
  saveNotifications(notifications);
  return notifications;
}
