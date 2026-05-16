// frontend/src/lib/api.ts

export const API_BASE_URL = "http://localhost:8000";

export async function apiFetch(url: string, options: RequestInit = {}, token?: string) {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers,
  });
  return response;
}
