'use client';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import type { EnriqItem } from '@/app/types/dados-dashboard';

export default function BarEnriquecimento({ data }: { data: EnriqItem[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} layout="vertical">
        <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
        <YAxis dataKey="atributo" type="category" width={120} />
        <Tooltip formatter={(v:number) => `${v}%`} />
        <Bar dataKey="cobertura" />
      </BarChart>
    </ResponsiveContainer>
  );
}
