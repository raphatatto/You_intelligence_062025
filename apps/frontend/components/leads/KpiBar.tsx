// components/leads/KpiBar.tsx
'use client';
import CardKPI from '@/components/ui/CardKPI';
import { TrendingUp } from 'lucide-react';
import type { KpiLead } from '@/app/types/leads-dashboard';

export default function KpiBar({ kpis }: { kpis: KpiLead[] }) {
  return (
    <div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-6">
      {kpis.map(k => (
        <CardKPI
          key={k.label}
          title={k.label}
          value={k.valor.toLocaleString('pt-BR')}
          icon={<TrendingUp />}
        />
      ))}
    </div>
  );
}
