'use client';

import dynamic from 'next/dynamic';
import { Flame } from 'lucide-react';

const MapaHeat = dynamic(() => import('@/components/mapa/MapaHeat'), {
  ssr: false,
});

export default function MapaHeatPage() {
  return (
    <section className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-white flex items-center gap-2">
        <Flame size={24} /> Mapa de Calor de DIC Médio
      </h1>

      <div className="bg-zinc-900 border border-zinc-700 rounded-xl p-4">
        <MapaHeat />
      </div>
    </section>
  );
}
