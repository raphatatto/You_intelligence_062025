// app/mapa/page.tsx
'use client';
import MapView from '@/components/mapa/MapView';
import { useLeads } from '@/services/leads';

export default function MapaPage() {
  const { data: leads } = useLeads();  // ← já traz mock

  return (
    <div className="h-screen">
      <MapView leads={leads ?? []} />
    </div>
  );
}
