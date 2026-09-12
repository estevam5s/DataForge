// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/vitrine.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Vitrine",
  description: "Um programa de cima para baixo vira uma página web. Sem HTML, sem JavaScript, sem separar o que calcula do que mostra.",
};

const blocos: Bloco[] = [
  {"p": "**Vitrine** é o framework de painéis e aplicações de dados do DataForge. Você escreve um programa de cima para baixo; ele vira uma página web."},
  { code: `adopt Arcane.Vitrine as V

action painel():
    V.titulo("Vendas")
    regiao := V.escolha("Região", ["Sul", "Sudeste", "Norte"])
    V.metrica("Receita", "R$ 128.400", variacao := 12.5)
    V.grafico_barras(vendas_de(regiao), x := "mes")

V.rodar(painel, porta := 8501)`, lang: 'df' },
  {"p": "Isso é a aplicação inteira. Não há HTML, não há CSS, não há JavaScript, não há build, e não há separação entre o que calcula e o que mostra."},
  {"h2": "O modelo de execução"},
  {"p": "A cada interação, **o programa inteiro roda de novo** — e o estado da sessão sobrevive."},
  { code: `clique  →  o programa roda do começo  →  a árvore vira HTML  →  a tela troca
              ↑                                                      │
              └──────────  o estado da sessão continua  ─────────────┘`, lang: 'text' },
  {"p": "Parece desperdício e é o contrário. Quem escreve nunca pensa em callback, em diffing, nem em qual pedaço da tela atualizar: a linha de cima sempre aconteceu antes da linha de baixo, como em qualquer programa."},
  {"p": "É por isso que um componente **devolve** o que quem escreve precisa. `V.botao(…)` devolve `yes` ou `no`; `V.entrada(…)` devolve o texto digitado. A linha seguinte já usa o valor:"},
  { code: `given V.botao("Salvar"):
    salvar(V.entrada("Nome"))
    V.sucesso("Pronto.")`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O preço", "texto": "A página precisa ser rápida o bastante para rodar a cada clique. Daí o [`V.cache`](/docs/vitrine/estado), que existe desde o primeiro dia e não como otimização posterior — e o [`V.formulario`](/docs/vitrine/componentes), para campos ligados a consulta pesada."}},
  {"h2": "Vitrine ou Kiln?"},
  {"p": "Os dois são frameworks web, e a escolha é clara:"},
  {"table": {"head": ["", "Kiln", "Vitrine"], "rows": [["Para", "sites e APIs", "painéis e aplicações de dados"], ["Você escreve", "rotas que devolvem o que quiser", "um programa de cima para baixo"], ["A página é", "um template que você controla", "a árvore que o programa montou"], ["Cliente", "o que você puser lá", "~4 KB, prontos"], ["Exemplo", "uma loja, uma API REST", "um dashboard, um formulário interno"]]}},
  {"p": "A Vitrine **roda sobre o Kiln**: HTTP, rotas, arquivos estáticos, sessão, cabeçalhos de segurança e REST já existiam lá, testados. Reimplementá-los criaria duas implementações do mesmo protocolo para divergirem. `V.montar()` devolve o app Kiln por baixo, e nele você acrescenta rota, REST ou middleware."},
  {"callout": {"tipo": "nota", "titulo": "Por que não se chama Stream", "texto": "`Arcane.Stream` já é o módulo de streaming de dados — tópicos, partições, offsets, grupos de consumo. Duas coisas chamadas Stream no mesmo `adopt` seria exatamente a ambiguidade que este projeto passa o tempo todo evitando. *Vitrine* é onde a peça pronta é exposta; o nome segue a metáfora da forja, como Kiln, Crucible e Forge."}},
  {"h2": "Um painel completo"},
  { code: `adopt Arcane.Vitrine as V

V.app("Business Intelligence", icone := "📊")

mark @V.cache
action vendas():
    yield Banco.consultar("SELECT mes, receita, meta FROM vendas")

action painel():
    lado := V.lateral()
    regiao := lado.escolha("Região", ["Sudeste", "Sul", "Norte"])

    V.titulo("Dashboard de Vendas", icone := "📊")

    colunas := V.colunas(4)
    colunas[0].metrica("Receita", "R$ 850.000", variacao := 18.0)
    colunas[1].metrica("Clientes", "12.450", variacao := 8.0)
    colunas[2].metrica("Pedidos", "32.500", variacao := 14.0)
    colunas[3].metrica("Conversão", "8.4%", variacao := 1.2)

    V.cabecalho("Evolução")
    V.grafico_linha(vendas(), x := "mes", y := ["receita", "meta"])

    V.cabecalho("Dados")
    V.frame(vendas())
    V.exportar_csv(vendas())

V.pagina("/", painel)
V.rodar(porta := 8501)`, lang: 'df' },
  {"p": "O arquivo que roda está em `examples/vitrine_dashboard.df`, e ele se testa sozinho:"},
  { code: `dataforge run examples/vitrine_dashboard.df              # os testes
dataforge run examples/vitrine_dashboard.df -- --servir  # no navegador`, lang: 'bash' },
  {"h2": "Zero dependência, inclusive no navegador"},
  {"p": "O gráfico é **SVG escrito no servidor**. O cliente são ~4 KB de JavaScript sem build e sem CDN — ele manda de volta o que o usuário fez e troca o miolo da página."},
  {"p": "Não é purismo: uma biblioteca de gráficos vinda de CDN quebra qualquer aplicação que rode em rede fechada, que é exatamente onde painel de dados costuma rodar. E SVG imprime, escala e é legível por leitor de tela."},
  {"h2": "Onde continuar"},
  {"cards": [{"href": "/docs/vitrine/componentes", "title": "Componentes", "meta": "texto, entrada, dados", "desc": "Os 40 componentes, o que cada um devolve e quando usar formulário."}, {"href": "/docs/vitrine/layout", "title": "Layout", "meta": "colunas, abas, cartões", "desc": "Por que a área é um objeto, e não um bloco de contexto."}, {"href": "/docs/vitrine/estado", "title": "Estado e cache", "meta": "sessão, global, TTL, LRU", "desc": "Os três lugares onde um valor mora, e quem enxerga cada um."}, {"href": "/docs/vitrine/graficos", "title": "Gráficos", "meta": "sete tipos, em SVG", "desc": "A forma curta e a construída, e o que os dados precisam parecer."}, {"href": "/docs/vitrine/paginas", "title": "Páginas e segurança", "meta": "rotas, login, permissões", "desc": "Multipágina, parâmetros de URL, autenticação e autorização."}, {"href": "/docs/vitrine/testes", "title": "Testes", "meta": "sem navegador", "desc": "A sonda clica, digita e pergunta — e o pedido HTTP sem socket."}, {"href": "/docs/vitrine/producao", "title": "Produção", "meta": "hot reload, métricas, plugins", "desc": "Subir, observar, e o que colocar na frente."}, {"href": "/docs/vitrine/referencia", "title": "Referência", "meta": "105 símbolos", "desc": "Tudo o que sai de `adopt Arcane.Vitrine`, em uma tabela."}]},
];

const headings = [{ id: 'o-modelo-de-execucao', text: "O modelo de execução", level: 2 as const }, { id: 'vitrine-ou-kiln', text: "Vitrine ou Kiln?", level: 2 as const }, { id: 'um-painel-completo', text: "Um painel completo", level: 2 as const }, { id: 'zero-dependencia-inclusive-no-navegador', text: "Zero dependência, inclusive no navegador", level: 2 as const }, { id: 'onde-continuar', text: "Onde continuar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Vitrine"}
      description={"Um programa de cima para baixo vira uma página web. Sem HTML, sem JavaScript, sem separar o que calcula do que mostra."}
      href={"/docs/vitrine"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
