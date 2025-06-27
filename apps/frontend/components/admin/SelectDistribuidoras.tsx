'use client'

import { useState } from 'react'

const distribuidorasDisponiveis = [
  'ENEL DISTRIBUIÇÃO RIO',
  'CPFL PAULISTA',
  'NEOENERGIA COELBA',
  'ELETROCAR',
  'EDP SP'
]

type Props = {
  selected: string[]
  setSelected: (value: string[]) => void
}

export default function SelectDistribuidoras({ selected, setSelected }: Props) {
  const toggle = (nome: string) => {
    if (selected.includes(nome)) {
      setSelected(selected.filter((item) => item !== nome))
    } else {
      setSelected([...selected, nome])
    }
  }

  return (
    <div>
      <label className="block text-sm font-medium mb-1">🏷️ Distribuidoras:</label>
      <div className="flex flex-col gap-1 border p-3 rounded-md max-h-40 overflow-y-auto w-64">
        {distribuidorasDisponiveis.map((nome) => (
          <label key={nome} className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={selected.includes(nome)}
              onChange={() => toggle(nome)}
              className="accent-blue-600"
            />
            {nome}
          </label>
        ))}
      </div>
    </div>
  )
}
