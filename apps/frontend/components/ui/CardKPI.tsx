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
    <div className={`p-4 rounded-xl shadow ${className}`}>
      <div className="flex items-center space-x-3">
        <div className="text-xl">{icon}</div>
        <div className="flex flex-col">
          <span className="text-sm text-muted-foreground">{title}</span>
          <span className="text-2xl font-bold">{value}</span>

          {trend === 'up' && (
            <span className="text-green-400 text-xs flex items-center gap-1 mt-1">
              <ArrowUpRight size={14} /> {trendValue}
            </span>
          )}

          {trend === 'down' && (
            <span className="text-red-400 text-xs flex items-center gap-1 mt-1">
              <ArrowDownRight size={14} /> {trendValue}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
