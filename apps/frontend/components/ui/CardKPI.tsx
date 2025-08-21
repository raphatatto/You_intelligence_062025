// components/ui/CardKPI.jsx
"use client"

import { ArrowUpRight, ArrowDownRight } from "lucide-react";

type CardKPIProps = {
  title: string;
  value: string;
  icon: React.ReactNode;
  className?: string;
  trend?: 'up' | 'down';
  trendValue?: string;
};

export default function CardKPI({
  title,
  value,
  icon,
  className,
  trend,
  trendValue,
}: CardKPIProps) {
  return (
    <div className={`p-5 rounded-xl border border-zinc-800 bg-zinc-900/70 backdrop-blur-sm transition-all duration-300 hover:border-green-500/30 hover:shadow-lg hover:shadow-green-500/10 ${className}`}>
      <div className="flex items-center space-x-4">
        <div className="p-2 rounded-lg bg-green-900/30 border border-green-800/30">
          {icon}
        </div>
        <div className="flex flex-col">
          <span className="text-sm text-zinc-400 mb-1">{title}</span>
          <span className="text-xl font-bold text-white">{value}</span>

          {trend === 'up' && (
            <span className="text-green-400 text-xs flex items-center gap-1 mt-2">
              <ArrowUpRight size={14} /> {trendValue}
            </span>
          )}

          {trend === 'down' && (
            <span className="text-red-400 text-xs flex items-center gap-1 mt-2">
              <ArrowDownRight size={14} /> {trendValue}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}