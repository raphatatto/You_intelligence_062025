'use client';

import {ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip} from 'recharts';

type Props = {data: {mes: string; mwh: number}[]};

export default function BarEnergy({data}: Props) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <XAxis dataKey="mes" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="mwh" />
      </BarChart>
    </ResponsiveContainer>
  );
}
