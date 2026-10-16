import api from '@src/shared/api/client';

import type { LoginDto, LoginRes } from './login.dto';

export const login = async (data: LoginDto) => {
  return (await api.post<LoginRes>('/auth/login', data))
    .data;
};
