'use client'
import { useMemo, useState } from 'react'
import { Search, MapPin, BarChart2, Zap, Wind, Activity, Sun } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend, PieChart, Pie, Cell, BarChart, Bar } from 'recharts'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

function keyMun(s: string) {
  return s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
}

export default function Client({ data }: { data: { index: any; nomes: Record<string,string> } }) {
  const [municipio, setMunicipio] = useState('')
  const [municipioSelecionado, setMunicipioSelecionado] = useState('')

  const item = useMemo(() => {
    const k = keyMun(municipioSelecionado);
    return data.index[k] ?? null;
  }, [municipioSelecionado, data.index])

  return (
    <div className="flex flex-col min-h-screen bg-black text-white">
      <header className="border-b border-gray-700 p-6">
        <div className="flex items-center gap-4">
          <BarChart2 className="text-blue-400" size={28} />
          <div>
            <h1 className="text-2xl font-bold">Análise de Mercado por Município</h1>
            <p className="text-gray-400">Dados pré-processados no servidor (carrega instantâneo)</p>
          </div>
        </div>
      </header>

      <section className="p-6 border-b border-gray-700 bg-gray-900">
        <div className="flex flex-col md:flex-row gap-4 max-w-4xl mx-auto">
          <div className="flex-1 relative">
            <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <Input
              type="text"
              placeholder="Digite o município (ex.: São Paulo)"
              className="pl-10 text-black"
              value={municipio}
              onChange={(e) => setMunicipio(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && setMunicipioSelecionado(municipio)}
              list="mun-list"
            />
            <datalist id="mun-list">
              {Object.entries(data.nomes).slice(0, 5000).map(([k, v]) => (
                <option key={k} value={v} />
              ))}
            </datalist>
          </div>
          <Button onClick={() => setMunicipioSelecionado(municipio)} className="gap-2">
            <Search size={18} /> Pesquisar
          </Button>
        </div>
      </section>

      <main className="flex-1 p-6">
        {municipioSelecionado && item ? (
          <>
            <div className="mb-6 flex items-center gap-2">
              <MapPin className="text-blue-400" size={20} />
              <h2 className="text-xl font-semibold">Dados para {data.nomes[keyMun(municipioSelecionado)] ?? municipioSelecionado}</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm text-gray-400">Intensidade de Mercado</CardTitle>
                  <Activity className="h-4 w-4 text-blue-400" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{item.metrics.total} UCs/Registros</div>
                  <p className="text-xs mt-1 text-gray-400">Consolidado (4 bases)</p>
                </CardContent>
              </Card>

              {item.metrics.tarifa != null && (
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm text-gray-400">Tarifa média</CardTitle>
                    <Zap className="h-4 w-4 text-yellow-400" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">R$ {item.metrics.tarifa.toFixed(2)}/kWh</div>
                  </CardContent>
                </Card>
              )}

              {item.metrics.renovaveis != null && (
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm text-gray-400">Fontes renováveis</CardTitle>
                    <Sun className="h-4 w-4 text-green-400" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{item.metrics.renovaveis.toFixed(0)}%</div>
                  </CardContent>
                </Card>
              )}
            </div>

            {item.metrics.distribuidoras?.length > 0 && (
              <div className="mb-8">
                <Card>
                  <CardHeader><CardTitle className="text-sm text-gray-400">Distribuidoras</CardTitle></CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {item.metrics.distribuidoras.map((d: string) => (
                        <span key={d} className="px-3 py-1 rounded-full bg-gray-800 text-sm">{d}</span>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {item.metrics.consumoMensal && (
              <Card className="mb-8">
                <CardHeader><CardTitle className="flex items-center gap-2"><Activity size={18}/>Volume por mês</CardTitle></CardHeader>
                <CardContent>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={item.metrics.consumoMensal}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="mes" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="consumo" stroke="#8884d8" activeDot={{ r: 6 }} name="Registros" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            )}

            {item.metrics.fontesGeracao?.length > 0 && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                <Card>
                  <CardHeader><CardTitle>Fontes / Tipo de Sistema</CardTitle></CardHeader>
                  <CardContent>
                    <div className="h-80">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie data={item.metrics.fontesGeracao} cx="50%" cy="50%" outerRadius={90} dataKey="value" nameKey="name"
                               label={({ name, percent }) => `${name}: ${(percent*100).toFixed(0)}%`}>
                            {item.metrics.fontesGeracao.map((_: any, i: number) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                          </Pie>
                          <Tooltip /><Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader><CardTitle>Distribuição por Fonte</CardTitle></CardHeader>
                  <CardContent>
                    <div className="h-80">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={item.metrics.fontesGeracao}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" /><YAxis /><Tooltip /><Legend />
                          <Bar dataKey="value" name="Registros" fill="#8884d8" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </>
        ) : (
          <div className="flex flex-col items-center justify-center h-64 text-center">
            <Search className="h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-xl font-medium text-gray-300 mb-2">Pesquise um município</h3>
            <p className="text-gray-400 max-w-md">Os dados já estão carregados e cacheados — a busca é instantânea.</p>
          </div>
        )}
      </main>
    </div>
  )
}
