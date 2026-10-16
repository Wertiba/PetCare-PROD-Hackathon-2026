import { UserDto } from '@src/entities';

/** Mirrors the backend's `UserLoginBody`. */
export interface LoginDto {
  email: string;
  password: string;
}

export interface LoginRes {
  accessToken: string;
  expiresIn: number;
  user: UserDto;
}
