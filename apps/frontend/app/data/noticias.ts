import type { Noticia } from '@/app/types/noticia';

export const noticias: Noticia[] = [
  {
    id: 'n1',
    titulo: 'ANEEL aprova novas regras de compensação de energia',
    resumo: 'Mudanças entram em vigor em julho e impactam geradores solares.',
    fonte: 'Valor Econômico',
    url: 'https://valor.globo.com/…',
    data: '2025-06-12',
    imagem: 'https://tse1.mm.bing.net/th/id/OIP.D_Tfomt2K5xiO8b_wkBInwHaFj?rs=1&pid=ImgDetMain&cb=idpwebpc1',
  },
  {
    id: 'n2',
    titulo: 'Investimento em baterias estacionárias cresce 40 % em 2025',
    resumo: 'Mercado brasileiro atrai fabricantes asiáticos.',
    fonte: 'Canal Energia',
    url: 'https://canalenergia.com.br/…',
    data: '2025-06-10',
  },
];
