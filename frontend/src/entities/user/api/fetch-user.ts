import api from '@src/shared/api/client';

import { UserDto } from './user.dto';

export const fetchUser = async () =>
  (await api.get<UserDto>('/users/me')).data;
