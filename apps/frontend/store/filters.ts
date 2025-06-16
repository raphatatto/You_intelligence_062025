// store/filters.ts
import { create } from 'zustand';

type State = {
  regioes: string[];     
  solucoes: string[];       
};
type Actions = {
  toggleRegiao: (r: string) => void;
  toggleSolucao: (s: string) => void;
  reset: () => void;
};

export const useFilters = create<State & Actions>((set) => ({
  regioes: [],
  solucoes: [],
  toggleRegiao: (r) =>
    set((s) => ({
      regioes: s.regioes.includes(r)
        ? s.regioes.filter((x) => x !== r)
        : [...s.regioes, r],
    })),
  toggleSolucao: (sln) =>
    set((s) => ({
      solucoes: s.solucoes.includes(sln)
        ? s.solucoes.filter((x) => x !== sln)
        : [...s.solucoes, sln],
    })),
  reset: () => set({ regioes: [], solucoes: [] }),
}));
