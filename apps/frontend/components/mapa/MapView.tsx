'use client';

import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import Map, {NavigationControl} from 'react-map-gl';

// estilo público gratuito (Stadia Maps Positron GL). Pode trocar por outro:
const MAP_STYLE =
  'https://tiles.stadiamaps.com/styles/alidade_smooth_dark.json';

export default function MapView() {
  return (
    <Map
      mapLib={maplibregl}          
      mapStyle={MAP_STYLE}
      initialViewState={{longitude: -51.23, latitude: -30.02, zoom: 11}}
      style={{width: '100%', height: '100%'}}
    >
      <NavigationControl position="top-left" />
      {/* markers, layers… */}
    </Map>
  );
}
