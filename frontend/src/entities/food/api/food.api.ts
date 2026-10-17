import api from '@src/shared/api/client';

import type {
  CreateFoodReqDto,
  FetchFoodsReqDto,
  FetchFoodsResDto,
  Food,
} from './food.dto';

export const fetchFoods = async (query: FetchFoodsReqDto) =>
  (
    await api.get<FetchFoodsResDto>('/foods', {
      params: query,
    })
  ).data;

export const createFood = async (food: CreateFoodReqDto) =>
  (await api.post<Food>('/foods', food)).data;
