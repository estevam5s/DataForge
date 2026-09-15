// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/plataforma.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Url",
  description: "Endereços: ler em partes, montar de volta, resolver relativo e escapar o que precisa ser escapado.",
};

const blocos: Bloco[] = [
  {"p": "Todo programa que fala HTTP mexe com URL, e a linguagem não tinha onde. O Kiln partia a query string por dentro para entregar `req[\"query\"]`, e o `Arcane.Http` montava endereço concatenando texto — nada disso estava ao alcance de quem escreve."},
  { code: `adopt Arcane.Url as U

p := U.ler("https://loja.com/itens?pagina=2&q=caf%C3%A9#topo")
out p["host"]        // loja.com
out p["query"]       // {pagina: 2, q: café}
out p["porta"]       // void — a URL não disse`, lang: 'df' },
  {"h2": "Por que não dá para fazer com split"},
  {"p": "Dois bugs conhecidos: o `?` que também aparece **dentro** de um valor, e o acento que precisa virar `%C3%A9` — e não virava. Escapar à mão erra na primeira busca com espaço."},
  { code: `U.escapar("/itens/ação nova")      // /itens/a%C3%A7%C3%A3o%20nova
U.escapar_tudo("/itens/ação")      // %2Fitens%2Fa%C3%A7%C3%A3o
U.desescapar("caf%C3%A9+quente")   // café quente`, lang: 'df' },
  {"h2": "A chave que repete"},
  {"p": "`?tag=a&tag=b` é legítimo e comum em filtro de busca, e um vault não guarda as duas. `query` devolve a **última** (o que quase todo servidor usa) e `query_lista` devolve as duas — a diferença está escrita, em vez de virar surpresa."},
  { code: `p := U.ler("https://a.com/b?tag=a&tag=b")
out p["query"]["tag"]         // b
out p["query_lista"]["tag"]   // [a, b]`, lang: 'df' },
  {"h2": "Montar, e paginar"},
  {"p": "`montar` é o contrário de `ler`, e recusa campo que não conhece: `caminh` montaria um endereço **sem caminho**, sem nada denunciando. `com_query` troca um parâmetro e preserva os outros — é o que se faz para paginar —, e `void` ali **apaga** o parâmetro, como se tira um filtro."},
  { code: `U.montar({"esquema": "https", "host": "a.com", "caminho": "/b",
          "query": {"q": "com espaço", "tags": ["p", "q"]}})
// https://a.com/b?q=com+espa%C3%A7o&tags=p&tags=q

U.com_query("https://a.com/l?pagina=1&q=z", {"pagina": 3})
// https://a.com/l?pagina=3&q=z

U.com_query("https://a.com/l?pagina=1&q=z", {"q": void})
// https://a.com/l?pagina=1

U.juntar("https://a.com/doc/x", "../y")     // https://a.com/y`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "A porta é Integer, e a origem não leva senha", "texto": "A porta vem de texto na URL, e devolvê-la como texto faria `porta + 1` **concatenar** em vez de somar. Sem porta, `void` — e não 80, que seria inventar o que a URL não disse. E `origem` traz só esquema, host e porta: ela vai para log e para cabeçalho de CORS, e a senha de `https://ana:s3nha@a.com` vazaria por ali sem ninguém pedir."}},
];

const headings = [{ id: 'por-que-nao-da-para-fazer-com-split', text: "Por que não dá para fazer com split", level: 2 as const }, { id: 'a-chave-que-repete', text: "A chave que repete", level: 2 as const }, { id: 'montar-e-paginar', text: "Montar, e paginar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Url"}
      description={"Endereços: ler em partes, montar de volta, resolver relativo e escapar o que precisa ser escapado."}
      href={"/docs/biblioteca/url"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
