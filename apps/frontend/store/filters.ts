import { create } from 'zustand';

type FiltersState = {
  
  estado: string;
  setEstado: (uf: string) => void;
};

export const useFilters = create<FiltersState>((set) => ({
  estado: '',
  setEstado: (uf) => set({ estado: uf }),
}));
