import api from '@src/shared/api/client';

import type { Post } from '../model';

export const fetchPosts = async () =>
  (await api.get<Post[]>('/posts')).data;

export const fetchPostById = async (postId: number) =>
  await api.get<Post>(`/posts/${postId}`);
