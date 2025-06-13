import {ReactNode} from 'react';

export default function CardKPI({title, value, icon}: {title: string; value: string; icon: ReactNode}) {
  return (
    <div className="rounded-xl bg-white shadow p-4 flex items-center gap-4">
      <div className="text-3xl">{icon}</div>
      <div>
        <p className="text-sm text-gray-500">{title}</p>
        <p className="text-2xl font-semibold">{value}</p>
      </div>
    </div>
  );
}
