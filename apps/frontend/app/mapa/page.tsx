import MapView from '@/components/mapa/MapView';
import type {Lead} from '../types/lead';

const leads: Lead[] = [
  {id: '1', nome: 'Acme Ltda', lng: -23.724198, lat: -46.714637, status: 'qualificado'},
  {id: '2', nome: 'Beta S.A.', lng: -51.18, lat: -30.05, status: 'novo'},
];

export default function MapaPage() {
  return (
    <div className="h-screen">
      <MapView leads={leads} />
    </div>
  );
}


//-23.724198, -46.714637