import { create } from 'zustand';

type FiltersState = {
  estado: string;
  distribuidora: string;
  segmento: string;
  busca: string;
  setEstado: (uf: string) => void;
  setDistribuidora: (codigo: string) => void;
  setSegmento: (cnae: string) => void;
  setBusca: (texto: string) => void;
  clearFilters: () => void;
};

export const useFilters = create<FiltersState>((set) => ({
  estado: '',
  distribuidora: '',
  segmento: '',
  busca: '',
  setEstado: (uf: string) => set({ estado: uf }),
  setDistribuidora: (c: string) => set({ distribuidora: c }),
  setSegmento: (cnae: string) => set({ segmento: cnae }),
  setBusca: (texto: string) => set({ busca: texto }),
  clearFilters: (): void =>
    set({ estado: '', distribuidora: '', segmento: '', busca: '' }),
}));
