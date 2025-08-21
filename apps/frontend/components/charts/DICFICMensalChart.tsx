// components/charts/DICFICMensalChart.jsx
'use client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function DICFICMensalChart({ data }: { data: { mes: string; dic: number; fic: number }[] }) {
  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-5 h-full">
      <h3 className="text-lg font-semibold text-white mb-1">Indicadores Mensais</h3>
      <p className="text-sm text-zinc-400 mb-4">Duração e Frequência de Interrupções</p>
      
      <ResponsiveContainer width="100%" height="80%">
        <BarChart
          data={data}
          margin={{ top: 20, right: 20, left: 0, bottom: 5 }}
          barGap={4}
          barCategoryGap={12}
        >
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="#374151" 
            vertical={false}
          />
          <XAxis 
            dataKey="mes"
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
            formatter={(value: number, name: string) => [
              <span key="value" className={`font-bold ${
                name === 'DIC (min)' ? 'text-green-400' : 'text-cyan-400'
              }`}>
                {value} {name.includes('DIC') ? 'min' : 'vezes'}
              </span>,
              name
            ]}
            labelFormatter={(label) => (
              <div className="text-white font-medium">
                Mês: {label}
              </div>
            )}
            cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }}
          />
          <Bar 
            dataKey="dic"
            name="DIC (min)"
            radius={[4, 4, 0, 0]}
            fill="#22c55e"
          />
          <Bar 
            dataKey="fic"
            name="FIC (vezes)"
            radius={[4, 4, 0, 0]}
            fill="#06b6d4"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}