// components/charts/DemandaMensalChart.jsx
'use client';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function DemandaMensalChart({ data }: { data: { mes: string; demanda_kw: number }[] }) {
  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-5 h-full">
      <h3 className="text-lg font-semibold text-white mb-1">Demanda Mensal (kW)</h3>
      <p className="text-sm text-zinc-400 mb-4">Variação da demanda energética por mês</p>
      
      <ResponsiveContainer width="100%" height="80%">
        <LineChart
          data={data}
          margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
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
            width={40}
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
              <span key="value" className="text-green-400 font-bold">{value} kW</span>
            ]}
            labelFormatter={(label) => (
              <div className="text-white font-medium">
                Mês: {label}
              </div>
            )}
            cursor={{ stroke: '#22c55e', strokeWidth: 1, strokeDasharray: '3 3' }}
          />
          <Line 
            type="monotone"
            dataKey="demanda_kw"
            name="Demanda (kW)"
            stroke="#22c55e"
            strokeWidth={3}
            dot={{ r: 4, fill: '#22c55e', strokeWidth: 2 }}
            activeDot={{ r: 6, fill: '#4ade80', stroke: '#166534', strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}