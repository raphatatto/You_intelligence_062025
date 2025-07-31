// components/market/RegionalAnalysis.tsx
'use client'

import { MapPin, BarChart2, Zap, Droplet, Wind, Sun } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { CustomBarChart, CustomMapChart } from '@/components/ui/charts'
import clsx from 'clsx'

export function RegionalAnalysis() {
  // Dados de exemplo por região
  const regionalData = [
    {
      region: 'Sudeste',
      demand: 45,
      generation: 38,
      sources: [
        { name: 'Hidrelétrica', value: 55 },
        { name: 'Termelétrica', value: 25 },
        { name: 'Eólica', value: 12 },
        { name: 'Solar', value: 8 }
      ]
    },
    // Adicione dados para outras regiões...
  ]

  // Dados para o mapa
  const mapData = [
    { id: 'BR-SE', value: 45, name: 'Sudeste', color: '#3b82f6' },
    { id: 'BR-S', value: 18, name: 'Sul', color: '#10b981' },
    { id: 'BR-NE', value: 15, name: 'Nordeste', color: '#f59e0b' },
    { id: 'BR-N', value: 8, name: 'Norte', color: '#ef4444' },
    { id: 'BR-CO', value: 14, name: 'Centro-Oeste', color: '#8b5cf6' }
  ]

  // Fonte de energia por região
  const energySources = [
    { name: 'Hidrelétrica', icon: Droplet, value: 58, color: '#3b82f6' },
    { name: 'Termelétrica', icon: Zap, value: 22, color: '#ef4444' },
    { name: 'Eólica', icon: Wind, value: 12, color: '#10b981' },
    { name: 'Solar', icon: Sun, value: 8, color: '#f59e0b' }
  ]

  return (
    <div className="space-y-6">
      {/* Cabeçalho */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Análise Regional</h2>
          <p className="text-gray-400">Distribuição da demanda e geração por região</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <MapPin className="h-4 w-4" />
          <span>Última atualização: {new Date().toLocaleDateString()}</span>
        </div>
      </div>

      {/* Mapa Interativo */}
      <Card className="p-0 overflow-hidden">
        <div className="p-4 border-b border-gray-800">
          <h3 className="font-medium flex items-center gap-2">
            <BarChart2 className="h-4 w-4 text-blue-400" />
            Mapa de Distribuição Energética
          </h3>
        </div>
        <div className="h-[500px]">
          <CustomMapChart 
            data={mapData}
            region="brazil"
          />
        </div>
      </Card>

      {/* Grid de Informações */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Demanda por Região */}
        <Card>
          <div className="p-4 border-b border-gray-800">
            <h3 className="font-medium">Demanda por Região (MW)</h3>
          </div>
          <div className="p-4 h-80">
            <CustomBarChart
              data={regionalData.map(r => ({ name: r.region, demand: r.demand }))}
              colors={['#3b82f6']}
              height={300}
            />
          </div>
        </Card>

        {/* Geração por Região */}
        <Card>
          <div className="p-4 border-b border-gray-800">
            <h3 className="font-medium">Geração por Região (MW)</h3>
          </div>
          <div className="p-4 h-80">
            <CustomBarChart
              data={regionalData.map(r => ({ name: r.region, generation: r.generation }))}
              colors={['#10b981']}
              height={300}
            />
          </div>
        </Card>

        {/* Fontes de Energia */}
        <Card>
          <div className="p-4 border-b border-gray-800">
            <h3 className="font-medium">Distribuição por Fonte</h3>
          </div>
          <div className="p-4 space-y-3">
            {energySources.map((source, index) => (
              <div key={index} className="space-y-1">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <source.icon className="h-4 w-4" style={{ color: source.color }} />
                    <span className="text-sm">{source.name}</span>
                  </div>
                  <span className="text-sm font-medium">{source.value}%</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div 
                    className="h-2 rounded-full" 
                    style={{
                      width: `${source.value}%`,
                      backgroundColor: source.color
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Tabela Detalhada */}
      <Card>
        <div className="p-4 border-b border-gray-800">
          <h3 className="font-medium">Dados Regionais Detalhados</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="text-left text-gray-400 text-sm border-b border-gray-800">
              <tr>
                <th className="p-4">Região</th>
                <th className="p-4">Demanda (MW)</th>
                <th className="p-4">Geração (MW)</th>
                <th className="p-4">Déficit/Superávit</th>
                <th className="p-4">Principais Fontes</th>
              </tr>
            </thead>
            <tbody>
              {regionalData.map((region, index) => (
                <tr key={index} className="border-b border-gray-800 hover:bg-gray-800/50">
                  <td className="p-4 font-medium">{region.region}</td>
                  <td className="p-4">{region.demand.toLocaleString()}</td>
                  <td className="p-4">{region.generation.toLocaleString()}</td>
                  <td className={clsx(
                    "p-4",
                    region.generation >= region.demand ? "text-green-400" : "text-red-400"
                  )}>
                    {((region.generation - region.demand) / region.demand * 100).toFixed(1)}%
                  </td>
                  <td className="p-4">
                    <div className="flex gap-1">
                      {region.sources.slice(0, 3).map((source, i) => (
                        <span 
                          key={i} 
                          className="px-2 py-1 text-xs rounded-full bg-gray-700"
                        >
                          {source.name} ({source.value}%)
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}