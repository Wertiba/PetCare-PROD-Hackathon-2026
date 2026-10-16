import api from '@src/shared/api/client';

/**
 * Revokes the current refresh token and clears the backend cookie.
 * The access token is not sent: the endpoint is cookie-authenticated.
 */
export const logout = async () =>
  (await api.post<void>('/auth/logout')).data;
