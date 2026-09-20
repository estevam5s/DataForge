import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

// Gerado por tools/gerar_ref_vitrine.py — não edite à mão.

export const metadata: Metadata = {
  title: "Referência da Vitrine",
  description: "Os 213 símbolos do módulo, agrupados por assunto, com a assinatura extraída do código-fonte.",
};

const blocos: Bloco[] = [
  {
    "p": "Esta página é gerada a partir de `dataforge/stdlib/vitrine/`. São **213 símbolos**, e o gerador recusa rodar se algum deles ficar de fora."
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
        ],
        [
          "`V.modo_servidor()`",
          "`yes` quando quem chamou quer o servidor **no ar** — é o que faz o mesmo arquivo servir com `dataforge vitrine dev` e ser testável com `dataforge run`."
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
        ],
        [
          "`V.escrever(*valores)`",
          "Mostra o que vier, escolhendo o componente **pelo valor**."
        ],
        [
          "`V.legenda(conteudo)`",
          "Texto pequeno e discreto — a nota sob um gráfico."
        ],
        [
          "`V.citacao(conteudo, autor='')`",
          "Um bloco citado, com autor opcional."
        ],
        [
          "`V.selo(texto, cor='neutro', icone='')`",
          "Uma etiqueta curta, na cor do tema."
        ],
        [
          "`V.selos(itens, cor='neutro')`",
          "Vários selos numa linha só."
        ],
        [
          "`V.formula(expressao, bloco=True)`",
          "Fração, potência, índice e as letras gregas."
        ],
        [
          "`V.ajuda(alvo)`",
          "A assinatura e a documentação de uma ação, na página."
        ],
        [
          "`V.fluxo(gerador, velocidade=18)`",
          "Consome um gerador de texto e mostra o resultado."
        ],
        [
          "`V.icone(nome, tamanho=18, cor='')`",
          "Um dos 48 ícones desenhados no módulo."
        ],
        [
          "`V.icones()`",
          "Os nomes de todos os ícones."
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
        ],
        [
          "`V.hora(rotulo, valor='09:00', passo=60, chave=None)`",
          "Um horário. Devolve `\"14:30\"`."
        ],
        [
          "`V.periodo(rotulo, inicio='', fim='', chave=None)`",
          "Duas datas. Devolve `[inicio, fim]`, já em ordem."
        ],
        [
          "`V.faixa(rotulo, minimo=0, maximo=100, valor=None, passo=1, chave=None)`",
          "Dois cursores na mesma trilha. Devolve `[menor, maior]`."
        ],
        [
          "`V.deslizante_opcoes(rotulo, opcoes, indice=0, chave=None)`",
          "Um cursor sobre rótulos. Devolve o rótulo."
        ],
        [
          "`V.pilulas(rotulo, opcoes, padrao=None, varios=False, chave=None)`",
          "Botões arredondados, um ou vários. O filtro que fica visível."
        ],
        [
          "`V.segmentado(rotulo, opcoes, indice=0, chave=None)`",
          "Um grupo colado, com um segmento aceso."
        ],
        [
          "`V.avaliacao(rotulo, tipo='estrelas', maximo=5, valor=0, chave=None)`",
          "Estrelas, corações ou polegares. Devolve `0` sem nota."
        ],
        [
          "`V.tags(rotulo, valor=None, sugestoes=None, chave=None)`",
          "Etiquetas que se acrescenta digitando. Devolve um cluster."
        ],
        [
          "`V.autocompletar(rotulo, opcoes, valor='', dica='', chave=None)`",
          "Campo de texto com sugestões — que **não** restringem."
        ],
        [
          "`V.senha(rotulo='Senha', dica='', chave=None)`",
          "`V.entrada` com o tipo senha."
        ],
        [
          "`V.busca(rotulo='Buscar', dica='', chave=None)`",
          "`V.entrada` com o tipo busca."
        ],
        [
          "`V.email(rotulo='E-mail', valor='', dica='', chave=None)`",
          "`V.entrada` com o tipo e-mail."
        ],
        [
          "`V.camera(rotulo='Foto', chave=None)`",
          "Tira uma foto pela câmera. Exige HTTPS e permissão."
        ],
        [
          "`V.mudou(chave)`",
          "`yes` quando o campo dessa chave chegou diferente agora."
        ],
        [
          "`V.mudancas()`",
          "As chaves que mudaram nesta execução."
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
        ],
        [
          "`V.grade(dados, colunas=None, busca=True, paginar=25, selecionar='', ordenar_por='', decrescente=False, destacar=None, totais=None, altura=None, densidade='normal', numerar=False, chave=None, vazio='sem dados')`",
          "A tabela de trabalho: pagina, ordena e filtra **no servidor**."
        ],
        [
          "`V.editor(dados, colunas=None, acrescentar=True, remover=True, altura=None, chave=None)`",
          "Uma tabela que se edita na tela. Devolve as linhas novas."
        ],
        [
          "`V.coluna(nome, titulo='', tipo='texto', formato='', largura=0, alinhar='', casas=None, ajuda='', editavel=False, opcoes=None, minimo=None, maximo=None, prefixo='', sufixo='', cores=None, oculta=False)`",
          "A configuração de uma coluna da grade, como vault."
        ],
        [
          "`V.regra(coluna_alvo, condicao, valor=None, cor='aviso', coluna_pintada='')`",
          "Uma regra de formatação condicional para a grade."
        ],
        [
          "`V.indicador(rotulo, valor, variacao=None, cor='', ajuda='', nota='', mini=None, alvo=None, formato='', icone='')`",
          "O cartão de um número: faixa de cor, nota, meta e série."
        ],
        [
          "`V.indicadores(itens, colunas=0)`",
          "Vários indicadores numa faixa que se ajusta à largura."
        ],
        [
          "`V.estatisticas(dados, colunas=None)`",
          "Contagem, ausências, média, desvio, quartis."
        ],
        [
          "`V.formatar(valor, formato='', casas=None)`",
          "Aplica um formato conhecido pelo nome."
        ],
        [
          "`V.moeda(valor, simbolo='R$', casas=2)`",
          "`1091947.91` vira `R$ 1.091.947,91`."
        ],
        [
          "`V.numero_br(valor, casas=0)`",
          "Separador de milhar e vírgula decimal."
        ],
        [
          "`V.percentual(valor, casas=1, ja_e_percentual=True)`",
          "`12.5` vira `12,5%`."
        ],
        [
          "`V.compacto(valor, casas=1)`",
          "`1234567` vira `1,2 mi`."
        ],
        [
          "`V.data_br(valor)`",
          "`2026-09-20` vira `20/09/2026`."
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
        ],
        [
          "`V.pdf(origem, altura=640, pagina=1)`",
          "Mostra um PDF na própria página."
        ],
        [
          "`V.iframe(origem, altura=420, titulo='Conteúdo incorporado')`",
          "Incorpora outra página, em `sandbox`."
        ],
        [
          "`V.logo(origem, destino='/', largura=132)`",
          "A marca, no alto da barra lateral."
        ],
        [
          "`V.galeria(imagens, colunas=3, legendas=None)`",
          "Várias imagens numa grade."
        ],
        [
          "`V.toast(mensagem, icone='', nivel='info', segundos=4)`",
          "Um aviso flutuante, que aparece e some sozinho."
        ],
        [
          "`V.esqueleto(linhas=3, altura=14, largura='100%')`",
          "O contorno cinza do que ainda não chegou."
        ],
        [
          "`V.comemorar(tipo='balao')`",
          "Balões, neve ou confete, por alguns segundos."
        ],
        [
          "`V.excecao(erro, detalhe='')`",
          "Um erro desenhado como erro: tipo, mensagem e rastro."
        ],
        [
          "`V.status(rotulo, estado='rodando', aberto=True)`",
          "Uma caixa com estado, que se escreve por dentro."
        ],
        [
          "`V.chat(altura=None)`",
          "A área de uma conversa."
        ],
        [
          "`V.chat_mensagem(quem='assistente', conteudo='', avatar='', hora='')`",
          "Uma bolha. Devolve a área, para escrever dentro."
        ],
        [
          "`V.chat_entrada(dica='Escreva uma mensagem…', chave=None, desabilitado=False)`",
          "A caixa de escrever. Devolve o texto enviado, ou `void`."
        ],
        [
          "`V.historico_de_chat(chave='__chat__')`",
          "A lista de mensagens guardada na sessão."
        ],
        [
          "`V.guardar_no_chat(quem, conteudo, chave='__chat__')`",
          "Acrescenta ao histórico e devolve a lista inteira."
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
        ],
        [
          "`V.malha(colunas=3, espacamento='medio', minimo=240)`",
          "Uma grade que se reorganiza pela **largura**, não pelo número."
        ],
        [
          "`V.painel(titulo='', subtitulo='', cor='', icone='', compacto=False, altura=None)`",
          "O bloco de painel: faixa de cor, título discreto, conteúdo."
        ],
        [
          "`V.barra_superior(titulo='', itens=None, ativo='', logo='', subtitulo='')`",
          "Marca, navegação e o canto dos filtros."
        ],
        [
          "`V.dialogo(titulo, aberto=None, largura=520, chave=None)`",
          "Uma janela por cima da página. O estado é de quem escreve."
        ],
        [
          "`V.popover(rotulo, icone='', largura=300)`",
          "Um botão que abre um cartãozinho."
        ],
        [
          "`V.passos(rotulos, atual=0, concluidos=None)`",
          "A trilha de um processo, com o passo aceso."
        ],
        [
          "`V.separador(texto='', icone='')`",
          "Uma linha com um rótulo no meio."
        ],
        [
          "`V.rolagem(altura=320, borda=True)`",
          "Uma caixa com rolagem própria, de altura fixa."
        ],
        [
          "`V.fragmento(chave, a_cada=0)`",
          "Um pedaço que se redesenha **sozinho**, sem a página junto."
        ],
        [
          "`V.fragmentos()`",
          "As chaves dos fragmentos montados nesta execução."
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
        ],
        [
          "`V.tipos_de_grafico`",
          "Os nomes de todos os tipos, como cluster."
        ],
        [
          "`V.grafico_combo(dados, x='', barras=None, linhas=None, titulo='', altura=None, cores=None, formato='', direita=None, empilhado=False, …)`",
          "Barras e linhas juntas, com **duas** escalas."
        ],
        [
          "`V.grafico_barras_100(dados, x='', y=None, titulo='', altura=None, cores=None, …)`",
          "Barras em que cada categoria soma 100%."
        ],
        [
          "`V.grafico_area_empilhada(dados, x='', y=None, titulo='', altura=None, cores=None, …)`",
          "Áreas somadas: o todo e as partes."
        ],
        [
          "`V.grafico_funil(dados, x='', y='', titulo='', altura=None, cores=None, formato='', …)`",
          "Quanto sobra em cada etapa, com as duas conversões."
        ],
        [
          "`V.grafico_treemap(dados, rotulo='', valor='', titulo='', altura=None, cores=None, formato='', …)`",
          "Retângulos proporcionais, para itens demais."
        ],
        [
          "`V.grafico_cascata(dados, x='', y='', titulo='', altura=None, cores=None, formato='', total=True, …)`",
          "De onde veio a diferença entre o começo e o fim."
        ],
        [
          "`V.grafico_pareto(dados, x='', y='', titulo='', altura=None, cores=None, formato='', corte=80, …)`",
          "Barras em ordem, com a curva do acumulado."
        ],
        [
          "`V.grafico_radar(dados, x='', y=None, titulo='', altura=None, cores=None, …)`",
          "Eixos saindo do centro — vale até umas oito pontas."
        ],
        [
          "`V.grafico_caixa(dados, y=None, titulo='', altura=None, cores=None, formato='', …)`",
          "Mediana, quartis e os pontos fora da curva."
        ],
        [
          "`V.grafico_bolhas(dados, x='', y='', tamanho='', rotulo='', titulo='', altura=None, cores=None, formato='', …)`",
          "Três grandezas: posição, posição e **área**."
        ],
        [
          "`V.grafico_dispersao_xy(dados, x='', y='', titulo='', altura=None, cores=None, formato='', tendencia=False, …)`",
          "Dispersão com o eixo x numérico, e a tendência."
        ],
        [
          "`V.grafico_velas(dados, data='', abertura='abertura', maxima='maxima', minima='minima', fechamento='fechamento', titulo='', altura=None, cores=None, formato='', …)`",
          "Abertura, máxima, mínima e fechamento."
        ],
        [
          "`V.grafico_sankey(ligacoes, titulo='', altura=None, cores=None, formato='', …)`",
          "Para onde o dinheiro (ou o usuário) foi."
        ],
        [
          "`V.grafico_gantt(tarefas, titulo='', altura=None, cores=None, …)`",
          "Barras no tempo — o cronograma."
        ],
        [
          "`V.grafico_mapa(pontos, titulo='', altura=None, cores=None, formato='', …)`",
          "Pontos por latitude e longitude. **Sem** mapa por baixo."
        ],
        [
          "`V.grafico_rede(ligacoes, titulo='', altura=None, cores=None, …)`",
          "Nós e arestas, dispostos em círculo."
        ],
        [
          "`V.grafico_calendario(dados, data='', valor='', ano=None, titulo='', altura=None, cores=None, escala=None, …)`",
          "Um ano em quadradinhos, uma semana por coluna."
        ],
        [
          "`V.mapa_de_calor(dados, x='', y='', valor='', titulo='', altura=None, cores=None, formato='', escala=None, …)`",
          "Uma matriz colorida: hora × dia, produto × região."
        ],
        [
          "`V.medidor(valor, minimo=0, maximo=100, titulo='', faixas=None, altura=None, formato='', rotulo='', cores=None, …)`",
          "Um ponteiro numa escala, com faixas coloridas."
        ],
        [
          "`V.grafico_bala(valor, alvo, minimo=0, maximo=None, rotulo='', faixas=None, titulo='', altura=None, cores=None, formato='', …)`",
          "O valor, a meta e as faixas numa linha só."
        ],
        [
          "`V.mini_grafico(valores, tipo='linha', cor='', altura=34, largura=120, mostrar_valor=False)`",
          "Uma série miúda, do tamanho de uma linha de texto."
        ]
      ]
    }
  },
  {
    "h2": "Estado, cache e conexões"
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
        ],
        [
          "`V.recurso(*args, …args)`",
          "`mark @V.recurso` guarda o **objeto** — conexão, modelo."
        ],
        [
          "`V.conexao(nome, arquivo='', tipo='sqlite', **opcoes)`",
          "Abre (ou devolve) uma conexão do processo, com cache."
        ],
        [
          "`V.conexao_de(nome, bruta, tipo='externa')`",
          "Registra uma conexão que **você** abriu."
        ],
        [
          "`V.conexoes()`",
          "Os nomes das conexões vivas."
        ],
        [
          "`V.fechar_conexoes()`",
          "Fecha todas. Devolve quantas eram."
        ],
        [
          "`V.segredos(recarregar=False)`",
          "Todos os segredos, como vault."
        ],
        [
          "`V.segredo(chave, padrao='')`",
          "Um segredo. O **ambiente vence o arquivo**."
        ],
        [
          "`V.segredos_mascarados()`",
          "As chaves, com o valor escondido."
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
          "`V.sessoes_em_banco(caminho)`",
          "As sessões num SQLite que vários processos abrem (`sessoes_em := …`)."
        ],
        [
          "`V.sessoes_em_arquivos(pasta)`",
          "As sessões num JSON por sessão, numa pasta que os processos dividem."
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
    "h2": "Exportar e aparência"
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
          "`V.exportar_svg(grafico, nome='grafico.svg', rotulo='Baixar SVG')`",
          "O gráfico como arquivo SVG — o mesmo que a página desenha."
        ],
        [
          "`V.exportar_excel(dados, nome='dados.xlsx', rotulo='Baixar Excel', aba='Dados')`",
          "Uma planilha `.xlsx` de verdade, sem dependência."
        ],
        [
          "`V.html_da_pagina()`",
          "A página atual como HTML."
        ],
        [
          "`V.markdown_para_html(texto)`",
          "Converte Markdown sem pôr nada na página."
        ],
        [
          "`V.tema(qual=None, densidade=None)`",
          "Lê ou troca o tema e a densidade da aplicação."
        ],
        [
          "`V.temas()`",
          "Os seis temas prontos."
        ],
        [
          "`V.seletor_de_tema(rotulo='Tema')`",
          "Desenha a troca de tema e devolve o escolhido."
        ]
      ]
    }
  },
  {
    "h2": "Validação e idioma"
  },
  {
    "table": {
      "head": [
        "Símbolo",
        "Faz"
      ],
      "rows": [
        [
          "`V.validar(valor, regra, mensagem='')`",
          "Confere um valor e desenha o erro **sob o campo**."
        ],
        [
          "`V.campo_validado(rotulo, regra, mensagem='', valor='', tipo='texto', dica='', chave=None)`",
          "Um campo com a regra junto. Devolve `(valor, bom)`."
        ],
        [
          "`V.i18n`",
          "Tradução: `carregar`, `idioma`, `traduzir`, `seletor`."
        ],
        [
          "`V.t(chave, **valores)`",
          "O texto de uma chave, no idioma da sessão. Atalho de `traduzir`."
        ],
        [
          "`V.traduzir(chave, **valores)`",
          "O mesmo que `t`, pelo nome inteiro."
        ]
      ]
    }
  },
  {
    "h2": "Componentes próprios"
  },
  {
    "table": {
      "head": [
        "Símbolo",
        "Faz"
      ],
      "rows": [
        [
          "`V.componente(nome, acao=None)`",
          "Registra um componente reaproveitável, pelo nome."
        ],
        [
          "`V.usar(nome, *args, …args)`",
          "Chama um componente registrado."
        ],
        [
          "`V.componentes()`",
          "Os nomes registrados."
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

const headings = [{ id: 'aplicacao-e-servidor', text: "Aplicação e servidor", level: 2 as const }, { id: 'texto', text: "Texto", level: 2 as const }, { id: 'entrada', text: "Entrada", level: 2 as const }, { id: 'dados', text: "Dados", level: 2 as const }, { id: 'retorno-ao-usuario', text: "Retorno ao usuário", level: 2 as const }, { id: 'layout', text: "Layout", level: 2 as const }, { id: 'graficos', text: "Gráficos", level: 2 as const }, { id: 'estado-cache-e-conexoes', text: "Estado, cache e conexões", level: 2 as const }, { id: 'navegacao', text: "Navegação", level: 2 as const }, { id: 'seguranca', text: "Segurança", level: 2 as const }, { id: 'operacao', text: "Operação", level: 2 as const }, { id: 'exportar-e-aparencia', text: "Exportar e aparência", level: 2 as const }, { id: 'validacao-e-idioma', text: "Validação e idioma", level: 2 as const }, { id: 'componentes-proprios', text: "Componentes próprios", level: 2 as const }, { id: 'testes', text: "Testes", level: 2 as const }, { id: 'os-metodos-da-sonda', text: "Os métodos da sonda", level: 2 as const }, { id: 'as-rotas-que-vem-prontas', text: "As rotas que vêm prontas", level: 2 as const }];

export default function Page() {
  return (
    <DocPage
      title="Referência da Vitrine"
      description="Os 213 símbolos do módulo, agrupados por assunto, com a assinatura extraída do código-fonte."
      href="/docs/vitrine/referencia"
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
