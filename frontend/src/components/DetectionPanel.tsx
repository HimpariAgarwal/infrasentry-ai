
import { useState } from "react";
import {
  detectRoadDamage,
  type DetectionResponse
} from "../services/detectionApi";

export default function DetectionPanel() {
  const [file, setFile] = useState<File | null>(null);
  const [confidence, setConfidence] = useState(0.10);
  const [result, setResult] = useState<DetectionResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleDetect() {
    if (!file) {
      setError("Please select a road image first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await detectRoadDamage(file, confidence);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Detection failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section style={{
      maxWidth: 720,
      margin: "24px auto",
      padding: 24,
      border: "1px solid #d1d5db",
      borderRadius: 12,
      fontFamily: "Arial, sans-serif"
    }}>
      <h2>InfraSentry AI – Road Damage Detection</h2>
      <p>Upload a road image to detect visible damage.</p>

      <input
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={(event) => {
          setFile(event.target.files?.[0] ?? null);
          setResult(null);
          setError("");
        }}
      />

      <div style={{ marginTop: 20 }}>
        <label htmlFor="confidence-threshold">
          **Confidence Threshold: {(confidence * 100).toFixed(0)}%**
        </label>

        <input
          id="confidence-threshold"
          type="range"
          min="0.10"
          max="0.90"
          step="0.05"
          value={confidence}
          onChange={(event) => {
            setConfidence(Number(event.target.value));
            setResult(null);
          }}
          disabled={loading}
          style={{ width: "100%", marginTop: 10 }}
        />

        <p>
          Lower threshold may detect more objects, including uncertain
          predictions. Higher threshold keeps more confident detections.
        </p>
      </div>

      <div style={{ marginTop: 16 }}>
        <button onClick={handleDetect} disabled={loading || !file}>
          {loading ? "Analyzing..." : "Detect Road Damage"}
        </button>
      </div>

      {error && <p role="alert">{error}</p>}

      {result && (
        <div style={{ marginTop: 20 }}>
          <h3>Detection Results</h3>
          <p>{result.message}</p>
          <p>Model: {result.model}</p>
          <p>Threshold used: {(result.confidence_threshold * 100).toFixed(0)}%</p>
          <p>Detections: {result.detections_count}</p>
          <p>Inference: {result.inference_time_ms} ms</p>

          {result.detections.map((item, index) => (
            <div key={index} style={{
              padding: 10,
              marginTop: 8,
              background: "#f3f4f6",
              borderRadius: 8
            }}>
              <strong>{item.damage_type}</strong>
              <p>Confidence: {(item.confidence * 100).toFixed(2)}%</p>
              <p>Bounding box: {item.bounding_box.join(", ")}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
