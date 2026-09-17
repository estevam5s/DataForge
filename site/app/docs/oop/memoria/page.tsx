// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/oop_meta.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Ciclo de vida e memória",
  description: "Construção, teardown, referências fracas e o coletor: o que acontece com um objeto do spawn ao descarte.",
};

const blocos: Bloco[] = [
  {"h2": "Do spawn ao descarte"},
  {"list": ["`on_spawn` da metaclasse — pode entregar um objeto pronto;", "`__new__` — idem;", "os padrões dos campos, copiados quando mutáveis;", "os parâmetros do cabeçalho, com tipo e padrão;", "`setup` (ou `initiate`, ou `__init__`), e o corpo solto do blueprint;", "as invariantes e `on_ready`;", "…a vida do objeto…", "`teardown` (ou `__del__`) quando o último nome o solta."], "ordered": true},
  {"h2": "teardown"},
  {"p": "O DataForge roda sobre o CPython e herda o modelo de memória dele: cada objeto tem um **contador de referências** e morre no instante em que ele chega a zero. É por isso que `teardown` roda na hora, e não \"em algum momento\". Só os blueprints que declaram finalizador pagam por ele."},
  { code: `log := []

blueprint Arquivo(nome):
    action teardown():
        log.append($"fechou {self.nome}")

a := spawn Arquivo("dados.csv")
a := void
assert log is ["fechou dados.csv"]`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Para recurso, prefira with ou defer", "texto": "`teardown` depende de o último nome soltar o objeto — um objeto preso num ciclo espera o coletor. Arquivo, conexão e trava fecham melhor com `with` ou `defer`, que rodam num ponto conhecido do código."}},
  {"h2": "Referências fracas"},
  {"p": "Uma referência **fraca** aponta sem segurar. É o que um cache e um registro de observadores precisam — guardar o objeto enquanto ele existir, sem ser a razão de ele existir. Um cache com referência forte é o vazamento de memória mais comum que existe."},
  { code: `adopt Arcane.Memoria as Mem

blueprint Sessao:
    usuario := "ana"

s := spawn Sessao()
ref := Mem.fraca(s)
assert ref.viva()
assert ref.obter().usuario is "ana"

s := void
assert not ref.viva()
assert ref.obter() is void

cache := Mem.mapa_fraco()
chave := spawn Sessao()
cache.definir(chave, "dados caros")
assert cache.tamanho is 1
chave := void
assert cache.tamanho is 0`, lang: 'df' },
  {"h2": "O coletor"},
  {"table": {"head": ["Função", "O que responde"], "rows": [["`Mem.coletar()`", "força a coleta de ciclos; devolve quantos objetos soltou"], ["`Mem.vivos(Tipo)`", "quantas instâncias do blueprint (e das filhas) existem agora"], ["`Mem.tamanho(obj)`", "bytes aproximados do objeto e do que só ele alcança"], ["`Mem.referencias(obj)`", "o contador do CPython"], ["`Mem.ao_descartar(obj, acao)`", "roda a ação quando o objeto for coletado"], ["`Mem.estatisticas()`", "gerações, limiares e coletas"]]}},
  {"p": "Para economizar memória por objeto, `slots` guarda os campos numa lista em vez de num vault — ver [slots](/docs/oop/slots)."},
];

const headings = [{ id: 'do-spawn-ao-descarte', text: "Do spawn ao descarte", level: 2 as const }, { id: 'teardown', text: "teardown", level: 2 as const }, { id: 'referencias-fracas', text: "Referências fracas", level: 2 as const }, { id: 'o-coletor', text: "O coletor", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Ciclo de vida e memória"}
      description={"Construção, teardown, referências fracas e o coletor: o que acontece com um objeto do spawn ao descarte."}
      href={"/docs/oop/memoria"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
