// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/vitrine.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Painel profissional",
  description: "Indicadores, a grade que pagina no servidor, 27 tipos de gráfico e o fragmento que redesenha um pedaço só.",
};

const blocos: Bloco[] = [
  {"p": "Os componentes da página anterior montam um **relatório**. O que faz um **painel** é o que vem aqui: a faixa de indicadores, o bloco com título discreto, a tabela que pagina sem recarregar a tela, e os gráficos que respondem às perguntas que uma linha e uma barra não respondem."},
  {"callout": {"tipo": "dica", "titulo": "O exemplo roda", "texto": "`examples/vitrine_painel_financeiro.df` monta o painel inteiro desta página e confere o resultado com os próprios `assert`. Para ver no navegador: `dataforge run examples/vitrine_painel_financeiro.df -- --servir`."}},
  {"h2": "O indicador"},
  {"p": "`V.metrica` mostra um número. O **indicador** é o bloco de que um painel é feito: faixa de cor à esquerda, nota embaixo, meta com barra de progresso e uma série miúda ao fundo."},
  { code: `V.indicador("Patrimônio líquido", 1091947.91,
    formato := "moeda", cor := "aviso", variacao := 4.2,
    nota := "Total em ago/26")

V.indicador("Aportes", 8495.0,
    formato := "moeda", cor := "info", alvo := 12000.0,
    mini := [6200, 7100, 6800, 9300, 8495])`, lang: 'df' },
  {"p": "`V.indicadores` põe vários numa faixa que se ajusta sozinha à largura — quatro cartões numa tela larga, um no celular, sem ninguém escolher o número."},
  { code: `V.indicadores([
    {"rotulo": "Receita", "valor": 128400.0, "formato": "moeda"},
    {"rotulo": "Clientes", "valor": 2500, "variacao": 8.1},
    {"rotulo": "Churn", "valor": 2.4, "formato": "percentual", "cor": "erro"}])`, lang: 'df' },
  {"p": "Uma chave que não existe é **ignorada**, e não vira um cartão com o padrão: `formatto` seria um engano passando calado."},
  {"h2": "Malha e painel"},
  {"p": "`V.malha` quebra pela **largura**, e não pelo número de colunas: com `minimo := 260`, três painéis numa tela larga viram dois numa média e um no celular. O servidor não mede a tela, então quem decide é o CSS."},
  { code: `m := V.malha(3, minimo := 260)

carteira := m.painel("Balanceamento", subtitulo := "6 tipos", icone := "pizza")
carteira.grafico_rosca({"Ações": 303561.0, "Fundos": 377733.0})

fluxo := m.painel("Receitas × despesas", cor := "info")
fluxo.grafico_barras(movimento, x := "mes", y := ["receitas", "despesas"])`, lang: 'df' },
  {"p": "O título de um painel é pequeno e em caixa alta de propósito: num painel com doze blocos, o que precisa saltar é o **dado** — não doze títulos competindo com ele."},
  {"h2": "A barra do topo"},
  { code: `topo := V.barra_superior("Gestão financeira",
    subtitulo := "Cliente",
    itens := ["Dados", "Carteira", "Painel"],
    ativo := "Painel")

ano := topo.escolha("Período", ["2026", "2025"])`, lang: 'df' },
  {"p": "Ela devolve a área da **direita**, que é onde os filtros ficam. O seletor é lido ali e devolvido para quem chamou: o programa roda de cima para baixo, e a linha seguinte já usa o ano."},
  {"h2": "A grade"},
  {"p": "A `V.frame` ordena e filtra **no navegador**, com o que já está na tela: é instantâneo e mente sobre um conjunto de cem mil linhas, porque só as que vieram participam. A **grade** ordena, filtra e pagina **no servidor**, sobre o conjunto inteiro."},
  { code: `escolhidas := V.grade(pedidos,
    colunas := [
        V.coluna("cliente", "Cliente", largura := 240),
        V.coluna("total", "Total", tipo := "moeda"),
        V.coluna("margem", "Margem", tipo := "barra", maximo := 100),
        V.coluna("situacao", "Situação", tipo := "selo")],
    destacar := [V.regra("margem", "menor", 10, "erro")],
    totais := {"total": "soma"},
    selecionar := "varias",
    paginar := 25)

given len(escolhidas) bigger 0:
    V.exportar_csv(escolhidas, "selecionadas.csv")`, lang: 'df' },
  {"p": "A paginação vem **ligada** porque uma listagem sem teto é a forma mais comum de um painel travar: mil linhas viram mil vezes o custo de desenhar, a cada clique. `paginar := 0` a desliga."},
  {"table": {"head": ["Tipo de coluna", "O que ele desenha"], "rows": [["`texto`", "o valor como veio"], ["`moeda` · `numero` · `percentual` · `compacto`", "formatado em pt-BR, alinhado à direita"], ["`data`", "`2026-09-20` vira `20/09/2026`"], ["`barra` · `progresso`", "uma barra dentro da célula, com o valor ao lado"], ["`mini`", "uma série miúda — a coluna carrega um cluster"], ["`selo`", "uma etiqueta colorida; a cor sai do valor"], ["`link` · `imagem` · `logico`", "âncora, miniatura e ✓/—"]]}},
  {"p": "O formato é aplicado **na hora de desenhar**, nunca no dado: a coluna continua numérica, e é isso que permite ordenar por valor e somar o rodapé depois de a célula já dizer `R$ 1.091.947,91`."},
  {"h2": "O editor"},
  { code: `linhas := V.editor(precos, colunas := [
    V.coluna("produto", editavel := no),
    V.coluna("preco", tipo := "moeda")])

given V.botao("Salvar"):
    cycle linha in linhas:
        Banco.executar("UPDATE precos SET preco = ? WHERE produto = ?",
                       [linha["preco"], linha["produto"]])`, lang: 'df' },
  {"p": "O que sai é um cluster de vaults **novo** — o original não é tocado, como em `record`/`with`. E o valor volta **no tipo da coluna**: devolver `\"12\"` onde havia `12` faria a soma do rodapé concatenar, e o sintoma seria um total absurdo, não um erro."},
  {"h2": "Os 27 tipos de gráfico"},
  {"table": {"head": ["Para responder", "O gráfico"], "rows": [["quanto, ao longo do tempo", "`grafico_linha`, `grafico_area`, `grafico_area_empilhada`"], ["quanto, por categoria", "`grafico_barras`, `grafico_barras_h`, `grafico_pareto`"], ["de que isto é feito", "`grafico_pizza`, `grafico_rosca`, `grafico_treemap`, `grafico_barras_100`"], ["duas grandezas de escalas diferentes", "`grafico_combo` com `eixo_direito`"], ["de onde veio a diferença", "`grafico_cascata`"], ["quanto sobra em cada etapa", "`grafico_funil`"], ["estamos perto da meta?", "`medidor`, `grafico_bala`"], ["quando acontece", "`mapa_de_calor`, `grafico_calendario`"], ["como se distribui", "`histograma`, `grafico_caixa`"], ["um está ligado ao outro?", "`grafico_dispersao_xy`, `grafico_bolhas`"], ["comparar em vários critérios", "`grafico_radar`"], ["para onde foi", "`grafico_sankey`, `grafico_rede`"], ["quando cada coisa acontece", "`grafico_gantt`"], ["o mercado", "`grafico_velas`"], ["onde", "`grafico_mapa`"], ["a tendência ao lado de um número", "`mini_grafico`"]]}},
  { code: `g := V.grafico_combo(mes_a_mes, x := "mes",
    barras := ["receita", "despesa"],
    linhas := ["margem"],
    direita := ["margem"])`, lang: 'df' },
  {"p": "`direita` põe aquelas séries numa **segunda escala**. Sem ela, uma margem de 0 a 100 desenhada ao lado de uma receita de milhões vira uma linha colada no zero: o gráfico existe e não mostra nada."},
  {"h2": "Três decisões que o desenho toma por você"},
  {"p": "**A barra é ancorada no zero; a linha, não.** Numa barra o que significa é o comprimento, e cortar o eixo faz uma barra 3% maior parecer o dobro — o gráfico enganoso clássico. Numa linha o que significa é a posição: forçar o zero num patrimônio que vai de 1,02 a 1,13 milhão desenha uma reta horizontal, e a variação some."},
  {"p": "**`void` é um vão, não um zero.** A linha de um acumulado **para** no mês que ainda não aconteceu, em vez de despencar. Um gráfico que mostra uma queda de um milhão onde só falta o dado é pior que um gráfico que para: ele afirma um número."},
  {"p": "**O texto cresce quando o espaço encolhe.** O desenho é feito num sistema de 800 unidades e o CSS o encolhe para caber no bloco. Num painel de um terço da tela o fator é 0,45, e um rótulo de 11px chegaria ao olho com 5px. O layout informa a largura, e o desenho compensa."},
  {"h2": "Fragmento: redesenhar um pedaço"},
  { code: `f := V.fragmento("cotacoes", a_cada := 5)
f.metrica("Dólar", cotacao("USD"))
f.metrica("Euro", cotacao("EUR"))`, lang: 'df' },
  {"p": "Um clique dentro do fragmento ainda roda o programa inteiro no servidor — isso não muda —, mas a resposta carrega **só este pedaço**. A diferença aparece onde importa: o filtro da barra lateral não perde o foco, a rolagem da tabela ao lado não volta ao topo, e um gráfico pesado em outro canto não é redesenhado."},
  {"p": "A resposta volta a ser a página inteira quando houve falha, quando mais de um campo mudou, ou quando o fragmento saiu da árvore. Responder a página inteira sem precisar custa desempenho; responder um pedaço sem poder custa correção."},
  {"h2": "Conversa, situação e aviso"},
  { code: `pergunta := V.chat_entrada()
given pergunta is not void:
    V.guardar_no_chat("usuario", pergunta)
    V.guardar_no_chat("assistente", responder(pergunta))

cycle m in V.historico_de_chat():
    V.chat_mensagem(m["quem"], m["conteudo"])`, lang: 'df' },
  { code: `passo := V.status("Consultando o banco…")
passo.texto("1.200 linhas")
passo.concluir("Pronto")

V.toast("Salvo", nivel := "sucesso")`, lang: 'df' },
  {"p": "O `V.toast` não ocupa espaço no fluxo: é para confirmar o que acabou de acontecer sem empurrar o resto da tela para baixo. O `V.esqueleto` faz o contrário — ocupa o espaço do que ainda não chegou, para a página não saltar quando o dado chegar."},
  {"h2": "Conexão, recurso e segredo"},
  { code: `banco := V.conexao("vendas", arquivo := "dados/vendas.db")
linhas := banco.consultar("SELECT * FROM pedidos WHERE mes = ?",
                          [mes], validade := 300)`, lang: 'df' },
  {"p": "A conexão é **do processo**: chamar de novo com o mesmo nome devolve a mesma. Sem isso, cada execução da página abriria outra — o gargalo mais fácil de criar e o mais difícil de notar, porque cada abertura é rápida."},
  {"table": {"head": ["", "`V.cache`", "`V.recurso`"], "rows": [["guarda", "o **resultado** de um cálculo", "o **objeto** em si"], ["vence", "por validade, ou por teto", "nunca, enquanto o processo viver"], ["vai a disco", "pode", "não"], ["serve para", "consulta, API, agregação", "conexão, modelo, cliente"]]}},
  {"p": "A diferença não é de tamanho. Um cache com teto solta o menos usado; se a conexão do banco caísse fora por isso, a próxima página abriria outra e o pool do banco acabaria — o bug que faz um painel morrer só depois de uma hora no ar."},
  { code: `chave := V.segredo("OPENAI_API_KEY")
V.vault(V.segredos_mascarados())`, lang: 'df' },
  {"p": "O **ambiente vence o arquivo**: é assim que um deploy troca a senha sem reescrever nada. E `V.segredos_mascarados` mostra só os quatro últimos caracteres — o suficiente para conferir *qual* chave está configurada sem entregá-la a quem está olhando a tela junto."},
  {"h2": "Tema e densidade"},
  { code: `V.app("Painel", tema := "meia-noite", densidade := "compacta")`, lang: 'df' },
  {"p": "Seis temas prontos: `claro`, `escuro`, `meia-noite`, `oceano`, `contraste` e `papel`. Um tema escuro pedido **pelo nome** vale sempre — deixá-lo no automático faria o tema escolhido deixar de valer numa máquina configurada como clara."},
  {"p": "A densidade muda espaçamento e tamanho sem tocar em cor nenhuma. Um painel de operação cabe um terço mais de linha na mesma tela com `compacta`, e é a diferença entre rolar e não rolar."},
  {"h2": "Onde continuar"},
  {"cards": [{"href": "/docs/vitrine/graficos", "title": "Gráficos", "desc": "A forma curta, a construída, e por que SVG no servidor."}, {"href": "/docs/vitrine/referencia", "title": "Referência", "meta": "213 símbolos", "desc": "Tudo o que sai de `adopt Arcane.Vitrine`."}, {"href": "/docs/vitrine/producao", "title": "Produção", "desc": "Sessão entre processos, saúde e métricas."}, {"href": "/docs/vitrine/testes", "title": "Testar sem navegador", "desc": "A sonda clica, digita e pergunta."}]},
];

