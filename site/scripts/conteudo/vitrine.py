# -*- coding: utf-8 -*-
"""Arcane.Vitrine — o framework de dashboards e aplicações de dados."""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/vitrine",
"title": "Vitrine",
"description": "Um programa de cima para baixo vira uma página web. Sem HTML, sem JavaScript, sem separar o que calcula do que mostra.",
"blocos": [
 {"p": "**Vitrine** é o framework de painéis e aplicações de dados do DataForge. Você escreve um programa de cima para baixo; ele vira uma página web."},
 {"code": """adopt Arcane.Vitrine as V

action painel():
    V.titulo("Vendas")
    regiao := V.escolha("Região", ["Sul", "Sudeste", "Norte"])
    V.metrica("Receita", "R$ 128.400", variacao := 12.5)
    V.grafico_barras(vendas_de(regiao), x := "mes")

V.rodar(painel, porta := 8501)""", "lang": "df"},
 {"p": "Isso é a aplicação inteira. Não há HTML, não há CSS, não há JavaScript, não há build, e não há separação entre o que calcula e o que mostra."},

 {"h2": "O modelo de execução"},
 {"p": "A cada interação, **o programa inteiro roda de novo** — e o estado da sessão sobrevive."},
 {"code": """clique  →  o programa roda do começo  →  a árvore vira HTML  →  a tela troca
              ↑                                                      │
              └──────────  o estado da sessão continua  ─────────────┘""", "lang": "text"},
 {"p": "Parece desperdício e é o contrário. Quem escreve nunca pensa em callback, em diffing, nem em qual pedaço da tela atualizar: a linha de cima sempre aconteceu antes da linha de baixo, como em qualquer programa."},
 {"p": "É por isso que um componente **devolve** o que quem escreve precisa. `V.botao(…)` devolve `yes` ou `no`; `V.entrada(…)` devolve o texto digitado. A linha seguinte já usa o valor:"},
 {"code": """given V.botao("Salvar"):
    salvar(V.entrada("Nome"))
    V.sucesso("Pronto.")""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "O preço", "texto": "A página precisa ser rápida o bastante para rodar a cada clique. Daí o [`V.cache`](/docs/vitrine/estado), que existe desde o primeiro dia e não como otimização posterior — e o [`V.formulario`](/docs/vitrine/componentes), para campos ligados a consulta pesada."}},

 {"h2": "Vitrine ou Kiln?"},
 {"p": "Os dois são frameworks web, e a escolha é clara:"},
 {"table": {"head": ["", "Kiln", "Vitrine"], "rows": [
   ["Para", "sites e APIs", "painéis e aplicações de dados"],
   ["Você escreve", "rotas que devolvem o que quiser", "um programa de cima para baixo"],
   ["A página é", "um template que você controla", "a árvore que o programa montou"],
   ["Cliente", "o que você puser lá", "~4 KB, prontos"],
   ["Exemplo", "uma loja, uma API REST", "um dashboard, um formulário interno"]]}},
 {"p": "A Vitrine **roda sobre o Kiln**: HTTP, rotas, arquivos estáticos, sessão, cabeçalhos de segurança e REST já existiam lá, testados. Reimplementá-los criaria duas implementações do mesmo protocolo para divergirem. `V.montar()` devolve o app Kiln por baixo, e nele você acrescenta rota, REST ou middleware."},
 {"callout": {"tipo": "nota", "titulo": "Por que não se chama Stream", "texto": "`Arcane.Stream` já é o módulo de streaming de dados — tópicos, partições, offsets, grupos de consumo. Duas coisas chamadas Stream no mesmo `adopt` seria exatamente a ambiguidade que este projeto passa o tempo todo evitando. *Vitrine* é onde a peça pronta é exposta; o nome segue a metáfora da forja, como Kiln, Crucible e Forge."}},

 {"h2": "Um painel completo"},
 {"code": """adopt Arcane.Vitrine as V

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
V.rodar(porta := 8501)""", "lang": "df"},
 {"h2": "Começar"},
 {"code": """dataforge vitrine new meupainel
cd meupainel
dataforge vitrine dev        # http://127.0.0.1:8501""", "lang": "bash"},
 {"p": "O projeto criado já tem página, dados, testes e um `forge.toml` — e passa nos próprios testes antes de você tocar em qualquer coisa."},
 {"p": "O painel completo do exemplo está em `examples/vitrine_dashboard.df`, e ele também se testa sozinho:"},
 {"code": """dataforge run examples/vitrine_dashboard.df              # os testes
dataforge run examples/vitrine_dashboard.df -- --servir  # no navegador""", "lang": "bash"},

 {"h2": "Zero dependência, inclusive no navegador"},
 {"p": "O gráfico é **SVG escrito no servidor**. O cliente são ~4 KB de JavaScript sem build e sem CDN — ele manda de volta o que o usuário fez e troca o miolo da página."},
 {"p": "Não é purismo: uma biblioteca de gráficos vinda de CDN quebra qualquer aplicação que rode em rede fechada, que é exatamente onde painel de dados costuma rodar. E SVG imprime, escala e é legível por leitor de tela."},

 {"h2": "Onde continuar"},
 {"cards": [
   {"href": "/docs/vitrine/componentes", "title": "Componentes", "meta": "texto, entrada, dados", "desc": "Os 40 componentes, o que cada um devolve e quando usar formulário."},
   {"href": "/docs/vitrine/layout", "title": "Layout", "meta": "colunas, abas, cartões", "desc": "Por que a área é um objeto, e não um bloco de contexto."},
   {"href": "/docs/vitrine/estado", "title": "Estado e cache", "meta": "sessão, global, TTL, LRU", "desc": "Os três lugares onde um valor mora, e quem enxerga cada um."},
   {"href": "/docs/vitrine/graficos", "title": "Gráficos", "meta": "sete tipos, em SVG", "desc": "A forma curta e a construída, e o que os dados precisam parecer."},
   {"href": "/docs/vitrine/paginas", "title": "Páginas e segurança", "meta": "rotas, login, permissões", "desc": "Multipágina, parâmetros de URL, autenticação e autorização."},
   {"href": "/docs/vitrine/acessibilidade", "title": "Acessibilidade e idioma", "meta": "ARIA, teclado, i18n", "desc": "O que já vem pronto para teclado e leitor de tela, e como traduzir."},
   {"href": "/docs/vitrine/testes", "title": "Testes", "meta": "sem navegador", "desc": "A sonda clica, digita e pergunta — e o pedido HTTP sem socket."},
   {"href": "/docs/vitrine/producao", "title": "Produção", "meta": "hot reload, métricas, plugins", "desc": "Subir, observar, e o que colocar na frente."},
   {"href": "/docs/vitrine/referencia", "title": "Referência", "meta": "105 símbolos", "desc": "Tudo o que sai de `adopt Arcane.Vitrine`, em uma tabela."}]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/vitrine/componentes",
"title": "Componentes",
"description": "Os quarenta componentes da Vitrine: texto, entrada, dados e retorno — e o que cada um devolve.",
"blocos": [
 {"p": "Todo componente faz duas coisas: **põe um nó na árvore** e **devolve o que quem escreve precisa**. É essa devolução que dispensa callback."},

 {"h2": "Texto"},
 {"code": """V.titulo("Vendas", icone := "📊")
V.subtitulo("Primeiro semestre")
V.cabecalho("Por região", nivel := 3)
V.texto("Um parágrafo.")
V.markdown("**negrito**, `código`, [link](/docs) e tabelas.")
V.codigo("x := 10", linguagem := "dataforge")
V.divisor()
V.espaco(24)""", "lang": "df"},
 {"p": "`V.texto` aceita vários argumentos e junta com espaço, como o `out`."},
 {"callout": {"tipo": "atencao", "titulo": "V.html não escapa nada", "texto": "`V.html(\"<b>x</b>\")` insere o HTML cru. É a única porta de XSS da Vitrine, e ela existe porque às vezes não há alternativa. **Nunca passe por ali algo que veio do usuário** — para isso, `V.texto`, que escapa."}},

 {"h2": "Entrada"},
 {"table": {"head": ["Componente", "Devolve", "Para"], "rows": [
   ["`V.botao(rótulo)`", "`yes` no ciclo do clique", "uma ação"],
   ["`V.entrada(rótulo)`", "o texto digitado", "uma linha de texto"],
   ["`V.area_de_texto(rótulo)`", "o texto digitado", "várias linhas"],
   ["`V.numero(rótulo)`", "o número", "quantidade, com mínimo e máximo"],
   ["`V.deslizante(rótulo, min, max)`", "o número", "escolher numa faixa"],
   ["`V.caixa(rótulo)`", "`yes`/`no`", "uma opção ligada ou desligada"],
   ["`V.interruptor(rótulo)`", "`yes`/`no`", "o mesmo, com cara de chave"],
   ["`V.opcao(rótulo, opções)`", "a escolhida", "uma de poucas, em rádio"],
   ["`V.escolha(rótulo, opções)`", "a escolhida", "uma de muitas, em lista"],
   ["`V.escolhas(rótulo, opções)`", "um cluster", "várias de muitas"],
   ["`V.data(rótulo)`", "`\"2026-03-14\"`", "uma data"],
   ["`V.cor(rótulo)`", "`\"#FED403\"`", "uma cor"],
   ["`V.arquivo(rótulo)`", "`void` ou o vault do arquivo", "enviar arquivo"]]}},
 {"code": """nome := V.entrada("Nome", "", dica := "como no documento")
senha := V.entrada("Senha", tipo := "senha")
idade := V.numero("Idade", 18, minimo := 0, maximo := 120)
fatia := V.deslizante("Desconto", 0, 100, valor := 10, passo := 5)
tags  := V.escolhas("Tags", ["novo", "urgente", "revisar"])""", "lang": "df"},

 {"h3": "O botão vale por uma execução"},
 {"p": "`V.botao` devolve `yes` **só** no ciclo em que foi clicado. Se fosse permanente, a ação dispararia de novo no próximo carregamento da página — e duplicar um pagamento é o tipo de bug que ninguém perdoa."},

 {"h3": "Formulário: quando cada tecla custa caro"},
 {"p": "Sem formulário, **cada tecla digitada roda o programa inteiro**. Num campo ligado a uma consulta pesada, isso é a diferença entre um app usável e um que trava a cada letra."},
 {"code": """forma := V.formulario("cadastro")
nome  := forma.entrada("Nome")
email := forma.entrada("E-mail", tipo := "email")

given forma.enviar("Cadastrar"):
    criar_usuario(nome, email)
    V.sucesso("Usuário cadastrado.")""", "lang": "df"},
 {"p": "Dentro do formulário, os valores só chegam ao programa quando alguém aperta o botão de envio. Com `limpar := yes`, os campos são esvaziados depois — e só os **deste** formulário, não os da página inteira."},

 {"h3": "Arquivos"},
 {"code": """arq := V.arquivo("Planilha", tipos := [".csv"], varios := no)
given arq is not void:
    V.texto($"{arq["nome"]} — {arq["tamanho"]} bytes")
    linhas := arq["texto"].lines()
    V.tabela(linhas)""", "lang": "df"},
 {"p": "O vault tem `nome`, `tamanho`, `tipo`, `conteudo` (bytes) e `texto`. Com `varios := yes`, devolve um cluster deles. O teto padrão é 8 MB, ajustável em `V.configurar(\"limite_upload\", …)`."},

 {"h3": "Validação"},
 {"p": "O erro aparece **sob o campo**, e não num alerta no topo. Num formulário de doze campos, um alerta dizendo \"há erros\" obriga a pessoa a caçar qual deles — e é a diferença entre corrigir na hora e desistir."},
 {"code": """adopt Arcane.Regex as Regex

email := V.entrada("E-mail")
V.validar(email, Regex.is_email, "Digite um e-mail válido.")

// ou com a regra junto, devolvendo (valor, esta_bom)
senha, ok := V.campo_validado("Senha", lambda s: len(s) bigger 7,
                              "Mínimo de 8 caracteres.", tipo := "senha")""", "lang": "df"},
 {"p": "A regra é uma ação que recebe o valor e devolve `yes`/`no` — e aí a mensagem é a que você passou — ou um **texto**, que vira a mensagem (vazio significa que passou)."},
 {"code": """V.validar(senha, lambda s: "" given len(s) bigger 7
                            otherwise $"faltam {8 - len(s)} caracteres")""", "lang": "df"},
 {"table": {"head": ["Comportamento", "Por quê"], "rows": [
   ["campo vazio e nunca tocado não é acusado", "reclamar antes de a pessoa digitar é ruído, não ajuda"],
   ["uma regra que **dispara** vira \"a regra de validação falhou\"", "dizer \"E-mail inválido\" ali esconderia o bug real"],
   ["o campo ganha `aria-invalid` e aponta para a mensagem", "senão quem não vê a tela descobre o erro só ao voltar nele, se voltar"]]}},

 {"h2": "Dados"},
 {"code": """V.tabela(linhas)                      // estática
V.frame(linhas)                       // com busca e ordenação
V.metrica("Receita", "R$ 850 mil", variacao := 18.0, ajuda := "vs. meta")
V.json(vault)
V.vault(vault)                        // lista de chave e valor""", "lang": "df"},
 {"p": "`V.tabela` e `V.frame` aceitam **três formas**, porque são as três que o resto da linguagem devolve:"},
 {"table": {"head": ["Forma", "Exemplo", "Vem de"], "rows": [
   ["cluster de vaults", "`[{\"a\": 1}, {\"a\": 2}]`", "`IO.read_csv`, `Banco.consultar`"],
   ["vault de colunas", "`{\"a\": [1, 2]}`", "um `group_by`"],
   ["matriz", "`[[1, 2], [3, 4]]`", "cálculo direto"]]}},
 {"p": "Um `frame` do `Arcane.Analytics` também entra direto. A ordem das colunas é a de **aparição**, e não a alfabética: quem montou o vault escolheu uma ordem, e ela costuma ser a certa."},
 {"p": "A variação da métrica é um **número** e não um texto, porque a Vitrine precisa saber o sinal: ela sobe em verde e desce em vermelho."},

 {"h2": "Retorno ao usuário"},
 {"code": """V.sucesso("Salvo.")
V.erro("Não foi possível salvar.")
V.aviso("Isto não pode ser desfeito.")
V.informacao("Os dados são de ontem.")

V.progresso(0.62, "62% processado")
V.carregando("Consultando o banco…")

V.imagem("/static/grafico.png", legenda := "Vendas")
V.audio("/static/podcast.mp3")
V.video("/static/tour.mp4")
V.link("Documentação", "/docs", nova_aba := yes)
V.baixar("Baixar relatório", texto, "relatorio.txt")""", "lang": "df"},
 {"p": "Para exportar dados já formatados, `V.exportar_csv(linhas)` e `V.exportar_json(dados)` desenham o botão e cuidam do escape."},

 {"h2": "Componentes próprios"},
 {"p": "Uma ação **já é** um componente. Chamá-la desenha o que ela desenha, e nada além disso é necessário:"},
 {"code": """action cartao_de_usuario(nome, email):
    caixa := V.cartao(nome)
    caixa.texto(email)

cartao_de_usuario("Ana", "ana@exemplo.br")""", "lang": "df"},
 {"p": "O registro por nome existe para o caso em que o nome precisa atravessar módulos — um plugin que acrescenta componentes, ou um tema que substitui um deles sem que quem chama saiba:"},
 {"code": """V.componente("usuario", cartao_de_usuario)
V.usar("usuario", "Ana", "ana@exemplo.br")

// também serve de decorador
mark @V.componente("usuario")
action cartao_de_usuario(nome, email):
    …""", "lang": "df"},
 {"p": "O registro vive na **aplicação**, e não no módulo: dois apps no mesmo processo — o que os testes fazem o tempo todo — não podem ver os componentes um do outro. E um nome errado sugere o parecido, em vez de falhar em silêncio."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/vitrine/layout",
"title": "Layout",
"description": "Colunas, abas, cartões, barra lateral e formulários — e por que a área é um objeto.",
"blocos": [
 {"h2": "A área é um objeto"},
 {"p": "Em Python isto seria um `with`. A DataForge não tem bloco de contexto, e inventar um só para o layout significaria acrescentar uma palavra reservada à linguagem inteira para resolver um problema de um módulo."},
 {"p": "A saída é o idioma que a linguagem já tem: **a área é um objeto, e os componentes são métodos dele**."},
 {"code": """colunas := V.colunas(3)
colunas[0].metrica("Vendas", "R$ 100K")
colunas[1].metrica("Clientes", "2.500")
colunas[2].metrica("Pedidos", "8.400")""", "lang": "df"},
 {"p": "Lê-se melhor, aninha sem indentação extra, e a área pode ser guardada numa variável e passada adiante — o que um `with` não permite:"},
 {"code": """action cartao_de_metrica(area, rotulo, valor):
    caixa := area.cartao(rotulo)
    caixa.metrica(rotulo, valor)
    caixa.texto("atualizado agora")

colunas := V.colunas(2)
cartao_de_metrica(colunas[0], "Receita", "R$ 850K")
cartao_de_metrica(colunas[1], "Custo", "R$ 310K")""", "lang": "df"},
 {"p": "Toda área oferece os **mesmos** componentes que `V`, mais os layouts aninhados. Aprender um ensina todos."},

 {"h2": "Colunas"},
 {"code": """V.colunas(3)              // três iguais
V.colunas([2, 1])         // a primeira com o dobro da largura
V.colunas(2, espacamento := "grande")""", "lang": "df"},
 {"p": "Abaixo de 860 px cada coluna ocupa a largura inteira — o layout é responsivo sem que você faça nada."},

 {"h2": "Barra lateral"},
 {"p": "`V.lateral()` devolve sempre a mesma área, chamada de onde for. É o lugar dos filtros:"},
 {"code": """lado := V.lateral()
lado.cabecalho("Filtros", 4)
regiao := lado.escolha("Região", ["Sul", "Norte"])
de     := lado.data("De")
ate    := lado.data("Até")
lado.divisor()
given lado.botao("Limpar", tipo := "secundario"):
    V.estado.limpar()""", "lang": "df"},
 {"p": "Se nada for posto nela, a barra não aparece."},

 {"h2": "Abas"},
 {"code": """abas := V.abas(["Resumo", "Detalhe", "Sobre"])
abas[0].metrica("Total", 128400)
abas[1].frame(linhas)
abas[2].markdown("Feito com **Arcane.Vitrine**.")""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Todas as abas são montadas", "texto": "Só a escolhida aparece, mas **todas** rodam. É uma decisão consciente: montar apenas a visível deixaria o programa com um caminho diferente por aba, e um erro escondido atrás de um clique é um erro que só aparece em produção."}},

 {"h2": "Cartões, seções e containers"},
 {"code": """cartao := V.cartao("Vendas", subtitulo := "primeiro semestre")
cartao.metrica("Receita", "R$ 850K")

secao := V.expandir("Detalhes técnicos", aberto := no)
secao.codigo(consulta_sql, linguagem := "sql")

caixa := V.container(borda := yes, altura := 320)
cycle item in muitos:
    caixa.texto(item)

barra := V.linha(alinhar := "entre")
barra.texto("Resultados")
barra.botao("Exportar", tipo := "secundario")""", "lang": "df"},
 {"p": "`V.expandir` guarda o estado de aberto ou fechado entre execuções. `V.linha` põe os filhos lado a lado, e `V.espacador()` empurra o que vem depois para a outra ponta."},

 {"h2": "Espaço reservado"},
 {"p": "`V.vazio()` reserva um lugar para ser preenchido depois — serve para escrever \"Calculando…\" e substituir pelo resultado sem que a página salte:"},
 {"code": """lugar := V.vazio()
lugar.carregando("Consultando…")
dados := consulta_demorada()
lugar.frame(dados)""", "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/vitrine/estado",
"title": "Estado e cache",
"description": "Os três lugares onde um valor pode morar numa aplicação Vitrine, e quem enxerga cada um.",
"blocos": [
 {"p": "O programa roda inteiro a cada interação. Sem um lugar que sobreviva, um contador voltaria a zero a cada clique. Há três, e a diferença entre eles é **quem enxerga**:"},
 {"table": {"head": ["Onde", "Quem vê", "Some quando"], "rows": [
   ["`V.estado`", "uma sessão", "a sessão expira"],
   ["`V.geral`", "**todas** as sessões", "o processo termina"],
   ["`V.cache`", "todas, por argumento", "o TTL vence ou é invalidado"]]}},

 {"h2": "Estado da sessão"},
 {"code": """V.estado.padrao("contador", 0)       // define só se ainda não existe

given V.botao("Incrementar"):
    V.estado.somar("contador")

V.texto($"Valor: {V.estado.obter("contador")}")""", "lang": "df"},
 {"p": "`V.estado.padrao` substitui as três linhas que todo app escreve no começo. `V.estado.somar` é **atômico**: duas abas clicando ao mesmo tempo não perdem uma das somas, o que o ler-somar-escrever à mão perderia."},
 {"table": {"head": ["Chamada", "Faz"], "rows": [
   ["`V.estado.obter(chave, padrão)`", "lê"],
   ["`V.estado.definir(chave, valor)`", "escreve"],
   ["`V.estado.padrao(chave, valor)`", "escreve só se não existe; devolve o que vale"],
   ["`V.estado.somar(chave, quanto)`", "incrementa, sem corrida"],
   ["`V.estado.existe(chave)`", "`yes`/`no`"],
   ["`V.estado.remover(chave)`", "apaga uma"],
   ["`V.estado.limpar()`", "apaga todas"],
   ["`V.estado.tudo()`", "o vault, sem as chaves internas"],
   ["`V.estado.id()`", "o identificador da sessão"]]}},

 {"h2": "Estado global"},
 {"p": "`V.geral` é compartilhado por **todas** as sessões — configuração, um contador de visitas, um modelo de ML carregado uma vez."},
 {"code": """V.geral.definir("versao", "1.0.0")
V.geral.somar("visitas")""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Não guarde ali o que é de um usuário", "texto": "Dois visitantes veriam os dados um do outro, e nada daria erro. A trava protege o dicionário, não a lógica de quem lê-e-depois-escreve — para contar, `V.geral.somar`, que é atômico."}},

 {"h2": "Cache"},
 {"p": "`mark @V.cache` sobre uma ação, e ela para de recalcular. Vale **por argumento**: `vendas(\"2026-01\")` e `vendas(\"2026-02\")` ocupam entradas diferentes."},
 {"code": """mark @V.cache
action vendas(mes):
    yield Banco.consultar("SELECT … WHERE mes = ?", [mes])""", "lang": "df"},
 {"p": "Com ajustes:"},
 {"code": """mark @V.cache(validade := 300, teto := 32)
action cotacao(moeda):
    yield Http.get($"https://…/{moeda}").json()

mark @V.cache(pasta := ".cache/ibge")
action municipios():
    yield Http.get("https://…/municipios").json()""", "lang": "df"},
 {"table": {"head": ["Opção", "Faz"], "rows": [
   ["`validade`", "segundos até o valor vencer (TTL)"],
   ["`teto`", "quantos valores guardar; ao encher, sai o menos usado (LRU)"],
   ["`pasta`", "também grava em disco, e sobrevive a reiniciar"]]}},
 {"p": "O teto existe porque um cache sem limite é um vazamento com outro nome: uma ação chamada com mil argumentos diferentes guardaria mil resultados e não soltaria nenhum."},

 {"h3": "Esvaziar"},
 {"code": """V.cache.invalidar(vendas)     // só essa ação
V.cache.invalidar()           // tudo
V.cache.estatisticas()        // acertos, erros e taxa, por ação""", "lang": "df"},
 {"p": "E `vendas.sem_cache(mes)` chama a ação original — é o que permite testá-la sem o cache no caminho."},
 {"callout": {"tipo": "nota", "titulo": "O cache em disco só guarda o que vira JSON", "texto": "Guardar objeto arbitrário exigiria `pickle`, e ler `pickle` de um arquivo que outro processo escreveu é execução de código. Num framework web, isso é a porta aberta. Um valor que não vira JSON continua valendo em memória."}},

 {"h2": "Identidade do componente"},
 {"p": "O valor de um campo sobrevive a um clique em outro lugar da página porque cada componente tem uma **chave**. Sem `chave`, ela sai do tipo, do rótulo e da posição — estável enquanto o programa não muda."},
 {"code": """// Dê uma chave quando a ordem dos componentes pode mudar:
cycle cliente in clientes:
    V.entrada("Observação", chave := $"obs-{cliente["id"]}")""", "lang": "df"},
 {"p": "Sem a chave explícita aqui, remover um cliente da lista faria as observações dos seguintes escorregarem uma posição."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/vitrine/graficos",
"title": "Gráficos",
"description": "Sete tipos de gráfico, desenhados em SVG no servidor — sem biblioteca e sem CDN.",
"blocos": [
 {"h2": "A forma curta"},
 {"code": """V.grafico_linha(dados, x := "mes", y := "receita")
V.grafico_barras(dados, x := "mes", y := ["receita", "meta"])
V.grafico_area(dados, x := "dia", y := "acumulado")
V.grafico_dispersao(dados, x := "peso", y := "altura")
V.grafico_pizza(dados, x := "categoria", y := "valor")
V.grafico_rosca(dados, x := "categoria", y := "valor")
V.grafico_barras_h(dados, x := "produto", y := "vendas")
V.histograma(dados, campo := "idade", faixas := 12)""", "lang": "df"},
 {"p": "Sem `x` e `y`, a Vitrine adivinha: a primeira coluna não numérica vira o eixo, e as numéricas viram as séries. É o suficiente para um `V.grafico_linha(vendas)` funcionar na primeira tentativa."},

 {"h2": "A forma construída"},
 {"p": "Quando há mais a dizer:"},
 {"code": """g := V.grafico("barras", vendas)
g.eixo_x("mes")
g.eixo_y(["receita", "meta"])
g.titulo("Vendas por período")
g.cores(["#FED403", "#0F62FE"])
g.altura(340)
g.empilhar(yes)
g.rotular(yes)
g.limite_y(0, 1000)
V.desenhar(g)""", "lang": "df"},
 {"p": "Cada método devolve o próprio gráfico, então também dá para encadear. Nada aparece na página até `V.desenhar`."},
 {"table": {"head": ["Método", "Faz"], "rows": [
   ["`eixo_x(campo)`", "a coluna das categorias"],
   ["`eixo_y(campo)`", "uma coluna, ou um cluster delas"],
   ["`serie(campo)`", "acrescenta mais uma ao mesmo gráfico"],
   ["`titulo(texto)`", "o título acima"],
   ["`cores(cluster)`", "a paleta"],
   ["`altura(px)`", "a altura do desenho"],
   ["`empilhar(yes)`", "barras somadas em vez de lado a lado"],
   ["`suavizar(yes)`", "curva em vez de linha reta"],
   ["`rotular(yes)`", "o valor escrito sobre cada barra"],
   ["`legenda(no)` · `grade(no)`", "desliga a legenda ou a grade"],
   ["`limite_y(min, max)`", "fixa a escala"]]}},

 {"h2": "O que os dados precisam parecer"},
 {"p": "As mesmas três formas de `V.tabela`, mais uma quarta que um `group_by` costuma devolver:"},
 {"code": """[{"mes": "Jan", "receita": 120}]       // cluster de vaults
{"mes": ["Jan"], "receita": [120]}     // vault de colunas
[["Jan", 120]]                         // matriz
{"Sul": 120, "Norte": 90}              // rótulo → número""", "lang": "df"},

 {"h2": "Por que SVG no servidor"},
 {"p": "Uma dependência de JavaScript obrigaria a página a buscar centenas de kilobytes de uma CDN, o que quebra qualquer aplicação que rode numa rede fechada — e é exatamente onde painel de dados costuma rodar."},
 {"p": "SVG também imprime, escala, é legível por leitor de tela, e o arquivo que sai daqui é o mesmo em qualquer navegador. A escala do eixo é arredondada para um número redondo: um eixo que vai até 1 237 não ajuda ninguém a ler o gráfico; até 1 500, com marcas de 500 em 500, ajuda."},
 {"callout": {"tipo": "nota", "titulo": "A paleta padrão", "texto": "A primeira cor é o amarelo da marca; as demais foram escolhidas para continuarem distinguíveis em escala de cinza e para quem não separa vermelho de verde — 8% dos homens. `V.paleta` traz as dez."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/vitrine/paginas",
"title": "Páginas e segurança",
"description": "Multipágina, rotas com parâmetro, autenticação, permissões e os cabeçalhos que toda resposta leva.",
"blocos": [
 {"h2": "Várias páginas"},
 {"code": """V.app("Painel")

V.pagina("/", inicio, titulo := "Início", icone := "🏠")
V.pagina("/vendas", vendas, titulo := "Vendas", icone := "📊")
V.pagina("/produto/:id", produto, oculta := yes)

V.rodar(porta := 8501)""", "lang": "df"},
 {"p": "Também funciona como decorador:"},
 {"code": """mark @V.pagina("/vendas")
action vendas():
    V.titulo("Vendas")""", "lang": "df"},
 {"p": "`V.menu()` desenha o menu das páginas registradas na barra lateral, na ordem do registro. Uma página `oculta` continua alcançável pela URL e não aparece no menu."},

 {"h2": "Parâmetros"},
 {"code": """action produto():
    id := V.parametro("id")              // da rota: /produto/:id
    ordem := V.parametro("ordem", "asc")  // da query: ?ordem=desc
    V.titulo($"Produto {id}")""", "lang": "df"},
 {"p": "`V.parametros()` devolve os dois juntos; `V.caminho()` devolve onde a página está."},

 {"h2": "Navegar e parar"},
 {"code": """V.navegar("/entrar")      // vai para outra página, e para aqui
V.parar()                 // acaba a página neste ponto, sem erro
V.recarregar()            // roda de novo, do começo, jogando fora a árvore""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "V.recarregar() tem teto", "texto": "Quatro reexecuções por interação. Um `V.recarregar()` sem `given` em volta vira uma mensagem na página — e não um servidor travado."}},

 {"h2": "Autenticação"},
 {"p": "Registre a ação que confere usuário e senha. Ela recebe os dois e devolve o vault do usuário, ou `void`:"},
 {"code": """action conferir(usuario, senha):
    linha := Banco.um("SELECT * FROM usuarios WHERE email = ?", [usuario])
    given linha is not void and Crypto.conferir_senha(senha, linha["hash"]):
        yield {"nome": linha["nome"], "papel": linha["papel"]}
    yield void

V.autenticacao(conferir, {
    "admin":  ["ver", "editar", "apagar"],
    "leitor": ["ver"]
})""", "lang": "df"},
 {"p": "E a barreira, na primeira linha de cada página protegida:"},
 {"code": """action relatorio():
    V.exigir_login()
    V.titulo($"Olá, {V.usuario()["nome"]}")

action edicao():
    V.exigir_permissao("editar")
    V.titulo("Edição")""", "lang": "df"},
 {"p": "`V.exigir_login()` desenha o formulário de entrada e **para** a página. Quando já há alguém logado, ela devolve o usuário e não desenha nada — o que permite chamá-la sempre na primeira linha."},
 {"callout": {"tipo": "dica", "titulo": "O login reexecuta a página do começo", "texto": "Continuar de onde parou parece mais barato e não funciona: quem escreveu `given V.autenticado(): …` já passou por esse teste com a resposta antiga, e a tela sairia vazia no instante em que a pessoa acertou a senha."}},
 {"table": {"head": ["Chamada", "Devolve"], "rows": [
   ["`V.usuario()`", "o vault de quem está logado, ou `void`"],
   ["`V.autenticado()`", "`yes`/`no`"],
   ["`V.pode(permissão)`", "`yes`/`no`, pelo papel"],
   ["`V.entrar(usuario, senha)`", "o vault, ou `void`"],
   ["`V.sair()`", "derruba a sessão de quem está logado"]]}},

 {"h2": "Segurança"},
 {"p": "Toda resposta HTML leva estes cabeçalhos, sem configuração:"},
 {"table": {"head": ["Cabeçalho", "Contra"], "rows": [
   ["`X-Content-Type-Options: nosniff`", "o navegador adivinhar o tipo do conteúdo"],
   ["`X-Frame-Options: SAMEORIGIN`", "clickjacking"],
   ["`Referrer-Policy`", "vazar a URL inteira para terceiros"],
   ["`Content-Security-Policy`", "script de outra origem"]]}},
 {"p": "O cookie de sessão é `HttpOnly` e `SameSite=Lax`. Com `V.configurar(\"https\", yes)` ele também ganha `Secure`."},
 {"p": "Todo texto que vai à página é escapado — o único que não é passa por `V.html`, que avisa disso. E `V.markdown` escapa **antes** de reconhecer a marcação, além de recusar link `javascript:`."},
 {"p": "Para limite de taxa e CORS, use o middleware do Kiln sobre `V.montar()` — ver [Middleware do Kiln](/docs/kiln/middleware)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/vitrine/acessibilidade",
"title": "Acessibilidade e idioma",
"description": "O que a Vitrine já faz por quem usa teclado e leitor de tela, e como traduzir a aplicação.",
"blocos": [
 {"h2": "O que vem pronto"},
 {"p": "Nada disto precisa ser ligado. É como os componentes são desenhados."},
 {"table": {"head": ["O quê", "Como"], "rows": [
   ["HTML semântico", "`<main>`, `<aside>`, `<fieldset>`/`<legend>`, `<table>` com `<thead>`"],
   ["Link para pular a navegação", "o primeiro elemento da página, visível só ao receber foco"],
   ["Foco sempre visível", "`:focus-visible` com contorno de 2 px, em todo elemento interativo"],
   ["Rótulo ligado ao campo", "`<label for>` em todos os campos com rótulo"],
   ["Erro anunciado", "`role=\"alert\"` na mensagem, `aria-invalid` e `aria-describedby` no campo"],
   ["Abas pelo teclado", "`role=\"tablist\"`, setas ← →, Home e End, e só a ativa no caminho do Tab"],
   ["Alerta com a urgência certa", "`role=\"alert\"` para erro e aviso, `role=\"status\"` para o resto"],
   ["Progresso legível", "`role=\"progressbar\"` com `aria-valuenow` e `aria-label`"],
   ["Movimento respeitado", "`prefers-reduced-motion` desliga as animações"],
   ["Tema do sistema", "`prefers-color-scheme` escolhe claro ou escuro sozinho"]]}},
 {"callout": {"tipo": "nota", "titulo": "A seta ▲ não diz \"aumento de\"", "texto": "A variação de uma métrica sai com o símbolo marcado `aria-hidden` e a palavra ao lado, visível só para leitor de tela. Cor e seta sozinhas excluem quem não vê a tela **e** quem não separa vermelho de verde — 8% dos homens."}},
 {"p": "A paleta clara usa `#B28600` como primária, e não o amarelo `#FED403` da marca: amarelo sobre branco dá contraste 1,3:1, e a WCAG pede 4,5:1 para texto. O amarelo continua sendo a marca no tema escuro, onde ele funciona."},

 {"h2": "O que fica com você"},
 {"table": {"head": ["O quê", "Como fazer"], "rows": [
   ["Texto alternativo de imagem", "`V.imagem(origem, legenda := \"…\")` — a legenda vira o `alt`"],
   ["Ordem de leitura", "é a ordem do programa; escreva na ordem em que se lê"],
   ["Rótulo que descreve", "`V.botao(\"Excluir pedido 42\")` diz mais que `V.botao(\"Excluir\")`"],
   ["Contraste do seu tema", "se trocar as cores, confira 4,5:1 para texto e 3:1 para borda"],
   ["`V.html`", "o que você puser ali passa cru, sem nenhuma dessas garantias"]]}},

 {"h2": "Idioma"},
 {"p": "Carregue as chaves e peça o texto. O idioma é **por sessão**: dois visitantes podem estar lendo a mesma página em línguas diferentes, e guardar isso num lugar só faria um trocar o idioma do outro."},
 {"code": """V.i18n.carregar("pt-BR", {
    "painel.titulo": "Painel de Vendas",
    "ola": "Olá, {nome}",
    "vazio": "Nenhum resultado."
})
V.i18n.carregar("en-US", {
    "painel.titulo": "Sales Dashboard",
    "ola": "Hello, {nome}",
    "vazio": "No results."
})

action painel():
    V.titulo(V.t("painel.titulo"))
    V.texto(V.t("ola", nome := V.usuario()["nome"]))""", "lang": "df"},
 {"table": {"head": ["Chamada", "Faz"], "rows": [
   ["`V.i18n.carregar(idioma, vault)`", "acrescenta chaves a um idioma"],
   ["`V.i18n.idioma()`", "o idioma desta sessão"],
   ["`V.i18n.idioma(\"en-US\")`", "troca, e reexecuta a página"],
   ["`V.i18n.idiomas()`", "os carregados"],
   ["`V.i18n.seletor(\"Idioma\")`", "desenha a troca, pronta"],
   ["`V.t(chave, …)`", "o texto, com `{nome}` substituído"]]}},
 {"callout": {"tipo": "dica", "titulo": "Uma chave sem tradução aparece crua", "texto": "`V.t(\"painel.titulo\")` sem tradução devolve `painel.titulo`, e não vazio. Feio o bastante na tela para alguém corrigir, e informativo o bastante para dizer **qual** chave falta."}},
 {"p": "O seletor troca o idioma e **reexecuta a página**: mudá-lo no meio deixaria a metade de cima na língua anterior."},
 {"code": """V.lateral().espaco(8)
V.i18n.seletor("Idioma", {"pt-BR": "Português", "en-US": "English"})""", "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/vitrine/testes",
"title": "Testar sem navegador",
"description": "A sonda clica, digita e pergunta; e o pedido HTTP roda sem socket.",
"blocos": [
 {"p": "O framework foi desenhado para isto: a árvore de componentes é um **dado**, e conferir um dado é o que um teste sabe fazer."},
 {"code": """adopt Arcane.Vitrine as V
adopt Crucible

action painel():
    V.titulo("Painel")
    given V.botao("Somar"):
        V.estado.somar("total")
    V.metrica("Total", V.estado.obter("total", 0))

crucible "o painel":
    trial "o botão soma":
        t := V.testar(painel)
        t.clicar("Somar")
        assert t.metrica("Total") is "1"

    trial "e não soma sozinho":
        t := V.testar(painel)
        t.rodar()
        assert t.metrica("Total") is "0\"""", "lang": "df"},

 {"h2": "Agir"},
 {"table": {"head": ["Chamada", "Faz"], "rows": [
   ["`t.clicar(rótulo)`", "clica no botão e roda a página de novo"],
   ["`t.digitar(rótulo, valor)`", "preenche um campo"],
   ["`t.marcar(rótulo, yes)`", "liga uma caixa ou interruptor"],
   ["`t.selecionar(rótulo, valor)`", "escolhe numa lista"],
   ["`t.abrir_aba(rótulo)`", "troca de aba"],
   ["`t.enviar(formulário)`", "aperta o botão de envio"],
   ["`t.enviar_arquivo(rótulo, nome, conteúdo)`", "simula um upload"],
   ["`t.ir_para(caminho)`", "vai para outra página"],
   ["`t.rodar()`", "roda de novo, sem interação"]]}},

 {"h2": "Perguntar"},
 {"table": {"head": ["Chamada", "Devolve"], "rows": [
   ["`t.texto()`", "a página como texto corrido — para `assert \"erro\" in …`"],
   ["`t.achar(tipo)`", "todos os nós de um tipo"],
   ["`t.primeiro(tipo)`", "o primeiro"],
   ["`t.quantos(tipo)`", "quantos existem"],
   ["`t.existe(tipo, rótulo)`", "`yes`/`no`"],
   ["`t.metrica(rótulo)`", "o valor de uma métrica"],
   ["`t.valor(rótulo)`", "o valor de um campo"],
   ["`t.alertas(nível)`", "as mensagens de sucesso, erro, aviso"],
   ["`t.estado(chave)`", "o estado da sessão"],
   ["`t.falhou()` · `t.falhas()`", "se algo disparou, e o quê"],
   ["`t.html()` · `t.arvore()`", "a página como HTML, ou como vault"]]}},
 {"p": "Quando um rótulo não existe, a mensagem lista os que existem na página — o erro mais comum ao escrever um teste é errar o texto do botão."},

 {"h2": "HTTP de verdade, sem socket"},
 {"p": "A sonda pula o HTTP. Para testar status, cabeçalho e redirecionamento, `V.pedir`:"},
 {"code": """r := V.pedir(app, "GET", "/")
assert r["status"] is 200
assert r["headers"]["X-Content-Type-Options"] is "nosniff"

r2 := V.pedir(app, "GET", "/produto/42")
assert "Produto 42" in r2["body"]""", "lang": "df"},
 {"p": "É o `Kiln.test` por baixo: executa a rota inteira, com middleware, sem abrir porta nenhuma."},
 {"callout": {"tipo": "atencao", "titulo": "O que só aparece com um servidor de verdade", "texto": "`V.pedir` roda tudo numa thread e para antes do cabeçalho `Set-Cookie`. Bug de concorrência e bug de cookie só aparecem com `V.servir(0)` e um cliente HTTP real — foi assim que se descobriu um cookie malformado que fazia cada pedido abrir uma sessão nova, com o sintoma de um contador que nunca passava de 1."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/vitrine/producao",
"title": "Produção",
"description": "Subir, recarregar ao salvar, observar, estender com plugins e o que colocar na frente.",
"blocos": [
 {"h2": "A linha de comando"},
 {"code": """dataforge vitrine new meupainel   # cria o projeto
dataforge vitrine dev             # sobe recarregando ao salvar
dataforge vitrine run             # sobe, sem recarregar
dataforge vitrine doctor          # diz por que ela não sobe

dataforge vitrine dev --porta=8600 --host=0.0.0.0""", "lang": "bash"},
 {"p": "Sem argumento, ele procura `main.df`, `app.df`, `painel.df` e `src/main.df`, nessa ordem, e depois a entrada do `forge.toml`. A porta e o host da linha de comando **vencem** o que está escrito no arquivo — é o que permite trocar a porta sem editar o programa."},
 {"p": "O `doctor` responde as perguntas de quem está vendo uma tela em branco, da causa mais provável para a menos: o módulo carrega, o Kiln está lá, existe um arquivo que sobe, ele compila, ele adota a Vitrine, ele chama `V.subir`, a porta está livre."},
 {"callout": {"tipo": "nota", "titulo": "Não há `build` nem `deploy`", "texto": "Não existe etapa de build numa aplicação Vitrine: sem bundler, sem transpilação, sem `node_modules` — o que roda é o próprio `.df`. E `deploy` seria inventar uma opinião sobre Docker, systemd ou nuvem que o projeto não tem. Os dois comandos existem só para **explicar isso** a quem veio de outro framework, em vez de responder \"comando desconhecido\"."}},
 {"p": "Para distribuir o projeto, `dataforge pack`."},

 {"h2": "Subir"},
 {"code": """V.rodar(painel, porta := 8501)                 // uma página
V.subir(porta := 8501, recarregar := yes)      // com hot reload
porta := V.servir(0)                            // em segundo plano
V.parar_servidor()""", "lang": "df"},
 {"p": "`V.servir(0)` deixa o sistema escolher a porta e devolve qual foi — é o que torna um teste de integração independente de porta ocupada."},

 {"h2": "Hot reload"},
 {"p": "Com `recarregar := yes`, salvar um `.df` do projeto **reinicia o processo**. Reiniciar, e não recarregar o módulo: o estado de um módulo recarregado pela metade produz erros que não existem no código, e depurar isso custa mais do que o segundo do reinício."},

 {"h2": "Configuração"},
 {"code": """V.app("Painel",
      icone := "📊",
      descricao := "Vendas da Forja Ltda.",
      tema := "escuro",
      producao := yes,
      validade_sessao := 1800,
      limite_upload := 4194304)

V.configurar("atualizar_a_cada", 30)""", "lang": "df"},
 {"table": {"head": ["Chave", "Faz"], "rows": [
   ["`titulo` · `icone` · `descricao`", "aba do navegador e metadados"],
   ["`tema`", "`\"claro\"`, `\"escuro\"` ou um vault de cores"],
   ["`modo_tema`", "`\"automatico\"` segue o sistema de quem abre"],
   ["`producao`", "esconde o detalhe do erro e o diagnóstico"],
   ["`validade_sessao`", "segundos até a sessão ociosa sair da memória"],
   ["`limite_upload`", "bytes por arquivo enviado"],
   ["`atualizar_a_cada`", "segundos entre recargas automáticas"],
   ["`css` · `javascript`", "o seu, injetado na página"],
   ["`manifesto`", "serve um manifesto PWA em `/__vitrine__/manifesto.json`"],
   ["`https`", "marca o cookie de sessão como `Secure`"]]}},

 {"h3": "Tema"},
 {"code": """V.configurar("tema", {
    "primaria": "#0F62FE",
    "raio": "4px",
    "largura": "1400px"
})""", "lang": "df"},
 {"p": "Um tema é um vault de variáveis CSS. Mudar a cor primária muda o botão, o link, o foco, a borda do campo e a primeira série do gráfico ao mesmo tempo — e não em nove lugares. Um tema parcial completa o que falta a partir do claro **e** do escuro, para que quem trocou a primária não perca o modo escuro por isso."},

 {"h2": "Observabilidade"},
 {"code": """V.registrar("consulta lenta", "aviso", {"ms": 1840})
V.logs(50, "erro")
V.metricas()      // execuções, erros, média em ms, sessões, cache
V.saude()         // o que um balanceador pergunta""", "lang": "df"},
 {"p": "Duas rotas vêm prontas: `GET /__vitrine__/saude` e `GET /__vitrine__/metricas`. O log em memória tem teto de 2 000 linhas — sem teto, ele é um vazamento que só aparece depois de semanas no ar."},

 {"h2": "Middleware"},
 {"code": """action so_de_dia(ctx):
    given Time.hora() bigger 22:
        V.aviso("O painel está fechado à noite.")
        yield no                  // 'no' interrompe a página
    yield yes

V.antes(so_de_dia)""", "lang": "df"},
 {"p": "`V.antes` roda antes de toda página e pode interromper; `V.depois` recebe o contexto já montado. Para middleware de **HTTP** — CORS, limite de taxa, compressão —, use o do Kiln sobre `V.montar()`."},

 {"h2": "Trabalho fora do pedido"},
 {"code": """V.tarefa(enviar_email, destinatario)    // roda numa thread, não espera
V.agendar(recalcular_totais, 3600)      // de hora em hora""", "lang": "df"},
 {"p": "`V.tarefa` é para o que a página não vai mostrar agora. Para um resultado que a página precisa, `Arcane.Async`, que tem `await`. O primeiro disparo de `V.agendar` é depois do primeiro intervalo — agendar algo \"a cada hora\" não deveria fazê-lo agora e de novo em uma hora."},

 {"h2": "Plugins"},
 {"code": """action tema_da_empresa(app):
    app.configurar("tema", {"primaria": "#7B1FA2"})
    app.configurar("css", ".v-titulo { letter-spacing: -.03em }")

V.plugin("tema-empresa", tema_da_empresa)""", "lang": "df"},
 {"p": "Um plugin é uma ação que recebe a aplicação e acrescenta algo. Registrar duas vezes o mesmo nome é **erro**, e não substituição silenciosa: quase sempre é um `adopt` duplicado, e descobrir isso por um comportamento que sumiu é caro."},

 {"h2": "O que colocar na frente"},
 {"callout": {"tipo": "atencao", "titulo": "Em produção pública, ponha um nginx ou Caddy na frente", "texto": "A Vitrine roda sobre o Kiln, que roda sobre o `http.server` do Python: não há HTTP/2, TLS nem streaming de resposta. O proxy cuida de TLS, compressão e arquivos estáticos; a Vitrine cuida da aplicação."}},
 {"p": "E a sessão vive **na memória do processo**. Com mais de um processo, dois pedidos da mesma pessoa caem em memórias diferentes — para escalar horizontalmente, uma sessão compartilhada precisa existir primeiro. Um processo por aplicação, com o proxy na frente, é a forma testada."},

 {"h2": "Atualização automática"},
 {"code": """action acompanhar():
    V.atualizar_a_cada(15)
    V.metrica("Fila", tamanho_da_fila())""", "lang": "df"},
 {"p": "A página se recarrega sozinha nesse intervalo — e **não** quando a aba está escondida, porque cobrar do servidor por uma página que ninguém está vendo é desperdício puro."},
 {"p": "É o \"tempo real\" do framework, e ele é por pergunta e não por empurrão: o Kiln não tem WebSocket. Para um painel que muda a cada segundos, perguntar é suficiente e não quebra atrás de proxy nenhum."},
]},
]
