import { API_BASE, authenticatedFetch } from "./authService";

export async function apiRequest(
  endpoint: string,
  options: RequestInit = {},
): Promise<Response> {
  const url = endpoint.startsWith("http")
    ? endpoint
    : `${API_BASE}${endpoint}`;

  return authenticatedFetch(url, options);
}

export async function apiJson<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await apiRequest(endpoint, options);

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `API request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}
