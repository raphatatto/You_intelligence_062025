'use client';

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { CNAE_SEGMENTOS } from '@/utils/cnae';

export default function BarTopCNAE({ data }: { data: { nome: string; total: number }[] }) {
  const dataComDescricao = data.map((item) => ({
    ...item,
    codigo: item.nome,
    descricao: CNAE_SEGMENTOS[item.nome] ?? 'Segmento desconhecido',
  }));

  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart layout="vertical" data={dataComDescricao}>
        <XAxis type="number" />
        <YAxis dataKey="codigo" type="category" width={100} />
        <Tooltip
            formatter={(value: number) => [`${value}`, 'Leads']}
            labelFormatter={(label: string) =>
                `${label} - ${CNAE_SEGMENTOS[label] ?? 'Segmento desconhecido'}`
            }
            contentStyle={{ backgroundColor: 'white', color: 'black', borderRadius: 8 }}
            itemStyle={{ color: 'black' }}
            labelStyle={{ color: 'black', fontWeight: 'bold' }}
            />

        <Bar dataKey="total" fill="#facc15" />
      </BarChart>
    </ResponsiveContainer>
  );
}
