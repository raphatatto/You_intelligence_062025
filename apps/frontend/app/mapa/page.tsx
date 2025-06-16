'use client';

import MapView      from '@/components/mapa/MapView';
import { useLeads } from '@/services/leads';

export default function MapaPage() {
  // se quiser filtros, componha query string aqui e passe pra useLeads(qs)
  const { data: leads, isLoading, error } = useLeads();

  if (isLoading) return <p className="p-4">Carregando…</p>;
  if (error)     return <p className="p-4 text-red-600">Falha ao buscar dados.</p>;

  return (
    <div className="h-screen">
      <MapView leads={leads ?? []} />
    </div>
  );
}
