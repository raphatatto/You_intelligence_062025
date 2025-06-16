'use client';

import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { MapPin } from 'lucide-react';
import {Lead} from '@/app/types/lead'; 


import Map, {
  Marker,
  Popup,
  NavigationControl,
} from 'react-map-gl/maplibre';

import {useState} from 'react';


type Props = {
  leads: Lead[];
};

const MAP_STYLE =
  'https://tiles.stadiamaps.com/styles/alidade_smooth_dark.json';

export default function MapView({leads}: Props) {
  const [selecionado, setSelecionado] = useState<Lead | null>(null);

  return (
    <Map
      mapLib={maplibregl}
      mapStyle={MAP_STYLE}
      initialViewState={{longitude: -51.23, latitude: -30.02, zoom: 11}}
      style={{width: '100%', height: '100%'}}
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
      onClick={() => setSelecionado(l)}    
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
          <p className="text-xs capitalize text-gray-500">
            {selecionado.status}
          </p>
        </Popup>
      )}
    </Map>
  );
}
