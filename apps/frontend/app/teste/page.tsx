'use client'

import { useLeads } from '@/components/hooks/useLeads'
import { Lead } from '@/app/types/lead'
import CardKPI from '@/components/dashboard/CardKPI'
import { LeadCard } from '@/components/leads/LeadCard'
import { Bolt, MapPin } from 'lucide-react'

export default function LeadsPage() {
  const {leads, isLoading, error } = useLeads()

  if (isLoading) return <p className="p-4">🔄 Carregando dados...</p>
  if (error) return <p className="p-4 text-red-500">Erro ao carregar leads.</p>

  // KPIs
  const totalLeads = leads.length
  const mediaDIC = (
  leads.reduce((acc: number, l:Lead) => acc + (l.dicMed ?? 0), 0) / totalLeads
).toFixed(2)

const mediaFIC = (
  leads.reduce((acc: number, l: Lead) => acc + (l.ficMed ?? 0), 0) / totalLeads
).toFixed(2)

  return (
    <section className="space-y-8 px-6 lg:px-12 py-10">
      <h1 className="text-3xl font-bold">Leads Mapeados</h1>
      <p className="text-muted-foreground text-sm">
        Exibindo {totalLeads} leads com dados de qualidade, energia e localização.
      </p>

      {/* KPIs */}
      <div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-6">
        <CardKPI title="Total de Leads" value={totalLeads} icon={<MapPin />} />
        <CardKPI title="Média DIC" value={mediaDIC} icon={<Bolt />} />
        <CardKPI title="Média FIC" value={mediaFIC} icon={<Bolt />} />
      </div>

      {/* Cards de Lead */}
      <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
        {leads.map((lead: Lead) => (
          <LeadCard key={lead.id} lead={lead} />
        ))}
      </div>
    </section>
  )
}
