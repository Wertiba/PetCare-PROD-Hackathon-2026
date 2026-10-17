import api from '@src/shared/api/client';
import { Uid } from '@src/shared/api/global.types';

import type { Category } from '../model';
import {
  CreateCategoryReqDto,
  FetchCategoriesReqDto,
  FetchCategoriesResDto,
  UpdateCategoryReqDto,
} from './category.dto';

export const fetchCategories = async (
  query: FetchCategoriesReqDto,
) =>
  (
    await api.get<FetchCategoriesResDto>('/categories', {
      params: query,
    })
  ).data;

export const fetchCategoryById = async (id: Uid) =>
  (await api.get<Category>(`/categories/${id}`)).data;

export const createCategory = async (
  category: CreateCategoryReqDto,
) =>
  (await api.post<Category>('/categories', category)).data;

export const updateCategory = async (
  id: Uid,
  category: UpdateCategoryReqDto,
) =>
  (await api.patch<Category>(`/categories/${id}`, category))
    .data;

export const deleteCategory = async (id: Uid) =>
  (await api.delete<void>(`/categories/${id}`)).data;
