const API_BASE = import.meta.env.VITE_API_URL ?? "";

export function getToken(): string | null {
  return sessionStorage.getItem("infrasentry_token");
}

export function saveToken(token: string): void {
  sessionStorage.setItem("infrasentry_token", token);
}

export function clearToken(): void {
  sessionStorage.removeItem("infrasentry_token");
}

export async function login(username: string, password: string) {
  const body = new URLSearchParams();
  body.append("username", username);
  body.append("password", password);

  const response = await fetch(`${API_BASE}/api/v1/auth/token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body,
  });

  if (!response.ok) {
    throw new Error("Invalid username or password.");
  }

  const data = await response.json();
  saveToken(data.access_token);
  return data;
}

export async function authenticatedFetch(
  input: RequestInfo | URL,
  init: RequestInit = {},
): Promise<Response> {
  const token = getToken();
  const headers = new Headers(init.headers);

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(input, {
    ...init,
    headers,
  });

  if (response.status === 401) {
    clearToken();
    window.dispatchEvent(new Event("infrasentry:session-expired"));
  }

  return response;
}

export async function verifySession(): Promise<boolean> {
  const token = getToken();
  if (!token) return false;

  try {
    const response = await authenticatedFetch(
      `${API_BASE}/api/v1/auth/me`,
    );

    return response.ok;
  } catch {
    return false;
  }
}

export { API_BASE };
