// app/analise-de-mercado/page.tsx
'use client'

import { useState } from 'react'
import { Search, MapPin, BarChart2, Zap, BatteryCharging, Droplet, Sun, Wind, Activity } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts'

// Dados mockados para exemplificação
const mockMunicipalData = {
  'São Paulo': {
    consumo: 1245,
    tarifa: 0.72,
    renovaveis: 58,
    trendConsumo: 3.2,
    trendTarifa: 5.1,
    trendRenovaveis: 8.3,
    consumoMensal: [
      { mes: 'Jan', consumo: 1200 },
      { mes: 'Fev', consumo: 1150 },
      { mes: 'Mar', consumo: 1300 },
      { mes: 'Abr', consumo: 1250 },
      { mes: 'Mai', consumo: 1400 },
      { mes: 'Jun', consumo: 1350 },
    ],
    comparativoTarifas: [
      { tipo: 'Municipal', valor: 0.72 },
      { tipo: 'Estadual', valor: 0.68 },
      { tipo: 'Nacional', valor: 0.65 },
    ],
    fontesGeracao: [
      { name: 'Hidrelétrica', value: 45 },
      { name: 'Solar', value: 15 },
      { name: 'Eólica', value: 12 },
      { name: 'Gás Natural', value: 20 },
      { name: 'Outros', value: 8 },
    ],
    infoAdicionais: {
      populacao: '12.33 milhões',
      area: '1.521 km²',
      pibPerCapita: 'R$ 45.876',
      distribuidora: 'Enel SP'
    }
  },
  'Rio de Janeiro': {
    consumo: 980,
    tarifa: 0.81,
    renovaveis: 42,
    trendConsumo: 2.1,
    trendTarifa: 6.3,
    trendRenovaveis: 5.7,
    consumoMensal: [
      { mes: 'Jan', consumo: 950 },
      { mes: 'Fev', consumo: 920 },
      { mes: 'Mar', consumo: 1000 },
      { mes: 'Abr', consumo: 980 },
      { mes: 'Mai', consumo: 1050 },
      { mes: 'Jun', consumo: 1020 },
    ],
    comparativoTarifas: [
      { tipo: 'Municipal', valor: 0.81 },
      { tipo: 'Estadual', valor: 0.76 },
      { tipo: 'Nacional', valor: 0.65 },
    ],
    fontesGeracao: [
      { name: 'Hidrelétrica', value: 35 },
      { name: 'Solar', value: 8 },
      { name: 'Eólica', value: 5 },
      { name: 'Gás Natural', value: 40 },
      { name: 'Outros', value: 12 },
    ],
    infoAdicionais: {
      populacao: '6.75 milhões',
      area: '1.200 km²',
      pibPerCapita: 'R$ 39.245',
      distribuidora: 'Light'
    }
  }
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

export default function MarketAnalysisPage() {
  const [municipio, setMunicipio] = useState('')
  const [municipioSelecionado, setMunicipioSelecionado] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSearch = () => {
    if (!municipio) return
    
    setIsLoading(true)
    
    // Simula busca de dados
    setTimeout(() => {
      setMunicipioSelecionado(municipio)
      setIsLoading(false)
    }, 800)
  }

  const dadosMunicipio = mockMunicipalData[municipioSelecionado as keyof typeof mockMunicipalData]

  return (
    <div className="flex flex-col min-h-screen bg-black  text-white">
      {/* Cabeçalho */}
      <header className="border-b border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center gap-4">
          <BarChart2 className="text-blue-500 dark:text-blue-400" size={28} />
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Análise de Mercado por Município
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Consulte dados energéticos específicos por localidade
            </p>
          </div>
        </div>
      </header>

      {/* Barra de pesquisa */}
      <section className="p-6 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="flex flex-col md:flex-row gap-4 max-w-4xl mx-auto">
          <div className="flex-1 relative">
            <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <Input
              type="text"
              placeholder="Digite o nome do município (ex: São Paulo, Rio de Janeiro)"
              className="pl-10 text-black"
              value={municipio}
              onChange={(e) => setMunicipio(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
          <Button onClick={handleSearch} disabled={isLoading} className="gap-2">
            <Search size={18} />
            {isLoading ? 'Buscando...' : 'Pesquisar'}
          </Button>
        </div>
      </section>

      {/* Resultados */}
      <main className="flex-1 p-6">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : municipioSelecionado && dadosMunicipio ? (
          <>
            {/* Título com o município selecionado */}
            <div className="mb-6 flex items-center gap-2">
              <MapPin className="text-blue-500" size={20} />
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Dados energéticos para {municipioSelecionado}
              </h2>
            </div>

            {/* Cards de indicadores */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Consumo Médio
                  </CardTitle>
                  <Activity className="h-4 w-4 text-blue-500 dark:text-blue-400" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{dadosMunicipio.consumo} MWh/mês</div>
                  <p className={`text-xs mt-1 ${
                    dadosMunicipio.trendConsumo >= 0 ? 'text-green-500 dark:text-green-400' : 'text-red-500 dark:text-red-400'
                  }`}>
                    {dadosMunicipio.trendConsumo >= 0 ? '+' : ''}{dadosMunicipio.trendConsumo}% em relação ao ano anterior
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Tarifa Média
                  </CardTitle>
                  <Zap className="h-4 w-4 text-yellow-500 dark:text-yellow-400" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">R$ {dadosMunicipio.tarifa.toFixed(2)}/kWh</div>
                  <p className={`text-xs mt-1 ${
                    dadosMunicipio.trendTarifa >= 0 ? 'text-red-500 dark:text-red-400' : 'text-green-500 dark:text-green-400'
                  }`}>
                    {dadosMunicipio.trendTarifa >= 0 ? '+' : ''}{dadosMunicipio.trendTarifa}% em relação ao ano anterior
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Fontes Renováveis
                  </CardTitle>
                  <Sun className="h-4 w-4 text-green-500 dark:text-green-400" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{dadosMunicipio.renovaveis}%</div>
                  <p className={`text-xs mt-1 ${
                    dadosMunicipio.trendRenovaveis >= 0 ? 'text-green-500 dark:text-green-400' : 'text-red-500 dark:text-red-400'
                  }`}>
                    {dadosMunicipio.trendRenovaveis >= 0 ? '+' : ''}{dadosMunicipio.trendRenovaveis}% em relação ao ano anterior
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Informações adicionais */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">População</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-lg font-semibold">{dadosMunicipio.infoAdicionais.populacao}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">Área</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-lg font-semibold">{dadosMunicipio.infoAdicionais.area}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">PIB per capita</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-lg font-semibold">{dadosMunicipio.infoAdicionais.pibPerCapita}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">Distribuidora</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-lg font-semibold">{dadosMunicipio.infoAdicionais.distribuidora}</div>
                </CardContent>
              </Card>
            </div>

            {/* Gráfico de consumo mensal */}
            <Card className="mb-8">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity size={18} />
                  Consumo Energético Mensal
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={dadosMunicipio.consumoMensal}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="mes" />
                      <YAxis label={{ value: 'MWh', angle: -90, position: 'insideLeft' }} />
                      <Tooltip />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="consumo"
                        stroke="#8884d8"
                        activeDot={{ r: 8 }}
                        name="Consumo (MWh)"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Comparativo de tarifas e fontes de geração */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Zap size={18} />
                    Comparativo de Tarifas
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={dadosMunicipio.comparativoTarifas}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="tipo" />
                        <YAxis label={{ value: 'R$/kWh', angle: -90, position: 'insideLeft' }} />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="valor" fill="#8884d8" name="Valor (R$/kWh)" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Wind size={18} />
                    Fontes de Geração de Energia
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={dadosMunicipio.fontesGeracao}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                          nameKey="name"
                          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        >
                          {dadosMunicipio.fontesGeracao.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>
          </>
        ) : municipioSelecionado && !dadosMunicipio ? (
          <div className="flex flex-col items-center justify-center h-64 text-center">
            <MapPin className="h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-xl font-medium text-gray-700 dark:text-gray-300 mb-2">
              Município não encontrado
            </h3>
            <p className="text-gray-500 dark:text-gray-400 max-w-md">
              Não encontramos dados para "{municipioSelecionado}". Verifique o nome e tente novamente.
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-64 text-center">
            <Search className="h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-xl font-medium text-gray-700 dark:text-gray-300 mb-2">
              Pesquise um município
            </h3>
            <p className="text-gray-500 dark:text-gray-400 max-w-md">
              Digite o nome de um município no campo de pesquisa acima para visualizar os dados
              energéticos específicos da localidade.
            </p>
          </div>
        )}
      </main>
    </div>
  )
}