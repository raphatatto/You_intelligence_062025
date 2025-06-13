'use client';

import {ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip} from 'recharts';

type Props = {data: {dia: string; leads: number}[]};

export default function LineLeads({data}: Props) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <XAxis dataKey="dia" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="leads" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}
