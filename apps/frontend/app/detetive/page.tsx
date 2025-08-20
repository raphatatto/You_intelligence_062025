// components/detective/SidebarPanel.tsx
'use client'

import { 
  Search, Building, MapPin, X, 
  User, Mail, Phone, Zap, AlertCircle,
  FileText, Download, ChevronLeft
} from 'lucide-react'
import { useState } from 'react'

export default function DetectiveSidebarPanel({ onClose }: { onClose: () => void }) {
  const [searchTerm, setSearchTerm] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [selectedLead, setSelectedLead] = useState<any>(null)
  const [isSearching, setIsSearching] = useState(false)
  const [activeTab, setActiveTab] = useState<'search' | 'history'>('search')

  // Simulação de busca na base de dados
  const handleSearch = () => {
    if (!searchTerm.trim()) return
    
    setIsSearching(true)
    
    // Simulando uma busca assíncrona
    setTimeout(() => {
      // Dados mockados para demonstração
      const mockResults = [
        {
          id: 1,
          cnpj: '12.345.678/0001-90',
          razaoSocial: 'Empresa Exemplo Ltda',
          nomeFantasia: 'Exemplo Energia',
          endereco: 'Rua das Flores, 123 - São Paulo/SP',
          consumoMedio: 15000,
          demandaContratada: 200,
          distribuidora: 'Enel',
          submercado: 'Sudeste',
          ultimaAtualizacao: '2023-10-15',
          contato: {
            nome: 'Carlos Silva',
            email: 'carlos@exemplo.com',
            telefone: '(11) 99999-9999'
          },
          historicoConsumo: [
            { mes: 'Jan/2023', consumo: 14200 },
            { mes: 'Fev/2023', consumo: 14800 },
            { mes: 'Mar/2023', consumo: 15300 },
            { mes: 'Abr/2023', consumo: 14900 },
            { mes: 'Mai/2023', consumo: 15600 },
            { mes: 'Jun/2023', consumo: 16200 }
          ]
        },
        {
          id: 2,
          cnpj: '98.765.432/0001-10',
          razaoSocial: 'Comércio de Energia SA',
          nomeFantasia: 'Comércio Energ',
          endereco: 'Av. Paulista, 1000 - São Paulo/SP',
          consumoMedio: 25000,
          demandaContratada: 350,
          distribuidora: 'CPFL',
          submercado: 'Sudeste',
          ultimaAtualizacao: '2023-09-20',
          contato: {
            nome: 'Ana Santos',
            email: 'ana.santos@comercioenerg.com',
            telefone: '(11) 98888-8888'
          }
        },
        {
          id: 3,
          cnpj: '55.444.333/0001-22',
          razaoSocial: 'Indústria Sustentável ME',
          nomeFantasia: 'Indústria Sustentável',
          endereco: 'Rua Industrial, 456 - Campinas/SP',
          consumoMedio: 38000,
          demandaContratada: 500,
          distribuidora: 'CPFL',
          submercado: 'Sudeste',
          ultimaAtualizacao: '2023-11-05',
          contato: {
            nome: 'Roberto Lima',
            email: 'roberto.lima@industriasustentavel.com',
            telefone: '(19) 97777-7777'
          }
        }
      ]
      
      setSearchResults(mockResults)
      setIsSearching(false)
    }, 1500)
  }

  const handleSelectLead = (lead: any) => {
    setSelectedLead(lead)
  }

  const handleClearSearch = () => {
    setSearchTerm('')
    setSearchResults([])
    setSelectedLead(null)
  }

  return (
    <div className="h-full bg-zinc-900 border-r border-zinc-800 flex flex-col">
      {/* Header do Painel */}
      <div className="flex items-center justify-between p-4 border-b border-zinc-800 bg-zinc-900">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-green-900/30">
            <Search className="w-5 h-5 text-green-400" />
          </div>
          <div>
            <h3 className="font-semibold text-white">Detective ANEEL</h3>
            <p className="text-xs text-zinc-400">Busca na base de dados</p>
          </div>
        </div>
        <button 
          onClick={onClose}
          className="p-1 text-zinc-400 hover:text-white rounded-md hover:bg-zinc-800"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Abas de navegação */}
      <div className="flex border-b border-zinc-800">
        <button
          className={`flex-1 py-3 text-sm font-medium ${activeTab === 'search' ? 'text-green-400 border-b-2 border-green-400' : 'text-zinc-400 hover:text-zinc-300'}`}
          onClick={() => setActiveTab('search')}
        >
          Busca
        </button>
        <button
          className={`flex-1 py-3 text-sm font-medium ${activeTab === 'history' ? 'text-green-400 border-b-2 border-green-400' : 'text-zinc-400 hover:text-zinc-300'}`}
          onClick={() => setActiveTab('history')}
        >
          Histórico
        </button>
      </div>

      {/* Conteúdo */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 'search' ? (
          <>
            {/* Campo de busca */}
            <div className="relative mb-4">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-4 w-4 text-zinc-400" />
              </div>
              <input
                type="text"
                className="block w-full pl-10 pr-12 py-2 border border-zinc-700 bg-zinc-800/50 rounded-lg text-white placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Buscar por CNPJ, nome ou endereço..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <div className="absolute inset-y-0 right-0 flex items-center pr-2">
                {searchTerm && (
                  <button
                    onClick={handleClearSearch}
                    className="p-1 text-zinc-400 hover:text-white rounded-md"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>

            {/* Botão de busca */}
            <button
              onClick={handleSearch}
              disabled={isSearching || !searchTerm.trim()}
              className="w-full py-2 px-4 bg-green-600 hover:bg-green-700 disabled:bg-zinc-700 disabled:cursor-not-allowed rounded-lg text-white font-medium transition-colors flex items-center justify-center gap-2 mb-6"
            >
              {isSearching ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Buscando...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  Buscar na Base ANEEL
                </>
              )}
            </button>

            {/* Resultados da busca */}
            {searchResults.length > 0 && !selectedLead && (
              <div className="mb-6">
                <h4 className="text-sm font-medium text-zinc-300 mb-3">
                  {searchResults.length} resultado(s) encontrado(s)
                </h4>
                <div className="space-y-3">
                  {searchResults.map((result) => (
                    <div 
                      key={result.id}
                      onClick={() => handleSelectLead(result)}
                      className="p-3 border border-zinc-800 rounded-lg bg-zinc-800/30 hover:bg-zinc-800/50 cursor-pointer transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <h5 className="font-medium text-white">{result.razaoSocial}</h5>
                          <p className="text-xs text-zinc-400">{result.nomeFantasia}</p>
                          <p className="text-xs text-zinc-400 mt-1">{result.cnpj}</p>
                        </div>
                        <div className="text-xs bg-green-900/30 text-green-400 px-2 py-1 rounded-full">
                          {result.distribuidora}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Detalhes do lead selecionado */}
            {selectedLead && (
              <div className="bg-zinc-800/30 border border-zinc-800 rounded-xl p-4 mb-4">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-semibold text-white">Detalhes do Lead</h4>
                  <button 
                    onClick={() => setSelectedLead(null)}
                    className="p-1 text-zinc-400 hover:text-white rounded-md"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                <div className="space-y-4">
                  <div>
                    <h5 className="text-sm font-medium text-zinc-300 mb-2 flex items-center gap-2">
                      <Building className="w-4 h-4 text-green-400" />
                      Informações da Empresa
                    </h5>
                    <div className="grid grid-cols-1 gap-2 text-sm">
                      <div>
                        <span className="text-zinc-400">Razão Social:</span>
                        <p className="text-white">{selectedLead.razaoSocial}</p>
                      </div>
                      <div>
                        <span className="text-zinc-400">Nome Fantasia:</span>
                        <p className="text-white">{selectedLead.nomeFantasia}</p>
                      </div>
                      <div>
                        <span className="text-zinc-400">CNPJ:</span>
                        <p className="text-white">{selectedLead.cnpj}</p>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h5 className="text-sm font-medium text-zinc-300 mb-2 flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-green-400" />
                      Localização
                    </h5>
                    <div className="text-sm">
                      <span className="text-zinc-400">Endereço:</span>
                      <p className="text-white">{selectedLead.endereco}</p>
                      <div className="grid grid-cols-1 gap-2 mt-2">
                        <div>
                          <span className="text-zinc-400">Distribuidora:</span>
                          <p className="text-white">{selectedLead.distribuidora}</p>
                        </div>
                        <div>
                          <span className="text-zinc-400">Submercado:</span>
                          <p className="text-white">{selectedLead.submercado}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h5 className="text-sm font-medium text-zinc-300 mb-2 flex items-center gap-2">
                      <Zap className="w-4 h-4 text-green-400" />
                      Dados Energéticos
                    </h5>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="text-zinc-400">Consumo Médio:</span>
                        <p className="text-white">{selectedLead.consumoMedio.toLocaleString('pt-BR')} kWh</p>
                      </div>
                      <div>
                        <span className="text-zinc-400">Demanda Contratada:</span>
                        <p className="text-white">{selectedLead.demandaContratada} kW</p>
                      </div>
                    </div>
                  </div>

                  {selectedLead.contato && (
                    <div>
                      <h5 className="text-sm font-medium text-zinc-300 mb-2 flex items-center gap-2">
                        <User className="w-4 h-4 text-green-400" />
                        Contato
                      </h5>
                      <div className="grid grid-cols-1 gap-2 text-sm">
                        <div>
                          <span className="text-zinc-400">Nome:</span>
                          <p className="text-white">{selectedLead.contato.nome}</p>
                        </div>
                        <div>
                          <span className="text-zinc-400">Email:</span>
                          <p className="text-white">{selectedLead.contato.email}</p>
                        </div>
                        <div>
                          <span className="text-zinc-400">Telefone:</span>
                          <p className="text-white">{selectedLead.contato.telefone}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="flex justify-between items-center pt-3 border-t border-zinc-800">
                    <span className="text-xs text-zinc-400">
                      Última atualização: {selectedLead.ultimaAtualizacao}
                    </span>
                    <button className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-xs text-white font-medium">
                      Adicionar ao CRM
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Ajuda/Instruções */}
            {!searchResults.length && !selectedLead && !isSearching && (
              <div className="bg-zinc-800/30 border border-zinc-800 rounded-xl p-4 mt-6">
                <h4 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-green-400" />
                  Como usar o Detective ANEEL
                </h4>
                <ul className="text-xs text-zinc-400 space-y-2">
                  <li className="flex items-start gap-2">
                    <div className="mt-1 w-1.5 h-1.5 rounded-full bg-green-400 flex-shrink-0"></div>
                    <span>Digite CNPJ, nome da empresa ou endereço para buscar</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="mt-1 w-1.5 h-1.5 rounded-full bg-green-400 flex-shrink-0"></div>
                    <span>Clique em um resultado para ver detalhes completos</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="mt-1 w-1.5 h-1.5 rounded-full bg-green-400 flex-shrink-0"></div>
                    <span>Adicione leads relevantes diretamente ao CRM</span>
                  </li>
                </ul>
              </div>
            )}
          </>
        ) : (
          /* Aba de Histórico */
          <div>
            <h4 className="text-sm font-medium text-zinc-300 mb-4">Buscas Recentes</h4>
            <div className="space-y-3">
              <div className="p-3 border border-zinc-800 rounded-lg bg-zinc-800/30">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-white text-sm">12.345.678/0001-90</span>
                  <span className="text-xs text-zinc-400">15/11/2023</span>
                </div>
                <p className="text-xs text-zinc-400">Empresa Exemplo Ltda</p>
              </div>
              <div className="p-3 border border-zinc-800 rounded-lg bg-zinc-800/30">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-white text-sm">Av. Paulista</span>
                  <span className="text-xs text-zinc-400">10/11/2023</span>
                </div>
                <p className="text-xs text-zinc-400">3 resultados encontrados</p>
              </div>
              <div className="p-3 border border-zinc-800 rounded-lg bg-zinc-800/30">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-white text-sm">Comércio de Energia</span>
                  <span className="text-xs text-zinc-400">05/11/2023</span>
                </div>
                <p className="text-xs text-zinc-400">2 resultados encontrados</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}