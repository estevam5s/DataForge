// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "28 · Vitrine",
  description: "1 exercícios: painéis e aplicações de dados sem escrever HTML.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 28`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[220](#220-uma-aplicacao-de-dados-com-a-vitrine)", "**Uma aplicacao de dados com a Vitrine**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "220 · Uma aplicacao de dados com a Vitrine"},
  { code: `// ════════════════════════════════════════════════════════════
//  Exercicio 220 — Uma aplicacao de dados com a Vitrine
//
//  Um programa de cima para baixo que vira uma pagina web, e um teste
//  que confere o que ela faz sem abrir navegador nenhum.
// ════════════════════════════════════════════════════════════

adopt Arcane.Vitrine as V

// ── 1. A pagina mais simples que existe ─────────────────────
//
// Componente e chamada de acao. Ela devolve o que quem escreve
// precisa: 'V.botao' devolve yes/no, 'V.entrada' devolve o texto.

action ola():
    V.titulo("Olá")
    nome := V.entrada("Seu nome", "mundo")
    V.texto($"Bom dia, {nome}!")

t := V.testar(ola)
assert "Bom dia, mundo!" in t.texto()

t.digitar("Seu nome", "Ana")
assert "Bom dia, Ana!" in t.texto()

// ── 2. O estado sobrevive; o clique, nao ────────────────────
//
// O programa roda INTEIRO a cada interacao. Sem um lugar que
// sobreviva, o contador voltaria a zero a cada clique. Ja o botao
// vale por UMA execucao — um clique que continuasse verdadeiro
// dispararia a acao de novo no carregamento seguinte.

action contador():
    V.estado.padrao("n", 0)
    given V.botao("Somar"):
        V.estado.somar("n")
    V.metrica("Total", V.estado.obter("n"))

c := V.testar(contador)
assert c.metrica("Total") is "0"
c.clicar("Somar")
assert c.metrica("Total") is "1"
c.rodar()
assert c.metrica("Total") is "1"  // sem clique, nao soma
c.clicar("Somar")
assert c.metrica("Total") is "2"

// ── 3. Layout: a area e um objeto ───────────────────────────
//
// A linguagem nao tem bloco de contexto, entao a coluna e um objeto
// e os componentes sao metodos dele. Aninha sem indentacao extra, e
// da para guardar a area numa variavel.

action colunado():
    colunas := V.colunas([2, 1])
    colunas[0].texto("conteúdo")
    lado := colunas[1].cartao("Resumo")
    lado.metrica("Itens", 42)

l := V.testar(colunado)
raiz := l.achar("colunas")[0]
assert len(raiz.filhos) is 2
assert raiz.filhos[0].props["proporcao"] is 66.6667
assert l.metrica("Itens") is "42"

// ── 4. Cache: rodar tudo de novo exige nao recalcular tudo ──

vezes := {"n": 0}

mark @V.cache
action pesado(chave):
    vezes["n"] := vezes["n"] + 1
    yield [{"x":chave, "y":10}]

action com_cache():
    V.tabela(pesado("a"))
    V.tabela(pesado("a"))

V.testar(com_cache)
assert vezes["n"] is 1

// ── 5. Grafico: SVG escrito no servidor ─────────────────────
//
// Sem biblioteca de JavaScript: uma CDN quebraria o app em rede
// fechada, que e onde painel de dados costuma rodar.

action grafico():
    dados := [
        {"mes": "Jan", "receita": 120},
        {"mes": "Fev", "receita": 90},
        {"mes": "Mar", "receita": 160}
    ]
    V.grafico_barras(dados, x := "mes", y := "receita", titulo := "Vendas")

g := V.testar(grafico)
assert "<svg" in g.html()
assert "<rect" in g.html()
assert g.primeiro("grafico").props["series"][0]["valores"] is [120, 90, 160]

// ── 6. Formulario: so entrega no envio ──────────────────────
//
// Sem formulario, CADA tecla roda o programa inteiro. Num campo
// ligado a uma consulta pesada, e a diferenca entre um app usavel e
// um que trava a cada letra.

salvos := []

action cadastro():
    forma := V.formulario("novo")
    nome := forma.entrada("Nome")
    forma.numero("Idade", 18)
    given forma.enviar("Cadastrar"):
        salvos.append(nome)
        V.sucesso($"{nome} cadastrado.")

f := V.testar(cadastro)
f.digitar("Nome", "Bruno")
assert len(salvos) is 0  // digitar nao salva
f.enviar("novo")
assert salvos is ["Bruno"]
assert "Bruno cadastrado." in f.texto()

// ── 7. Um erro na pagina nao derruba o servidor ─────────────

action quebrada():
    V.titulo("antes")
    trigger "falhou de propósito"

q := V.testar(quebrada)
assert q.falhou()
assert "antes" in q.texto()  // o que ja montou continua

// ── 8. Validacao: o erro sob o campo ────────────────────────
//
// Num formulario de doze campos, um alerta no topo dizendo "ha erros"
// obriga a pessoa a cacar qual deles.

adopt Arcane.Regex as Regex

action com_validacao():
    aviso := "Digite um e-mail válido."
    email, bom := V.campo_validado("E-mail", Regex.is_email, aviso)
    given bom:
        V.sucesso($"ok: {email}")

v := V.testar(com_validacao)
assert v.problemas() is []  // vazio e intocado nao acusa

v.digitar("E-mail", "sem-arroba")
assert v.problema("E-mail") is "Digite um e-mail válido."
assert "aria-invalid" in v.html()

v.digitar("E-mail", "ana@exemplo.br")
assert v.problemas() is []
assert "ok" in v.texto()

// ── 9. Idioma: por sessao, nao por processo ─────────────────

V.i18n.carregar("pt-BR", {"ola": "Olá, {nome}"})
V.i18n.carregar("en-US", {"ola": "Hello, {nome}"})

action saudacao():
    V.texto(V.t("ola", nome := "Ana"))
    V.texto(V.t("sem.traducao"))

i := V.testar(saudacao)
assert "Olá, Ana" in i.texto()
assert "sem.traducao" in i.texto()  // chave sem traducao aparece crua

V.i18n.idioma("en-US")
assert "Hello, Ana" in V.testar(saudacao).texto()
V.i18n.idioma("pt-BR")

// ── 10. HTTP de verdade, sem socket ─────────────────────────

action inicio():
    V.titulo("Loja")

app := V.app("Teste")
V.pagina("/", inicio)

r := V.pedir(app, "GET", "/")
assert r["status"] is 200
assert "<!DOCTYPE html>" in r["body"]
assert r["headers"]["X-Content-Type-Options"] is "nosniff"

out "218 ok — vitrine"`, lang: 'df', title: `exercicios/28-vitrine/220_vitrine.df` },
  {"h3": "Conceitos"},
  { code: `adopt Arcane.Vitrine as V

action painel():
    V.titulo("Vendas")
    regiao := V.escolha("Região", ["Sul", "Norte"])
    V.metrica("Total", 128400)
    V.grafico_barras(dados_de(regiao), x := "mes")

V.rodar(painel, porta := 8501)`, lang: 'df' },
  {"p": "Não há palavra reservada nova. A Vitrine é um módulo da biblioteca, e tudo nela é chamada de ação."},
  {"h3": "O modelo de execução"},
  {"p": "A cada interação, **o programa inteiro roda de novo** — e o estado da sessão sobrevive."},
  { code: `clique  →  o programa roda do começo  →  a árvore vira HTML  →  a tela troca
              ↑                                                      │
              └──────────  o estado da sessão continua  ─────────────┘`, lang: 'text' },
  {"p": "Isso parece desperdício e é o contrário: quem escreve nunca pensa em callback, em diffing, nem em qual pedaço da tela atualizar. A linha de cima sempre aconteceu antes da linha de baixo, como em qualquer programa. O preço é que a página precisa ser rápida a cada clique — daí o `V.cache`, que existe desde o primeiro dia e não como otimização posterior."},
  {"h3": "Para que serve"},
  {"p": "Mostrar dado é metade do trabalho de quem trabalha com dado, e a outra metade normalmente exige HTML, CSS, JavaScript, um servidor e um build. A Vitrine troca tudo isso por um programa que já se sabe escrever."},
  {"p": "O `Kiln` continua sendo o framework de **sites e APIs**, onde cada rota devolve o que quiser. A Vitrine é para **painel e aplicação de dados**, onde a página é o programa. Ela roda sobre o Kiln: HTTP, rota, sessão e cabeçalho de segurança já estavam lá, testados."},
  {"h3": "O que o exercício cobre"},
  {"table": {"head": ["Parte", "Ideia"], "rows": [["1", "componente é chamada de ação, e ela **devolve** o valor"], ["2", "o estado sobrevive; o clique vale por **uma** execução"], ["3", "a área de layout é um objeto, e os componentes são métodos dela"], ["4", "`mark @V.cache` faz a leitura acontecer uma vez, e não por clique"], ["5", "gráfico vira SVG escrito no servidor, sem biblioteca"], ["6", "formulário só entrega os valores quando alguém confirma"], ["7", "um erro aparece **na página**, e não derruba o servidor"], ["8", "validação: o erro aparece **sob o campo**, não num alerta no topo"], ["9", "idioma por sessão; chave sem tradução aparece crua"], ["10", "`V.pedir` faz um pedido HTTP de verdade, sem socket"]]}},
  {"h3": "Três armadilhas"},
  {"p": "**O botão vale por uma execução.** `given V.botao(\"Pagar\")` é verdadeiro no ciclo do clique e falso nos seguintes. Se fosse permanente, o pagamento aconteceria de novo no próximo carregamento da página."},
  {"p": "**Cada tecla roda o programa inteiro.** É o preço do modelo. Num campo ligado a uma consulta pesada, ponha-o dentro de um `V.formulario(...)`: aí os valores só chegam quando alguém aperta o botão de envio."},
  {"p": "**`V.html` não escapa nada.** É a única porta de XSS da Vitrine, e ela existe porque às vezes não há alternativa. Nunca passe por ali algo que veio do usuário — para isso, `V.texto`, que escapa."},
  {"h3": "Para ver no navegador"},
  { code: `dataforge run exercicios/28-vitrine/218_vitrine.df    # os testes
dataforge run examples/vitrine_dashboard.df -- --servir`, lang: 'bash' },
  {"p": "Ou comece do zero, com um projeto que já passa nos próprios testes:"},
  { code: `dataforge vitrine new meupainel
cd meupainel
dataforge vitrine dev        # http://127.0.0.1:8501
dataforge vitrine doctor     # se não subir, ele diz por quê`, lang: 'bash' },
  {"p": "O segundo sobe em `http://127.0.0.1:8501` um painel com quatro métricas, quatro gráficos, abas, filtro na barra lateral e exportação para CSV."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/28-vitrine/220_vitrine.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '220-uma-aplicacao-de-dados-com-a-vitrine', text: "220 · Uma aplicacao de dados com a Vitrine", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-modelo-de-execucao', text: "O modelo de execução", level: 3 as const }, { id: 'para-que-serve', text: "Para que serve", level: 3 as const }, { id: 'o-que-o-exercicio-cobre', text: "O que o exercício cobre", level: 3 as const }, { id: 'tres-armadilhas', text: "Três armadilhas", level: 3 as const }, { id: 'para-ver-no-navegador', text: "Para ver no navegador", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"28 · Vitrine"}
      description={"1 exercícios: painéis e aplicações de dados sem escrever HTML."}
      href={"/docs/exercicios/28-vitrine"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
