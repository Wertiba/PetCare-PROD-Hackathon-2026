import type { UserAndTokenDto } from '@src/entities/user';
import api from '@src/shared/api/client';

import type { LoginDto } from './login.dto';

export const login = async (data: LoginDto) =>
  (await api.post<UserAndTokenDto>('/auth/login', data))
    .data;
