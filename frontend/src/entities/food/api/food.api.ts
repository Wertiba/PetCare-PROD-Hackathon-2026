import api from '@src/shared/api/client';

import type {
  FetchFoodsReqDto,
  FetchFoodsResDto,
} from './food.dto';

export const fetchFoods = async (query: FetchFoodsReqDto) =>
  (
    await api.get<FetchFoodsResDto>('/foods', {
      params: query,
    })
  ).data;
