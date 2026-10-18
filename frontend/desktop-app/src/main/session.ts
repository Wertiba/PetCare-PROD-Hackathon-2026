import {
  existsSync,
  readFileSync,
  renameSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import { join } from 'node:path';

import { app, safeStorage } from 'electron';

import type { LoginDto } from '../shared/login.dto';
import {
  ApiError,
  type Tokens,
  login,
  logout,
  refresh,
} from './api';

const EXPIRY_MARGIN_MS = 30_000;

let refreshToken: string | null = null;
let accessToken: string | null = null;
let accessExpiresAt = 0;
let refreshing: Promise<string> | null = null;
let onExpired: () => void = () => undefined;

const sessionFile = () =>
  join(app.getPath('userData'), 'session.bin');

/** Called when the backend rejects the refresh token. */
export function setOnSessionExpired(listener: () => void) {
  onExpired = listener;
}

export const isSignedIn = () => refreshToken !== null;

function persist(token: string | null) {
  const file = sessionFile();
  if (token === null) {
    rmSync(file, { force: true });
    return;
  }
  // Without OS-level encryption the token lives in memory only:
  // it never reaches the disk in plain text.
  if (!safeStorage.isEncryptionAvailable()) return;
  const tmp = `${file}.tmp`;
  writeFileSync(tmp, safeStorage.encryptString(token), {
    mode: 0o600,
  });
  renameSync(tmp, file);
}

function apply(tokens: Tokens) {
  refreshToken = tokens.refreshToken;
  accessToken = tokens.accessToken;
  accessExpiresAt = Date.now() + tokens.expiresIn * 1000;
  persist(tokens.refreshToken);
}

function clear() {
  refreshToken = null;
  accessToken = null;
  accessExpiresAt = 0;
  persist(null);
}

/** Restores the refresh token saved by a previous run. */
export function restoreSession(): boolean {
  const file = sessionFile();
  if (
    !existsSync(file) ||
    !safeStorage.isEncryptionAvailable()
  ) {
    return false;
  }
  try {
    refreshToken = safeStorage.decryptString(
      readFileSync(file),
    );
    return true;
  } catch (error) {
    // The key changed (e.g. the app was re-signed): sign in again.
    console.warn('[session] cannot decrypt session', error);
    clear();
    return false;
  }
}

export async function signIn(dto: LoginDto) {
  apply(await login(dto));
}

export async function signOut() {
  const token = refreshToken;
  clear();
  if (!token) return;
  try {
    await logout(token);
  } catch (error) {
    console.warn('[session] logout request failed', error);
  }
}

function refreshAccessToken(): Promise<string> {
  // One request at a time: the backend rotates the refresh token,
  // so a second parallel refresh would present a revoked one.
  refreshing ??= (async () => {
    const token = refreshToken;
    if (!token) throw new ApiError(401, 'Нет сессии');
    try {
      const tokens = await refresh(token);
      apply(tokens);
      return tokens.accessToken;
    } catch (error) {
      const rejected =
        error instanceof ApiError &&
        error.status >= 400 &&
        error.status < 500;
      if (rejected && refreshToken === token) {
        clear();
        onExpired();
      }
      throw error;
    } finally {
      refreshing = null;
    }
  })();
  return refreshing;
}

/** Runs a request with a fresh access token; retries once after a 401. */
export async function authorized<T>(
  request: (accessToken: string) => Promise<T>,
): Promise<T> {
  const token =
    accessToken &&
    Date.now() < accessExpiresAt - EXPIRY_MARGIN_MS
      ? accessToken
      : await refreshAccessToken();
  try {
    return await request(token);
  } catch (error) {
    if (!(
      error instanceof ApiError && error.status === 401
    )) {
      throw error;
    }
    return request(await refreshAccessToken());
  }
}
