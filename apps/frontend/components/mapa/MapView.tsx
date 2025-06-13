'use client';

import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { MapPin } from 'lucide-react';


import Map, {
  Marker,
  Popup,
  NavigationControl,
} from 'react-map-gl/maplibre';

import {useState} from 'react';

// ---------- tipos ----------
export type Lead = {
  id: string;
  nome: string;
  lng: number;
  lat: number;
  status: 'novo' | 'qualificado' | 'contato';
};

// ---------- props ----------
type Props = {
  leads: Lead[];
};

// ---------- style ----------
const MAP_STYLE =
  'https://tiles.stadiamaps.com/styles/alidade_smooth_dark.json';

// ---------- componente ----------
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
      onClick={() => setSelecionado(l)}
    >
      <MapPin className="w-6 h-6 text-red-600 drop-shadow-lg" />
    </Marker>
  ))}
      {selecionado && (
        <Popup
          longitude={selecionado.lng}
          latitude={selecionado.lat}
          anchor="top"
          onClose={() => setSelecionado(null)}
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
