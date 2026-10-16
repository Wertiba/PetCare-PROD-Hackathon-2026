/**
 * Base URL for API calls. Defaults to '' (same-origin): the Next.js server
 * proxies /api/v1/* to the backend (see `rewrites` in next.config.ts), so no
 * CORS is involved. Set NEXT_PUBLIC_API_BASE_URL to call a backend on another
 * origin directly (that backend must then allow this origin's CORS).
 */
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
