import { Uid } from '@src/shared/api/global.types';

export type CategoryType = 'check' | 'number' | 'scale';
export type CategoryKind =
  'sum' | 'avg' | 'last' | 'count' | 'min' | 'max';

export type CategoryUnit =
  | 'none'
  | 'g'
  | 'ml'
  | 'min'
  | 'm'
  | 'times'
  | 'rub'
  | 'points';

export interface Category {
  id: Uid;
  name: string;
  kind: CategoryKind;
  type: CategoryType;
  unit: CategoryUnit;
  createdBy: Uid | null;
  isSystem: boolean;
}
