export interface DamageDetection {
  class_id: number;
  damage_type: string;
  confidence: number;
  bounding_box: number[];
}

export interface DetectionResponse {
  success: boolean;
  filename: string;
  model: string;
  image_width: number;
  image_height: number;
  confidence_threshold: number;
  detections_count: number;
  detections: DamageDetection[];
  inference_time_ms: number;
  message: string;
}

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function detectRoadDamage(
  file: File,
  confidence = 0.10
): Promise<DetectionResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    `${API_URL}/api/v1/detect?confidence=${confidence}`,
    {
      method: "POST",
      body: formData
    }
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Road damage detection failed.");
  }

  return response.json();
}
