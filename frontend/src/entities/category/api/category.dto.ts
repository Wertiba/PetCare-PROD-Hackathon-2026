import {
  Category,
  CategoryKind,
  CategoryType,
  CategoryUnit,
} from '../model';

export interface FetchCategoriesReqDto {
  page: number;
  size: number;
}

export interface FetchCategoriesResDto {
  items: Category[];
  page: number;
  size: number;
  total: number;
}

export interface CreateCategoryReqDto {
  name: string;
  kind: CategoryKind;
  type: CategoryType;
  unit: CategoryUnit;
}

export interface UpdateCategoryReqDto {
  name?: string;
  kind?: CategoryKind;
  type?: CategoryType;
  unit?: CategoryUnit;
}
