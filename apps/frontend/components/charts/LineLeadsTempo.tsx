'use client';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';
import type { SerieTemporal } from '@/app/types/leads-dashboard';

export default function LineLeadsTempo({ data }: { data: SerieTemporal[] }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data}>
        <XAxis dataKey="dia" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="leads" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}
