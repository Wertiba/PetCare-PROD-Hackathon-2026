/** Mirrors the backend's `UserRole` enum. */
export type UserRole = 'USER' | 'ADMIN';

/** Mirrors the backend's `UserReadResponse`. */
export interface UserDto {
  id: string;
  email: string;
  fullName: string;
  role: UserRole;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
}

/** Mirrors the backend's `UserAndAccessTokenResponse` returned by register and login. */
export interface UserAndTokenDto {
  accessToken: string;
  expiresIn: number;
  user: UserDto;
}
