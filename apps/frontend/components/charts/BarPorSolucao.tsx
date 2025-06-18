'use client';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import type { PorSolucao } from '@/app/types/leads-dashboard';

export default function BarPorSolucao({ data }: { data: PorSolucao[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <XAxis dataKey="solucao" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="leads" />
      </BarChart>
    </ResponsiveContainer>
  );
}
