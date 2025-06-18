'use client';
import { ResponsiveContainer, FunnelChart, Funnel, LabelList, Tooltip } from 'recharts';
import type { PorEstagio } from '@/app/types/leads-dashboard';

export default function FunnelPorEstagio({ data }: { data: PorEstagio[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <FunnelChart>
        <Tooltip />
        <Funnel dataKey="qtd" data={data} isAnimationActive>
          <LabelList position="right" dataKey="estagio" />
        </Funnel>
      </FunnelChart>
    </ResponsiveContainer>
  );
}
