'use client'

import useSWR from 'swr'

type Importacao = {
  distribuidora: string
  ano: number
  camada: string
  status: string
  data_execucao: string
}

const statusBadge = (status: string) => {
  const base = 'px-2 py-1 text-xs font-semibold rounded';
  switch (status) {
    case 'success':
      return <span className={`${base} bg-green-100 text-green-800`}>✅ concluído</span>
    case 'failed':
      return <span className={`${base} bg-red-100 text-red-800`}>❌ erro</span>
    case 'importando':
      return <span className={`${base} bg-yellow-100 text-yellow-800`}>⏳ importando</span>
    default:
      return <span className={`${base} bg-gray-200 text-gray-800`}>{status}</span>
  }
}

const fetcher = (url: string) => fetch(url).then(res => res.json())

export default function TabelaStatusImportacoes() {
  const { data, error, isLoading } = useSWR<Importacao[]>('/v1/admin/importacoes', fetcher, {
    refreshInterval: 5000
  })

  if (error) return <p className="text-red-600">Erro ao carregar status.</p>
  if (isLoading || !data) return <p className="text-gray-500">Carregando...</p>

  return (
    <div className="overflow-auto">
      <table className="min-w-full border text-sm text-left">
        <thead className="bg-gray-100">
          <tr>
            <th className="px-4 py-2 border">Distribuidora</th>
            <th className="px-4 py-2 border">Ano</th>
            <th className="px-4 py-2 border">Camada</th>
            <th className="px-4 py-2 border">Status</th>
            <th className="px-4 py-2 border">Data Execução</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, idx) => (
            <tr key={idx} className="border-b">
              <td className="px-4 py-2 border">{item.distribuidora}</td>
              <td className="px-4 py-2 border">{item.ano}</td>
              <td className="px-4 py-2 border">{item.camada}</td>
              <td className="px-4 py-2 border">{statusBadge(item.status)}</td>
              <td className="px-4 py-2 border">{new Date(item.data_execucao).toLocaleString('pt-BR')}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
