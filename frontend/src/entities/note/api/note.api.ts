import api from '@src/shared/api/client';
import { Timestamp, Uid } from '@src/shared/api/global.types';

export interface Note {
  content: string;
  createdAt: Timestamp;
  id: Uid;
  petId: Uid;
  updatedAt: Timestamp;
}

export interface FetchNotesResponse {
  items: Note[];
  page: number;
  size: number;
  total: number;
}

export const fetchNotes = async (petId: Uid) =>
  (
    await api.get<FetchNotesResponse>('/notes', {
      params: { page: 0, size: 20, petId },
    })
  ).data;

export const createNote = async ({
  content,
  petId,
}: Pick<Note, 'content' | 'petId'>) =>
  (await api.post<Note>('/notes', { content, petId })).data;
