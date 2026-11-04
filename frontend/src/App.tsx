
import {
  useEffect,
  useState,
  type ChangeEvent,
  type FormEvent,
} from "react";

import {
  Activity,
  MapPin,
  ShieldCheck,
  Send,
} from "lucide-react";

import "./App.css";

interface Report {
  id: string;
  damage_type: string;
  description: string;
  latitude: number;
  longitude: number;
  severity: number;
  status: string;
  created_at: string;
}

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const [form, setForm] = useState({
    damage_type: "Pothole",
    description: "",
    latitude: "28.6692",
    longitude: "77.4538",
    severity: "3",
  });

  // Fetch all reports from backend
  async function loadReports() {
    try {
      const response = await fetch(`${API_URL}/reports`);

      if (!response.ok) {
        throw new Error("Could not load reports");
      }

      const data = await response.json();

      setReports(data.reports);
    } catch {
      setMessage("Cannot connect to backend. Is FastAPI running?");
    }
  }

  // Load reports when website opens
  useEffect(() => {
    loadReports();
  }, []);

  // Handle form input changes
  function handleChange(
    event: ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) {
    setForm({
      ...form,
      [event.target.name]: event.target.value,
    });
  }

  // Submit a new damage report
  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(`${API_URL}/reports`, {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          damage_type: form.damage_type,
          description: form.description,
          latitude: Number(form.latitude),
          longitude: Number(form.longitude),
          severity: Number(form.severity),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail?.[0]?.msg ||
          data.detail ||
          "Report submission failed"
        );
      }

      setMessage("Report submitted successfully!");

      setForm({
        damage_type: "Pothole",
        description: "",
        latitude: "28.6692",
        longitude: "77.4538",
        severity: "3",
      });

      await loadReports();

    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Something went wrong"
      );

    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">

      {/* Navigation */}
      <header className="navbar">
        <div className="brand">
          <ShieldCheck size={28} />
          <h2>InfraSentry AI</h2>
        </div>

        <span>Infrastructure Intelligence</span>
      </header>


      <main className="container">

        {/* Hero Section */}
        <section className="hero">
          <h1>Smarter Infrastructure.</h1>

          <p>
            Report road damage. Help make our roads safer.
          </p>
        </section>


        {/* Dashboard Statistics */}
        <section className="dashboard">

          <div className="stat-card">
            <Activity size={26} />

            <h3>{reports.length}</h3>

            <p>Total Reports</p>
          </div>

          <div className="stat-card">
            <MapPin size={26} />

            <h3>Live</h3>

            <p>Report Tracking</p>
          </div>

        </section>


        {/* Damage Report Form */}
        <section className="report-section">

          <h2>Submit a Damage Report</h2>

          <p className="section-description">
            Tell us about the infrastructure problem.
          </p>


          <form onSubmit={handleSubmit}>

            <label>Damage Type</label>

            <select
              name="damage_type"
              value={form.damage_type}
              onChange={handleChange}
            >
              <option value="Pothole">Pothole</option>
              <option value="Crack">Road Crack</option>
              <option value="Surface Damage">
                Surface Damage
              </option>
            </select>


            <label>Description</label>

            <textarea
              name="description"
              value={form.description}
              onChange={handleChange}
              placeholder="Describe the damage..."
              minLength={10}
              maxLength={500}
              required
            />


            <div className="form-row">

              <div>
                <label>Latitude</label>

                <input
                  name="latitude"
                  type="number"
                  step="any"
                  min="-90"
                  max="90"
                  value={form.latitude}
                  onChange={handleChange}
                  required
                />
              </div>


              <div>
                <label>Longitude</label>

                <input
                  name="longitude"
                  type="number"
                  step="any"
                  min="-180"
                  max="180"
                  value={form.longitude}
                  onChange={handleChange}
                  required
                />
              </div>

            </div>


            <label>Severity</label>

            <select
              name="severity"
              value={form.severity}
              onChange={handleChange}
            >
              <option value="1">1 - Very Low</option>
              <option value="2">2 - Low</option>
              <option value="3">3 - Moderate</option>
              <option value="4">4 - High</option>
              <option value="5">5 - Critical</option>
            </select>


            <button type="submit" disabled={loading}>
              <Send size={18} />

              {loading
                ? "Submitting..."
                : "Submit Report"}
            </button>

          </form>


          {message && (
            <p className="message" role="status">
              {message}
            </p>
          )}

        </section>


        {/* Recent Reports */}
        <section className="reports-section">

          <div className="reports-heading">

            <h2>Recent Reports</h2>

            <button
              type="button"
              className="refresh-button"
              onClick={loadReports}
            >
              Refresh
            </button>

          </div>


          {reports.length === 0 ? (

            <p className="empty-state">
              No reports submitted yet.
            </p>

          ) : (

            reports.map((report) => (

              <article
                className="report-card"
                key={report.id}
              >

                <div>
                  <h3>{report.damage_type}</h3>

                  <p>{report.description}</p>

                  <small>
                    Location: {report.latitude},{" "}
                    {report.longitude}
                  </small>
                </div>


                <div className="report-meta">

                  <span>
                    Severity: {report.severity}/5
                  </span>

                  <span>{report.status}</span>

                </div>

              </article>

            ))

          )}

        </section>

      </main>


      {/* Footer */}
      <footer>
        InfraSentry AI · Development Version 0.3.0
      </footer>

    </div>
  );
}

export default App;
