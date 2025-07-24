'use client'

import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { MapPin, ChevronRight, Info, Crosshair } from 'lucide-react'
import { Lead } from '@/app/types/lead'
import { useRouter } from 'next/navigation'
import { MapRef } from 'react-map-gl/maplibre'
import { useEffect, useRef, useState } from 'react'
import { clsx } from 'clsx'
import Map, { Marker, Popup, NavigationControl, GeolocateControl } from 'react-map-gl/maplibre'

type Props = {
  leads: Lead[]
  selectedId?: string | null
}

const MAP_STYLE = 'https://tiles.stadiamaps.com/styles/alidade_smooth_dark.json'

type LeadComCoords = Lead & { lat: number; lng: number }

export default function MapView({ leads, selectedId }: Props) {
  const [pontos, setPontos] = useState<LeadComCoords[]>([])
  const [selecionado, setSelecionado] = useState<LeadComCoords | null>(null)
  const [loading, setLoading] = useState(true)
  const mapRef = useRef<MapRef>(null)
  const router = useRouter()

  useEffect(() => {
    async function carregarPontos() {
      setLoading(true)
      
      const leadsValidos = leads.filter((l) => !!l.cep)
      const pontos: LeadComCoords[] = leadsValidos
        .filter((l) => l.latitude !== undefined && l.longitude !== undefined)
        .map((l) => ({ 
          ...l, 
          lat: Number(l.latitude), 
          lng: Number(l.longitude),
        }))

      setPontos(pontos)
      setLoading(false)

      // Se houver um lead selecionado, centraliza o mapa nele
      if (selectedId) {
        const leadSelecionado = pontos.find(l => l.id === selectedId)
        if (leadSelecionado) {
          setTimeout(() => {
            mapRef.current?.flyTo({
              center: [leadSelecionado.lng, leadSelecionado.lat],
              zoom: 14
            })
          }, 500)
        }
      }
    }

    carregarPontos()
  }, [leads, selectedId])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-900">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="mt-4 text-gray-300">Carregando mapa...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="relative h-full w-full">
      <Map
        ref={mapRef}
        mapLib={maplibregl}
        mapStyle={MAP_STYLE}
        initialViewState={{ longitude: -51.23, latitude: -30.02, zoom: 5 }}
        style={{ width: '100%', height: '100%' }}
        attributionControl={false}
      >
        <NavigationControl 
          position="top-left" 
          showCompass={false}
          visualizePitch={false}
        />
        
        <GeolocateControl
          position="top-left"
          trackUserLocation={true}
          showUserLocation={true}
          showAccuracyCircle={false}
          style={{ marginTop: '50px' }}
        />

        {pontos.map((l) => (
          <Marker
            key={l.id}
            longitude={l.lng}
            latitude={l.lat}
            anchor="bottom"
          >
            <div
              onMouseEnter={() => setSelecionado(l)}
              onMouseLeave={() => setSelecionado(null)}
              onClick={() => router.push(`/leads?id=${l.id}`)}
              className="cursor-pointer transform transition-transform hover:scale-125"
            >
              <div className="relative">
                <MapPin
                  className={clsx(
                    'w-7 h-7 drop-shadow-lg transition-all',
                    l.id === selectedId 
                      ? 'text-lime-400 fill-lime-400 scale-125' 
                      : 'text-red-500 fill-red-500 hover:fill-red-400 hover:text-red-400'
                  )}
                />
                {l.id === selectedId && (
                  <div className="absolute -top-2 -right-2 bg-lime-400 rounded-full w-4 h-4 flex items-center justify-center">
                    <span className="text-xs font-bold text-gray-900">✓</span>
                  </div>
                )}
              </div>
            </div>
          </Marker>
        ))}

        {selecionado && (
          <Popup
            longitude={selecionado.lng}
            latitude={selecionado.lat}
            anchor="bottom"
            closeButton={false}
            offset={[0, -10]}
            className="custom-popup"
            onClose={() => setSelecionado(null)}
          >
            <div className="max-w-xs p-2">
              <h3 className="font-bold text-gray-900 truncate">
                {selecionado.descricao || 'Lead sem nome'}
              </h3>
              
              <div className="mt-2 space-y-1 text-sm text-gray-700">
                <div className="flex items-start">
                  <Info className="w-4 h-4 mr-2 mt-0.5 text-gray-500 flex-shrink-0" />
                  <div>
                    <p className="font-medium">DIC: <span className="font-normal">{selecionado.dicMed || 'N/A'}</span></p>
                    <p className="font-medium">FIC: <span className="font-normal">{selecionado.ficMed || 'N/A'}</span></p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <Crosshair className="w-4 h-4 mr-2 mt-0.5 text-gray-500 flex-shrink-0" />
                  <div>
                    <p className="font-medium">CNAE: <span className="font-normal">{selecionado.cnae || 'N/A'}</span></p>
                    <p className="font-medium">Estado: <span className="font-normal">{selecionado.estado || 'N/A'}</span></p>
                  </div>
                </div>
                
                <p className="font-medium">Distribuidora: <span className="font-normal">{selecionado.distribuidora || 'N/A'}</span></p>
              </div>
              
              <button
                onClick={() => router.push(`/leads?id=${selecionado.id}`)}
                className="mt-3 w-full flex items-center justify-between px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-md transition-colors"
              >
                Ver detalhes
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </Popup>
        )}
      </Map>

      <div className="absolute bottom-4 left-4 bg-gray-900 bg-opacity-70 text-white text-xs px-3 py-2 rounded-md">
        {pontos.length} leads no mapa
      </div>
    </div>
  )
}