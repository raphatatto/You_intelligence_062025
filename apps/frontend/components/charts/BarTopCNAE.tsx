// components/charts/BarTopCNAE.jsx
'use client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';
import { CNAE_SEGMENTOS } from '@/utils/cnae';

const COLORS = ['#22c55e', '#16a34a', '#15803d', '#166534', '#14532d', '#0f766e', '#22d3ee', '#06b6d4', '#0891b2'];

export default function BarTopCNAE({ data }: { data: { nome: string; total: number }[] }) {
  const dataComDescricao = data.map((item) => ({
    ...item,
    codigo: item.nome,
    descricao: CNAE_SEGMENTOS[item.nome] ?? 'Segmento desconhecido',
  }));

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-5 h-full">
      <h3 className="text-lg font-semibold text-white mb-1">Top Segmentos CNAE</h3>
      <p className="text-sm text-zinc-400 mb-4">Distribuição de leads por classificação CNAE</p>
      
      <ResponsiveContainer width="100%" height="80%">
        <BarChart
          layout="vertical"
          data={dataComDescricao}
          margin={{ top: 5, right: 20, left: 2, bottom: 5 }}
          barSize={24}
        >
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="#374151" 
            horizontal={true}
            vertical={false}
          />
          <XAxis 
            type="number"
            tick={{ fill: '#9CA3AF', fontSize: 12 }}
            tickLine={false}
            axisLine={{ stroke: '#374151' }}
          />
          <YAxis 
            dataKey="codigo"
            type="category"
            width={110}
            tick={{ fill: '#E5E7EB', fontSize: 12 }}
            tickLine={false}
            axisLine={{ stroke: '#374151' }}
          />
          <Tooltip
            contentStyle={{
              background: 'rgba(17, 24, 39, 0.95)',
              border: '1px solid rgba(34, 197, 94, 0.3)',
              borderRadius: '0.5rem',
              backdropFilter: 'blur(4px)',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.2)',
            }}
            formatter={(value: number) => [
              <span key="value" className="text-green-400 font-bold">{value}</span>, 
              <span key="label" className="text-zinc-300">Leads</span>
            ]}
            labelFormatter={(label: string) => (
              <span className="text-white font-medium">
                {CNAE_SEGMENTOS[label] || 'Segmento desconhecido'}
                <span className="text-xs text-zinc-400 mt-1">CNAE: {label}</span>
              </span>
            )}
            cursor={{ fill: 'rgba(34, 197, 94, 0.1)' }}
          />
          <Bar 
            dataKey="total" 
            name="Total de Leads"
            radius={[0, 4, 4, 0]}
          >
            {dataComDescricao.map((entry, index) => (
              <Cell 
                key={`cell-${index}`}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}