import type { UserAndTokenDto } from '@src/entities/user';
import api from '@src/shared/api/client';

import type { RegisterDto } from './register.dto';

export const register = async (data: RegisterDto) =>
  (await api.post<UserAndTokenDto>('/auth/register', data))
    .data;
