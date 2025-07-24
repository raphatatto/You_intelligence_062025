'use client';

import { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import type { FeatureCollection, Feature, Point } from 'geojson';
import { Loader2, Crosshair, Layers, Thermometer } from 'lucide-react';

const base = process.env.NEXT_PUBLIC_API_BASE ?? '';

export default function MapaHeat() {
  const mapRef = useRef<maplibregl.Map | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [heatmapVisible, setHeatmapVisible] = useState(true);
  const [pointCount, setPointCount] = useState(0);
  const geolocateRef = useRef<maplibregl.GeolocateControl | null>(null);

  useEffect(() => {
    const timeout = setTimeout(() => {
      if (!containerRef.current || mapRef.current) {
        console.log('⚠️ Mapa já inicializado ou container não disponível');
        return;
      }

      console.log('🗺️ Inicializando mapa...');

      const map = new maplibregl.Map({
        container: containerRef.current,
        style: 'https://tiles.stadiamaps.com/styles/alidade_smooth_dark.json',
        center: [-46.63, -23.55],
        zoom: 5.5,
        attributionControl: false
      });

      // Adiciona controles ao mapa
      map.addControl(new maplibregl.NavigationControl(), 'top-right');
      map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-left');
      
      const geolocate = new maplibregl.GeolocateControl({
        positionOptions: {
          enableHighAccuracy: true
        },
        trackUserLocation: true,
        showUserLocation: true,
        showAccuracyCircle: false
      });
      map.addControl(geolocate, 'top-right');
      geolocateRef.current = geolocate; 
      mapRef.current = map;

      map.on('load', async () => {
        try {
          console.log('📡 Mapa carregado! Buscando leads...');
          setLoading(true);
          const res = await fetch(`${base}/leads-geo`);

          if (!res.ok) throw new Error(`Erro na requisição: ${res.status}`);

          const leads = await res.json();
          console.log('✅ Leads carregados:', leads);

          const validLeads = leads.filter((l: any) =>
            typeof l.latitude === 'number' &&
            typeof l.longitude === 'number' &&
            !isNaN(l.latitude) &&
            !isNaN(l.longitude)
          );

          setPointCount(validLeads.length);

          const geojson: FeatureCollection<Point> = {
            type: 'FeatureCollection',
            features: validLeads.map((l: any): Feature<Point> => ({
              type: 'Feature',
              geometry: {
                type: 'Point',
                coordinates: [l.longitude, l.latitude],
              },
              properties: {
                peso: l.dicMed ?? 1,
                id: l.id,
                nome: l.nome,
                dicMed: l.dicMed,
                ficMed: l.ficMed
              },
            }))
          };

          map.addSource('leads', {
            type: 'geojson',
            data: geojson,
          });

          // Camada de heatmap
          map.addLayer({
            id: 'heatmap-leads',
            type: 'heatmap',
            source: 'leads',
            maxzoom: 14,
            paint: {
              'heatmap-weight': ['interpolate', ['linear'], ['get', 'peso'], 0, 0, 6, 1],
              'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 0, 1, 9, 3],
              'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 0, 2, 9, 20],
              'heatmap-opacity': 0.7,
              'heatmap-color': [
                'interpolate',
                ['linear'],
                ['heatmap-density'],
                0, 'rgba(33, 102, 172, 0)',
                0.2, 'rgb(103, 169, 207)',
                0.4, 'rgb(209, 229, 240)',
                0.6, 'rgb(253, 219, 199)',
                0.8, 'rgb(239, 138, 98)',
                1, 'rgb(178, 24, 43)'
              ],
            },
          });

          // Camada de pontos (opcional)
          map.addLayer({
            id: 'points-leads',
            type: 'circle',
            source: 'leads',
            minzoom: 10,
            paint: {
              'circle-radius': ['interpolate', ['linear'], ['zoom'], 10, 3, 14, 6],
              'circle-color': 'rgba(255, 255, 255, 0.3)',
              'circle-stroke-color': 'rgba(255, 255, 255, 0.5)',
              'circle-stroke-width': 0.5
            },
            filter: ['==', '$type', 'Point']
          });

          // Popup ao clicar nos pontos
          map.on('click', 'points-leads', (e) => {
            if (e.features && e.features.length > 0) {
              const feature = e.features[0];
              const coordinates = (feature.geometry as Point).coordinates.slice();
              const props = feature.properties || {};
              
              while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
              }
              
              new maplibregl.Popup()
                .setLngLat(coordinates as [number, number])
                .setHTML(`
                  <div class="popup-content">
                    <h3 class="font-bold">${props.nome || 'Lead sem nome'}</h3>
                    <div class="mt-1 text-sm">
                      <p><strong>DIC:</strong> ${props.dicMed || 'N/A'}</p>
                      <p><strong>FIC:</strong> ${props.ficMed || 'N/A'}</p>
                    </div>
                  </div>
                `)
                .addTo(map);
            }
          });

          // Muda o cursor ao passar sobre pontos
          map.on('mouseenter', 'points-leads', () => {
            map.getCanvas().style.cursor = 'pointer';
          });
          map.on('mouseleave', 'points-leads', () => {
            map.getCanvas().style.cursor = '';
          });

          console.log('✅ Camadas adicionadas com sucesso');
          setLoading(false);
        } catch (err) {
          console.error('❌ Erro no mapa de calor:', err);
          setError('Falha ao carregar dados do mapa');
          setLoading(false);
        }
      });
    }, 0);

    return () => {
      mapRef.current?.remove();
      console.log('🧹 Mapa desmontado');
      clearTimeout(timeout);
    };
  }, []);

  const toggleHeatmap = () => {
    if (mapRef.current) {
      const visibility = mapRef.current.getLayoutProperty('heatmap-leads', 'visibility');
      const newVisibility = visibility === 'visible' ? 'none' : 'visible';
      mapRef.current.setLayoutProperty('heatmap-leads', 'visibility', newVisibility);
      setHeatmapVisible(newVisibility === 'visible');
    }
  };

  return (
    <div className="relative w-full h-[600px] rounded-lg overflow-hidden border border-gray-700 shadow-xl">
      <div ref={containerRef} className="w-full h-full" />
      
      {/* Overlay de carregamento */}
      {loading && (
        <div className="absolute inset-0 bg-gray-900 bg-opacity-70 flex items-center justify-center z-10">
          <div className="text-center">
            <Loader2 className="w-12 h-12 animate-spin text-blue-400 mx-auto" />
            <p className="mt-4 text-white font-medium">Carregando mapa de calor...</p>
          </div>
        </div>
      )}
      
      {/* Mensagem de erro */}
      {error && (
        <div className="absolute inset-0 bg-gray-900 bg-opacity-70 flex items-center justify-center z-10">
          <div className="bg-red-900 text-white p-4 rounded-lg max-w-md text-center">
            <p className="font-bold">Erro ao carregar mapa</p>
            <p className="mt-2">{error}</p>
            <button 
              onClick={() => window.location.reload()}
              className="mt-3 px-4 py-2 bg-white text-red-900 rounded-md font-medium"
            >
              Tentar novamente
            </button>
          </div>
        </div>
      )}
      
      {/* Controles personalizados */}
      <div className="absolute top-4 right-4 z-10 space-y-2">
        <button
          onClick={toggleHeatmap}
          className={`p-2 rounded-full shadow-lg ${heatmapVisible ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300'}`}
          title={heatmapVisible ? 'Ocultar mapa de calor' : 'Mostrar mapa de calor'}
        >
          <Thermometer className="w-5 h-5" />
        </button>
        
         <button
            className="p-2 rounded-full bg-gray-800 text-gray-300 shadow-lg"
            title="Centralizar no usuário"
            onClick={() => {
              geolocateRef.current?.trigger();
            }}
          >
            <Crosshair className="w-5 h-5" />
          </button>
      </div>
      
      {/* Legenda */}
      <div className="absolute bottom-4 left-4 bg-gray-900 bg-opacity-70 text-white p-3 rounded-lg z-10">
        <div className="flex items-center mb-2">
          <Thermometer className="w-5 h-5 mr-2" />
          <h3 className="font-bold">Intensidade do Heatmap</h3>
        </div>
        <div className="flex items-center h-4 w-full mb-1">
          <div className="h-full w-full bg-gradient-to-r from-blue-500 via-yellow-500 to-red-500 rounded"></div>
        </div>
        <div className="flex justify-between text-xs">
          <span>Baixa</span>
          <span>Alta</span>
        </div>
        <div className="mt-2 text-sm">
          <p>{pointCount} pontos no mapa</p>
        </div>
      </div>
    </div>
  );
}