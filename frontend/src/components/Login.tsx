import { useState } from "react";
import { LockKeyhole, ShieldCheck, User } from "lucide-react";
import { login } from "../services/authService";
import "./Login.css";

interface LoginProps {
  onLogin: () => void;
}

export default function Login({ onLogin }: LoginProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(username.trim(), password);
      onLogin();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-card">
        <div className="login-brand-icon">
          <ShieldCheck size={34} />
        </div>

        <h1>InfraSentry AI</h1>
        <p className="login-subtitle">
          Secure Infrastructure Intelligence Platform
        </p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="login-username">Username</label>
          <div className="login-input-wrap">
            <User size={18} />
            <input
              id="login-username"
              type="text"
              placeholder="Enter administrator username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              autoComplete="username"
              required
            />
          </div>

          <label htmlFor="login-password">Password</label>
          <div className="login-input-wrap">
            <LockKeyhole size={18} />
            <input
              id="login-password"
              type="password"
              placeholder="Enter password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
              required
            />
          </div>

          {error && <div className="login-error">{error}</div>}

          <button type="submit" disabled={loading}>
            {loading ? "Authenticating..." : "Secure Login"}
          </button>
        </form>

        <p className="login-security-note">
          <LockKeyhole size={13} />
          JWT protected administrator access
        </p>
      </section>
    </main>
  );
}
