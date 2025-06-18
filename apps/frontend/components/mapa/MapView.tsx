'use client';

import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { MapPin } from 'lucide-react';
import {Lead} from '@/app/types/lead';
import { useRouter } from 'next/navigation'; 
import { MapRef } from 'react-map-gl/maplibre';
import { useEffect, useRef } from 'react';

import Map, {
  Marker,
  Popup,
  NavigationControl,
} from 'react-map-gl/maplibre';

import {useState} from 'react';

type Props = {
  leads: Lead[];
  selectedId?: number | null;
};

const MAP_STYLE =
  'https://tiles.stadiamaps.com/styles/alidade_smooth_dark.json';

export default function MapView({leads, selectedId}: Props) {
  const [selecionado, setSelecionado] = useState<Lead | null>(null);
  const router = useRouter();
  const [mapReady, setMapReady]       = useState(false);
  const mapRef = useRef<MapRef>(null);
    useEffect(() => {
     if (!mapReady || selectedId == null) return; 

    const alvo = leads.find(l => (l.id) === +selectedId);
    if (!alvo) return;

    // centraliza e faz zoom suave
    mapRef.current?.flyTo({
      center: [alvo.lng, alvo.lat],
      zoom:   12,
      duration: 1000,
    });

    setSelecionado(alvo);       // abre o popup
  }, [mapReady,selectedId, leads]);

  return (
    <Map
      ref={mapRef}
      mapLib={maplibregl}
      mapStyle={MAP_STYLE}
      initialViewState={{longitude: -51.23, latitude: -30.02, zoom: 11}}
      style={{width: '100%', height: '100%'}}
      onLoad={() => setMapReady(true)}
    >
      <NavigationControl position="top-left" />

     {leads.map((l) => (
    <Marker
      key={l.id}
      longitude={l.lng}
      latitude={l.lat}
      anchor="bottom"
      draggable={false}
    >
    <div
      onMouseEnter={() => setSelecionado(l)}
      onMouseLeave={() => setSelecionado(null)}
      onClick={() => router.push(`/leads?id=${l.id}`)}    
      className="cursor-pointer"           
    >
      <MapPin className="w-6 h-6 text-red-600 drop-shadow-lg" />
      </div>
    </Marker>
  ))}
      {selecionado && (
        <Popup
          longitude={selecionado.lng}
          latitude={selecionado.lat}
          anchor="top"
          closeButton={false}
          offset={[0, 10]}
        >
          <p className="text-sm font-semibold">{selecionado.nome}</p>
          <p className="text-xs text-gray-500">ID: {selecionado.id}</p>
          <p className="text-xs text-gray-500">Dic: {selecionado.dicMed}</p>
          <p className="text-xs text-gray-500">Fic: {selecionado.ficMed}</p>
          <p className="text-xs text-gray-500">CNAE: {selecionado.CNAE}</p>
          <p className="text-xs text-gray-500">Estado: {selecionado.estado}</p>
          <p className="text-xs text-gray-500">Descrição: {selecionado.descricao}</p>
        </Popup>
      )}
    </Map>
  );
}
