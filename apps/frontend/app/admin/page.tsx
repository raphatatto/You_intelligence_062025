'use client'

import { useState } from 'react'
import SelectDistribuidoras from '@/components/admin/SelectDistribuidoras'
import SelectAnos from '@/components/admin/SelectAnos'
import ButtonImportar from '@/components/admin/ButtonImportar'
import TabelaStatusImportacoes from '@/components/admin/TabelaStatusImportacoes'
import PainelEnriquecimento from '@/components/admin/PainelEnriquecimento'

export default function AdminPage() {
  const [distribuidoras, setDistribuidoras] = useState<string[]>([])
  const [anos, setAnos] = useState<number[]>([])
  const [loading, setLoading] = useState(false)

  const handleImportar = async () => {
    setLoading(true)

    try {
      for (const distribuidora of distribuidoras) {
        const prefixo = distribuidora.replace(/\s+/g, "_") // ou mapeie corretamente se necessário

        for (const ano of anos) {
          const payload = {
            distribuidora,
            prefixo,
            ano,
            url: '', // o front precisa mapear isso com base no JSON indexador
            camadas: ['UCAT', 'UCMT', 'UCBT']
          }

          await fetch('/v1/admin/importacoes/rodar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          })
        }
      }
    } catch (err) {
      console.error(err)
      alert('Erro ao importar dados')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-center mb-10">
        🧠 Painel de Administração de Dados
      </h1>

      {/* Seção 1: Seleção e disparo de importação */}
      <section className="bg-white shadow-md rounded-xl p-6 mb-10">
        <h2 className="text-lg font-semibold mb-4">📦 Importação de Dados</h2>
        <div className="flex flex-wrap items-end gap-4">
          <SelectDistribuidoras selected={distribuidoras} setSelected={setDistribuidoras} />
          <SelectAnos selected={anos} setSelected={setAnos} />
          <ButtonImportar distribuidoras={distribuidoras} anos={anos} onImportar={handleImportar} loading={loading} />
        </div>
      </section>

      {/* Seção 2: Status das importações */}
      <section className="bg-white shadow-md rounded-xl p-6 mb-10">
        <h2 className="text-lg font-semibold mb-4">📊 Status de Importações</h2>
        <TabelaStatusImportacoes />
      </section>

      {/* Seção 3: Enriquecimento */}
      <section className="bg-white shadow-md rounded-xl p-6 mb-10">
        <h2 className="text-lg font-semibold mb-4">🧬 Enriquecimento de Leads</h2>
        <PainelEnriquecimento />
      </section>
    </main>
  )
}
