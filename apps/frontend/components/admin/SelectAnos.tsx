'use client'

type Props = {
  selected: number[]
  setSelected: (value: number[]) => void
}

export default function SelectAnos({ selected, setSelected }: Props) {
  const anos = [2019, 2020, 2021, 2022, 2023, 2024, 2025]

  const toggle = (ano: number) => {
    if (selected.includes(ano)) {
      setSelected(selected.filter((a) => a !== ano))
    } else {
      setSelected([...selected, ano])
    }
  }

  return (
    <div>
      <label className="block text-sm font-medium mb-1">📅 Anos:</label>
      <div className="flex flex-col gap-1 border p-3 rounded-md max-h-40 overflow-y-auto w-40">
        {anos.map((ano) => (
          <label key={ano} className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={selected.includes(ano)}
              onChange={() => toggle(ano)}
              className="accent-blue-600"
            />
            {ano}
          </label>
        ))}
      </div>
    </div>
  )
}
