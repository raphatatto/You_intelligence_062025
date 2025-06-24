'use client';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export default function BarLeadsEstado({
  data,
}: {
  data: { estado: string; total: number }[];
}) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <XAxis dataKey="estado" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="total" fill="#b3d430" />
      </BarChart>
    </ResponsiveContainer>
  );
}
