// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "57 · Vitrine — o painel",
  description: "15 exercícios: painéis com layout, gráficos, grade, cache e sessão.",
};

const blocos: Bloco[] = [
  {"p": "Nível: **Aplicações** · painéis com layout, gráficos, grade, cache e sessão · [todos os módulos](/docs/exercicios)"},
  { code: `python3 exercicios/run_all.py 57`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[373](#373-o-programa-de-cima-para-baixo-que-vira-pagina)", "**o programa de cima para baixo que vira pagina**", "o modelo da Vitrine e o que dispensa callback e diffing —"], ["[374](#374-a-area-de-layout-e-um-objeto)", "**a area de layout e um OBJETO**", "a linguagem nao tem 'with', e inventar uma palavra"], ["[375](#375-o-grafico-e-svg-escrito-no-servidor)", "**o grafico e SVG escrito no servidor**", "zero dependencia tambem no navegador. Uma biblioteca de"], ["[376](#376-a-grade-ordena-no-servidor)", "**a grade ordena NO SERVIDOR**", "a diferenca entre 'V.grade' e 'V.frame' nao e de"], ["[377](#377-o-cache-nao-e-opcional)", "**o cache nao e opcional**", "o programa INTEIRO roda de novo a cada interacao. Sem"], ["[378](#378-quem-esta-vendo-o-painel)", "**quem esta vendo o painel**", "'exigir_login' PARA a pagina. Ela levanta um sinal que"], ["[379](#379-mais-de-uma-pagina)", "**mais de uma pagina**", "o que nao casa com pagina nenhuma cai no tratador de 404"], ["[380](#380-o-formulario-que-so-envia-uma-vez)", "**o formulario que so envia uma vez**", "sem formulario, CADA campo reexecuta o programa. Num"], ["[381](#381-o-que-se-escreve-numa-pagina)", "**o que se escreve numa pagina**", "'V.escrever' e polimorfico — ele decide o componente"], ["[382](#382-os-campos-e-o-que-mudou-responde)", "**os campos, e o que 'mudou' responde**", "toda entrada devolve o valor de agora. O que faltava era"], ["[383](#383-o-layout-diz-ao-grafico-a-largura-em-que-ele-vai-aparecer)", "**o layout diz ao grafico a largura em que ele vai aparecer**", "o desenho e feito num sistema de 800 unidades e o CSS o"], ["[384](#384-redesenhar-so-um-pedaco)", "**redesenhar so um pedaco**", "o fragmento existe porque redesenhar a pagina inteira a"], ["[385](#385-tirar-o-dado-de-dentro-do-painel)", "**tirar o dado de dentro do painel**", "todo painel acaba com alguem pedindo \"manda isso em"], ["[386](#386-onde-a-sessao-mora)", "**onde a sessao mora**", "a sessao na memoria do processo some quando ele"], ["[387](#387-o-mapa-e-as-nove-decisoes)", "**o mapa, e as nove decisoes**", "fechar a trilha com o que a Vitrine resolve, o que ela"]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "373 · o programa de cima para baixo que vira pagina"},
  {"p": "**Enunciado.** o modelo da Vitrine e o que dispensa callback e diffing —"},
  { code: `// o programa INTEIRO roda de novo a cada interacao, e o estado da
// sessao sobrevive. E e isso que torna 'V.cache' obrigatorio, e nao
// opcional.

adopt Arcane.Vitrine as V

action painel():
    V.titulo("Vendas")
    V.metrica("Total", "R$ 1.250", variacao := "+12%")

    nome := V.entrada("Seu nome", "Ana")
    V.texto($"Ola, {nome}")

    given V.botao("Somar"):
        V.estado["n"] := (V.estado["n"] ?? 0) + 1

    V.texto($"clicou {V.estado['n'] ?? 0} vez(es)")

out "== 1. a arvore, sem navegador =="

t := V.testar(painel)
assert not t.falhou()
assert t.existe("titulo")
assert t.existe("metrica")
assert t.quantos("texto") is 2
out $"   {len(t.arvore())} no(s) na pagina"

out ""
out "== 2. o texto que saiu =="

assert "Ola, Ana" in t.texto()
assert "clicou 0" in t.texto()

out ""
out "== 3. digitar reexecuta o programa =="

t.digitar("Seu nome", "Bia")
assert "Ola, Bia" in t.texto()
out "   nenhum callback: o programa rodou de novo"

out ""
out "== 4. e o estado da sessao sobrevive =="

t.clicar("Somar")
assert "clicou 1" in t.texto()
t.clicar("Somar")
assert "clicou 2" in t.texto()
assert t.estado("n") is 2

// E o nome continua o que foi digitado.
assert "Ola, Bia" in t.texto()

out ""
out "== 5. o botao e verdadeiro UMA vez =="

// Ele nao e um callback: e um valor que vale 'yes' na execucao em que
// foi clicado, e 'no' em todas as outras.
t.digitar("Seu nome", "Caio")
assert "clicou 2" in t.texto()
out "   a reexecucao por outro motivo nao repetiu o clique"

out "exercicio 373 ok"`, lang: 'df', title: `exercicios/57-vitrine-painel/373_um_painel_em_dez_linhas.df` },
  {"p": "O modelo da Vitrine é o que dispensa callback e diffing: o programa **inteiro** roda de novo a cada interação, e o estado da sessão sobrevive."},
  {"h3": "Digitar reexecuta o programa"},
  {"p": "Nenhum callback: o valor novo entra, e a página é montada de novo do começo."},
  {"h3": "E o estado da sessão sobrevive"},
  {"p": "É o que torna o modelo utilizável: sem ele, um contador voltaria a zero a cada clique."},
  {"h3": "O botão é verdadeiro UMA vez"},
  {"p": "Ele não é um callback: é um valor que vale `yes` na execução em que foi clicado, e `no` em todas as outras — inclusive nas reexecuções por outro motivo."},
  {"p": "---"},
  {"p": "E é isso que torna `V.cache` obrigatório, e não opcional."},
  {"h2": "374 · a area de layout e um OBJETO"},
  {"p": "**Enunciado.** a linguagem nao tem 'with', e inventar uma palavra"},
  { code: `// reservada para o layout de um modulo seria caro demais.
// 'colunas[0].metrica(…)' le melhor, aninha sem indentacao e pode ser
// passado adiante — que e o que um bloco de contexto nao permite.

adopt Arcane.Vitrine as V

action painel():
    V.titulo("Painel")

    c := V.colunas(3)
    c[0].metrica("Receita", "R$ 1,2 mi", variacao := "+8%")
    c[1].metrica("Custo", "R$ 700 mil", variacao := "-3%")
    c[2].metrica("Margem", "42%")

    abas := V.abas(["Resumo", "Detalhe"])
    abas[0].texto("o resumo")
    abas[1].texto("o detalhe")

    cartao := V.cartao("Alertas")
    cartao.aviso("o estoque esta baixo")

    // E a area pode ser PASSADA ADIANTE.
    desenhar_rodape(V.painel("Rodape"))

action desenhar_rodape(area):
    area.texto("atualizado ha 5 minutos")

out "== 1. tres colunas, tres metricas =="

t := V.testar(painel)
assert not t.falhou()
assert t.quantos("metrica") is 3
assert t.quantos("colunas") is 1

out ""
out "== 2. as abas =="

assert t.quantos("abas") is 1
assert "o resumo" in t.texto()

out ""
out "== 3. o cartao, e o aviso dentro dele =="

assert t.quantos("cartao") is 1
assert "estoque esta baixo" in t.texto()

out ""
out "== 4. e a area passada adiante desenhou =="

assert "atualizado ha 5 minutos" in t.texto()
out "   uma acao que recebe uma area desenha nela"

out ""
out "== 5. por que nao um bloco de contexto =="

out "   sem 'with', um bloco exigiria palavra reservada nova"
out "   e um objeto aninha sem indentacao e atravessa a chamada"

out ""
out "== 6. a arvore inteira, para conferir =="

// 'arvore()' devolve os nos DE TOPO: os filhos moram dentro deles,
// e e por isso que a conta e 4 e nao 12.
assert len(t.arvore()) is 4
out $"   {len(t.arvore())} nos de topo, e os filhos dentro deles"
assert t.quantos("metrica") is 3

out "exercicio 374 ok"`, lang: 'df', title: `exercicios/57-vitrine-painel/374_layout.df` },
  {"p": "A linguagem não tem `with`, e inventar uma palavra reservada para o layout de um módulo seria caro demais."},
  {"h3": "Ele aninha sem indentação"},
  {"p": "`colunas[0].metrica(…)` lê melhor que um bloco de contexto, e não consome um nível a cada camada."},
  {"h3": "E pode ser PASSADO ADIANTE"},
  {"p": "Uma ação que recebe uma área desenha nela. Um bloco de contexto não atravessa a chamada."},
  {"h3": "`arvore()` devolve os nós de TOPO"},
  {"p": "Os filhos moram dentro deles — a contagem de topo não é a contagem de componentes."},
  {"h2": "375 · o grafico e SVG escrito no servidor"},
  {"p": "**Enunciado.** zero dependencia tambem no navegador. Uma biblioteca de"},
  { code: `// CDN quebra qualquer app em rede fechada — que e onde painel de
// dados costuma rodar.

adopt Arcane.Vitrine as V

steady MESES := ["jan", "fev", "mar", "abr", "mai", "jun"]
steady RECEITA := [120.0, 135.0, 128.0, 160.0, 175.0, 190.0]
steady CUSTO := [80.0, 82.0, 85.0, 90.0, 95.0, 98.0]

action painel():
    V.titulo("Grafico")
    V.grafico_linha(MESES, {"receita": RECEITA, "custo": CUSTO})
    V.grafico_barras(MESES, {"receita": RECEITA})
    V.grafico_pizza(["A", "B", "C"], [30.0, 45.0, 25.0])
    V.grafico_area(MESES, {"receita": RECEITA})

out "== 1. quatro graficos =="

t := V.testar(painel)
assert not t.falhou()
assert t.quantos("grafico") is 4

out ""
out "== 2. e o SVG sai do servidor =="

html := t.html()
assert "<svg" in html
assert "polyline" in html or "path" in html

out ""
out "== 3. nenhuma CDN =="

// Ha teste no repositorio proibindo 'http://', 'https://' e 'cdn' no
// CSS e no JS da Vitrine, e e por isso que ela roda em rede fechada.
assert "cdn." not in lower(html)
out "   nada e buscado de fora"

out ""
out "== 4. os tipos disponiveis =="

tipos := V.tipos_de_grafico
assert len(tipos) bigger_eq 20
assert "linha" in tipos
assert "sankey" in tipos
assert "gantt" in tipos
assert "cascata" in tipos
out $"   {len(tipos)} tipos"

out ""
out "== 5. a barra e ancorada no zero; a linha, nao =="

// Nao e estetica. Numa barra o que significa e o COMPRIMENTO, e
// cortar o eixo faz uma barra 3% maior parecer o dobro. Numa linha o
// que significa e a POSICAO: forcar o zero num patrimonio que vai de
// 1,02 a 1,13 milhao desenha uma reta, e a variacao some.
out "   barra: comprimento · linha: posicao"

out ""
out "== 6. e 'void' numa serie e um VAO, e nao um zero =="

steady COM_BURACO := [120.0, 135.0, void, 160.0, void, 190.0]

action com_vao():
    V.grafico_linha(MESES, {"receita": COM_BURACO})

t2 := V.testar(com_vao)
assert not t2.falhou()
// O caminho antigo convertia ausencia para 0.0, e a linha despencava
// ao chegar no mes que ainda nao aconteceu.
assert "<svg" in t2.html()
out "   o caminho e partido em trechos, e os vaos ficam vazios"

out "exercicio 375 ok"`, lang: 'df', title: `exercicios/57-vitrine-painel/375_graficos.df` },
  {"p": "Zero dependência também no navegador. Uma biblioteca de CDN quebra qualquer app em rede fechada — que é onde painel de dados costuma rodar."},
  {"h3": "A barra é ancorada no zero; a linha, não"},
  {"p": "Não é estética. Numa barra o que significa é o **comprimento**, e cortar o eixo faz uma barra 3% maior parecer o dobro. Numa linha o que significa é a **posição**: forçar o zero num patrimônio que vai de 1,02 a 1,13 milhão desenha uma reta, e a variação some."},
  {"h3": "`void` numa série é um VÃO, e não um zero"},
  {"p": "O caminho antigo convertia ausência para `0.0`, e a linha de um acumulado despencava ao chegar no mês que ainda não aconteceu — um gráfico que mostra uma queda de um milhão onde só falta o dado."},
  {"h3": "E há teste proibindo `http://` no CSS e no JS"},
  {"p": "É o que garante a rede fechada."},
  {"h2": "376 · a grade ordena NO SERVIDOR"},
  {"p": "**Enunciado.** a diferenca entre 'V.grade' e 'V.frame' nao e de"},
  { code: `// tamanho: e de ONDE a decisao mora. A 'frame' ordena o que ja esta
// na tela, e num conjunto de cem mil linhas isso e mentira.

adopt Arcane.Vitrine as V

steady VENDAS := [
    {"vendedor": "Ana", "regiao": "sul", "valor": 1200.0},
    {"vendedor": "Bia", "regiao": "sul", "valor": 800.0},
    {"vendedor": "Caio", "regiao": "norte", "valor": 2400.0},
    {"vendedor": "Dora", "regiao": "norte", "valor": 600.0},
    {"vendedor": "Eva", "regiao": "sul", "valor": 3000.0},
    {"vendedor": "Fabio", "regiao": "leste", "valor": 1500.0}
]

action painel():
    V.titulo("Vendas")
    V.grade(VENDAS, paginar := 3)
    V.frame(VENDAS)
    V.indicadores([
            {"rotulo": "Total", "valor": "R$ 9.500"},
            {"rotulo": "Media", "valor": "R$ 1.583"}
        ])

out "== 1. a grade e a frame convivem =="

t := V.testar(painel)
assert not t.falhou()
assert t.quantos("grade") is 1
assert t.quantos("frame") is 1

out ""
out "== 2. a paginacao vem LIGADA =="

// Uma listagem sem teto e a forma mais comum de um painel travar.
grade := t.primeiro("grade")
assert grade.props["por_pagina"] is 3
out $"   {grade.props['por_pagina']} linhas por pagina"

out ""
out "== 3. os indicadores =="

assert t.quantos("indicadores") is 1

out ""
out "== 4. os formatos pt-BR =="

assert V.moeda(1234.5) is "R$ 1.234,50"
assert V.numero_br(1234567.89, 2) is "1.234.567,89"
// O valor JA vem em porcentagem: 12.34 e "12,3%".
assert V.percentual(12.34) is "12,3%"
assert V.compacto(1234567) is "1,2 mi"
out $"   {V.moeda(1234.5)} · {V.compacto(1234567)} · {V.percentual(12.34)}"

out ""
out "== 5. e a data =="

assert V.data_br("2026-09-21") is "21/09/2026"

out ""
out "== 6. o que a grade sabe fazer =="

steady NA_GRADE := [
    "paginar (ligado por padrao)",
    "ordenar por coluna",
    "filtrar por texto",
    "selecionar linhas",
    "somar um total no rodape",
    "pintar a celula por regra"
]
assert len(NA_GRADE) is 6
cycle n in NA_GRADE:
    out $"   - {n}"

out "exercicio 376 ok"`, lang: 'df', title: `exercicios/57-vitrine-painel/376_grade_e_dados.df` },
  {"p": "A diferença entre `V.grade` e `V.frame` não é de tamanho: é de **onde a decisão mora**. A `frame` ordena o que já está na tela, e num conjunto de cem mil linhas isso é mentira."},
  {"h3": "A paginação vem LIGADA"},
  {"p": "Uma listagem sem teto é a forma mais comum de um painel travar."},
  {"h3": "Os formatos pt-BR"},
  {"p": "Moeda, número, percentual, compacto e data — num lugar só, e não espalhados em cinco `replace` pelo projeto."},
  {"h3": "E o que a grade sabe fazer"},
  {"p": "Paginar, ordenar, filtrar, selecionar, somar um total e pintar a célula por regra — tudo no servidor."},
  {"h2": "377 · o cache nao e opcional"},
  {"p": "**Enunciado.** o programa INTEIRO roda de novo a cada interacao. Sem"},
  { code: `// cache, a consulta que carrega os dados roda a cada tecla digitada —
// e o painel fica inutilizavel com qualquer fonte que nao seja
// instantanea.

adopt Arcane.Vitrine as V

contas := {"n": 0}

action carregar(regiao):
    contas["n"] := contas["n"] + 1
    yield [{"regiao":regiao, "valor":100.0 * contas["n"]}]

// 'V.cache' e um decorador: com a acao, envolve; com opcoes,
// devolve o decorador. Aqui usamos a forma direta.
steady carregar_com_cache := V.cache(carregar)

action painel():
    V.titulo("Cache")
    regiao := V.escolha("Regiao", ["sul", "norte"])
    dados := carregar_com_cache(regiao)
    V.frame(dados)
    V.texto($"consultas: {contas['n']}")

out "== 1. a primeira execucao consulta =="

t := V.testar(painel)
assert not t.falhou()
assert contas["n"] is 1

out ""
out "== 2. reexecutar com o MESMO argumento nao consulta =="

t.selecionar("Regiao", "sul")
assert contas["n"] is 1
out "   o painel redesenhou, e a fonte nao foi tocada"

out ""
out "== 3. trocar o argumento consulta de novo =="

t.selecionar("Regiao", "norte")
assert contas["n"] is 2

// E voltar ao anterior VOLTA ao cache.
t.selecionar("Regiao", "sul")
assert contas["n"] is 2
out "   dois argumentos, duas consultas — e nada mais"

out ""
out "== 4. sem o cache, cada redesenho consultaria =="

sem := {"n": 0}

action carregar_sem(_regiao):
    sem["n"] := sem["n"] + 1
    yield [{"x":1}]

action painel_sem():
    regiao := V.escolha("Regiao", ["sul", "norte"])
    V.frame(carregar_sem(regiao))

t2 := V.testar(painel_sem)
t2.selecionar("Regiao", "norte")
t2.selecionar("Regiao", "sul")
assert sem["n"] is 3
out $"   tres redesenhos, {sem['n']} consultas"

out ""
out "== 5. o deposito e por IDENTIDADE da acao =="

// Duas acoes 'carregar' em arquivos diferentes dividiriam o mesmo
// cache, e o teto da primeira venceria calado sobre o da segunda.
// Mas 'id()' nao e identidade ao longo do TEMPO: o CPython
// reaproveita o endereco de um objeto coletado, e uma acao nova caia
// na chave de uma acao morta — herdando o VALOR dela.
out "   por isso o deposito guarda a acao junto: enquanto ele existir,"
out "   aquele id nao pode ser de mais ninguem"

out ""
out "== 6. e o recurso, para o que NAO e dado =="

// 'V.cache' guarda VALOR; 'V.recurso' guarda um OBJETO que se abre
// uma vez — uma conexao, um modelo carregado.
abertas := {"n": 0}

action abrir():
    abertas["n"] := abertas["n"] + 1
    yield {"conexao": abertas["n"]}

steady conexao := V.recurso(abrir)

action painel_recurso():
    c := conexao()
    V.texto($"conexao {c['conexao']}")

t3 := V.testar(painel_recurso)
t3.rodar()
t3.rodar()
assert abertas["n"] is 1
out "   tres execucoes, uma conexao"

out "exercicio 377 ok"`, lang: 'df', title: `exercicios/57-vitrine-painel/377_cache.df` },
  {"p": "O programa **inteiro** roda de novo a cada interação. Sem cache, a consulta que carrega os dados roda a cada tecla digitada — e o painel fica inutilizável com qualquer fonte que não seja instantânea."},
  {"h3": "Dois argumentos, duas consultas — e nada mais"},
  {"p": "Voltar ao argumento anterior volta ao cache."},
  {"h3": "O depósito é indexado por IDENTIDADE da ação"},
  {"p": "Duas ações `carregar` em arquivos diferentes dividiriam o mesmo cache, e o teto da primeira venceria calado sobre o da segunda. Mas `id()` não é identidade ao longo do **tempo**: o CPython reaproveita o endereço de um objeto coletado, e uma ação nova caía na chave de uma ação morta — herdando o **valor** dela."},
  {"h3": "E o recurso, para o que NÃO é dado"},
  {"p": "`V.cache` guarda **valor**; `V.recurso` guarda um objeto que se abre uma vez — uma conexão, um modelo carregado."},
  {"h2": "378 · quem esta vendo o painel"},
  {"p": "**Enunciado.** 'exigir_login' PARA a pagina. Ela levanta um sinal que"},
  { code: `// deriva de BaseException, como 'halt' e 'skip' — sem isso, o
// interpretador embrulharia numa mensagem de erro no meio da tela, e
// a pagina continuaria desenhando o que o visitante nao pode ver.

adopt Arcane.Vitrine as V

steady USUARIOS := {
    "ana": {"senha": "1234", "papel": "admin"},
    "bia": {"senha": "5678", "papel": "leitor"}
}

action conferir(usuario, senha):
    // A forma afirmativa e de proposito: com 'given dados is void or
    // dados["senha"] …', o analisador continua achando que 'dados'
    // pode ser void no segundo termo — ele nao acompanha o
    // curto-circuito do 'or', e esta certo em nao concluir.
    dados := USUARIOS[usuario] ?? void
    given dados is not void:
        given dados["senha"] is senha:
            yield {"nome": usuario, "papel": dados["papel"]}
    yield void

action painel():
    V.autenticacao(conferir, {"admin": ["tudo"], "leitor": []})
    V.exigir_login()

    V.titulo($"Ola, {V.usuario()['nome']}")
    V.texto("conteudo de quem entrou")

    given V.pode("tudo"):
        V.texto("area do administrador")

out "== 1. sem login, a pagina PARA =="

t := V.testar(painel)
assert not t.falhou()
assert "conteudo de quem entrou" not in t.texto()
out "   nada do conteudo protegido apareceu"

out ""
out "== 2. entrar reexecuta a pagina do COMECO =="

// Continuar de onde parou deixaria a tela vazia para quem escreveu
// 'given V.autenticado(): …' — o teste ja passou com a resposta
// antiga.
action entrar(sonda, usuario, senha):
    "A sonda entra pelo formulario, como uma pessoa entraria."
    sonda.digitar("Usuário", usuario)
    sonda.digitar("Senha", senha)
    sonda.clicar("Entrar")

entrar(t, "ana", "1234")
assert "Ola, ana" in t.texto()
assert "conteudo de quem entrou" in t.texto()

out ""
out "== 3. o papel decide o que aparece =="

assert "area do administrador" in t.texto()

t2 := V.testar(painel)
entrar(t2, "bia", "5678")
assert "conteudo de quem entrou" in t2.texto()
assert "area do administrador" not in t2.texto()
out "   a leitora nao ve a area do administrador"

out ""
out "== 4. a senha errada nao entra =="

t3 := V.testar(painel)
entrar(t3, "ana", "errada")
assert "conteudo de quem entrou" not in t3.texto()

out ""
out "== 5. o erro de login e mostrado, e nao engolido =="

// Um login que falha em silencio e o pior desfecho: a pessoa clica de
// novo achando que nao clicou.
assert "inválidos" in t3.texto() or "invalidos" in t3.texto()
out "   a senha errada avisou"

out ""
out "== 6. e o cookie de sessao e uma STRING =="

// O Kiln guarda cookie como a linha 'Set-Cookie' pronta, e nao como
// vault. Passar um dicionario faz o navegador DESCARTAR o cookie, e
// cada pedido abre sessao nova — o sintoma e um contador que nunca
// passa de 1 e um login que nunca 'pega', sem nenhum erro.
out "   e 'V.testar' nao devolve cookies: esse bug so aparece com socket"

out "exercicio 378 ok"`, lang: 'df', title: `exercicios/57-vitrine-painel/378_sessao_e_login.df` },
  {"p": "`exigir_login` **para** a página. Ela levanta um sinal que deriva de `BaseException`, como `halt` e `skip`."},
  {"h3": "Sem isso, viraria uma mensagem no meio da tela"},
  {"p": "O interpretador embrulha toda `Exception` que sai de função Python num `RuntimeError_` — e a página continuaria desenhando o que o visitante não pode ver."},
  {"h3": "Entrar reexecuta a página do COMEÇO"},
  {"p": "Continuar de onde parou deixaria a tela vazia para quem escreveu `given V.autenticado(): …`."},
  {"h3": "E o cookie de sessão é uma STRING"},
  {"p": "O Kiln guarda cookie como a linha `Set-Cookie` pronta. Passar um vault faz o navegador **descartar** o cookie, e cada pedido abre sessão nova — o sintoma é um contador que nunca passa de 1, sem nenhum erro. E `V.testar` não devolve cookies: esse bug só aparece com socket."},
  {"h2": "379 · mais de uma pagina"},
  {"p": "**Enunciado.** o que nao casa com pagina nenhuma cai no tratador de 404"},
  { code: `// do Kiln, e NAO numa rota curinga. Uma curinga e casada na ORDEM do
// registro, entao ela engoliria toda rota acrescentada depois do
// 'V.montar()' — que e exatamente o que se faz para servir uma API ao
// lado do painel.

adopt Arcane.Vitrine as V

action inicio():
    V.titulo("Inicio")
    V.texto("a pagina inicial")

action relatorio():
    V.titulo("Relatorio")
    V.texto("os numeros do mes")

action ajuda():
    V.titulo("Ajuda")
    V.texto("como usar")

out "== 1. registrar as paginas =="

// Uma chamada por pagina: caminho, acao e o titulo que aparece no
// menu.
V.pagina("/", inicio, "Inicio")
V.pagina("/relatorio", relatorio, "Relatorio")
V.pagina("/ajuda", ajuda, "Ajuda")

assert len(V.paginas()) is 3
out $"   {len(V.paginas())} paginas registradas"

t := V.testar(inicio)
assert not t.falhou()
assert "a pagina inicial" in t.texto()

out ""
out "== 2. cada pagina desenha a sua =="

t2 := V.testar(relatorio)
assert "os numeros do mes" in t2.texto()
assert "a pagina inicial" not in t2.texto()

out ""
out "== 3. o menu sai da lista, e nao de uma copia =="

// Duas listas — a das rotas e a do menu — divergiriam, e o item
// apontaria para uma pagina que nao existe mais.
titulos := [p["titulo"] cycle p in V.paginas()]
assert titulos is ["Inicio", "Relatorio", "Ajuda"]
out $"   {titulos}"

out ""
out "== 4. e o 404 responde 404 =="

// A pagina de "nao achei" responde 404, e nao 200 com "404" no
// corpo: um monitor que so olha o status veria o site saudavel.
out "   404 no status, e nao so no texto"

out ""
out "== 5. o parametro da URL =="

action com_parametro():
    id := V.parametro("id", "0")
    V.titulo($"Pedido {id}")

t3 := V.testar(com_parametro)
assert "Pedido 0" in t3.texto()
out "   sem o parametro, o padrao"

out ""
out "== 6. e navegar troca a pagina SEM recarregar tudo =="

out "   'V.navegar(rota)' levanta um sinal, como 'exigir_login'"
out "   e ele deriva de BaseException, para nao virar mensagem de erro"

out "exercicio 379 ok"`, lang: 'df', title: `exercicios/57-vitrine-painel/379_paginas_e_navegacao.df` },
  {"p": "O que não casa com página nenhuma cai no tratador de 404 do Kiln, e **não** numa rota curinga."},
  {"h3": "Uma curinga engoliria o que vier depois"},
  {"p": "Ela é casada na **ordem** do registro, então engoliria toda rota acrescentada depois do `V.montar()` — que é exatamente o que se faz para servir uma API ao lado do painel."},
  {"h3": "O menu sai da lista, e não de uma cópia"},
  {"p": "Duas listas divergiriam, e o item apontaria para uma página que não existe mais."},
  {"h3": "E o 404 responde 404"},
  {"p": "E não 200 com \"404\" no corpo: um monitor que só olha o status veria o site saudável."},
  {"h2": "380 · o formulario que so envia uma vez"},
  {"p": "**Enunciado.** sem formulario, CADA campo reexecuta o programa. Num"},
  { code: `// cadastro de oito campos isso sao oito execucoes — e se um deles
// consulta o banco, sao oito consultas para preencher um cadastro.

adopt Arcane.Vitrine as V

execucoes := {"n": 0}
salvos := []

action painel():
    execucoes["n"] := execucoes["n"] + 1
    V.titulo("Cadastro")

    f := V.formulario("cadastro")
    nome := f.entrada("Nome")
    email := f.email("E-mail")
    idade := f.numero("Idade", 0)

    given f.enviar("Salvar"):
        salvos.append({"nome": nome, "email": email, "idade": idade})
        V.sucesso("Salvo!")

out "== 1. os campos ficam agrupados =="

t := V.testar(painel)
assert not t.falhou()
assert t.quantos("formulario") is 1

t.digitar("Nome", "Ana")
t.digitar("E-mail", "ana@x.com")
t.digitar("Idade", "30")

// Nada foi salvo ainda: o formulario segura ate o envio.
assert len(salvos) is 0
out "   tres campos digitados, zero salvamentos"

out ""
out "== 2. e o envio manda tudo de uma vez =="

t.clicar("Salvar")
assert len(salvos) is 1
assert salvos[0]["nome"] is "Ana"
assert salvos[0]["idade"] is 30
out $"   {salvos[0]}"

out ""
out "== 3. sem formulario, cada campo reexecuta o programa =="

sem := {"n": 0}

action painel_sem():
    sem["n"] := sem["n"] + 1
    V.entrada("Nome")
    V.entrada("E-mail")

t2 := V.testar(painel_sem)
base := sem["n"]
t2.digitar("Nome", "Ana")
t2.digitar("E-mail", "ana@x.com")
assert sem["n"] is base + 2
out $"   dois campos, {sem['n'] - base} reexecucoes do programa"

// Num cadastro de oito campos isso sao oito execucoes — e se um deles
// consulta o banco, sao oito consultas para preencher um cadastro.
//
// A ECONOMIA do formulario acontece no NAVEGADOR: ele segura os
// valores e manda tudo no envio. A sonda nao ve isso — ela simula um
// pedido por acao, e e uma das fronteiras dela.
out "   a economia e no navegador, e a sonda nao a enxerga"

out ""
out "== 4. a validacao de campo fica JUNTO do campo =="

action maior_de_idade(texto):
    monitor:
        yield int(texto) bigger_eq 18
    handle Error:
        yield no

action com_validacao():
    // Ele devolve o par (valor, esta_bom).
    idade, bom := V.campo_validado("Idade", maior_de_idade,
        "Precisa ter 18 anos ou mais.")
    given bom:
        V.sucesso($"idade {idade}")

t3 := V.testar(com_validacao)
assert not t3.falhou()

// Um campo VAZIO e nunca tocado nao e acusado: reclamar antes de a
// pessoa digitar qualquer coisa e ruido, e nao ajuda.
assert "Precisa ter 18" not in t3.texto()

t3.digitar("Idade", "10")
assert "Precisa ter 18" in t3.texto()

t3.digitar("Idade", "30")
assert "idade 30" in t3.texto()
// O erro aparece ligado ao campo, com 'role="alert"' e
// 'aria-describedby' — e nao numa caixa solta no topo da pagina.
assert "alert" in t3.html()
out "   o erro fica no campo, e nao numa caixa no topo"

out ""
out "== 5. o que a acessibilidade exige, e que ja esta la =="

steady ACESSIBILIDADE := [
    "<fieldset>/<legend> nos grupos",
    "role=alert no erro, com aria-describedby ligando ao campo",
    "setas nas abas, e so a ativa no Tab",
    "a variacao da metrica com a PALAVRA ao lado da seta"
]
assert len(ACESSIBILIDADE) is 4
cycle a in ACESSIBILIDADE:
    out $"   - {a}"

out "exercicio 380 ok"`, lang: 'df', title: `exercicios/57-vitrine-painel/380_formulario.df` },
  {"p": "Sem formulário, **cada** campo reexecuta o programa. Num cadastro de oito campos isso são oito execuções — e se um deles consulta o banco, são oito consultas para preencher um cadastro."},
  {"h3": "A economia acontece no NAVEGADOR"},
  {"p": "Ele segura os valores e manda tudo no envio. A sonda não vê isso — ela simula um pedido por ação, e é uma das fronteiras dela."},
  {"h3": "A validação fica JUNTO do campo"},
  {"p": "Com `role=\"alert\"` e `aria-describedby` ligando ao campo — e não numa caixa solta no topo da página."},
  {"h3": "E um campo vazio e nunca tocado não é acusado"},
  {"p": "Reclamar antes de a pessoa digitar qualquer coisa é ruído, não ajuda."},
  {"h2": "381 · o que se escreve numa pagina"},
  {"p": "**Enunciado.** 'V.escrever' e polimorfico — ele decide o componente"},
  { code: `// pelo TIPO do valor. E o que faz um painel exploratorio caber numa
// linha por resultado, sem escolher o componente a cada passo.

adopt Arcane.Vitrine as V

action painel():
    V.titulo("Conteudo", icone := "grafico")
    V.subtitulo("tudo o que cabe numa pagina")

    V.escrever("um texto simples")
    V.escrever(42)
    V.escrever([{"a":1, "b":2}, {"a":3, "b":4}])
    V.escrever({"chave": "valor"})

    V.markdown("**negrito** e \`codigo\`")
    V.codigo("x := 1", "dataforge")
    V.citacao("uma citacao", autor := "alguem")
    V.formula("E = mc^2")

    V.selo("novo", cor := "verde")
    V.icone("conferir")
    V.divisor()

    V.informacao("uma informacao")
    V.sucesso("deu certo")
    V.aviso("cuidado")
    V.erro("deu errado")

out "== 1. 'escrever' escolhe o componente =="

t := V.testar(painel)
assert not t.falhou()
assert t.quantos("texto") bigger_eq 2
assert t.quantos("frame") is 1
assert t.quantos("vault") is 1
out "   texto, numero, cluster de vaults e vault — quatro componentes"

out ""
out "== 2. os quatro avisos sao UM componente, com nivel =="

// 'informacao', 'sucesso', 'aviso' e 'erro' desenham o mesmo
// 'alerta', mudando o nivel: quatro componentes separados dariam
// quatro desenhos para manter em dia.
assert t.quantos("alerta") is 4
niveis := [a.props["nivel"] cycle a in t.arvore()["filhos"]
    given a.tipo is "alerta"]
assert niveis is ["info", "sucesso", "aviso", "erro"]
out $"   {niveis}"

out ""
out "== 3. markdown e codigo =="

assert t.quantos("markdown") is 1
assert t.quantos("codigo") is 1
assert "<strong>" in t.html() or "<b>" in t.html()

out ""
out "== 4. e o icone e SVG embutido =="

// Sao dezenas de icones desenhados NO ARQUIVO: nenhuma fonte de
// icone, nenhum arquivo a baixar, e funciona em rede fechada.
assert t.quantos("icone") is 1
assert "<svg" in t.html()
assert len(V.icones()) bigger_eq 48
out $"   {len(V.icones())} icones, zero requisicoes"

// E um nome que nao existe e RECUSADO, com a lista: um icone que sai
// vazio e um buraco na tela que ninguem percebe em revisao.
action so_um_icone_errado():
    V.icone("nao-existe")

falhou := V.testar(so_um_icone_errado)
assert falhou.falhou()
assert "icone" in falhou.falhas()[0]
out $"   {falhou.falhas()[0]}"

out ""
out "== 5. o que existe, em grupos =="

steady GRUPOS := {
    "texto": "titulo, subtitulo, texto, markdown, codigo, citacao, formula",
    "aviso": "informacao, sucesso, aviso, erro, excecao, status",
    "marca": "selo, icone, logo, divisor, espacador",
    "midia": "imagem, video, audio, pdf, galeria, iframe",
    "conversa": "chat, chat_mensagem, chat_entrada"
}
assert len(keys(GRUPOS)) is 5
cycle g in keys(GRUPOS):
    out $"   {g}: {GRUPOS[g]}"

out "exercicio 381 ok"`, lang: 'df', title: `exercicios/57-vitrine-painel/381_conteudo.df` },
  {"p": "`V.escrever` é polimórfico — ele decide o componente pelo **tipo** do valor. É o que faz um painel exploratório caber numa linha por resultado."},
  {"h3": "Os quatro avisos são UM componente, com nível"},
  {"p": "Quatro componentes separados dariam quatro desenhos para manter em dia."},
  {"h3": "O ícone é SVG embutido"},
  {"p": "Dezenas desenhados no arquivo: nenhuma fonte de ícone, nenhum arquivo a baixar. E um nome que não existe é **recusado**, com a lista — um ícone que sai vazio é um buraco na tela que ninguém percebe em revisão."},
  {"h2": "382 · os campos, e o que 'mudou' responde"},
  {"p": "**Enunciado.** toda entrada devolve o valor de agora. O que faltava era"},
  { code: `// saber se ele MUDOU nesta execucao — sem isso, uma consulta cara
// roda a cada redesenho, mesmo quando nada relevante mexeu.

adopt Arcane.Vitrine as V

consultas := []

action painel():
    V.titulo("Filtros")

    // 'mudou' pergunta pela CHAVE, e nao pelo rotulo: o rotulo e o
    // que a pessoa le, e pode mudar com a traducao.
    regiao := V.escolha("Regiao", ["sul", "norte", "leste"],
        chave := "regiao")
    faixa := V.deslizante("Valor minimo", 0, 5000, 1000)
    ativos := V.interruptor("So ativos", yes)
    _tags := V.pilulas("Categorias", ["cafe", "bolo", "suco"])

    given V.mudou("regiao"):
        consultas.append(regiao)

    V.texto($"regiao {regiao}, minimo {faixa}, ativos {ativos}")
    V.texto($"mudaram: {V.mudancas()}")

out "== 1. os valores padrao =="

t := V.testar(painel)
assert not t.falhou()
assert "regiao sul" in t.texto()
assert "minimo 1000" in t.texto()

out ""
out "== 2. trocar a escolha =="

t.selecionar("Regiao", "norte")
assert "regiao norte" in t.texto()

out ""
out "== 3. e 'mudou' respondeu so na execucao em que mudou =="

assert consultas is ["norte"]

t.marcar("So ativos", no)
assert consultas is ["norte"]
out "   outro campo mexeu, e a consulta nao rodou de novo"

out ""
out "== 4. os tipos de entrada =="

steady ENTRADAS := {
    "texto": "entrada, area_de_texto, senha, busca, email",
    "numero": "numero, deslizante, deslizante_opcoes, faixa",
    "escolha": "escolha, escolhas, opcao, pilulas, segmentado, tags",
    "sim/nao": "interruptor, caixa",
    "tempo": "data, hora, periodo",
    "outros": "arquivo, camera, cor, avaliacao, autocompletar"
}
assert len(keys(ENTRADAS)) is 6
cycle e in keys(ENTRADAS):
    out $"   {e}: {ENTRADAS[e]}"

out ""
out "== 5. e a chave, quando o rotulo repete =="

// Duas entradas com o mesmo rotulo dividiriam o mesmo estado — e uma
// sobrescreveria a outra, calada.
action dois_iguais():
    a := V.entrada("Nome", "", chave := "nome_do_cliente")
    b := V.entrada("Nome", "", chave := "nome_do_vendedor")
    V.texto($"{a}|{b}")

t2 := V.testar(dois_iguais)
assert not t2.falhou()
out "   a 'chave' separa dois campos com o mesmo rotulo"

out "exercicio 382 ok"`, lang: 'df', title: `exercicios/57-vitrine-painel/382_entradas.df` },
  {"p": "Toda entrada devolve o valor de agora. O que faltava era saber se ele **mudou** nesta execução — sem isso, uma consulta cara roda a cada redesenho, mesmo quando nada relevante mexeu."},
  {"h3": "Ele pergunta pela CHAVE, e não pelo rótulo"},
  {"p": "O rótulo é o que a pessoa lê, e pode mudar com a tradução."},
  {"h3": "É o `on_change` deste framework"},
  {"p": "E é uma **pergunta** em vez de um retorno de chamada: o programa roda inteiro a cada interação, então a linha que reage à mudança pode estar onde ela é lida."},
  {"h3": "E a chave separa dois campos com o mesmo rótulo"},
  {"p": "Sem ela, os dois dividiriam o mesmo estado — e um sobrescreveria o outro, calado."},
  {"h2": "383 · o layout diz ao grafico a largura em que ele vai aparecer"},
  {"p": "**Enunciado.** o desenho e feito num sistema de 800 unidades e o CSS o"},
  { code: `// encolhe para caber. Num painel de um terco da tela o fator e 0,45,
// e um rotulo de 11px chega ao olho com CINCO — ilegivel, sem nada
// que denuncie, porque de longe o grafico continua bonito.

adopt Arcane.Vitrine as V

steady MESES := ["jan", "fev", "mar"]
steady SERIE := [120.0, 135.0, 128.0]

action painel():
    V.titulo("Largura")

    // Largura inteira.
    V.grafico_linha(MESES, {"receita": SERIE})

    // Um terco da tela: o mesmo grafico, num container estreito.
    c := V.colunas(3)
    c[0].grafico_linha(MESES, {"receita": SERIE})
    c[1].grafico_barras(MESES, {"receita": SERIE})
    c[2].metrica("Total", "R$ 383")

out "== 1. os graficos desenham nos dois lugares =="

t := V.testar(painel)
assert not t.falhou()
assert t.quantos("grafico") is 3

out ""
out "== 2. e o de dentro da coluna sabe a largura =="

// 'Contexto.larguras' e uma pilha que cada area empurra; o no grava
// a largura NA MONTAGEM, porque no desenho o contexto ja acabou.
html := t.html()
assert "--v-fs" in html
out "   a escala do texto vai no proprio SVG"

out ""
out "== 3. o teto de 2,6x existe por um motivo =="

// Compensar por inteiro num container muito estreito faria o rotulo
// ocupar metade do grafico.
out "   compensar demais e tao ruim quanto nao compensar"

out ""
out "== 4. o tema =="

assert len(V.temas()) bigger_eq 4
assert "claro" in V.temas()
assert "escuro" in V.temas()
out $"   {len(V.temas())} temas: {V.temas()}"

out ""
out "== 5. e a primaria do tema claro NAO e o amarelo da marca =="

// Amarelo sobre branco da contraste 1,3:1 onde a WCAG pede 4,5:1.
// A cor da marca continua na identidade; o que muda e o que vai
// sobre fundo branco.
out "   #B28600 no claro — acessibilidade nao e camada por cima"

out ""
out "== 6. o seletor de tema, para quem prefere o outro =="

action com_seletor():
    V.seletor_de_tema()
    V.texto("conteudo")

t2 := V.testar(com_seletor)
assert not t2.falhou()
assert "conteudo" in t2.texto()

out "exercicio 383 ok"`, lang: 'df', title: `exercicios/57-vitrine-painel/383_tema_e_largura.df` },
  {"p": "O desenho é feito num sistema de 800 unidades e o CSS o encolhe para caber. Num painel de um terço da tela o fator é 0,45, e um rótulo de 11px chega ao olho com **cinco** — ilegível, sem nada que denuncie, porque de longe o gráfico continua bonito."},
  {"h3": "A largura é gravada na MONTAGEM"},
  {"p": "No desenho o contexto já acabou. `Contexto.larguras` é uma pilha que cada área empurra."},
  {"h3": "E o teto de 2,6× existe por um motivo"},
  {"p": "Compensar por inteiro num container muito estreito faria o rótulo ocupar metade do gráfico."},
  {"h3": "A primária do tema claro NÃO é o amarelo da marca"},
  {"p": "Amarelo sobre branco dá contraste 1,3:1 onde a WCAG pede 4,5:1. Acessibilidade é como os componentes são desenhados, e não uma camada por cima."},
  {"h2": "384 · redesenhar so um pedaco"},
  {"p": "**Enunciado.** o fragmento existe porque redesenhar a pagina inteira a"},
  { code: `// cada tecla e caro. E a duvida cai SEMPRE para a pagina inteira:
// responder a pagina inteira sem precisar custa desempenho; responder
// um pedaco sem poder custa CORRECAO.

adopt Arcane.Vitrine as V

execucoes := {"n": 0}

// ERRADO: o botao e tratado DEPOIS de a metrica ser desenhada, e a
// tela fica um passo atras. O programa roda de cima para baixo, e o
// que ja foi desenhado nao volta.
action atrasado():
    f := V.fragmento("contador")
    f.metrica("Cliques", str(V.estado["atrasado"] ?? 0))
    given V.botao("Somar"):
        V.estado["atrasado"] := (V.estado["atrasado"] ?? 0) + 1

// CERTO: trate a interacao PRIMEIRO, desenhe depois.
action painel():
    execucoes["n"] := execucoes["n"] + 1
    V.titulo("Painel")

    given V.botao("Somar"):
        V.estado["n"] := (V.estado["n"] ?? 0) + 1

    f := V.fragmento("contador")
    f.metrica("Cliques", str(V.estado["n"] ?? 0))

out "== 1. o fragmento e um no com nome =="

t := V.testar(painel)
assert not t.falhou()
assert t.quantos("fragmento") is 1

out ""
out "== 2. e ele contem o que foi desenhado dentro =="

assert t.quantos("metrica") is 1
assert t.metrica("Cliques") is "0"

t.clicar("Somar")
assert t.metrica("Cliques") is "1"
t.clicar("Somar")
assert t.metrica("Cliques") is "2"

out ""
out "== 2b. e a ordem IMPORTA =="

// O mesmo contador, com o botao tratado depois do desenho: a tela
// fica um passo atras, e o estado esta certo. E o defeito mais
// confuso deste modelo, porque o numero "quase" bate.
a := V.testar(atrasado)
a.clicar("Somar")
assert a.estado("atrasado") is 1
assert a.metrica("Cliques") is "0"
out "   estado 1, tela 0 — trate a interacao ANTES de desenhar"

out ""
out "== 3. as tres duvidas que caem para a pagina INTEIRA =="

steady DUVIDAS := [
    "houve falha — o erro e desenhado FORA do fragmento, e ficaria invisivel",
    "mais de um campo mudou — nao ha como saber de quem e a mudanca",
    "o fragmento sumiu da arvore — nao ha onde encaixar a resposta"
]
assert len(DUVIDAS) is 3
cycle d in DUVIDAS:
    out $"   - {d}"

out ""
out "== 4. o programa roda INTEIRO mesmo assim =="

// O fragmento economiza o que vai pela REDE, e nao a execucao: o
// modelo continua sendo 'roda tudo de novo'. Quem economiza execucao
// e o cache.
antes := execucoes["n"]
t.clicar("Somar")
assert execucoes["n"] is antes + 1
out "   uma interacao, uma execucao inteira"

out ""
out "== 5. e o fragmento sem nome nao existe =="

// Sem o nome, nao ha como a resposta parcial dizer ONDE encaixar.
assert t.primeiro("fragmento").props["chave"] is "contador"

out ""
out "== 6. a atualizacao periodica e por PERGUNTA =="

// 'V.atualizar_a_cada(n)' e o "tempo real" da Vitrine: o navegador
// pergunta de novo. Nao ha WebSocket nem SSE aqui — o Kiln tem, e a
// Vitrine nao os usa.
action com_atualizacao():
    V.atualizar_a_cada(5)
    V.texto("atualiza a cada cinco segundos")

t2 := V.testar(com_atualizacao)
assert not t2.falhou()
out "   por pergunta, e nao por empurrao"

out "exercicio 384 ok"`, lang: 'df', title: `exercicios/57-vitrine-painel/384_fragmento.df` },
  {"p": "O fragmento economiza o que vai pela **rede**, e não a execução: o modelo continua sendo \"roda tudo de novo\"."},
  {"h3": "A ordem IMPORTA"},
  {"p": "Trate a interação **antes** de desenhar. Com o botão tratado depois, a tela fica um passo atrás e o estado está certo — o defeito mais confuso deste modelo, porque o número \"quase\" bate."},
  {"h3": "A dúvida cai SEMPRE para a página inteira"},
  {"p": "Houve falha, mais de um campo mudou, ou o fragmento sumiu da árvore. Responder a página inteira sem precisar custa desempenho; responder um pedaço sem poder custa **correção**."},
  {"h3": "E a atualização periódica é por PERGUNTA"},
  {"p": "`V.atualizar_a_cada(n)`: o navegador pergunta de novo. Não há WebSocket nem SSE aqui — o Kiln tem, e a Vitrine não os usa."},
  {"h2": "385 · tirar o dado de dentro do painel"},
  {"p": "**Enunciado.** todo painel acaba com alguem pedindo \"manda isso em"},
  { code: `// Excel". Exportar e a diferenca entre um painel usado e um painel
// que vira captura de tela colada num e-mail.

adopt Arcane.Vitrine as V

steady VENDAS := [
    {"vendedor": "Ana", "regiao": "sul", "valor": 1200.0},
    {"vendedor": "Bia", "regiao": "norte", "valor": 800.0},
    {"vendedor": "Caio", "regiao": "sul", "valor": 2400.0}
]

action painel():
    V.titulo("Vendas")
    V.grade(VENDAS)
    V.exportar_csv(VENDAS, "vendas.csv")
    V.exportar_json(VENDAS, "vendas.json")
    V.exportar_excel(VENDAS, "vendas.xlsx")

out "== 1. os tres formatos =="

t := V.testar(painel)
assert not t.falhou()
assert t.quantos("baixar") is 3
out "   csv, json e xlsx"

out ""
out "== 2. o conteudo do CSV =="

// A Vitrine monta o arquivo NO SERVIDOR: nao ha biblioteca de
// planilha no navegador, e o .xlsx sai do 'Arcane.Excel', que grava
// sem dependencia externa.
baixaveis := [b cycle b in t.arvore()["filhos"] given b.tipo is "baixar"]
assert len(baixaveis) is 3
nomes := [b.props["nome"] cycle b in baixaveis]
assert nomes is ["vendas.csv", "vendas.json", "vendas.xlsx"]
out $"   {nomes}"

out ""
out "== 3. o conteudo fica no ESTADO, e nao no no =="

// O no leva so o rotulo, o nome do arquivo e a chave; os bytes ficam
// guardados, e o navegador os pede quando o botao e clicado. Mandar
// um .xlsx inteiro dentro do HTML de toda pagina seria absurdo.
assert keys(baixaveis[2].props) is ["rotulo", "nome", "chave"]
out "   o HTML leva o botao; os bytes ficam para quem clicar"

out ""
out "== 4. e o binario e preservado =="

// 'baixar' guarda BYTES: converter para texto e de volta corromperia
// o .xlsx, que e um ZIP. O teste disso vive em 'tests/test_vitrine.py',
// onde da para abrir o armazem.
out "   o .xlsx e um ZIP, e um 'para_texto' o destruiria"

out ""
out "== 5. e o SVG de um grafico tambem sai =="

action com_grafico():
    // Ele recebe o GRAFICO montado por 'V.grafico', e nao o atalho
    // 'V.grafico_linha' — que ja desenha e devolve os dados. O SVG
    // sai do desenho daquele grafico, e nao de uma captura da tela.
    // 'V.grafico' monta a partir de LINHAS, e nomeia as colunas: e a
    // forma para quem ja tem os dados tabulares, e a que o
    // 'exportar_svg' recebe.
    g := V.grafico("linha", [{"mes":"a", "valor":1.0},
            {"mes": "b", "valor": 2.0}])
    g.eixo_x("mes")
    g.serie("valor")
    V.desenhar(g)
    V.exportar_svg(g, "grafico.svg")

t2 := V.testar(com_grafico)
assert not t2.falhou()

out ""
out "== 6. o que 'build' e 'deploy' NAO fazem =="

// A Vitrine nao tem os dois, e os dois explicam por que: nao ha o que
// "construir" (nao ha bundle), e um deploy que falasse com o servidor
// por dentro esconderia o que a maquina e.
out "   'dataforge vitrine run' e 'dev' existem; 'build' e 'deploy' nao"

out "exercicio 385 ok"`, lang: 'df', title: `exercicios/57-vitrine-painel/385_exportar.df` },
  {"p": "Todo painel acaba com alguém pedindo \"manda isso em Excel\". Exportar é a diferença entre um painel usado e um painel que vira captura de tela colada num e-mail."},
  {"h3": "O arquivo é montado NO SERVIDOR"},
  {"p": "Não há biblioteca de planilha no navegador, e o `.xlsx` sai do `Arcane.Excel`, que grava sem dependência externa."},
  {"h3": "O conteúdo fica no estado, e não no nó"},
  {"p": "O HTML leva o botão; os bytes ficam para quem clicar. Mandar um `.xlsx` inteiro dentro do HTML de toda página seria absurdo."},
  {"h3": "E `build` e `deploy` não existem"},
  {"p": "Não há o que construir (não há bundle), e um `deploy` que falasse com o servidor por dentro esconderia o que a máquina é."},
  {"h2": "386 · onde a sessao mora"},
  {"p": "**Enunciado.** a sessao na memoria do processo some quando ele"},
  { code: `// reinicia, e nao atravessa dois processos. O armazem comum resolve
// os dois — e cobra tres coisas que so aparecem com processos de
// verdade.

adopt Arcane.Vitrine as V
adopt Arcane.IO as IO
adopt Arcane.OS as OS

steady pasta := $"{OS.temp_dir()}/df-386-{randint(100000, 999999)}"
IO.mkdir(pasta)

action painel():
    V.titulo("Contador")
    n := V.estado["n"] ?? 0
    given V.botao("Somar"):
        n := n + 1
        V.estado["n"] := n
    V.metrica("Total", str(n))

out "== 1. na memoria do processo =="

t := V.testar(painel)
t.clicar("Somar")
t.clicar("Somar")
assert t.estado("n") is 2

out ""
out "== 2. os quatro lugares onde a sessao pode morar =="

steady ARMAZENS := {
    "memoria": "o padrao — some quando o processo reinicia",
    "arquivos": "um arquivo por sessao, numa pasta",
    "banco": "SQLite, e atravessa processos",
    "proprio": "um blueprint seu, com ler e gravar"
}
assert len(keys(ARMAZENS)) is 4
cycle a in keys(ARMAZENS):
    out $"   {a}: {ARMAZENS[a]}"

out ""
out "== 3. so o que MUDOU e gravado =="

// Cada valor e codificado e comparado com a foto tirada ao abrir.
// Gravar no 'definir' perderia 'itens.append(x)', que nao passa por
// ele.
out "   a gravacao e no fim do pedido, comparando com a foto de abertura"

out ""
out "== 4. as tres armadilhas que custaram =="

steady ARMADILHAS := {
    "WAL": "trocar para WAL ignora o timeout: dois processos subindo juntos davam 'database is locked' na hora",
    "fixacao": "um id desconhecido vira sessao NOVA — senao o id plantado no cookie viraria sessao, e agora sobreviveria ao processo",
    "caminho": "so id de 32 hexadecimais chega ao armazem: em arquivos o id e NOME DE ARQUIVO, e '../x' escreveria fora da pasta"
}
assert len(keys(ARMADILHAS)) is 3
cycle a in keys(ARMADILHAS):
    out $"   {a}: {ARMADILHAS[a]}"

out ""
out "== 5. e encerrar marca, para a gravacao nao ressuscitar =="

// Sem a marca, a gravacao do fim do pedido recriava a sessao que
// acabou de ser apagada.
action com_logout():
    V.titulo("x")
    given V.botao("Sair"):
        V.encerrar_sessao()

t2 := V.testar(com_logout)
t2.clicar("Sair")
assert not t2.falhou()
out "   'encerrar_sessao' marca a sessao como encerrada"

out ""
out "== 6. e o que continua na memoria =="

// 'V.estado.somar' NAO e atomico entre processos: na mesma chave,
// vence a ultima gravacao. E a sessao do KILN continua na memoria do
// processo, sempre.
out "   'somar' entre processos: vence a ultima gravacao"

IO.remove_tree(pasta)
out "exercicio 386 ok"`, lang: 'df', title: `exercicios/57-vitrine-painel/386_sessao_fora_do_processo.df` },
  {"p": "A sessão na memória do processo some quando ele reinicia, e não atravessa dois processos."},
  {"h3": "Só o que MUDOU é gravado"},
  {"p": "Cada valor é codificado e comparado com a foto tirada ao abrir. Gravar no `definir` perderia `itens.append(x)`, que não passa por ele."},
  {"h3": "As três armadilhas que custaram"},
  {"p": "`PRAGMA journal_mode=WAL` ignora o `timeout` e dois processos subindo juntos davam `database is locked`; um id desconhecido vira sessão **nova**, senão o id plantado no cookie viraria sessão; e só id de 32 hexadecimais chega ao armazém, porque em arquivos o id é **nome de arquivo**."},
  {"h3": "E `encerrar_sessao` marca"},
  {"p": "Sem a marca, a gravação do fim do pedido recriava a sessão que acabou de ser apagada."},
  {"h2": "387 · o mapa, e as nove decisoes"},
  {"p": "**Enunciado.** fechar a trilha com o que a Vitrine resolve, o que ela"},
  { code: `// NAO resolve, e por que cada escolha foi feita. A ultima parte e a
// que evita usa-la onde o Kiln e a resposta.

adopt Arcane.Vitrine as V

out "== 1. os quinze grupos de componentes =="

steady GRUPOS := {
    "texto": "titulo, subtitulo, markdown, codigo, citacao, formula",
    "aviso": "informacao, sucesso, aviso, erro, excecao, status",
    "entrada": "entrada, numero, escolha, data, arquivo, camera…",
    "dados": "grade, frame, editor, indicador, estatisticas",
    "grafico": "27 tipos, todos em SVG do servidor",
    "layout": "colunas, abas, cartao, malha, painel, dialogo, popover",
    "midia": "imagem, video, audio, pdf, galeria, iframe",
    "estado": "estado, geral, cache, recurso",
    "sessao": "autenticacao, exigir_login, pode, encerrar_sessao",
    "pagina": "pagina, paginas, navegar, parametro, menu",
    "conexao": "conexao, conexao_de, segredos",
    "tema": "tema, temas, seletor_de_tema, paleta",
    "fluxo": "fragmento, atualizar_a_cada, agendar, tarefa",
    "saida": "exportar_csv, exportar_json, exportar_excel, exportar_svg",
    "teste": "testar — clica, digita e pergunta, sem navegador"
}
assert len(keys(GRUPOS)) is 15
out $"   {len(keys(GRUPOS))} grupos, {len(V.componentes())} componentes"

out ""
out "== 2. o modelo, em uma frase =="

out "   o programa INTEIRO roda de novo a cada interacao,"
out "   e o estado da sessao sobrevive."

out ""
out "== 3. e as consequencias diretas =="

steady CONSEQUENCIAS := [
    "nao ha callback nem diffing — e nao precisa haver",
    "'V.cache' e obrigatorio, e nao opcional",
    "a ordem importa: trate a interacao ANTES de desenhar",
    "o botao e um VALOR verdadeiro uma vez, e nao um evento"
]
assert len(CONSEQUENCIAS) is 4
cycle c in CONSEQUENCIAS:
    out $"   - {c}"

out ""
out "== 4. o que ela NAO tem =="

steady NAO_TEM := {
    "WebSocket/SSE": "o Kiln tem; a Vitrine atualiza por PERGUNTA (V.atualizar_a_cada)",
    "build": "nao ha bundle a construir — o cliente sao ~6 KB sem build",
    "deploy": "esconderia o que a maquina e, e nao haveria onde mexer",
    "CDN": "nada e buscado de fora — painel de dados roda em rede fechada"
}
assert len(keys(NAO_TEM)) is 4
cycle n in keys(NAO_TEM):
    out $"   {n}: {NAO_TEM[n]}"

out ""
out "== 5. quando usar o Kiln =="

out "   Vitrine: painel, ferramenta interna, app de dados"
out "   Kiln:    API, site publico, rota com contrato, WebSocket"

out ""
out "== 6. e a prova de que tudo isso e testavel =="

action painel():
    V.titulo("Final")
    c := V.colunas(2)
    c[0].metrica("A", "1")
    c[1].metrica("B", "2")
    V.grafico_linha(["x", "y"], {"s": [1.0, 2.0]})
    V.grade([{"n":1}, {"n":2}])

t := V.testar(painel)
assert not t.falhou()
assert t.quantos("metrica") is 2
assert t.quantos("grafico") is 1
assert t.quantos("grade") is 1
assert "<svg" in t.html()
out $"   {len(t.arvore()['filhos'])} nos de topo, zero navegadores"

out "exercicio 387 ok"`, lang: 'df', title: `exercicios/57-vitrine-painel/387_o_mapa_da_vitrine.df` },
  {"p": "Fechar a trilha com o que a Vitrine resolve, o que ela **não** resolve, e por que cada escolha foi feita. A última parte é a que evita usá-la onde o Kiln é a resposta."},
  {"h3": "O modelo, em uma frase"},
  {"p": "O programa inteiro roda de novo a cada interação, e o estado da sessão sobrevive."},
  {"h3": "As consequências diretas"},
  {"p": "Não há callback nem diffing — e não precisa haver. `V.cache` é obrigatório. A ordem importa: trate a interação antes de desenhar. E o botão é um **valor** verdadeiro uma vez, não um evento."},
  {"h3": "O que ela não tem"},
  {"p": "WebSocket/SSE (o Kiln tem; aqui é por **pergunta**), `build`, `deploy` e CDN."},
  {"h3": "E quando usar o Kiln"},
  {"p": "Vitrine: painel, ferramenta interna, app de dados. Kiln: API, site público, rota com contrato, WebSocket."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/57-vitrine-painel/373_um_painel_em_dez_linhas.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '373-o-programa-de-cima-para-baixo-que-vira-pagina', text: "373 · o programa de cima para baixo que vira pagina", level: 2 as const }, { id: 'digitar-reexecuta-o-programa', text: "Digitar reexecuta o programa", level: 3 as const }, { id: 'e-o-estado-da-sessao-sobrevive', text: "E o estado da sessão sobrevive", level: 3 as const }, { id: 'o-botao-e-verdadeiro-uma-vez', text: "O botão é verdadeiro UMA vez", level: 3 as const }, { id: '374-a-area-de-layout-e-um-objeto', text: "374 · a area de layout e um OBJETO", level: 2 as const }, { id: 'ele-aninha-sem-indentacao', text: "Ele aninha sem indentação", level: 3 as const }, { id: 'e-pode-ser-passado-adiante', text: "E pode ser PASSADO ADIANTE", level: 3 as const }, { id: 'arvore-devolve-os-nos-de-topo', text: "`arvore()` devolve os nós de TOPO", level: 3 as const }, { id: '375-o-grafico-e-svg-escrito-no-servidor', text: "375 · o grafico e SVG escrito no servidor", level: 2 as const }, { id: 'a-barra-e-ancorada-no-zero-a-linha-nao', text: "A barra é ancorada no zero; a linha, não", level: 3 as const }, { id: 'void-numa-serie-e-um-vao-e-nao-um-zero', text: "`void` numa série é um VÃO, e não um zero", level: 3 as const }, { id: 'e-ha-teste-proibindo-http-no-css-e-no-js', text: "E há teste proibindo `http://` no CSS e no JS", level: 3 as const }, { id: '376-a-grade-ordena-no-servidor', text: "376 · a grade ordena NO SERVIDOR", level: 2 as const }, { id: 'a-paginacao-vem-ligada', text: "A paginação vem LIGADA", level: 3 as const }, { id: 'os-formatos-pt-br', text: "Os formatos pt-BR", level: 3 as const }, { id: 'e-o-que-a-grade-sabe-fazer', text: "E o que a grade sabe fazer", level: 3 as const }, { id: '377-o-cache-nao-e-opcional', text: "377 · o cache nao e opcional", level: 2 as const }, { id: 'dois-argumentos-duas-consultas-e-nada-mais', text: "Dois argumentos, duas consultas — e nada mais", level: 3 as const }, { id: 'o-deposito-e-indexado-por-identidade-da-acao', text: "O depósito é indexado por IDENTIDADE da ação", level: 3 as const }, { id: 'e-o-recurso-para-o-que-nao-e-dado', text: "E o recurso, para o que NÃO é dado", level: 3 as const }, { id: '378-quem-esta-vendo-o-painel', text: "378 · quem esta vendo o painel", level: 2 as const }, { id: 'sem-isso-viraria-uma-mensagem-no-meio-da-tela', text: "Sem isso, viraria uma mensagem no meio da tela", level: 3 as const }, { id: 'entrar-reexecuta-a-pagina-do-comeco', text: "Entrar reexecuta a página do COMEÇO", level: 3 as const }, { id: 'e-o-cookie-de-sessao-e-uma-string', text: "E o cookie de sessão é uma STRING", level: 3 as const }, { id: '379-mais-de-uma-pagina', text: "379 · mais de uma pagina", level: 2 as const }, { id: 'uma-curinga-engoliria-o-que-vier-depois', text: "Uma curinga engoliria o que vier depois", level: 3 as const }, { id: 'o-menu-sai-da-lista-e-nao-de-uma-copia', text: "O menu sai da lista, e não de uma cópia", level: 3 as const }, { id: 'e-o-404-responde-404', text: "E o 404 responde 404", level: 3 as const }, { id: '380-o-formulario-que-so-envia-uma-vez', text: "380 · o formulario que so envia uma vez", level: 2 as const }, { id: 'a-economia-acontece-no-navegador', text: "A economia acontece no NAVEGADOR", level: 3 as const }, { id: 'a-validacao-fica-junto-do-campo', text: "A validação fica JUNTO do campo", level: 3 as const }, { id: 'e-um-campo-vazio-e-nunca-tocado-nao-e-acusado', text: "E um campo vazio e nunca tocado não é acusado", level: 3 as const }, { id: '381-o-que-se-escreve-numa-pagina', text: "381 · o que se escreve numa pagina", level: 2 as const }, { id: 'os-quatro-avisos-sao-um-componente-com-nivel', text: "Os quatro avisos são UM componente, com nível", level: 3 as const }, { id: 'o-icone-e-svg-embutido', text: "O ícone é SVG embutido", level: 3 as const }, { id: '382-os-campos-e-o-que-mudou-responde', text: "382 · os campos, e o que 'mudou' responde", level: 2 as const }, { id: 'ele-pergunta-pela-chave-e-nao-pelo-rotulo', text: "Ele pergunta pela CHAVE, e não pelo rótulo", level: 3 as const }, { id: 'e-o-onchange-deste-framework', text: "É o `on_change` deste framework", level: 3 as const }, { id: 'e-a-chave-separa-dois-campos-com-o-mesmo-rotulo', text: "E a chave separa dois campos com o mesmo rótulo", level: 3 as const }, { id: '383-o-layout-diz-ao-grafico-a-largura-em-que-ele-vai-aparecer', text: "383 · o layout diz ao grafico a largura em que ele vai aparecer", level: 2 as const }, { id: 'a-largura-e-gravada-na-montagem', text: "A largura é gravada na MONTAGEM", level: 3 as const }, { id: 'e-o-teto-de-26-existe-por-um-motivo', text: "E o teto de 2,6× existe por um motivo", level: 3 as const }, { id: 'a-primaria-do-tema-claro-nao-e-o-amarelo-da-marca', text: "A primária do tema claro NÃO é o amarelo da marca", level: 3 as const }, { id: '384-redesenhar-so-um-pedaco', text: "384 · redesenhar so um pedaco", level: 2 as const }, { id: 'a-ordem-importa', text: "A ordem IMPORTA", level: 3 as const }, { id: 'a-duvida-cai-sempre-para-a-pagina-inteira', text: "A dúvida cai SEMPRE para a página inteira", level: 3 as const }, { id: 'e-a-atualizacao-periodica-e-por-pergunta', text: "E a atualização periódica é por PERGUNTA", level: 3 as const }, { id: '385-tirar-o-dado-de-dentro-do-painel', text: "385 · tirar o dado de dentro do painel", level: 2 as const }, { id: 'o-arquivo-e-montado-no-servidor', text: "O arquivo é montado NO SERVIDOR", level: 3 as const }, { id: 'o-conteudo-fica-no-estado-e-nao-no-no', text: "O conteúdo fica no estado, e não no nó", level: 3 as const }, { id: 'e-build-e-deploy-nao-existem', text: "E `build` e `deploy` não existem", level: 3 as const }, { id: '386-onde-a-sessao-mora', text: "386 · onde a sessao mora", level: 2 as const }, { id: 'so-o-que-mudou-e-gravado', text: "Só o que MUDOU é gravado", level: 3 as const }, { id: 'as-tres-armadilhas-que-custaram', text: "As três armadilhas que custaram", level: 3 as const }, { id: 'e-encerrarsessao-marca', text: "E `encerrar_sessao` marca", level: 3 as const }, { id: '387-o-mapa-e-as-nove-decisoes', text: "387 · o mapa, e as nove decisoes", level: 2 as const }, { id: 'o-modelo-em-uma-frase', text: "O modelo, em uma frase", level: 3 as const }, { id: 'as-consequencias-diretas', text: "As consequências diretas", level: 3 as const }, { id: 'o-que-ela-nao-tem', text: "O que ela não tem", level: 3 as const }, { id: 'e-quando-usar-o-kiln', text: "E quando usar o Kiln", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"57 · Vitrine — o painel"}
      description={"15 exercícios: painéis com layout, gráficos, grade, cache e sessão."}
      href={"/docs/exercicios/57-vitrine-painel"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
