import { authenticatedFetch } from "../services/apiClient";
import { useEffect, useState } from "react";

type Detection = {
  damage_type: string;
  confidence: number;
};

type Sample = {
  image: string;
  detections_count: number;
  inference_time_ms: number;
  detections: Detection[];
};

type Benchmark = {
  benchmark_date_utc: string;
  benchmark_type: string;
  images_attempted: number;
  images_succeeded: number;
  images_failed: number;
  total_detections: number;
  images_with_detections: number;
  images_without_detections: number;
  average_inference_time_ms: number;
  median_inference_time_ms: number;
  maximum_inference_time_ms: number;
  minimum_inference_time_ms: number;
  results: Sample[];
};

const panel: React.CSSProperties = {
  background: "var(--panel, #ffffff)",
  border: "1px solid var(--border, #e5e7eb)",
  borderRadius: 14,
  padding: 20,
  minWidth: 0,
};

const muted: React.CSSProperties = {
  color: "var(--muted, #64748b)",
  fontSize: 13,
};

export default function BenchmarkAnalytics() {
  const [data, setData] = useState<Benchmark | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    authenticatedFetch("/data/day21_inference_benchmark.json")
      .then((response) => {
        if (!response.ok) throw new Error("Benchmark report could not be loaded.");
        return response.json();
      })
      .then((report: Benchmark) => setData(report))
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div style={panel}>Loading AI analytics...</div>;
  if (error) return <div style={panel}>Analytics error: {error}</div>;
  if (!data) return null;

  const warmRuns = data.results.slice(1);
  const warmMax = Math.max(1, ...warmRuns.map((item) => item.inference_time_ms));
  const detections = data.results.flatMap((item) => item.detections);
  const classCounts = detections.reduce<Record<string, number>>((acc, item) => {
    acc[item.damage_type] = (acc[item.damage_type] || 0) + 1;
    return acc;
  }, {});

  const metricCards = [
    { label: "Images tested", value: data.images_attempted, detail: `${data.images_succeeded} successful` },
    { label: "Total detections", value: data.total_detections, detail: "Across benchmark images" },
    { label: "Median inference", value: `${data.median_inference_time_ms} ms`, detail: "Typical measured latency" },
    { label: "Average inference", value: `${data.average_inference_time_ms} ms`, detail: "Includes first model load" },
  ];

  return (
    <div style={{ display: "grid", gap: 20, paddingBottom: 24 }}>
      <section style={panel}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
          <div>
            <h2 style={{ margin: "0 0 6px" }}>AI Performance Analytics</h2>
            <p style={muted}>YOLO road damage detection · Day 21 benchmark</p>
          </div>
          <span style={{ ...muted, alignSelf: "center" }}>Benchmark snapshot</span>
        </div>
        <p style={{ ...muted, marginBottom: 0 }}>
          {data.benchmark_type}
        </p>
      </section>

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 14 }}>
        {metricCards.map((metric) => (
          <div key={metric.label} style={panel}>
            <p style={muted}>{metric.label}</p>
            <h2 style={{ fontSize: 27, margin: "8px 0" }}>{metric.value}</h2>
            <p style={muted}>{metric.detail}</p>
          </div>
        ))}
      </section>

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 16 }}>
        <div style={panel}>
          <h3>Detection coverage</h3>
          <p style={muted}>Images with and without model detections</p>
          <div style={{ height: 14, display: "flex", borderRadius: 20, overflow: "hidden", background: "#e5e7eb" }}>
            <div style={{ width: `${data.images_attempted ? data.images_with_detections / data.images_attempted * 100 : 0}%`, background: "#16a36a" }} />
          </div>
          <p><strong>{data.images_with_detections}</strong> images with detections</p>
          <p><strong>{data.images_without_detections}</strong> images with zero detections</p>
          <p style={muted}>Failed images: {data.images_failed}</p>
        </div>

        <div style={panel}>
          <h3>Detection classes</h3>
          <p style={muted}>Classes returned by this benchmark</p>
          {Object.entries(classCounts).length === 0 ? (
            <p>No detections recorded.</p>
          ) : Object.entries(classCounts).map(([name, count]) => (
            <div key={name} style={{ display: "flex", justifyContent: "space-between", padding: "10px 0", borderBottom: "1px solid #e5e7eb" }}>
              <span>{name}</span><strong>{count}</strong>
            </div>
          ))}
        </div>
      </section>

      <section style={panel}>
        <h3>Inference time by image</h3>
        <p style={muted}>Warm-run timings; first image excluded because it includes model initialization.</p>
        <div style={{ display: "grid", gap: 10 }}>
          {warmRuns.map((item) => (
            <div key={item.image} style={{ display: "grid", gridTemplateColumns: "125px 1fr 75px", alignItems: "center", gap: 10 }}>
              <span style={{ ...muted, overflow: "hidden", textOverflow: "ellipsis" }}>{item.image.replace(".jpg", "")}</span>
              <div style={{ height: 12, background: "#e8edf3", borderRadius: 10, overflow: "hidden" }}>
                <div style={{ width: `${Math.max(2, item.inference_time_ms / warmMax * 100)}%`, height: "100%", background: "#3984d6", borderRadius: 10 }} />
              </div>
              <strong style={{ fontSize: 12, textAlign: "right" }}>{item.inference_time_ms.toFixed(1)} ms</strong>
            </div>
          ))}
        </div>
      </section>

      <section style={panel}>
        <h3>Detection results</h3>
        <p style={muted}>Actual detections and confidence scores returned by YOLO</p>
        {detections.length === 0 ? (
          <p>No detections in this benchmark.</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
              <thead>
                <tr>
                  <th style={{ padding: 10 }}>Damage class</th>
                  <th style={{ padding: 10 }}>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {detections.map((item, index) => (
                  <tr key={`${item.damage_type}-${index}`}>
                    <td style={{ padding: 10, borderTop: "1px solid #e5e7eb" }}>{item.damage_type}</td>
                    <td style={{ padding: 10, borderTop: "1px solid #e5e7eb" }}>{(item.confidence * 100).toFixed(2)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section style={{ ...panel, borderLeft: "4px solid #d99b32" }}>
        <h3>Model evaluation note</h3>
        <p style={muted}>
          This dashboard reports inference performance and raw model outputs only.
          Zero detections do not prove an image has no road damage. Detection accuracy
          requires comparison against ground-truth annotations.
        </p>
        <p style={muted}>First image latency: {data.results[0]?.inference_time_ms ?? "N/A"} ms</p>
        <p style={muted}>Minimum latency: {data.minimum_inference_time_ms} ms · Maximum latency: {data.maximum_inference_time_ms} ms</p>
      </section>
    </div>
  );
}
