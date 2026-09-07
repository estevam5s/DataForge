import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "evento",
  description: "Eventos: publicar, assinar, uma vez só e barramento tipado.",
};

const blocos: Bloco[] = [
  { code: `dataforge add evento`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"], ["Exporta", "6 símbolos"]]}},
  {"h2": "Por que existe"},
  {"p": "Um barramento resolve o acoplamento: quem publica não precisa saber quem escuta. O preço é que o fluxo deixa de ser óbvio na leitura — use quando os ouvintes forem mesmo independentes."},
  {"h2": "Uso"},
  { code: `adopt evento as E

bus := E.barramento()
bus.assinar("pedido.criado", lambda p => out $"novo: {p}")
bus.publicar("pedido.criado", {"id": 1})`, lang: 'df' },
  {"h2": "API"},
  {"p": "O que `relay` exporta — 6 símbolos:"},
  { code: `blueprint Barramento
barramento(guardar_historico := no)
GLOBAL
assinar(nome, ouvinte)
publicar(nome, dado := void)
uma_vez_so(nome, ouvinte)`, lang: 'df' },
  {"h2": "Instalar"},
  { code: `dataforge add evento
dataforge add evento@1.0.0
dataforge add evento@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'uso', text: "Uso", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"evento"}
      description={"Eventos: publicar, assinar, uma vez só e barramento tipado."}
      href={"/docs/pacotes/evento"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
