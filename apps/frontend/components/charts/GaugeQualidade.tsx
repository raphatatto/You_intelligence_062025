'use client';
import { ResponsiveContainer, RadialBarChart, RadialBar } from 'recharts';

export default function GaugeQualidade({ valor }: { valor: number }) {
  const data = [{ name: 'Qualidade', value: valor, fill: '#10b981' }];
  return (
    <ResponsiveContainer width="100%" height={220}>
      <RadialBarChart
        innerRadius="80%"
        outerRadius="100%"
        barSize={16}
        data={data}
        startAngle={90}
        endAngle={-270}
      >
        <RadialBar dataKey="value" cornerRadius={16} />
        <text
          x="50%" y="50%" textAnchor="middle" dominantBaseline="middle"
          className="text-3xl font-semibold"
        >
          {valor}%
        </text>
      </RadialBarChart>
    </ResponsiveContainer>
  );
}
