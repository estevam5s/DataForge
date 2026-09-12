import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

// Gerado por tools/gerar_ref_vitrine.py — não edite à mão.

export const metadata: Metadata = {
  title: "Referência da Vitrine",
  description: "Os 105 símbolos do módulo, agrupados por assunto, com a assinatura extraída do código-fonte.",
};

const blocos: Bloco[] = [
  {
    "p": "Esta página é gerada a partir de `dataforge/stdlib/vitrine/`. São **105 símbolos**, e o gerador recusa rodar se algum deles ficar de fora."
  },
  {
    "p": "Em todos os exemplos, `V` é o apelido de `adopt Arcane.Vitrine as V`."
  },
  {
    "callout": {
      "tipo": "dica",
      "titulo": "Toda área tem os mesmos componentes",
      "texto": "Os grupos **Texto**, **Entrada**, **Dados**, **Retorno** e **Gráficos** também são métodos de qualquer área de layout — `coluna.metrica(…)`, `aba.frame(…)`, `lateral.escolha(…)`. Aprender um lugar ensina todos."
    }
  },
  {
    "h2": "Aplicação e servidor"
  },
  {
    "table": {
      "head": [
        "Símbolo",
        "Faz"
      ],
      "rows": [
        [
          "`V.app(titulo='Vitrine', **config)`",
          "Cria a aplicação e passa a ser a atual."
        ],
        [
          "`V.configurar(chave=None, valor=None, …)`",
          "Ajusta uma opção, ou várias por vault."
        ],
        [
          "`V.configurar_pagina(titulo='', icone='', …)`",
          "Título e ícone **só desta** página."
        ],
        [
          "`V.pagina(caminho, acao=None, titulo='', icone='', oculta=False)`",
          "Registra uma página. Também serve de decorador."
        ],
        [
          "`V.paginas()`",
          "As páginas registradas, para montar um menu."
        ],
        [
          "`V.rodar(acao=None, porta=8501, host='127.0.0.1', recarregar=False, silencioso=False)`",
          "Sobe a aplicação. Com uma ação, ela vira a página de `/`."
        ],
        [
          "`V.subir(porta=8501, host='127.0.0.1', recarregar=False, silencioso=False)`",
          "Sobe e bloqueia. `recarregar := yes` reinicia ao salvar."
        ],
        [
          "`V.servir(porta=0, host='127.0.0.1')`",
          "Sobe em segundo plano e devolve a porta. Para testes."
        ],
        [
          "`V.parar_servidor()`",
          "Desliga o servidor."
        ],
        [
          "`V.montar()`",
          "O app Kiln por baixo — para acrescentar rota ou middleware."
        ]
      ]
    }
  },
  {
    "h2": "Texto"
  },
  {
    "table": {
      "head": [
        "Símbolo",
        "Faz"
      ],
      "rows": [
        [
          "`V.titulo(conteudo, icone='')`",
          "O título da página, com ícone opcional."
        ],
        [
          "`V.subtitulo(conteudo)`",
          "Um subtítulo."
        ],
        [
          "`V.cabecalho(conteudo, nivel=3)`",
          "Um cabeçalho de seção, do nível 1 ao 6."
        ],
        [
          "`V.texto(*partes)`",
          "Um parágrafo. Vários argumentos viram uma linha, como o `out`."
        ],
        [
          "`V.markdown(conteudo)`",
          "Títulos, listas, tabela, ênfase, código e link."
        ],
        [
          "`V.codigo(conteudo, linguagem='dataforge')`",
          "Um bloco de código, com a linguagem."
        ],
        [
          "`V.html(conteudo)`",
          "HTML **cru, sem escapar**. Nunca com o que veio do usuário."
        ],
        [
          "`V.divisor()`",
          "Uma linha horizontal."
        ],
        [
          "`V.espaco(altura=16)`",
          "Espaço vertical em pixels."
        ]
      ]
    }
  },
  {
    "h2": "Entrada"
  },
  {
    "table": {
      "head": [
        "Símbolo",
        "Faz"
      ],
      "rows": [
        [
          "`V.botao(rotulo, tipo='primario', chave=None, largura='')`",
          "Devolve `yes` no ciclo em que foi clicado, `no` nos outros."
        ],
        [
          "`V.entrada(rotulo, valor='', dica='', tipo='texto', chave=None)`",
          "Campo de texto. Devolve o que está digitado."
        ],
        [
          "`V.area_de_texto(rotulo, valor='', linhas=4, dica='', chave=None)`",
          "Campo de várias linhas."
        ],
        [
          "`V.numero(rotulo, valor=0, minimo=None, maximo=None, passo=1, chave=None)`",
          "Campo numérico, com mínimo, máximo e passo."
        ],
        [
          "`V.deslizante(rotulo, minimo=0, maximo=100, valor=None, passo=1, chave=None)`",
          "Escolher um número numa faixa."
        ],
        [
          "`V.caixa(rotulo, valor=False, chave=None)`",
          "Uma caixa de marcar. Devolve `yes`/`no`."
        ],
        [
          "`V.interruptor(rotulo, valor=False, chave=None)`",
          "O mesmo, com cara de chave."
        ],
        [
          "`V.opcao(rotulo, opcoes, indice=0, chave=None)`",
          "Uma de poucas, em botões de rádio."
        ],
        [
          "`V.escolha(rotulo, opcoes, indice=0, chave=None)`",
          "Uma de muitas, em lista suspensa."
        ],
        [
          "`V.escolhas(rotulo, opcoes, padrao=None, chave=None)`",
          "Várias de muitas. Devolve um cluster."
        ],
        [
          "`V.data(rotulo, valor='', chave=None)`",
          "Um seletor de data. Devolve `\"2026-03-14\"`."
        ],
        [
          "`V.cor(rotulo, valor='#FED403', chave=None)`",
          "Um seletor de cor. Devolve `\"#FED403\"`."
        ],
        [
          "`V.arquivo(rotulo, tipos=None, varios=False, chave=None)`",
          "Envio de arquivo. Devolve `void` até alguém mandar um."
        ]
      ]
    }
  },
  {
    "h2": "Dados"
  },
  {
    "table": {
      "head": [
        "Símbolo",
        "Faz"
      ],
      "rows": [
        [
          "`V.tabela(dados, colunas=None, altura=None)`",
          "Uma tabela estática. Aceita cluster de vaults, Frame ou matriz."
        ],
        [
          "`V.frame(dados, colunas=None, altura=None)`",
          "Uma tabela com busca e ordenação, para explorar dado."
        ],
        [
          "`V.metrica(rotulo, valor, variacao=None, ajuda='')`",
          "Um número grande, com a variação ao lado."
        ],
        [
          "`V.json(dados, expandido=True)`",
          "Um vault ou cluster, formatado e recolhível."
        ],
        [
          "`V.vault(dados)`",
          "Um vault como lista de chave e valor."
        ]
      ]
    }
  },
  {
    "h2": "Retorno ao usuário"
  },
  {
    "table": {
      "head": [
        "Símbolo",
        "Faz"
      ],
      "rows": [
        [
          "`V.sucesso(mensagem)`",
          "Uma mensagem verde."
        ],
        [
          "`V.erro(mensagem)`",
          "Uma mensagem vermelha."
        ],
        [
          "`V.aviso(mensagem)`",
          "Uma mensagem amarela."
        ],
        [
          "`V.informacao(mensagem)`",
          "Uma mensagem azul."
        ],
        [
          "`V.progresso(fracao, rotulo='')`",
          "Barra de 0 a 1."
        ],
        [
          "`V.carregando(mensagem='Carregando…')`",
          "Um giro com uma mensagem."
        ],
        [
          "`V.imagem(origem, legenda='', largura=None)`",
          "Uma imagem, com legenda."
        ],
        [
          "`V.audio(origem, formato='audio/mpeg')`",
          "Um tocador de áudio."
        ],
        [
          "`V.video(origem, formato='video/mp4')`",
          "Um tocador de vídeo."
        ],
        [
          "`V.link(rotulo, destino, nova_aba=False)`",
          "Um link, opcionalmente em nova aba."
        ],
        [
          "`V.baixar(rotulo, conteudo, nome='dados.txt', tipo='text/plain')`",
          "Um botão que entrega um arquivo ao visitante."
        ]
      ]
    }
  },
  {
    "h2": "Layout"
  },
  {
    "table": {
      "head": [
        "Símbolo",
        "Faz"
      ],
      "rows": [
        [
          "`V.colunas(quantidade, larguras=None, espacamento='medio')`",
          "Divide em colunas. Devolve um cluster de áreas."
        ],
        [
          "`V.linha(alinhar='inicio', espacamento='medio')`",
          "Container horizontal — os filhos ficam lado a lado."
        ],
        [
          "`V.container(borda=False, altura=None)`",
          "Um agrupamento, com borda e altura opcionais."
        ],
        [
          "`V.cartao(titulo='', subtitulo='')`",
          "Uma caixa com título e subtítulo."
        ],
        [
          "`V.expandir(rotulo, aberto=False)`",
          "Uma seção que abre e fecha; o estado sobrevive."
        ],
        [
          "`V.abas(rotulos)`",
          "Abas. **Todas** são montadas; só a escolhida aparece."
        ],
        [
          "`V.formulario(nome, limpar=False)`",
          "Agrupa campos que só valem no envio."
        ],
        [
          "`V.vazio()`",
          "Um espaço reservado para ser preenchido depois."
        ],
        [
          "`V.lateral()`",
          "A barra lateral. Sempre a mesma, chamada de onde for."
        ],
        [
          "`V.espacador()`",
          "Empurra o que vem depois para a outra ponta de uma `linha`."
        ]
      ]
    }
  },
  {
    "h2": "Gráficos"
  },
  {
    "table": {
      "head": [
        "Símbolo",
        "Faz"
      ],
      "rows": [
        [
          "`V.grafico(tipo='linha', dados=None)`",
          "Começa a montar um gráfico. Nada aparece até `desenhar`."
        ],
        [
          "`V.desenhar(g)`",
          "Põe o gráfico montado na página."
        ],
        [
          "`V.grafico_linha(dados, x='', y='', titulo='', altura=None, …)`",
          "Linha, a forma curta."
        ],
        [
          "`V.grafico_barras(dados, x='', y='', titulo='', altura=None, …)`",
          "Barras verticais."
        ],
        [
          "`V.grafico_barras_h(dados, x='', y='', titulo='', altura=None, …)`",
          "Barras horizontais, para categorias de nome longo."
        ],
        [
          "`V.grafico_area(dados, x='', y='', titulo='', altura=None, …)`",
          "Linha com a área preenchida."
        ],
        [
          "`V.grafico_dispersao(dados, x='', y='', titulo='', altura=None, …)`",
          "Pontos."
        ],
        [
          "`V.grafico_pizza(dados, x='', y='', titulo='', altura=None, …)`",
          "Fatias, com o percentual escrito."
        ],
        [
          "`V.grafico_rosca(dados, x='', y='', titulo='', altura=None, …)`",
          "O mesmo, com o miolo vazado."
        ],
        [
          "`V.histograma(dados, campo='', faixas=10, titulo='', altura=None)`",
          "Distribuição: conta quantos valores caem em cada faixa."
        ],
        [
          "`V.paleta`",
          "As dez cores padrão, como cluster."
        ]
      ]
    }
  },
  {
    "h2": "Estado e cache"
  },
  {
    "table": {
      "head": [
        "Símbolo",
        "Faz"
      ],
      "rows": [
        [
          "`V.estado`",
          "O estado da sessão: `obter`, `definir`, `padrao`, `somar`…"
        ],
        [
          "`V.geral`",
          "O estado do processo — **todas** as sessões veem o mesmo."
        ],
        [
          "`V.cache(*args, …args)`",
          "`mark @V.cache` sobre uma ação, e ela para de recalcular."
        ]
      ]
    }
  },
  {
    "h2": "Navegação"
  },
  {
    "table": {
      "head": [
        "Símbolo",
        "Faz"
      ],
      "rows": [
        [
          "`V.navegar(destino)`",
          "Vai para outra página. Interrompe o programa aqui."
        ],
        [
          "`V.parar()`",
          "Acaba a página neste ponto, sem erro."
        ],
        [
          "`V.recarregar()`",
          "Roda de novo, do começo, jogando fora o que foi montado."
        ],
        [
          "`V.caminho()`",
          "Onde a página está."
        ],
        [
          "`V.parametros()`",
          "Os da rota e os da query, juntos."
        ],
        [
          "`V.parametro(nome, padrao='')`",
          "Um deles, com padrão."
        ],
        [
          "`V.menu(rotulo='Páginas')`",
          "Desenha o menu das páginas registradas na barra lateral."
        ]
      ]
    }
  },
  {
    "h2": "Segurança"
  },
  {
    "table": {
      "head": [
        "Símbolo",
        "Faz"
      ],
      "rows": [
        [
          "`V.autenticacao(verificador, papeis=None)`",
          "Registra a ação que confere usuário e senha."
        ],
        [
          "`V.entrar(usuario, senha)`",
          "Tenta entrar. Devolve o vault do usuário, ou `void`."
        ],
        [
          "`V.sair()`",
          "Derruba a sessão de quem está logado."
        ],
        [
          "`V.usuario()`",
          "Quem está logado, ou `void`."
        ],
        [
          "`V.autenticado()`",
          "`yes`/`no`."
        ],
        [
          "`V.pode(permissao)`",
          "Se o papel de quem está logado tem a permissão."
        ],
        [
          "`V.exigir_login(mensagem='Entre para continuar.')`",
          "A barreira: desenha a entrada e para a página."
        ],
        [
          "`V.exigir_permissao(permissao, mensagem='')`",
          "O mesmo, e ainda cobra a permissão."
        ]
      ]
    }
  },
  {
    "h2": "Operação"
  },
  {
    "table": {
      "head": [
        "Símbolo",
        "Faz"
      ],
      "rows": [
        [
          "`V.registrar(mensagem, nivel='info', extra=None)`",
          "Escreve no log da aplicação."
        ],
        [
          "`V.logs(quantos=100, nivel='')`",
          "As últimas linhas, filtráveis por nível."
        ],
        [
          "`V.metricas()`",
          "Execuções, erros, média em ms, sessões e cache."
        ],
        [
          "`V.saude()`",
          "O que um balanceador pergunta antes de mandar tráfego."
        ],
        [
          "`V.plugin(nome, instalar)`",
          "Instala um plugin. O mesmo nome duas vezes é erro."
        ],
        [
          "`V.antes(funcao)`",
          "Middleware que roda antes de toda página; `no` interrompe."
        ],
        [
          "`V.depois(funcao)`",
          "Middleware de saída, com o contexto já montado."
        ],
        [
          "`V.sessoes()`",
          "Quantas sessões estão vivas."
        ],
        [
          "`V.encerrar_sessao()`",
          "Descarta a sessão de agora."
        ],
        [
          "`V.tarefa(acao, *args)`",
          "Roda numa thread e devolve na hora. A página não espera."
        ],
        [
          "`V.agendar(acao, a_cada, *args)`",
          "Roda de tempos em tempos, enquanto o processo viver."
        ],
        [
          "`V.atualizar_a_cada(segundos)`",
          "A página se recarrega sozinha nesse intervalo."
        ]
      ]
    }
  },
  {
    "h2": "Exportar"
  },
  {
    "table": {
      "head": [
        "Símbolo",
        "Faz"
      ],
      "rows": [
        [
          "`V.exportar_csv(dados, nome='dados.csv', rotulo='Baixar CSV', separador=',')`",
          "Um botão que entrega os dados como CSV."
        ],
        [
          "`V.exportar_json(dados, nome='dados.json', rotulo='Baixar JSON')`",
          "O mesmo, em JSON."
        ],
        [
          "`V.html_da_pagina()`",
          "A página atual como HTML."
        ],
        [
          "`V.markdown_para_html(texto)`",
          "Converte Markdown sem pôr nada na página."
        ]
      ]
    }
  },
  {
    "h2": "Testes"
  },
  {
    "table": {
      "head": [
        "Símbolo",
        "Faz"
      ],
      "rows": [
        [
          "`V.testar(pagina_ou_app, caminho='/')`",
          "Uma sonda: clica, digita e pergunta, sem navegador."
        ],
        [
          "`V.pedir(app, metodo, caminho, corpo=None, cabecalhos=None)`",
          "Um pedido HTTP de verdade contra a aplicação, sem socket."
        ]
      ]
    }
  },
  {
    "h2": "Os métodos da sonda"
  },
  {
    "p": "O que `V.testar(pagina)` devolve — ver [Testar sem navegador](/docs/vitrine/testes)."
  },
  {
    "table": {
      "head": [
        "Método",
        "Faz"
      ],
      "rows": [
        [
          "`t.clicar(rótulo)`",
          "clica num botão e roda a página de novo"
        ],
        [
          "`t.digitar(rótulo, valor)`",
          "preenche um campo"
        ],
        [
          "`t.marcar(rótulo, ligado)`",
          "liga uma caixa ou interruptor"
        ],
        [
          "`t.selecionar(rótulo, valor)`",
          "escolhe numa lista"
        ],
        [
          "`t.abrir_aba(rótulo)`",
          "troca de aba"
        ],
        [
          "`t.enviar(formulário)`",
          "aperta o botão de envio"
        ],
        [
          "`t.enviar_arquivo(rótulo, nome, conteúdo)`",
          "simula um upload"
        ],
        [
          "`t.ir_para(caminho)`",
          "vai para outra página"
        ],
        [
          "`t.rodar()`",
          "roda de novo, sem interação"
        ],
        [
          "`t.texto()`",
          "a página como texto corrido"
        ],
        [
          "`t.achar(tipo)` · `t.primeiro(tipo)`",
          "os nós de um tipo"
        ],
        [
          "`t.quantos(tipo)` · `t.existe(tipo, rótulo)`",
          "contar e conferir"
        ],
        [
          "`t.metrica(rótulo)` · `t.valor(rótulo)`",
          "o que a tela mostra"
        ],
        [
          "`t.alertas(nível)`",
          "as mensagens de sucesso, erro, aviso"
        ],
        [
          "`t.estado(chave)`",
          "o estado da sessão"
        ],
        [
          "`t.falhou()` · `t.falhas()`",
          "se algo disparou, e o quê"
        ],
        [
          "`t.html()` · `t.arvore()`",
          "a página como HTML, ou como vault"
        ]
      ]
    }
  },
  {
    "h2": "As rotas que vêm prontas"
  },
  {
    "table": {
      "head": [
        "Rota",
        "Devolve"
      ],
      "rows": [
        [
          "`GET /__vitrine__/saude`",
          "estado, tempo no ar, sessões"
        ],
        [
          "`GET /__vitrine__/metricas`",
          "execuções, erros, média em ms, cache"
        ],
        [
          "`POST /__vitrine__/acao`",
          "o miolo da página, após uma interação"
        ],
        [
          "`GET /__vitrine__/baixar/:chave`",
          "o arquivo de um `V.baixar`"
        ],
        [
          "`GET /__vitrine__/manifesto.json`",
          "o manifesto PWA, se ligado"
        ]
      ]
    }
  }
];

