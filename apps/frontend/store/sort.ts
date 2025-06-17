import { create } from 'zustand';

/** Chaves permitidas na UI de ordenação */
export type SortKey =
  | 'none'
  | 'dic-asc'
  | 'dic-desc'
  | 'fic-asc'
  | 'fic-desc';

type SortState = {
  order: SortKey;
  setOrder: (o: SortKey) => void;
};

export const useSort = create<SortState>((set) => ({
  order: 'none',
  setOrder: (o) => set({ order: o }),
}));
