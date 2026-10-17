import api from '@src/shared/api/client';
import { Uid } from '@src/shared/api/global.types';

import type { Event } from '../model';
import {
  CreateEventReqDto,
  FetchEventsReqDto,
  FetchEventsResDto,
  FetchUpcomingEventsReqDto,
  UpdateEventReqDto,
} from './event.dto';

export const fetchEvents = async (
  query: FetchEventsReqDto,
) =>
  (
    await api.get<FetchEventsResDto>('/events', {
      params: query,
    })
  ).data;

export const fetchUpcomingEvents = async (
  query: FetchUpcomingEventsReqDto,
) =>
  (
    await api.get<FetchEventsResDto>('/events/upcoming', {
      params: query,
    })
  ).data;

export const fetchEventById = async (id: Uid) =>
  (await api.get<Event>(`/events/${id}`)).data;

export const createEvent = async (
  event: CreateEventReqDto,
) => (await api.post<Event>('/events', event)).data;

export const updateEvent = async (
  id: Uid,
  event: UpdateEventReqDto,
) => (await api.patch<Event>(`/events/${id}`, event)).data;

export const deleteEvent = async (id: Uid) =>
  (await api.delete<void>(`/events/${id}`)).data;
