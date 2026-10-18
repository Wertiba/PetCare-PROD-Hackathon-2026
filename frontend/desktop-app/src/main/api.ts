import type { ErrorData } from '../shared/error-data';
import type { Uid } from '../shared/global.types';
import type { LoginDto } from '../shared/login.dto';
import type {
  FetchNotificationsReqDto,
  FetchNotificationsResDto,
} from '../shared/notification.dto';
import type { Notification } from '../shared/notification.types';
import type {
  FetchPetsReqDto,
  FetchPetsResDto,
} from '../shared/pet.dto';
import type { Animal, Pet } from '../shared/pet.types';
import type { UserAndTokenDto } from '../shared/user.dto';
import { API_URL, REQUEST_TIMEOUT_MS } from './config';

const REFRESH_COOKIE = 'refreshToken';

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

export interface Tokens {
  accessToken: string;
  expiresIn: number;
  refreshToken: string;
}

async function send(
  path: string,
  init: RequestInit = {},
): Promise<Response> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init.headers,
    },
    signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
  });
  if (!response.ok) {
    const data = (await response
      .json()
      .catch(() => null)) as Partial<ErrorData> | null;
    throw new ApiError(
      response.status,
      data?.message ?? response.statusText,
    );
  }
  return response;
}

/**
 * The backend hands the refresh token out only as an httpOnly cookie; there
 * is no cookie jar in the main process, so it is read and sent back by hand.
 */
function readRefreshCookie(response: Response): string {
  for (const cookie of response.headers.getSetCookie()) {
    const [pair = ''] = cookie.split(';');
    const separator = pair.indexOf('=');
    if (
      pair.slice(0, separator).trim() === REFRESH_COOKIE
    ) {
      return pair.slice(separator + 1).trim();
    }
  }
  throw new ApiError(
    response.status,
    'В ответе нет refresh-cookie',
  );
}

const refreshCookie = (refreshToken: string) => ({
  Cookie: `${REFRESH_COOKIE}=${refreshToken}`,
});

const bearer = (accessToken: string) => ({
  Authorization: `Bearer ${accessToken}`,
});

export async function login(
  dto: LoginDto,
): Promise<Tokens> {
  const response = await send('/auth/login', {
    method: 'POST',
    body: JSON.stringify(dto),
  });
  const data = (await response.json()) as UserAndTokenDto;
  return {
    accessToken: data.accessToken,
    expiresIn: data.expiresIn,
    refreshToken: readRefreshCookie(response),
  };
}

export async function refresh(
  refreshToken: string,
): Promise<Tokens> {
  const response = await send('/auth/refresh', {
    method: 'POST',
    headers: refreshCookie(refreshToken),
  });
  const data = (await response.json()) as Pick<
    UserAndTokenDto,
    'accessToken' | 'expiresIn'
  >;
  return {
    ...data,
    refreshToken: readRefreshCookie(response),
  };
}

export async function logout(
  refreshToken: string,
): Promise<void> {
  await send('/auth/logout', {
    method: 'POST',
    headers: refreshCookie(refreshToken),
  });
}

export async function fetchNotifications(
  accessToken: string,
  query: FetchNotificationsReqDto,
): Promise<FetchNotificationsResDto> {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined) params.set(key, String(value));
  }
  const response = await send(
    `/notifications?${params.toString()}`,
    { headers: bearer(accessToken) },
  );
  return (await response.json()) as FetchNotificationsResDto;
}

export async function fetchNotificationById(
  accessToken: string,
  id: Uid,
): Promise<Notification> {
  const response = await send(`/notifications/${id}`, {
    headers: bearer(accessToken),
  });
  return (await response.json()) as Notification;
}

export async function fetchPetById(
  accessToken: string,
  id: Uid,
): Promise<Pet> {
  const response = await send(`/pets/${id}`, {
    headers: bearer(accessToken),
  });
  return (await response.json()) as Pet;
}

export async function fetchAnimalById(
  accessToken: string,
  id: Uid,
): Promise<Animal> {
  const response = await send(`/animals/${id}`, {
    headers: bearer(accessToken),
  });
  return (await response.json()) as Animal;
}

export async function fetchPets(
  accessToken: string,
  { page, size }: FetchPetsReqDto,
): Promise<FetchPetsResDto> {
  const params = new URLSearchParams({
    page: String(page),
    size: String(size),
  });
  const response = await send(
    `/pets?${params.toString()}`,
    {
      headers: bearer(accessToken),
    },
  );
  return (await response.json()) as FetchPetsResDto;
}
