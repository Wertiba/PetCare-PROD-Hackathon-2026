import {
  Uid,
  UserRole,
} from '@src/shared/api/global.types';

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

export interface UpdateUserDto {
  fullName: string;
}

export interface UserAndTokenDto {
  accessToken: string;
  expiresIn: number;
  user: UserDto;
}
