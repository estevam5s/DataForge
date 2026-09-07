import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "cache",
  description: "Cache: memoização, TTL e LRU, com estatísticas de acerto.",
};

const blocos: Bloco[] = [
  { code: `dataforge add cache`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"], ["Exporta", "7 símbolos"]]}},
  {"h2": "Por que existe"},
  {"p": "Todo cache é uma aposta: gastar memória para não gastar tempo. As três estratégias aqui diferem no que fazem quando a memória acaba — nada, expirar por tempo, ou descartar o menos usado."},
  {"h2": "Uso"},
  { code: `adopt cache as K

lento := lambda n => n * n
rapido := K.memoizar(lento)
out rapido(9)      // calcula
out rapido(9)      // devolve o guardado`, lang: 'df' },
  {"h2": "API"},
  {"p": "O que `relay` exporta — 7 símbolos:"},
  { code: `blueprint Memo
blueprint CacheTTL
blueprint LRU
memoizar(acao, limite := 0)
memo_com_estatisticas(acao, limite := 0)
ttl(segundos := 60.0)
lru(limite := 100)`, lang: 'df' },
  {"h2": "Instalar"},
  { code: `dataforge add cache
dataforge add cache@1.0.0
dataforge add cache@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'uso', text: "Uso", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"cache"}
      description={"Cache: memoização, TTL e LRU, com estatísticas de acerto."}
      href={"/docs/pacotes/cache"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
