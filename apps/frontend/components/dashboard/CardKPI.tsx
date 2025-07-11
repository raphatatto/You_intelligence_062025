type CardKPIProps = {
  title: string
  value: string | number
  icon: React.ReactNode
}

export default function CardKPI({ title, value, icon }: CardKPIProps) {
  return (
    <div className="rounded-xl bg-white shadow p-4 flex items-center gap-4">
      <div className="text-3xl">{icon}</div>
      <div>
        <h4 className="text-sm text-gray-500">{title}</h4>
        <p className="text-xl font-bold">{value}</p>
      </div>
    </div>
  );
}
