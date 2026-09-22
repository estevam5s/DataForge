import type { Metadata } from 'next';
import { Roadmap } from '@/components/roadmap/Roadmap';

export const dynamic = 'force-static';

export const metadata: Metadata = {
  title: 'Roadmap — DataForge',
  description:
    'O mapa da linguagem: as dez fases de um arquivo, os 41 componentes do ecossistema com o veredito de cada um, os 83 módulos da biblioteca e sete trilhas para seguir. Em três dimensões, e conferido contra o código.',
  alternates: { canonical: '/roadmap' },
  openGraph: {
    title: 'Roadmap — DataForge',
    description:
      'As dez fases, os 41 componentes conferidos contra o disco, os 83 módulos e sete trilhas.',
    url: '/roadmap',
  },
};

export default function Pagina() {
  return <Roadmap />;
}
