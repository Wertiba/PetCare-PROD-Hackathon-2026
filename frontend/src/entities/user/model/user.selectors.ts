import { useUserStore } from './user.store';

export const selectUser = (
  state: ReturnType<typeof useUserStore.getState>,
) => state.user;

export const selectIsSessionRestored = (
  state: ReturnType<typeof useUserStore.getState>,
) => state.isSessionRestored;
