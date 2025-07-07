'use client';

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { DISTRIBUIDORAS_MAP } from '@/utils/distribuidoras';

export default function BarLeadsDistribuidora({ data }: { data: { nome: string; total: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <XAxis dataKey="nome" />
        <YAxis />
        <Tooltip 
        formatter={(value: number) => [`${value}`, 'Leads']}
                    labelFormatter={(label: string) =>
                        `${label} - ${DISTRIBUIDORAS_MAP[label] ?? 'Segmento desconhecido'}`
                    }
            itemStyle={{ color: 'black' }}
            labelStyle={{ color: 'black', fontWeight: 'bold' }}/>
        <Bar dataKey="total" fill="#a3e635" />
      </BarChart>
    </ResponsiveContainer>
  );
}
