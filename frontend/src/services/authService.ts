const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const TOKEN_KEY = "infrasentry_access_token";

export function getToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function saveToken(token: string): void {
  sessionStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  sessionStorage.removeItem(TOKEN_KEY);
}

export async function login(username: string, password: string) {
  const body = new URLSearchParams();
  body.set("username", username);
  body.set("password", password);

  const response = await fetch(`${API_BASE}/api/v1/auth/token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Login failed.");
  }

  saveToken(data.access_token);
  return data;
}

export async function authenticatedFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getToken();

  const headers = new Headers(options.headers);

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  return fetch(url, {
    ...options,
    headers,
  });
}

export async function verifySession(): Promise<boolean> {
  const token = getToken();

  if (!token) return false;

  try {
    const response = await authenticatedFetch(
      `${API_BASE}/api/v1/auth/me`
    );

    if (!response.ok) {
      clearToken();
      return false;
    }

    return true;
  } catch {
    return false;
  }
}
