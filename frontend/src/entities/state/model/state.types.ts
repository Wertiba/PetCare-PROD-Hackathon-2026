import {
  Timestamp,
  Uid,
} from '@src/shared/api/global.types';

export interface State {
  id: Uid;
  petId: Uid;
  categoryId: Uid;
  value: number;
  time: Timestamp;
}
