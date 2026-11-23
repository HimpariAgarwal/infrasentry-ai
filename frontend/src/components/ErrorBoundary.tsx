import { Component } from "react";
import type { ErrorInfo, ReactNode } from "react";

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  message: string;
}

class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  state: ErrorBoundaryState = {
    hasError: false,
    message: "",
  };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      message: error.message || "An unexpected application error occurred.",
    };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("InfraSentry AI application error:", error);
    console.error("Component stack:", info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            minHeight: "100vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "24px",
            background: "#0f172a",
            color: "#f8fafc",
            fontFamily: "Arial, sans-serif",
          }}
        >
          <div
            style={{
              maxWidth: "520px",
              width: "100%",
              padding: "36px",
              border: "1px solid #334155",
              borderRadius: "16px",
              background: "#1e293b",
              textAlign: "center",
            }}
          >
            <div style={{ fontSize: "44px", marginBottom: "16px" }}>
              ⚠️
            </div>

            <h1 style={{ fontSize: "24px", marginBottom: "12px" }}>
              Something went wrong
            </h1>

            <p style={{ color: "#cbd5e1", lineHeight: 1.6 }}>
              InfraSentry AI encountered an unexpected error.
              You can reload the application to try again.
            </p>

            <p
              style={{
                marginTop: "18px",
                padding: "12px",
                borderRadius: "8px",
                background: "#0f172a",
                color: "#fca5a5",
                fontSize: "12px",
                overflowWrap: "anywhere",
                textAlign: "left",
              }}
            >
              {this.state.message}
            </p>

            <button
              onClick={() => window.location.reload()}
              style={{
                marginTop: "22px",
                padding: "12px 24px",
                border: "none",
                borderRadius: "8px",
                background: "#2563eb",
                color: "white",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              Reload App
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
