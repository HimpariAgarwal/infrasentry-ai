import { authenticatedFetch } from "./services/apiClient";

import { useEffect, useState } from "react";
import { ImagePlus, Upload, CheckCircle, AlertCircle } from "lucide-react";

const API = "http://127.0.0.1:8000";

type Report = {
  id: string;
  damage_type: string;
  description: string;
};

function ImageUpload() {
  const [reports, setReports] = useState<Report[]>([]);
  const [selectedReport, setSelectedReport] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState("");
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [uploadedUrl, setUploadedUrl] = useState("");

  useEffect(() => {
    async function fetchReports() {
      try {
        const response = await authenticatedFetch(`${API}/reports`);

        if (!response.ok) {
          throw new Error("Could not fetch reports.");
        }

        const data = await response.json();

        const reportList = Array.isArray(data)
          ? data
          : Array.isArray(data?.reports)
            ? data.reports
            : Array.isArray(data?.items)
              ? data.items
              : null;

        if (!reportList) {
          throw new Error("Unexpected reports API response.");
        }

        setReports(reportList);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Could not load reports."
        );
      } finally {
        setFetching(false);
      }
    }

    fetchReports();
  }, []);

  useEffect(() => {
    if (!file) {
      setPreview("");
      return;
    }

    const objectUrl = URL.createObjectURL(file);
    setPreview(objectUrl);

    return () => URL.revokeObjectURL(objectUrl);
  }, [file]);

  function handleFileChange(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    const selectedFile = event.target.files?.[0];

    setError("");
    setSuccess("");
    setUploadedUrl("");

    if (!selectedFile) {
      setFile(null);
      return;
    }

    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "image/webp",
    ];

    if (!allowedTypes.includes(selectedFile.type)) {
      setError("Please select a JPG, PNG or WEBP image.");
      setFile(null);
      event.target.value = "";
      return;
    }

    if (selectedFile.size > 5 * 1024 * 1024) {
      setError("Image size must not exceed 5 MB.");
      setFile(null);
      event.target.value = "";
      return;
    }

    setFile(selectedFile);
  }

  async function uploadImage(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setSuccess("");
    setUploadedUrl("");

    if (!selectedReport) {
      setError("Please select a road damage report.");
      return;
    }

    if (!file) {
      setError("Please choose an image first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);

    try {
      const response = await authenticatedFetch(
        `${API}/images/upload/${encodeURIComponent(selectedReport)}`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Image upload failed.");
      }

      setSuccess("Image uploaded successfully!");

      setUploadedUrl(`${API}${data.image_url}`);
      setFile(null);

      const input = document.getElementById(
        "damage-image"
      ) as HTMLInputElement | null;

      if (input) input.value = "";
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Image upload failed."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="image-upload-section">
      <div className="image-upload-heading">
        <div className="upload-heading-icon">
          <ImagePlus size={21} />
        </div>

        <div>
          <h2>Road Damage Image Upload</h2>
          <p>
            Attach a photograph to an existing road damage report.
          </p>
        </div>
      </div>

      {error && (
        <div className="upload-error">
          <AlertCircle size={17} />
          {error}
        </div>
      )}

      {success && (
        <div className="upload-success">
          <CheckCircle size={17} />
          {success}
        </div>
      )}

      <form className="upload-form" onSubmit={uploadImage}>
        <div className="form-group">
          <label htmlFor="report-select">
            Select Damage Report *
          </label>

          <select
            id="report-select"
            value={selectedReport}
            onChange={(event) => setSelectedReport(event.target.value)}
            disabled={fetching || reports.length === 0}
            required
          >
            <option value="">
              {fetching
                ? "Loading reports..."
                : reports.length === 0
                  ? "No reports available"
                  : "Choose a report"}
            </option>

            {reports.map((report) => (
              <option key={report.id} value={report.id}>
                {report.damage_type} - {report.id.slice(0, 8)}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="damage-image">
            Choose Road Photograph *
          </label>

          <input
            id="damage-image"
            type="file"
            accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
            onChange={handleFileChange}
            required={!file}
          />

          <small>
            Supported formats: JPG, JPEG, PNG and WEBP. Maximum size: 5 MB.
          </small>
        </div>

        {preview && (
          <div className="image-preview">
            <p>Image Preview</p>
            <img src={preview} alt="Selected road damage preview" />
            <span>{file?.name}</span>
          </div>
        )}

        <button
          className="image-upload-button"
          type="submit"
          disabled={loading || fetching || reports.length === 0}
        >
          <Upload size={17} />
          {loading ? "Uploading..." : "Upload Image"}
        </button>
      </form>

      {uploadedUrl && (
        <div className="uploaded-result">
          <strong>Uploaded image</strong>
          <a href={uploadedUrl} target="_blank" rel="noreferrer">
            Open uploaded image
          </a>
        </div>
      )}
    </section>
  );
}

export default ImageUpload;
