import "./SystemHealth.css";
import { useCallback, useEffect, useState } from "react";
import {
  Activity, Cpu, Database, HardDrive, MemoryStick,
  RefreshCw, Server, Clock, AlertTriangle, CheckCircle, XCircle
} from "lucide-react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface HealthData {
  status: string;
  timestamp: string;
  uptime_seconds: number;
  system: {
    platform: string;
    platform_release: string;
    architecture: string;
    processor: string;
    cpu_percent: number;
    cpu_count: number;
    memory: {
      total_mb: number;
      used_mb: number;
      available_mb: number;
      percent: number;
    };
    disk: {
      total_gb: number;
      used_gb: number;
      free_gb: number;
      percent: number;
    };
  };
  database: {
    connected: boolean;
    status: string;
    error?: string;
  };
}

export default function SystemHealth() {
  const [data, setData] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState("");

  const fetchHealth = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/system-health`);
      if (!response.ok) throw new Error(`API error: ${response.status}`);
      const result: HealthData = await response.json();
      setData(result);
      setError("");
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to connect to backend");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
    const interval = window.setInterval(fetchHealth, 15000);
    return () => window.clearInterval(interval);
  }, [fetchHealth]);

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  const Metric = ({
    title, value, detail, icon: Icon, percent
  }: {
    title: string;
    value: string;
    detail: string;
    icon: typeof Activity;
    percent?: number;
  }) => (
    <div className="health-metric">
      <div className="health-metric-heading">
        <span>{title}</span>
        <Icon size={20} />
      </div>
      <div className="health-metric-value">{value}</div>
      <div className="health-metric-detail">{detail}</div>
      {percent !== undefined && (
        <div className="health-progress">
          <div style={{ width: `${Math.min(100, Math.max(0, percent))}%` }} />
        </div>
      )}
    </div>
  );

  if (loading && !data) {
    return <div className="health-message"><RefreshCw className="health-spin" /> Loading system health...</div>;
  }

  if (!data) {
    return (
      <div className="health-message health-error">
        <AlertTriangle size={24} />
        <p>{error || "System health information unavailable."}</p>
        <button onClick={fetchHealth}>Retry</button>
      </div>
    );
  }

  return (
    <section className="system-health-page">
      <div className="health-topbar">
        <div>
          <h2>System Health Monitor</h2>
          <p>Live infrastructure and resource monitoring</p>
        </div>
        <button className="health-refresh" onClick={fetchHealth}>
          <RefreshCw size={16} /> Refresh
        </button>
      </div>

      {error && <div className="health-warning"><AlertTriangle size={16} /> {error}</div>}

      <div className="health-status-card">
        <div className="health-status-icon">
          {data.status === "healthy" ? <CheckCircle size={26} /> : <AlertTriangle size={26} />}
        </div>
        <div>
          <strong>Backend {data.status.toUpperCase()}</strong>
          <p>Last updated: {lastUpdated || "Waiting..."}</p>
        </div>
        <span className={`health-status-badge ${data.status}`}>
          {data.status}
        </span>
      </div>

      <div className="health-grid">
        <Metric title="CPU Usage" value={`${data.system.cpu_percent}%`}
          detail={`${data.system.cpu_count} logical cores`} icon={Cpu}
          percent={data.system.cpu_percent} />
        <Metric title="Memory Usage" value={`${data.system.memory.percent}%`}
          detail={`${data.system.memory.used_mb.toFixed(0)} / ${data.system.memory.total_mb.toFixed(0)} MB`}
          icon={MemoryStick} percent={data.system.memory.percent} />
        <Metric title="Disk Usage" value={`${data.system.disk.percent}%`}
          detail={`${data.system.disk.used_gb} / ${data.system.disk.total_gb} GB`}
          icon={HardDrive} percent={data.system.disk.percent} />
        <Metric title="Backend Uptime" value={formatUptime(data.uptime_seconds)}
          detail="Since backend startup" icon={Clock} />
      </div>

      <div className="health-details-grid">
        <div className="health-detail-card">
          <h3><Server size={19} /> System Information</h3>
          <p><span>Operating System</span><strong>{data.system.platform} {data.system.platform_release}</strong></p>
          <p><span>Architecture</span><strong>{data.system.architecture}</strong></p>
          <p><span>Processor</span><strong>{data.system.processor}</strong></p>
          <p><span>CPU Cores</span><strong>{data.system.cpu_count}</strong></p>
          <p><span>Available RAM</span><strong>{data.system.memory.available_mb.toFixed(0)} MB</strong></p>
          <p><span>Free Disk</span><strong>{data.system.disk.free_gb} GB</strong></p>
        </div>

        <div className="health-detail-card">
          <h3><Database size={19} /> Service Status</h3>
          <p>
            <span>Backend API</span>
            <strong className="health-connected"><CheckCircle size={15} /> Connected</strong>
          </p>
          <p>
            <span>Database</span>
            <strong className={data.database.connected ? "health-connected" : "health-disconnected"}>
              {data.database.connected ? <CheckCircle size={15} /> : <XCircle size={15} />}
              {data.database.status}
            </strong>
          </p>
          {data.database.error && <p className="health-db-error">{data.database.error}</p>}
          <p><span>Monitoring</span><strong><Activity size={15} /> Active</strong></p>
          <p><span>Refresh Interval</span><strong>15 seconds</strong></p>
        </div>
      </div>
    </section>
  );
}
