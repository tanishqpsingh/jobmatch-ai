/**
 * Centralised API base URL.
 *
 * Set NEXT_PUBLIC_API_URL in your environment:
 *   Local dev:   NEXT_PUBLIC_API_URL=http://localhost:8000
 *   Production:  NEXT_PUBLIC_API_URL=https://<your-backend>.railway.app
 *
 * NEXT_PUBLIC_ prefix is required for Next.js to expose the variable
 * to the browser bundle. Do NOT put secrets in NEXT_PUBLIC_ variables.
 */
export const API_BASE_URL =
  (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");

/**
 * Build a full API URL from a path.
 * @example apiUrl("/api/v1/health") => "https://api.railway.app/api/v1/health"
 */
export function apiUrl(path: string): string {
  const normalised = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${normalised}`;
}

/**
 * Centralised fetch wrapper that guarantees credentials (cookies)
 * are always included on cross-origin requests to the backend.
 */
export async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  const url = apiUrl(path);
  return fetch(url, {
    ...init,
    credentials: "include",
  });
}
