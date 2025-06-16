
'use client';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';
import type { QualityPoint } from '@/app/types/dados-dashboard';

export default function LineQualidadeTrend({ data }: { data: QualityPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data}>
        <XAxis dataKey="mes" />
        <YAxis domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
        <Tooltip formatter={(v:number) => `${v}%`} />
        <Line type="monotone" dataKey="qualidade" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}
