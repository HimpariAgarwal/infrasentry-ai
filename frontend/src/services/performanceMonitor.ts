export interface PerformanceMetric {
  type: "page-load" | "api-request" | "api-error";
  name: string;
  durationMs: number;
  timestamp: string;
  status?: number;
  success: boolean;
  details?: string;
}

declare global {
  interface Window {
    __infrasentryPerformance?: PerformanceMetric[];
  }
}

const MAX_METRICS = 200;

function saveMetric(metric: PerformanceMetric) {
  window.__infrasentryPerformance ??= [];

  window.__infrasentryPerformance.push(metric);

  if (window.__infrasentryPerformance.length > MAX_METRICS) {
    window.__infrasentryPerformance.shift();
  }

  console.info(
    "[InfraSentry Performance]",
    JSON.stringify(metric)
  );

  window.dispatchEvent(
    new CustomEvent("infrasentry:performance", {
      detail: metric,
    })
  );
}

// Capture initial page-load timings.
function monitorPageLoad() {
  const navigation = performance.getEntriesByType(
    "navigation"
  )[0] as PerformanceNavigationTiming | undefined;

  if (!navigation) return;

  const metric: PerformanceMetric = {
    type: "page-load",
    name: window.location.pathname,
    durationMs: Number(navigation.loadEventEnd.toFixed(2)),
    timestamp: new Date().toISOString(),
    success: true,
    details: JSON.stringify({
      domContentLoadedMs: Number(
        navigation.domContentLoadedEventEnd.toFixed(2)
      ),
      domInteractiveMs: Number(
        navigation.domInteractive.toFixed(2)
      ),
      responseStartMs: Number(
        navigation.responseStart.toFixed(2)
      ),
    }),
  };

  saveMetric(metric);
}

window.addEventListener("load", monitorPageLoad, {
  once: true,
});

// Monitor API requests without changing existing API services.
const originalFetch = window.fetch.bind(window);

window.fetch = async (
  ...args: Parameters<typeof fetch>
): Promise<Response> => {
  const input = args[0];

  const url =
    input instanceof Request
      ? input.url
      : String(input);

  const isApiRequest =
    /\/api(?:\/|$)/i.test(url) ||
    /localhost:8000/i.test(url);

  if (!isApiRequest) {
    return originalFetch(...args);
  }

  const startedAt = performance.now();
  const method =
    args[1]?.method ||
    (input instanceof Request ? input.method : "GET");

  try {
    const response = await originalFetch(...args);
    const durationMs = Number(
      (performance.now() - startedAt).toFixed(2)
    );

    saveMetric({
      type: response.ok ? "api-request" : "api-error",
      name: `${method.toUpperCase()} ${url}`,
      durationMs,
      timestamp: new Date().toISOString(),
      status: response.status,
      success: response.ok,
      details: response.ok
        ? "API request completed"
        : `HTTP ${response.status} ${response.statusText}`,
    });

    return response;
  } catch (error) {
    const durationMs = Number(
      (performance.now() - startedAt).toFixed(2)
    );

    saveMetric({
      type: "api-error",
      name: `${method.toUpperCase()} ${url}`,
      durationMs,
      timestamp: new Date().toISOString(),
      success: false,
      details:
        error instanceof Error
          ? error.message
          : String(error),
    });

    throw error;
  }
};

console.info(
  "[InfraSentry] Performance monitoring initialized."
);
