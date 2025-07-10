import { create } from 'zustand';

type FiltersState = {
  estado: string;
  distribuidora: string;
  segmento: string;
  busca: string;
  tipo: string;
  setEstado: (uf: string) => void;
  setDistribuidora: (codigo: string) => void;
  setSegmento: (cnae: string) => void;
  setBusca: (texto: string) => void;
  setTipo: (tipo: string) => void;
  clearFilters: () => void;
};

export const useFilters = create<FiltersState>((set) => ({
  estado: '',
  distribuidora: '',
  segmento: '',
  busca: '',
  tipo: '',
  setEstado: (uf: string) => set({ estado: uf }),
  setDistribuidora: (c: string) => set({ distribuidora: c }),
  setSegmento: (cnae: string) => set({ segmento: cnae }),
  setBusca: (texto: string) => set({ busca: texto }),
  setTipo: (tipo: string) => set({ tipo }),
  clearFilters: (): void =>
    set({ estado: '', distribuidora: '', segmento: '', busca: '', tipo: '' }),
}));