const headings = [{ id: 'aplicacao-e-servidor', text: "Aplicação e servidor", level: 2 as const }, { id: 'texto', text: "Texto", level: 2 as const }, { id: 'entrada', text: "Entrada", level: 2 as const }, { id: 'dados', text: "Dados", level: 2 as const }, { id: 'retorno-ao-usuario', text: "Retorno ao usuário", level: 2 as const }, { id: 'layout', text: "Layout", level: 2 as const }, { id: 'graficos', text: "Gráficos", level: 2 as const }, { id: 'estado-e-cache', text: "Estado e cache", level: 2 as const }, { id: 'navegacao', text: "Navegação", level: 2 as const }, { id: 'seguranca', text: "Segurança", level: 2 as const }, { id: 'operacao', text: "Operação", level: 2 as const }, { id: 'exportar', text: "Exportar", level: 2 as const }, { id: 'testes', text: "Testes", level: 2 as const }, { id: 'os-metodos-da-sonda', text: "Os métodos da sonda", level: 2 as const }, { id: 'as-rotas-que-vem-prontas', text: "As rotas que vêm prontas", level: 2 as const }];

export default function Page() {
  return (
    <DocPage
      title="Referência da Vitrine"
      description="Os 105 símbolos do módulo, agrupados por assunto, com a assinatura extraída do código-fonte."
      href="/docs/vitrine/referencia"
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
