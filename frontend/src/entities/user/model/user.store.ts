import { create } from 'zustand';

import type { User } from './user.types';

interface UserStore {
  isSessionRestored: boolean;
  user: User | null;
  setUser: (user: User) => void;
  clearUser: () => void;
  setSessionRestored: () => void;
}

export const useUserStore = create<UserStore>()((set) => ({
  isSessionRestored: false,
  user: null,
  setUser: (user) => set({ user }),
  clearUser: () => set({ user: null }),
  setSessionRestored: () =>
    set({ isSessionRestored: true }),
}));
