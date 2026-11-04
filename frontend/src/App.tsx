
import { Activity, MapPin, ShieldCheck } from "lucide-react";
import "./App.css";

function App() {
  return (
    <div className="app">
      <header className="navbar">
        <h2>InfraSentry AI</h2>
        <span>Infrastructure Intelligence</span>
      </header>

      <main className="hero">
        <div className="icon">
          <ShieldCheck size={42} />
        </div>

        <h1>Smarter Infrastructure.</h1>

        <p>
          Detect. Understand. Predict. Protect.
        </p>

        <div className="features">
          <div>
            <Activity size={24} />
            <h3>AI Detection</h3>
            <p>Identify infrastructure damage.</p>
          </div>

          <div>
            <MapPin size={24} />
            <h3>Smart Mapping</h3>
            <p>Locate problems geographically.</p>
          </div>

          <div>
            <ShieldCheck size={24} />
            <h3>Risk Intelligence</h3>
            <p>Prioritise maintenance decisions.</p>
          </div>
        </div>

        <p className="status">
          System Initialised · Development Mode
        </p>
      </main>
    </div>
  );
}

export default App;
