// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "46 · Partida, pilha e capacidade",
  description: "1 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 46`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[264](#264-a-partida-a-pilha-e-a-fronteira-de-capacidade)", "**a partida, a pilha e a fronteira de capacidade**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "264 · a partida, a pilha e a fronteira de capacidade"},
  { code: `// Um programa nao comeca na primeira linha: antes dela o comptime
// rodou, os adopt carregaram e as declaracoes foram icadas. Nada disso
// era VISIVEL — e "por que a partida demora 400 ms?" nao tinha como ser
// respondido sem cronometrar a mao.

adopt Arcane.Inicio as I
adopt Arcane.Capacidade as Cap
adopt Arcane.Math as M

// tres modulos adotados: e o que a cronometragem da partida vai contar
assert M.sqrt(9) is 3.0

// ── as sete fases, nomeadas e em ordem ──
fases := I.fases()
assert [f["fase"] cycle f in fases] is
       ["lexer", "parser", "comptime", "hoisting", "adopt", "programa", "defer"]

// cada uma tem o que faz escrito ao lado — uma lista de nomes sem
// explicacao apodrece
assert len(fases[0]["o_que"]) bigger 20

// ── onde a partida foi gasta ──
// Sao dois floats por import, num lugar que roda UMA VEZ. Liga-la por
// opcao faria a medida existir so para quem ja desconfiava.
registro := I.adocoes()
assert len(registro) bigger_eq 3
assert "modulo" in registro[0] and "ms" in registro[0]

r := I.relatorio()
assert r["adocoes"] bigger_eq 3
assert r["total_ms"] bigger_eq 0.0
assert r["mais_caro"]["modulo"] isnt ""

// ── a pilha: ela tinha limite e nao tinha como ser perguntada ──
action folha():
    yield I.pilha()

action tronco():
    yield folha()

p := tronco()
assert p["profundidade"] bigger_eq 2
assert p["limite"] bigger 100
assert p["restante"] is p["limite"] - p["profundidade"]

// os quadros trazem quem chamou quem
action quem():
    yield [q["acao"] cycle q in I.quadros()]

nomes := quem()
assert "quem" in nomes

// o teto se ajusta, e BAIXA-LO vale de verdade
antes := I.limite_da_pilha()
I.limite_da_pilha(300)
assert I.pilha()["limite"] is 300
I.limite_da_pilha(antes)
assert I.pilha()["limite"] is antes

// subir demais e RECUSADO: cada chamada da linguagem gasta varios
// quadros do CPython, e um teto alto demais troca uma mensagem clara
// por um RecursionError cru que nao fala desta linguagem
monitor:
    I.limite_da_pilha(10000000)
    assert no
handle RuntimeError as e:
    assert "Python" in e.message or "recursion" in e.message

// ── uma variavel por thread ──
// 'inicial' e uma ACAO que constroi o valor, e nao o valor: um valor
// seria compartilhado por todas as threads, que e exatamente o que a
// variavel por thread existe para evitar.
contador := I.local(lambda => {"n": 0})
caixa := I.meu(contador)
caixa["n"] := caixa["n"] + 1
assert I.meu(contador)["n"] is 1
assert I.threads_com_valor(contador) bigger_eq 1

// limpar esquece, e o proximo 'meu' nasce de novo
I.limpar(contador)
assert I.meu(contador)["n"] is 0

// passar um VALOR em vez de uma acao e recusado, com o motivo
monitor:
    I.local({"n": 0})
    assert no
handle RuntimeError as e:
    assert "thread" in e.message

// ── a fronteira de capacidade ──
// O comptime ja recusava out, adopt e thread: e uma fronteira escrita a
// mao para um caso so. E o --plugin= roda um .df arbitrario do projeto
// com TODOS os poderes — uma regra de lint que pode abrir soquete.

// o que e puro roda sem permissao nenhuma
action formula():
    adopt Arcane.Math as Mat
    yield Mat.sqrt(16) + len("abc")

assert Cap.executar(formula, []) is 7.0

// o adopt ambiente e recusado pelo NOME da capacidade que falta
action ler_disco():
    adopt Arcane.IO as IO
    yield IO.exists(".")

monitor:
    Cap.executar(ler_disco, [])
    assert no
handle Error as e:
    assert "arquivos" in e.message
    assert "Arcane.IO" in e.message

// com a permissao, o MESMO codigo passa
assert Cap.executar(ler_disco, ["arquivos"])

// a ponte para o Python e capacidade PROPRIA, e nunca vem junto: ela
// alcanca tudo o que o Python alcanca, e deixa-la com outra faria o
// resto da lista virar enfeite
action escapar():
    adopt Python.os as so
    yield so.getcwd()

monitor:
    Cap.executar(escapar, ["arquivos", "rede", "processo", "banco",
                             "threads", "nativo", "ambiente"])
    assert no
handle Error as e:
    assert "python" in e.message

// uma capacidade inventada e recusada COM A LISTA: um erro de digitacao
// concederia silenciosamente nada, e o cofre pareceria mais aberto
monitor:
    Cap.executar(formula, ["superpoderes"])
    assert no
handle Error as e:
    assert "superpoderes" in e.message

// descobrir de que uma acao precisa, sem adivinhar
action tenta():
    monitor:
        adopt Arcane.OS as OS
        yield OS.name()
    handle Error:
        yield "negado"

visto := Cap.observar(tenta, [])
assert visto["resultado"] is "negado"
assert visto["negados"][0]["capacidade"] is "processo"

assert Cap.exige("Arcane.OS") is "processo"
assert Cap.exige("Arcane.Math") is void      // inofensivo
assert len(Cap.modulos_de("rede")) bigger 5

// ── o limite HONESTO, e ele e o modelo ──
// Capacidade e o que o codigo ALCANCA, nao o que lhe foi entregue. Um
// cofre que prometesse o contrario mentiria.
adopt Arcane.IO as IO

action com_o_que_recebeu(ferramenta):
    yield ferramenta.exists(".")

assert Cap.executar(com_o_que_recebeu, [], [IO])

// e o modulo diz na cara o que NAO e — se a doc prometesse contencao,
// alguem o usaria onde nao pode, e descobriria por incidente
limites := Cap.limites()
assert len(limites) bigger_eq 3
assert "hostil" in join(" ", limites)

// a fronteira se desfaz SEMPRE, inclusive quando o corpo falha
action quebra():
    yield 1 / 0        // df: permitir division-by-zero

monitor:
    Cap.executar(quebra, [])
handle Error:
    void

// fora da fronteira, o adopt volta a funcionar
adopt Arcane.IO as IO2
assert IO2.exists(".")

out "264 ok"`, lang: 'df', title: `exercicios/46-partida/264_partida_pilha_e_capacidade.df` },
  {"p": "Um programa não começa na primeira linha. Antes dela o `comptime` rodou numa caixa sem E/S, os `adopt` carregaram módulos e as declarações de topo foram içadas."},
  {"p": "Nada disso era **visível** — e \"por que a partida demora 400 ms?\" não tinha como ser respondido sem cronometrar à mão."},
  {"h3": "As sete fases"},
  { code: `lexer → parser → comptime → hoisting → adopt → programa → defer`, lang: 'text' },
  {"p": "Cada uma tem **o que faz escrito ao lado**: uma lista de nomes sem explicação apodrece, e há teste cobrando o tamanho da descrição."},
  {"p": "E cada `adopt` é **cronometrado**. São dois floats por import, num lugar que roda uma vez — ligar a medida por opção faria ela existir só para quem já desconfiava, e a pergunta aparece justamente quando ninguém desconfiava."},
  {"h3": "A pilha"},
  {"p": "O teto é **mil quadros**, e recursão legítima o atinge: uma travessia de árvore de cinco mil nós não tem nada de infinita. Quem a escreve precisa saber de quanto é o teto **antes** de bater nele."},
  {"p": "`I.pilha()` dá profundidade, limite e quanto falta; `I.quadros()` dá quem chamou quem."},
  {"p": "**Subir o teto é recusado** além do que o Python aguenta: cada chamada desta linguagem gasta vários quadros do CPython, e um teto alto demais troca uma mensagem clara (\"a recursão passou de mil quadros, e aqui estão as duas saídas\") por um `RecursionError` cru — que não fala desta linguagem e não diz o que fazer."},
  {"p": "As duas saídas continuam sendo as certas: `yield f(…)` como retorno inteiro vira salto e **não tem teto**, ou um `cycle` com pilha explícita."},
  {"h3": "Uma variável por thread"},
  {"p": "Um armazém por thread resolve metade do problema. A outra metade é o que costuma faltar: a **inicialização declarada num lugar só**, e o **finalizador** quando a thread acaba — sem ele, uma conexão aberta por thread fica aberta depois que ela morre, e o sintoma aparece no servidor, não no código."},
  {"p": "**`inicial` é uma ação, não um valor.** Um valor seria compartilhado por todas as threads — que é exatamente o que a variável por thread existe para evitar. Passar um valor é recusado, com esse motivo na mensagem."},
  {"p": "E o finalizador roda quando a thread é **coletada**, não no instante em que ela termina: é o que o Python garante, e prometer precisão maior seria prometer um gancho que não existe. Para liberar num instante exato, `Arcane.Posse`."},
  {"h3": "A fronteira de capacidade"},
  {"p": "O `comptime` já recusava `out`, `adopt` e `thread`: é uma fronteira de capacidade escrita à mão, para um caso só. E o `--plugin=` roda um `.df` arbitrário do projeto com **todos** os poderes — uma regra de lint que pode abrir soquete."},
  {"p": "`Cap.executar(acao, permissoes)` recusa o `adopt` de um módulo fora da lista **pelo nome da capacidade que falta**, e não por um erro genérico."},
  {"p": "A **ponte para o Python é capacidade própria**, e nunca vem junto: ela alcança tudo o que o Python alcança, e deixá-la com outra faria o resto da lista virar enfeite."},
  {"p": "Um nome inventado é **recusado com a lista** — um erro de digitação concederia silenciosamente nada, e a fronteira pareceria mais aberta do que é."},
  {"p": "E `Cap.observar` responde \"de que esta ação precisa?\": rode com a lista vazia e leia os negados."},
  {"h3": "O limite honesto — e ele é o modelo"},
  {"p": "**A fronteira não tira o que foi ENTREGUE.** Se você passa o módulo `IO` como argumento, o código tem `IO`."},
  {"p": "Isso **não é um furo: é o modelo**. Numa linguagem de capacidade, poder é o que se **passa**, não o que está no ar — e é por isso que bloquear o `adopt` (a autoridade ambiente) é a fronteira certa."},
  {"p": "O módulo diz na cara o que não é, e `Cap.limites()` devolve essa lista em tempo de execução:"},
  {"list": ["**não é uma caixa contra programa hostil**;", "a lista de módulos é escrita à mão, e um erro nela é um furo;", "contra código malicioso: processo separado, contêiner, ou o sistema"]},
  {"p": "operacional."},
  {"p": "Escrito assim de propósito. Um módulo chamado *Sandbox* que prometesse contenção seria usado onde não pode ser usado, e a descoberta viria por incidente."},
  {"p": "E a fronteira **se desfaz sempre**, inclusive quando o corpo falha: um cofre que não se desfizesse travaria o programa inteiro."},
  {"h3": "O que NÃO se aplica"},
  {"list": ["**boot, stack probes, stack guards, stack growth**: quem faz o boot e"]},
  {"p": "gerencia a pilha é o CPython."},
  {"list": ["**thread-local allocators**: quem aloca é o CPython.", "**global constructors** no sentido do C++: não há.", "**overflow de inteiro**: não existe aqui — o inteiro é de precisão"]},
  {"p": "arbitrária, e uma classe inteira de bug não acontece. O preço é a conta ser mais lenta que uma de 64 bits."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/46-partida/264_partida_pilha_e_capacidade.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '264-a-partida-a-pilha-e-a-fronteira-de-capacidade', text: "264 · a partida, a pilha e a fronteira de capacidade", level: 2 as const }, { id: 'as-sete-fases', text: "As sete fases", level: 3 as const }, { id: 'a-pilha', text: "A pilha", level: 3 as const }, { id: 'uma-variavel-por-thread', text: "Uma variável por thread", level: 3 as const }, { id: 'a-fronteira-de-capacidade', text: "A fronteira de capacidade", level: 3 as const }, { id: 'o-limite-honesto-e-ele-e-o-modelo', text: "O limite honesto — e ele é o modelo", level: 3 as const }, { id: 'o-que-nao-se-aplica', text: "O que NÃO se aplica", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"46 · Partida, pilha e capacidade"}
      description={"1 exercícios: ."}
      href={"/docs/exercicios/46-partida"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
