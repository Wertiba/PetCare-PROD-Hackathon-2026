import type { UserDto } from '@src/entities/user';

export interface LoginDto {
  login: string;
  password: string;
}

export interface LoginRes {
  accessToken: string;
  expiresIn: number;
  user: UserDto;
}
