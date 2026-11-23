import { useEffect, useMemo, useState } from "react";
import {
  CircleMarker,
  MapContainer,
  Popup,
  TileLayer,
  useMap,
} from "react-leaflet";
import type { LatLngBoundsExpression } from "leaflet";
import "leaflet/dist/leaflet.css";
import "./RoadDamageMap.css";

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

function MapAutoFit({ reports }: Props) {
  const map = useMap();

  useEffect(() => {
    if (!reports.length) return;

    const bounds: LatLngBoundsExpression = reports.map(report => [
      report.latitude,
      report.longitude,
    ]);

    map.fitBounds(bounds, { padding: [45, 45], maxZoom: 14 });
  }, [map, reports]);

  return null;
}

function markerColor(severity: number) {
  if (severity >= 4) return "#dc4444";
  if (severity === 3) return "#e59a26";
  return "#269b69";
}

function RoadDamageMap({ reports }: Props) {
  const [severityFilter, setSeverityFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  const validReports = useMemo(
    () => reports.filter(report =>
      Number.isFinite(Number(report.latitude)) &&
      Number.isFinite(Number(report.longitude)) &&
      Number(report.latitude) >= -90 &&
      Number(report.latitude) <= 90 &&
      Number(report.longitude) >= -180 &&
      Number(report.longitude) <= 180
    ),
    [reports]
  );

  const filteredReports = validReports.filter(report => {
    const severityMatches =
      severityFilter === "all" ||
      report.severity === Number(severityFilter);

    const statusMatches =
      statusFilter === "all" || report.status === statusFilter;

    return severityMatches && statusMatches;
  });

  const defaultCenter: [number, number] =
    filteredReports.length > 0
      ? [filteredReports[0].latitude, filteredReports[0].longitude]
      : [28.6139, 77.2090];

  return (
    <div className="road-map-page">
      <div className="road-map-heading">
        <div>
          <h2>Geographical Damage Intelligence</h2>
          <p>Explore road damage reports by their recorded coordinates.</p>
        </div>
        <span className="road-map-count">
          {filteredReports.length} / {validReports.length} locations
        </span>
      </div>

      <div className="road-map-stats">
        <div>
          <span>Mapped Reports</span>
          <strong>{validReports.length}</strong>
        </div>
        <div>
          <span>Critical Locations</span>
          <strong>{validReports.filter(r => r.severity >= 4).length}</strong>
        </div>
        <div>
          <span>Resolved</span>
          <strong>{validReports.filter(r => r.status === "resolved").length}</strong>
        </div>
      </div>

      <div className="road-map-filters">
        <label>
          Severity
          <select
            value={severityFilter}
            onChange={event => setSeverityFilter(event.target.value)}
          >
            <option value="all">All Levels</option>
            <option value="1">Level 1</option>
            <option value="2">Level 2</option>
            <option value="3">Level 3</option>
            <option value="4">Level 4</option>
            <option value="5">Level 5</option>
          </select>
        </label>

        <label>
          Status
          <select
            value={statusFilter}
            onChange={event => setStatusFilter(event.target.value)}
          >
            <option value="all">All Statuses</option>
            <option value="submitted">Submitted</option>
            <option value="under_review">Under Review</option>
            <option value="resolved">Resolved</option>
          </select>
        </label>

        <button
          type="button"
          onClick={() => {
            setSeverityFilter("all");
            setStatusFilter("all");
          }}
        >
          Clear Filters
        </button>
      </div>

      {validReports.length === 0 ? (
        <div className="road-map-empty">
          <h3>No valid report locations</h3>
          <p>Submit road damage reports with valid latitude and longitude to view them here.</p>
        </div>
      ) : filteredReports.length === 0 ? (
        <div className="road-map-empty">
          <h3>No matching locations</h3>
          <p>Try changing the map filters.</p>
        </div>
      ) : (
        <MapContainer
          center={defaultCenter}
          zoom={11}
          scrollWheelZoom
          className="road-leaflet-map"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <MapAutoFit reports={filteredReports} />

          {filteredReports.map(report => (
            <CircleMarker
              key={report.id}
              center={[report.latitude, report.longitude]}
              radius={Math.max(7, Number(report.severity) * 2.5)}
              pathOptions={{
                color: markerColor(report.severity),
                fillColor: markerColor(report.severity),
                fillOpacity: 0.75,
                weight: 2,
              }}
            >
              <Popup>
                <div className="road-map-popup">
                  <strong>{report.damage_type}</strong>
                  <p>{report.description}</p>
                  <span>Severity: {report.severity}/5</span>
                  <br />
                  <span>Status: {report.status.replace("_", " ")}</span>
                  <br />
                  <span>
                    Coordinates: {report.latitude}, {report.longitude}
                  </span>
                  <br />
                  <small>Report ID: {report.id}</small>
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      )}

      <div className="road-map-legend">
        <span><i className="legend-dot low" /> Low (1–2)</span>
        <span><i className="legend-dot medium" /> Moderate (3)</span>
        <span><i className="legend-dot high" /> High/Critical (4–5)</span>
      </div>

      <p className="road-map-note">
        Map markers use the coordinates submitted with each report. Map tiles are provided by OpenStreetMap.
      </p>
    </div>
  );
}

export default RoadDamageMap;
