import {
  Uid,
  UserRole,
} from '@src/shared/api/global.types';

export interface UserDto {
  id: Uid;
  name: string;
  login: string;
  password?: string;
  role: UserRole;
}

export interface UserAndTokenDto {
  accessToken: string;
  expiresIn: number;
  user: UserDto;
}
