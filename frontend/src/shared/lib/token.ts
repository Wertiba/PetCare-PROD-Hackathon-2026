const LEGACY_ACCESS_TOKEN_KEY = 'accessToken';

/**
 * The access token now lives only in the httpOnly `accessToken` cookie set by
 * the backend. Older sessions kept a copy in localStorage: remove it.
 */
export function removeLegacyAccessToken(): void {
  try {
    window.localStorage.removeItem(LEGACY_ACCESS_TOKEN_KEY);
  } catch {
    // Storage may be unavailable (private mode, blocked site data).
  }
}
