import api from '@src/shared/api/client';
import { Uid } from '@src/shared/api/global.types';

import type { State } from '../model';
import {
  CreateStateReqDto,
  FetchStatesReqDto,
  FetchStatesResDto,
  UpdateStateReqDto,
} from './state.dto';

export const fetchStates = async (
  query: FetchStatesReqDto,
) =>
  (
    await api.get<FetchStatesResDto>('/states', {
      params: query,
    })
  ).data;

export const fetchStateById = async (id: Uid) =>
  (await api.get<State>(`/states/${id}`)).data;

export const createState = async (
  state: CreateStateReqDto,
) => (await api.post<State>('/states', state)).data;

export const updateState = async (
  id: Uid,
  state: UpdateStateReqDto,
) => (await api.patch<State>(`/states/${id}`, state)).data;

export const deleteState = async (id: Uid) =>
  (await api.delete<void>(`/states/${id}`)).data;
