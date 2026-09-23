// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/faq.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Quando NÃO usar DataForge",
  description: "A pergunta honesta, respondida com a medida: onde a linguagem serve, onde ela custa caro e onde ela simplesmente não é a ferramenta.",
};

const blocos: Bloco[] = [
  {"p": "Toda linguagem tem uma resposta pronta para *por que me escolher*. Esta página é a outra. Ela existe porque a recomendação errada custa mais que a falta de recomendação — e porque quem descobre o limite em produção não volta."},
  {"h2": "Não use quando o trabalho é de CPU e o prazo é curto"},
  {"p": "DataForge é um **interpretador de árvore** escrito em Python, com compilação para fechamentos. Medido, de 1,5× a 1,8× mais rápido que a travessia de árvore pura — e ainda assim mais lento que o CPython, que já é mais lento que quase tudo."},
  {"table": {"head": ["Trabalho", "Resposta"], "rows": [["laço numérico apertado", "não — ou `adopt Python.numpy`, que roda vetorizado de verdade"], ["muitos núcleos, trabalho de CPU", "`P.map_processos` — medido 3,45× em 10 núcleos"], ["muitos núcleos, com `thread`", "**não**: o GIL continua no caminho, e a medida foi 0,97×"], ["rede, disco, banco", "sim — `async`/`await` sobrepõe de verdade"]]}},
  {"callout": {"tipo": "atencao", "titulo": "0,97× não é um número ruim, é o número certo", "texto": "Oito blocos de CPU em dez núcleos: série 1607 ms, threads 1654 ms. Threads **perderam** da série, porque o GIL serializa o trabalho e ainda cobra a troca de contexto. Quem espera ganho de `thread` em CPU vai medir isso mesmo."}},
  {"h2": "Não use como servidor público sem algo na frente"},
  {"p": "O Kiln roda sobre o `http.server` do Python. Ele **não tem TLS e não tem HTTP/2** — e isso não é uma pendência de roadmap, é uma decisão: refazer TLS em Python puro seria a pior escolha de segurança possível. Em produção pública, ponha um nginx ou um Caddy na frente."},
  {"p": "E ele atende **um pedido por thread**, sem sincronizar nada por você. Uma rota que lê, decide e escreve num estado em memória perde atualizações — medido: seis pedidos simultâneos entregaram **1 de 6**. O `check` avisa (`escrita-concorrente`), e a resposta é `Arcane.Concurrent`."},
  {"h2": "Não use onde o ecossistema é o produto"},
  {"p": "A biblioteca padrão tem 87 módulos e 2323 símbolos, sem uma única dependência externa. Isso cobre muito — e não cobre o PyTorch, o Kubernetes client, o driver do seu ERP. A ponte para o Python existe (`adopt Python.pandas as pd`) e é real, mas se **a maior parte** do seu sistema vai ser Python chamado de dentro, escreva em Python."},
  {"h2": "Não use se você precisa de um destes"},
  {"list": ["**Binário nativo** — não há backend LLVM, e não haverá: amarrar o LLVM tiraria a única propriedade inegociável do projeto, que é zero dependência externa.", "**Bare-metal / microcontrolador rodando a linguagem** — `Arcane.IoT` fala *com* a placa pela serial; a linguagem não roda *dentro* dela.", "**Aplicativo Android empacotado** — há PWA (`dataforge mobile pwa`), não há APK.", "**Alocador próprio** — o alocador é o do CPython. Há controle do **coletor** (`Arcane.Memoria`), que é outra coisa, e o projeto prefere nomear a diferença."]},
  {"h2": "Onde ela é uma boa escolha"},
  {"list": ["**Ferramenta interna** — CLI, script de dados, automação. `dataforge new` sai com testes, CI e `forge.toml`.", "**Painel de dados** — a Vitrine desenha o gráfico no servidor, em SVG, sem uma linha de CDN. É o que funciona em rede fechada.", "**Ensino** — a análise estática acusa antes de rodar, e as mensagens dizem o que fazer.", "**Prototipagem com hardware** — a placa vira periférico e o laço de trabalho passa a ser o do computador.", "**Sistema modular de verdade** — o `check` atravessa arquivos: `P.criar(1, 2, 3)` é acusado antes de rodar, mesmo vindo de outro `.df`."]},
  {"callout": {"tipo": "nota", "titulo": "A lista de ausências é conferida, não escrita", "texto": "`Arcane.Ecossistema.o_que_nao_existe()` responde em execução, e é **comparada com o disco** por um teste. Uma página que promete o que não existe reprova a suíte — foi assim que esta seção nasceu."}},
  {"cards": [{"href": "/docs/faq/producao", "title": "Pôr em produção", "desc": "o que falta, e o que pôr na frente"}, {"href": "/docs/faq/concorrencia", "title": "Concorrência", "desc": "thread, parallel, async e processos"}, {"href": "/docs/roadmap", "title": "Roadmap", "desc": "o mapa, com o que não existe"}]},
];

const headings = [{ id: 'nao-use-quando-o-trabalho-e-de-cpu-e-o-prazo-e-curto', text: "Não use quando o trabalho é de CPU e o prazo é curto", level: 2 as const }, { id: 'nao-use-como-servidor-publico-sem-algo-na-frente', text: "Não use como servidor público sem algo na frente", level: 2 as const }, { id: 'nao-use-onde-o-ecossistema-e-o-produto', text: "Não use onde o ecossistema é o produto", level: 2 as const }, { id: 'nao-use-se-voce-precisa-de-um-destes', text: "Não use se você precisa de um destes", level: 2 as const }, { id: 'onde-ela-e-uma-boa-escolha', text: "Onde ela é uma boa escolha", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Quando NÃO usar DataForge"}
      description={"A pergunta honesta, respondida com a medida: onde a linguagem serve, onde ela custa caro e onde ela simplesmente não é a ferramenta."}
      href={"/docs/faq/quando-nao-usar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