const headings = [{ id: 'o-indicador', text: "O indicador", level: 2 as const }, { id: 'malha-e-painel', text: "Malha e painel", level: 2 as const }, { id: 'a-barra-do-topo', text: "A barra do topo", level: 2 as const }, { id: 'a-grade', text: "A grade", level: 2 as const }, { id: 'o-editor', text: "O editor", level: 2 as const }, { id: 'os-27-tipos-de-grafico', text: "Os 27 tipos de gráfico", level: 2 as const }, { id: 'tres-decisoes-que-o-desenho-toma-por-voce', text: "Três decisões que o desenho toma por você", level: 2 as const }, { id: 'fragmento-redesenhar-um-pedaco', text: "Fragmento: redesenhar um pedaço", level: 2 as const }, { id: 'conversa-situacao-e-aviso', text: "Conversa, situação e aviso", level: 2 as const }, { id: 'conexao-recurso-e-segredo', text: "Conexão, recurso e segredo", level: 2 as const }, { id: 'tema-e-densidade', text: "Tema e densidade", level: 2 as const }, { id: 'onde-continuar', text: "Onde continuar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Painel profissional"}
      description={"Indicadores, a grade que pagina no servidor, 27 tipos de gráfico e o fragmento que redesenha um pedaço só."}
      href={"/docs/vitrine/painel"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
