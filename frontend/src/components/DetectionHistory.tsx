import { useCallback, useEffect, useState } from "react";
import {
  Clock,
  Database,
  Eye,
  RefreshCw,
  Trash2,
  X,
  AlertCircle,
  CheckCircle,
} from "lucide-react";
import "./DetectionHistory.css";

const API = "http://127.0.0.1:8000";

type Detection = {
  class_id?: number;
  damage_type?: string;
  confidence?: number;
  bounding_box?: number[];
};

type HistoryRecord = {
  id: string;
  filename: string;
  model: string;
  image_width: number;
  image_height: number;
  confidence_threshold: number;
  detections_count: number;
  inference_time_ms: number;
  detections: Detection[];
  created_at: string | null;
};

function getRecords(payload: any): HistoryRecord[] {
  if (Array.isArray(payload)) return payload;

  const candidates = [
    payload?.records,
    payload?.items,
    payload?.data,
    payload?.history,
  ];

  return candidates.find(Array.isArray) ?? [];
}

function formatDate(value: string | null) {
  if (!value) return "N/A";

  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "N/A" : date.toLocaleString();
}

export default function DetectionHistory() {
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [selected, setSelected] = useState<HistoryRecord | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [deletingId, setDeletingId] = useState("");

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API}/api/v1/history?limit=100&offset=0`);

      if (!response.ok) {
        throw new Error(`History API returned ${response.status}`);
      }

      const payload = await response.json();
      setRecords(getRecords(payload));
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not load detection history."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHistory();

    const refreshHandler = () => {
      fetchHistory();
    };

    window.addEventListener("infrasentry-history-refresh", refreshHandler);

    return () => {
      window.removeEventListener(
        "infrasentry-history-refresh",
        refreshHandler
      );
    };
  }, [fetchHistory]);

  async function viewDetails(id: string) {
    setDetailLoading(true);
    setError("");

    try {
      const response = await fetch(`${API}/api/v1/history/${id}`);

      if (!response.ok) {
        throw new Error(`Could not load record (${response.status}).`);
      }

      const payload = await response.json();
      setSelected(payload.record ?? payload);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Could not load record details."
      );
    } finally {
      setDetailLoading(false);
    }
  }

  async function deleteRecord(id: string) {
    if (!window.confirm("Delete this detection history record?")) return;

    setDeletingId(id);
    setError("");
    setSuccess("");

    try {
      const response = await fetch(`${API}/api/v1/history/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error(`Delete failed (${response.status}).`);
      }

      setRecords((current) => current.filter((item) => item.id !== id));

      if (selected?.id === id) setSelected(null);

      setSuccess("Detection history record deleted.");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Could not delete record."
      );
    } finally {
      setDeletingId("");
    }
  }

  const totalDetections = records.reduce(
    (total, item) => total + (item.detections_count || 0),
    0
  );

  const averageInference = records.length
    ? records.reduce(
        (total, item) => total + (item.inference_time_ms || 0),
        0
      ) / records.length
    : 0;

  return (
    <section className="history-page">
      <div className="history-heading">
        <div>
          <span className="history-eyebrow">AI MODEL RECORDS</span>
          <h2>Detection History</h2>
          <p>Review and manage previously saved AI inference results.</p>
        </div>

        <button
          className="history-refresh"
          onClick={fetchHistory}
          disabled={loading}
        >
          <RefreshCw size={16} className={loading ? "history-spinning" : ""} />
          {loading ? "Loading..." : "Refresh"}
        </button>
      </div>

      {error && (
        <div className="history-alert history-error">
          <AlertCircle size={17} />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="history-alert history-success">
          <CheckCircle size={17} />
          <span>{success}</span>
          <button onClick={() => setSuccess("")}>×</button>
        </div>
      )}

      <div className="history-stats">
        <div className="history-stat-card">
          <Database size={21} />
          <div>
            <span>Total Records</span>
            <strong>{records.length}</strong>
          </div>
        </div>

        <div className="history-stat-card">
          <CheckCircle size={21} />
          <div>
            <span>Detected Objects</span>
            <strong>{totalDetections}</strong>
          </div>
        </div>

        <div className="history-stat-card">
          <Clock size={21} />
          <div>
            <span>Average Inference</span>
            <strong>{averageInference.toFixed(1)} ms</strong>
          </div>
        </div>
      </div>

      <div className="history-table-panel">
        <div className="history-table-heading">
          <div>
            <h3>Saved Inference Records</h3>
            <p>{records.length} records loaded from the database</p>
          </div>
        </div>

        {loading ? (
          <div className="history-empty">Loading detection history...</div>
        ) : records.length === 0 ? (
          <div className="history-empty">
            <Database size={34} />
            <strong>No detection history found</strong>
            <span>Upload an image and run AI detection to create a record.</span>
          </div>
        ) : (
          <div className="history-table-scroll">
            <table className="history-table">
              <thead>
                <tr>
                  <th>Image</th>
                  <th>Model</th>
                  <th>Detections</th>
                  <th>Inference</th>
                  <th>Confidence</th>
                  <th>Date</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {records.map((record) => (
                  <tr key={record.id}>
                    <td>
                      <strong>{record.filename}</strong>
                      <small>
                        {record.image_width} × {record.image_height}
                      </small>
                    </td>

                    <td>
                      <span className="history-model">{record.model}</span>
                    </td>

                    <td>
                      <span className="history-count">
                        {record.detections_count}
                      </span>
                    </td>

                    <td>
                      {Number(record.inference_time_ms || 0).toFixed(1)} ms
                    </td>

                    <td>
                      {(
                        Number(record.confidence_threshold || 0) * 100
                      ).toFixed(0)}
                      %
                    </td>

                    <td>{formatDate(record.created_at)}</td>

                    <td>
                      <div className="history-actions">
                        <button
                          className="history-view-btn"
                          title="View details"
                          onClick={() => viewDetails(record.id)}
                          disabled={detailLoading}
                        >
                          <Eye size={16} />
                        </button>

                        <button
                          className="history-delete-btn"
                          title="Delete record"
                          onClick={() => deleteRecord(record.id)}
                          disabled={deletingId === record.id}
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selected && (
        <div className="history-detail-overlay">
          <div className="history-detail-modal">
            <div className="history-detail-heading">
              <div>
                <span className="history-eyebrow">RECORD DETAILS</span>
                <h3>{selected.filename}</h3>
              </div>

              <button
                className="history-close-btn"
                onClick={() => setSelected(null)}
                aria-label="Close details"
              >
                <X size={19} />
              </button>
            </div>

            <div className="history-detail-grid">
              <div>
                <span>Model</span>
                <strong>{selected.model}</strong>
              </div>
              <div>
                <span>Image dimensions</span>
                <strong>
                  {selected.image_width} × {selected.image_height}
                </strong>
              </div>
              <div>
                <span>Detections</span>
                <strong>{selected.detections_count}</strong>
              </div>
              <div>
                <span>Inference time</span>
                <strong>
                  {Number(selected.inference_time_ms || 0).toFixed(2)} ms
                </strong>
              </div>
              <div>
                <span>Confidence threshold</span>
                <strong>
                  {(Number(selected.confidence_threshold || 0) * 100).toFixed(0)}%
                </strong>
              </div>
              <div>
                <span>Created at</span>
                <strong>{formatDate(selected.created_at)}</strong>
              </div>
            </div>

            <h4>Detected Objects</h4>

            {!selected.detections?.length ? (
              <p className="history-no-detections">
                No objects were detected in this inference.
              </p>
            ) : (
              <div className="history-detection-list">
                {selected.detections.map((detection, index) => (
                  <div className="history-detection-item" key={index}>
                    <strong>{detection.damage_type ?? "Unknown"}</strong>
                    <span>
                      Confidence:{" "}
                      {(Number(detection.confidence || 0) * 100).toFixed(1)}%
                    </span>
                    <small>
                      Bounding box:{" "}
                      {detection.bounding_box?.join(", ") ?? "N/A"}
                    </small>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
