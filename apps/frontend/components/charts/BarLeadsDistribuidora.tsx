// components/charts/BarLeadsDistribuidora.jsx
'use client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';
import { DISTRIBUIDORAS_MAP } from '@/utils/distribuidoras';

const COLORS = ['#22c55e', '#16a34a', '#15803d', '#166534', '#14532d', '#0f766e'];

export default function BarLeadsDistribuidora({ data }: { data: { nome: string; total: number }[] }) {
  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-5 h-full">
      <h3 className="text-lg font-semibold text-white mb-1">Leads por Distribuidora</h3>
      <p className="text-sm text-zinc-400 mb-4">Distribuição de leads por concessionária</p>
      
      <ResponsiveContainer width="100%" height="80%">
        <BarChart
          data={data}
          margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
          barSize={28}
        >
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="#374151" 
            vertical={false} 
          />
          <XAxis 
            dataKey="nome" 
            tick={{ fill: '#9CA3AF', fontSize: 12 }}
            tickLine={false}
            axisLine={{ stroke: '#374151' }}
          />
          <YAxis 
            tick={{ fill: '#9CA3AF', fontSize: 12 }}
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
                {label} - {DISTRIBUIDORAS_MAP[label] ?? 'Segmento desconhecido'}
              </span>
            )}
            cursor={{ fill: 'rgba(34, 197, 94, 0.1)' }}
          />
          <Bar 
            dataKey="total" 
            name="Total de Leads"
            radius={[4, 4, 0, 0]}
          >
            {data.map((entry, index) => (
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