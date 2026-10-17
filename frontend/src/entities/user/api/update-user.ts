import api from '@src/shared/api/client';

import type { UpdateUserDto, UserDto } from './user.dto';

export const updateUser = async (data: UpdateUserDto) =>
  (await api.patch<UserDto>('/users/me', data)).data;
