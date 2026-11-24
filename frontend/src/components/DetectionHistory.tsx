import { authenticatedFetch } from "../services/apiClient";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Clock,
  Database,
  Eye,
  RefreshCw,
  Trash2,
  X,
  AlertCircle,
  CheckCircle,
  Search,
  Download,
  Filter,
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

  for (const key of ["records", "items", "data", "history"]) {
    if (Array.isArray(payload?.[key])) return payload[key];
  }

  return [];
}

function formatDate(value: string | null) {
  if (!value) return "N/A";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "N/A" : date.toLocaleString();
}

function csvCell(value: unknown): string {
  let text = String(value ?? "");

  // Prevent spreadsheet formula injection.
  if (/^[=+\-@\t\r]/.test(text)) text = "'" + text;

  return `"${text.replace(/"/g, '""')}"`;
}

export default function DetectionHistory() {
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [selected, setSelected] = useState<HistoryRecord | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [deletingId, setDeletingId] = useState("");

  const [search, setSearch] = useState("");
  const [modelFilter, setModelFilter] = useState("all");
  const [detectionFilter, setDetectionFilter] = useState("all");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [sortBy, setSortBy] = useState("newest");
  const [pageSize, setPageSize] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await authenticatedFetch(
        `${API}/api/v1/history?limit=100&offset=0`
      );

      if (!response.ok) {
        throw new Error(`History API returned ${response.status}`);
      }

      setRecords(getRecords(await response.json()));
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Could not load detection history."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHistory();

    const refreshHandler = () => fetchHistory();
    window.addEventListener("infrasentry-history-refresh", refreshHandler);

    return () => {
      window.removeEventListener("infrasentry-history-refresh", refreshHandler);
    };
  }, [fetchHistory]);

  const models = useMemo(
    () => [...new Set(records.map((record) => record.model).filter(Boolean))],
    [records]
  );

  const filteredRecords = useMemo(() => {
    const query = search.trim().toLowerCase();

    return records.filter((record) => {
      const matchesSearch =
        !query ||
        record.filename?.toLowerCase().includes(query) ||
        record.model?.toLowerCase().includes(query) ||
        record.id?.toLowerCase().includes(query) ||
        record.detections?.some((item) =>
          item.damage_type?.toLowerCase().includes(query)
        );

      const matchesModel =
        modelFilter === "all" || record.model === modelFilter;

      const count = Number(record.detections_count || 0);
      const matchesDetection =
        detectionFilter === "all" ||
        (detectionFilter === "detected" && count > 0) ||
        (detectionFilter === "none" && count === 0);

      const recordDate = record.created_at
        ? new Date(record.created_at)
        : null;

      const matchesFrom =
        !dateFrom ||
        (recordDate !== null &&
          !Number.isNaN(recordDate.getTime()) &&
          recordDate >= new Date(`${dateFrom}T00:00:00`));

      const matchesTo =
        !dateTo ||
        (recordDate !== null &&
          !Number.isNaN(recordDate.getTime()) &&
          recordDate <= new Date(`${dateTo}T23:59:59.999`));

      return (
        matchesSearch &&
        matchesModel &&
        matchesDetection &&
        matchesFrom &&
        matchesTo
      );
    });
  }, [records, search, modelFilter, detectionFilter, dateFrom, dateTo]);

  const sortedRecords = useMemo(() => {
    const result = [...filteredRecords];

    result.sort((a, b) => {
      if (sortBy === "oldest") {
        return new Date(a.created_at ?? 0).getTime() -
          new Date(b.created_at ?? 0).getTime();
      }

      if (sortBy === "fastest") {
        return Number(a.inference_time_ms || 0) -
          Number(b.inference_time_ms || 0);
      }

      if (sortBy === "slowest") {
        return Number(b.inference_time_ms || 0) -
          Number(a.inference_time_ms || 0);
      }

      if (sortBy === "most-detections") {
        return Number(b.detections_count || 0) -
          Number(a.detections_count || 0);
      }

      if (sortBy === "least-detections") {
        return Number(a.detections_count || 0) -
          Number(b.detections_count || 0);
      }

      return new Date(b.created_at ?? 0).getTime() -
        new Date(a.created_at ?? 0).getTime();
    });

    return result;
  }, [filteredRecords, sortBy]);

  const totalPages = Math.max(1, Math.ceil(sortedRecords.length / pageSize));

  const paginatedRecords = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sortedRecords.slice(start, start + pageSize);
  }, [sortedRecords, currentPage, pageSize]);

  useEffect(() => {
    setCurrentPage(1);
  }, [search, modelFilter, detectionFilter, dateFrom, dateTo, sortBy, pageSize]);

  useEffect(() => {
    if (currentPage > totalPages) setCurrentPage(totalPages);
  }, [currentPage, totalPages]);

  const totalDetections = records.reduce(
    (total, item) => total + Number(item.detections_count || 0),
    0
  );

  const averageInference = records.length
    ? records.reduce(
        (total, item) => total + Number(item.inference_time_ms || 0),
        0
      ) / records.length
    : 0;

  async function viewDetails(id: string) {
    setDetailLoading(true);
    setError("");

    try {
      const response = await authenticatedFetch(`${API}/api/v1/history/${id}`);

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
      const response = await authenticatedFetch(`${API}/api/v1/history/${id}`, {
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

  function exportCSV() {
    if (filteredRecords.length === 0) {
      setError("No records available to export.");
      return;
    }

    const headers = [
      "Record ID",
      "Filename",
      "Model",
      "Image Width",
      "Image Height",
      "Detection Count",
      "Confidence Threshold",
      "Inference Time (ms)",
      "Detected Classes",
      "Created At",
    ];

    const rows = filteredRecords.map((record) => [
      record.id,
      record.filename,
      record.model,
      record.image_width,
      record.image_height,
      record.detections_count,
      record.confidence_threshold,
      record.inference_time_ms,
      (record.detections ?? [])
        .map((item) => item.damage_type ?? "Unknown")
        .join("; "),
      record.created_at,
    ]);

    const csv = [
      headers.map(csvCell).join(","),
      ...rows.map((row) => row.map(csvCell).join(",")),
    ].join("\r\n");

    const blob = new Blob(["\uFEFF" + csv], {
      type: "text/csv;charset=utf-8;",
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `infrasentry_detection_history_${new Date()
      .toISOString()
      .slice(0, 10)}.csv`;

    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);

    setSuccess(`${filteredRecords.length} records exported to CSV.`);
    setError("");
  }

  function resetFilters() {
    setSearch("");
    setModelFilter("all");
    setDetectionFilter("all");
    setDateFrom("");
    setDateTo("");
  }

  return (
    <section className="history-page">
      <div className="history-heading">
        <div>
          <span className="history-eyebrow">AI MODEL RECORDS</span>
          <h2>Detection History</h2>
          <p>Search, filter and export saved AI inference results.</p>
        </div>

        <div className="history-heading-actions">
          <button
            className="history-export"
            onClick={exportCSV}
            disabled={filteredRecords.length === 0}
          >
            <Download size={16} />
            Export CSV
          </button>

          <button
            className="history-refresh"
            onClick={fetchHistory}
            disabled={loading}
          >
            <RefreshCw size={16} />
            {loading ? "Loading..." : "Refresh"}
          </button>
        </div>
      </div>

      {error && (
        <div className="history-alert history-error">
          <AlertCircle size={17} />
          <span>{error}</span>
          <button onClick={() => setError("")}>×</button>
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

      <div className="history-filter-panel">
        <div className="history-filter-title">
          <Filter size={17} />
          <strong>Search & Filters</strong>
        </div>

        <div className="history-filter-grid">
          <label className="history-search-field">
            <span>Search records</span>
            <div>
              <Search size={16} />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Filename, model, ID or damage class..."
              />
            </div>
          </label>

          <label>
            <span>Model</span>
            <select
              value={modelFilter}
              onChange={(event) => setModelFilter(event.target.value)}
            >
              <option value="all">All Models</option>
              {models.map((model) => (
                <option key={model} value={model}>{model}</option>
              ))}
            </select>
          </label>

          <label>
            <span>Detection Result</span>
            <select
              value={detectionFilter}
              onChange={(event) => setDetectionFilter(event.target.value)}
            >
              <option value="all">All Results</option>
              <option value="detected">Objects Detected</option>
              <option value="none">Zero Detections</option>
            </select>
          </label>

          <label>
            <span>Sort Records</span>
            <select
              value={sortBy}
              onChange={(event) => setSortBy(event.target.value)}
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="fastest">Fastest Inference</option>
              <option value="slowest">Slowest Inference</option>
              <option value="most-detections">Most Detections</option>
              <option value="least-detections">Least Detections</option>
            </select>
          </label>

          <label>
            <span>Rows Per Page</span>
            <select
              value={pageSize}
              onChange={(event) => setPageSize(Number(event.target.value))}
            >
              <option value={5}>5 records</option>
              <option value={10}>10 records</option>
              <option value={20}>20 records</option>
              <option value={50}>50 records</option>
            </select>
          </label>

          <label>
            <span>From Date</span>
            <input
              type="date"
              value={dateFrom}
              max={dateTo || undefined}
              onChange={(event) => setDateFrom(event.target.value)}
            />
          </label>

          <label>
            <span>To Date</span>
            <input
              type="date"
              value={dateTo}
              min={dateFrom || undefined}
              onChange={(event) => setDateTo(event.target.value)}
            />
          </label>

          <button className="history-reset-btn" onClick={resetFilters}>
            <X size={15} />
            Clear Filters
          </button>
        </div>

        <p className="history-filter-result">
          Showing <strong>{sortedRecords.length}</strong> of{" "}
          <strong>{records.length}</strong> records
        </p>
      </div>

      <div className="history-table-panel">
        <div className="history-table-heading">
          <div>
            <h3>Saved Inference Records</h3>
            <p>Records retrieved from the database</p>
          </div>
        </div>

        {loading ? (
          <div className="history-empty">Loading detection history...</div>
        ) : filteredRecords.length === 0 ? (
          <div className="history-empty">
            <Database size={34} />
            <strong>No matching records found</strong>
            <span>Try changing your search or filter settings.</span>
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
                {paginatedRecords.map((record) => (
                  <tr key={record.id}>
                    <td>
                      <strong>{record.filename}</strong>
                      <small>{record.image_width} × {record.image_height}</small>
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
                      {(Number(record.confidence_threshold || 0) * 100).toFixed(0)}%
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

      {!loading && sortedRecords.length > 0 && (
        <div className="history-pagination">
          <span>
            Showing {(currentPage - 1) * pageSize + 1}?
            {Math.min(currentPage * pageSize, sortedRecords.length)} of{" "}
            {sortedRecords.length}
          </span>

          <div className="history-pagination-controls">
            <button
              onClick={() => setCurrentPage(1)}
              disabled={currentPage === 1}
            >
              First
            </button>
            <button
              onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
              disabled={currentPage === 1}
            >
              Previous
            </button>

            <strong>Page {currentPage} / {totalPages}</strong>

            <button
              onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))}
              disabled={currentPage === totalPages}
            >
              Next
            </button>
            <button
              onClick={() => setCurrentPage(totalPages)}
              disabled={currentPage === totalPages}
            >
              Last
            </button>
          </div>
        </div>
      )}

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
              <div><span>Model</span><strong>{selected.model}</strong></div>
              <div>
                <span>Image dimensions</span>
                <strong>{selected.image_width} × {selected.image_height}</strong>
              </div>
              <div>
                <span>Detections</span>
                <strong>{selected.detections_count}</strong>
              </div>
              <div>
                <span>Inference time</span>
                <strong>{Number(selected.inference_time_ms || 0).toFixed(2)} ms</strong>
              </div>
              <div>
                <span>Confidence threshold</span>
                <strong>{(Number(selected.confidence_threshold || 0) * 100).toFixed(0)}%</strong>
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
                      Confidence: {(Number(detection.confidence || 0) * 100).toFixed(1)}%
                    </span>
                    <small>
                      Bounding box: {detection.bounding_box?.join(", ") ?? "N/A"}
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
