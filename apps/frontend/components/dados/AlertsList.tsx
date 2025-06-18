
'use client';
import type { AlertItem } from '@/app/types/dados-dashboard';
import { AlertTriangle, Info, ShieldAlert } from 'lucide-react';

export default function AlertsList({ items }: { items: AlertItem[] }) {
  const icon = { info: Info, warn: AlertTriangle, crit: ShieldAlert };
  const color = { info: 'text-blue-500', warn: 'text-yellow-500', crit: 'text-red-600' };
  return (
    <ul className="space-y-3">
      {items.map(a => {
        const Icon = icon[a.severidade];
        return (
          <li key={a.id} className="flex items-start gap-2">
            <Icon className={`w-5 h-5 mt-0.5 ${color[a.severidade]}`} />
            <span className="text-sm">{a.mensagem}</span>
          </li>
        );
      })}
    </ul>
  );
}
