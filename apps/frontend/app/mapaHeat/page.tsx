'use client';

import dynamic from 'next/dynamic';
import { Flame, Info, Layers, RefreshCw, Download } from 'lucide-react';
import { useState } from 'react';

const MapaHeat = dynamic(() => import('@/components/mapa/MapaHeat'), {
  ssr: false,
  loading: () => (
    <div className="h-[600px] flex items-center justify-center bg-zinc-900 rounded-lg">
      <div className="text-center">
        <div className="inline-flex items-center gap-2 mb-4">
          <RefreshCw className="animate-spin" />
          <span>Carregando mapa...</span>
        </div>
      </div>
    </div>
  )
});

export default function MapaHeatPage() {
  const [showInfo, setShowInfo] = useState(false);
  const [activeTab, setActiveTab] = useState('heatmap');

  return (
    <section className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-white flex items-center gap-3">
            <Flame size={28} className="text-orange-400" /> 
            <span>Mapa de Calor de DIC Médio</span>
          </h1>
          <p className="text-zinc-400 mt-1">
            Visualização geográfica da distribuição de leads por intensidade de DIC
          </p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => setShowInfo(!showInfo)}
            className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-lg transition-colors"
          >
            <Info size={18} />
            <span>Informações</span>
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
            <Download size={18} />
            <span>Exportar</span>
          </button>
        </div>
      </div>

      {showInfo && (
        <div className="bg-zinc-800/80 border border-zinc-700 rounded-xl p-4 animate-fade-in">
          <h2 className="font-semibold text-lg text-white mb-2">Sobre este mapa</h2>
          <div className="grid md:grid-cols-2 gap-4 text-zinc-300 text-sm">
            <div>
              <p className="mb-2">
                Este mapa de calor representa a concentração geográfica de leads com base no 
                <strong className="text-orange-400"> DIC Médio </strong>.
              </p>
              <p>
                Áreas mais quentes (vermelhas) indicam maior concentração de leads com DIC elevado.
              </p>
            </div>
            <div>
              <ul className="space-y-2">
                <li className="flex items-start">
                  <span className="inline-block w-4 h-4 bg-blue-500 rounded-full mt-1 mr-2"></span>
                  <span>Azul: Baixa concentração/intensidade</span>
                </li>
                <li className="flex items-start">
                  <span className="inline-block w-4 h-4 bg-yellow-500 rounded-full mt-1 mr-2"></span>
                  <span>Amarelo: Média concentração/intensidade</span>
                </li>
                <li className="flex items-start">
                  <span className="inline-block w-4 h-4 bg-red-500 rounded-full mt-1 mr-2"></span>
                  <span>Vermelho: Alta concentração/intensidade</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      )}

      <div className="bg-zinc-900 border border-zinc-700 rounded-xl overflow-hidden">
        <div className="flex border-b border-zinc-700">
          <button
            className={`px-6 py-3 font-medium flex items-center gap-2 ${activeTab === 'heatmap' ? 'text-orange-400 border-b-2 border-orange-400' : 'text-zinc-400 hover:text-zinc-300'}`}
            onClick={() => setActiveTab('heatmap')}
          >
            <Flame size={18} />
            Mapa de Calor
          </button>
          {/* <button
            className={`px-6 py-3 font-medium flex items-center gap-2 ${activeTab === 'points' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-zinc-400 hover:text-zinc-300'}`}
            onClick={() => setActiveTab('points')}
          >
            <Layers size={18} />
            Visualização por Pontos
          </button> */}
        </div>
        
        <div className="p-1">
          <MapaHeat />
        </div>
      </div>

      <div className="bg-zinc-900 border border-zinc-700 rounded-xl p-4 text-sm text-zinc-400">
        <div className="flex flex-wrap gap-4 justify-between">
          <div>
            <h3 className="font-medium text-zinc-300 mb-1">Atualização</h3>
            <p>Dados atualizados em: {new Date().toLocaleDateString()}</p>
          </div>
          <div>
            <h3 className="font-medium text-zinc-300 mb-1">Fonte</h3>
            <p>Sistema de Leads - {new Date().getFullYear()}</p>
          </div>
          <div>
            <h3 className="font-medium text-zinc-300 mb-1">Notas</h3>
            <p>Zoom e navegação disponíveis</p>
          </div>
        </div>
      </div>
    </section>
  );
}