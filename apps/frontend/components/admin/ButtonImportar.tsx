'use client'

type Props = {
  distribuidoras: string[]
  anos: number[]
  onImportar: () => void
  loading: boolean
}

export default function ButtonImportar({ distribuidoras, anos, onImportar, loading }: Props) {
  const disabled = distribuidoras.length === 0 || anos.length === 0 || loading

  return (
    <button
      onClick={onImportar}
      disabled={disabled}
      className={`bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition ${
        disabled ? 'opacity-50 cursor-not-allowed' : ''
      }`}
    >
      {loading ? 'Importando...' : '▶️ Importar Selecionados'}
    </button>
  )
}
