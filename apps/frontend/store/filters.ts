import { create } from 'zustand';

type FiltersState = {
  
  estado: string;
  setEstado: (uf: string) => void;
  distribuidora: string;
  setDistribuidora: (codigo: string) => void;
  segmento: string;
  setSegmento: (s: string) => void;
  clearFilters: () => void;
};

export const useFilters = create<FiltersState>((set) => ({
  estado: '',
  distribuidora: '',
  segmento: '',
  setEstado: (uf) => set({ estado: uf }),
  setDistribuidora: (c) => set({ distribuidora: c }),
  setSegmento: (s) => set({ segmento: s }),
  clearFilters: () => set({ estado: '', distribuidora: '', segmento: '' }),
}));