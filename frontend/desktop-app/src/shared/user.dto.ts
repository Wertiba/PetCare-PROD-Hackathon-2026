// Фрагмент frontend/src/entities/user/api/user.dto.ts
import { Uid, UserRole } from './global.types';

export interface UserDto {
  id: Uid;
  /** Display name returned by the users API. */
  fullName: string;
  /**
   * Legacy display-name field retained while existing dashboard views migrate
   * to `fullName`. The API does not return this field.
   */
  name?: string;
  login: string;
  role: UserRole;
}

export interface UserAndTokenDto {
  accessToken: string;
  expiresIn: number;
  user: UserDto;
}
