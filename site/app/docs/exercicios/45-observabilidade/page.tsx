// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "45 · Observabilidade e memória",
  description: "1 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 45`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[263](#263-medir-com-rigor-e-o-coletor-sob-controle)", "**medir com rigor, e o coletor sob controle**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "263 · medir com rigor, e o coletor sob controle"},
  { code: `// 'Arcane.Bench' responde "quanto tempo leva" com uma MEDIA. E o que
// quase toda ferramenta faz, e e onde quase toda decisao de performance
// erra: a media esconde a cauda, duas medias diferentes podem ser a
// mesma coisa com ruido, e um numero sozinho nao responde "piorou?".

adopt Arcane.Perfil as P
adopt Arcane.Memoria as Mem
adopt Arcane.IO as IO
adopt Arcane.OS as OS

action consulta():
    yield sum(range(400))

// ── percentis, com aquecimento separado ──
m := P.medir(consulta, {"amostras": 50, "aquecimento": 5})

assert m["amostras"] is 50
assert m["aquecimento"] is 5  // declarado, e nao misturado
assert m["p50"] smaller_eq m["p95"]
assert m["p95"] smaller_eq m["p99"]
assert m["min"] smaller_eq m["p50"] and m["p99"] smaller_eq m["max"]
assert "vazao" in m and "desvio" in m

// ── a cauda que a media esconde ──
// Cem medidas de 10 ms e uma de 1000 dao media 20. A pessoa que pegou a
// ultima esperou UM SEGUNDO, e nenhum relatorio de media conta isso.
resumo := P.resumir([10.0, 10.0, 10.0, 10.0, 1000.0])
assert resumo["media"] smaller resumo["p99"]
assert resumo["max"] is 1000.0

// o percentil sai da AMOSTRA, por posto — interpolar inventaria um
// valor que nao aconteceu
exato := P.resumir([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
assert exato["p50"] is 5
assert exato["min"] is 1 and exato["max"] is 10

// ── significancia: o teste que impede inventar ganho ──
// A MESMA acao dos dois lados. A diferenca e ruido, e a ferramenta tem
// de dizer isso — senao escolhe-se a implementacao errada com conviccao.
igual := P.comparar(consulta, consulta, {"amostras": 40})
assert igual["mais_rapido"] is "empate"
assert not igual["significativo"]

action lenta():
    yield sum(range(9000))

// e quando a diferenca EXISTE, ela e achada
d := P.comparar(consulta, lenta, {"amostras": 30})
assert d["significativo"]
assert d["mais_rapido"] is "a"
assert d["fator"] bigger 2
assert d["p_valor"] smaller 0.05

// o p diz SE ha diferenca; a sobreposicao diz QUANTO
assert d["sobreposicao"] bigger 0.8
assert d["sobreposicao"] smaller_eq 1.0

// ── regressao contra linha de base ──
base := $"{OS.temp_dir()}/df-263-{randint(100000, 999999)}.json"
P.guardar("consulta", {"p95": 1.0, "p50": 1.0, "media": 1.0}, base)

ruim := P.conferir("consulta", {"p95": 3.0, "p50": 3.0, "media": 3.0},
    {"arquivo": base, "tolerancia": 0.2})
assert ruim["conhecida"] and ruim["regrediu"]
assert ruim["fator"] is 3.0

// 5% de diferenca com 20% de tolerancia e ruido de maquina: sem
// tolerancia, todo CI fica vermelho e a primeira coisa que se faz com
// um CI vermelho por desenho e desliga-lo
ok := P.conferir("consulta", {"p95": 1.05, "p50": 1.05, "media": 1.05},
    {"arquivo": base, "tolerancia": 0.2})
assert not ok["regrediu"]

// uma melhora e relatada, e nao reprova
melhor := P.conferir("consulta", {"p95": 0.5, "p50": 0.5, "media": 0.5},
    {"arquivo": base, "tolerancia": 0.2})
assert melhor["melhorou"] and not melhor["regrediu"]

// a PRIMEIRA medida nunca reprova: sem base nao ha regressao
nova := P.conferir("nunca-medida", {"p95": 1.0}, {"arquivo": base})
assert not nova["conhecida"] and not nova["regrediu"]
IO.delete(base)

// ── pausas do coletor ──
// A pausa do coletor e o que transforma um p50 bom num p99 ruim, e ela
// NAO aparece em medida que olhe so o tempo total.
r := P.gc_pausas(consulta)
assert r["resultado"] is 79800
assert "p95" in r and "por_geracao" in r
assert r["pausas"] bigger_eq 0

// ── contencao de trava ──
// Contencao nao aparece num perfil de CPU: a thread bloqueada nao gasta
// CPU nenhuma. Ela aparece como latencia que ninguem explica.
trava := P.trava()
P.com_trava(trava, lambda => 1 + 1)
P.com_trava(trava, lambda => 2 + 2)

e := P.estatisticas_da_trava(trava)
assert e["aquisicoes"] is 2
assert e["esperas"] is 0  // sem disputa, ninguem esperou

// ── o coletor sob controle ──
// A distincao que quase todo mundo erra: quem libera no CPython e a
// CONTAGEM DE REFERENCIA, e ela roda na hora. O coletor existe so para
// o CICLO. Desligar o coletor NAO vaza memoria em geral.
assert Mem.gc_ligado()
assert Mem.sem_gc(consulta) is 79800
assert Mem.gc_ligado()  // voltou

// e volta mesmo quando o corpo FALHA — deixar o coletor desligado por
// causa de um erro e muito pior que a pausa que se queria evitar
monitor:
    Mem.sem_gc(lambda => 1 / 0)  // df: permitir division-by-zero
    assert no
handle Error:
    assert Mem.gc_ligado()

// os limiares e as geracoes
assert len(Mem.gc_limiares()) is 3
assert len(Mem.gc_geracoes()) is 3
assert "coletas" in Mem.gc_geracoes()[0]

// congelar tira o que JA VIVE das varreduras — o que um servidor faz
// depois da carga e antes do primeiro pedido
antes := Mem.gc_congelados()
Mem.gc_congelar()
assert Mem.gc_congelados() bigger antes
Mem.gc_descongelar()
assert Mem.gc_congelados() is 0

// ── arena ──
// NAO e um allocator: quem aloca continua sendo o Python. O que a arena
// troca e o PADRAO de uso.
arena := Mem.arena(3, lambda => {"n": 0})
a := Mem.pegar(arena)
_b := Mem.pegar(arena)
Mem.devolver(arena, a)
_c := Mem.pegar(arena)  // o MESMO objeto volta

conta := Mem.arena_estatisticas(arena)
assert conta["criados"] is 3  // o lote, preparado de uma vez
assert conta["reaproveitados"] is 1
assert conta["em_uso"] is 2

// 'limpar' solta o lote inteiro numa chamada: e o tempo de vida de
// arena da literatura, e a operacao que ela existe para ter
Mem.limpar(arena)
assert Mem.arena_estatisticas(arena)["em_uso"] is 0
assert Mem.arena_estatisticas(arena)["disponiveis"] is 3

// devolver o que nao veio dela e RECUSADO: o lote cresceria com
// estranhos, e o proximo 'pegar' entregaria um deles
monitor:
    Mem.devolver(arena, {"estranho": yes})
    assert no
handle RuntimeError as erro:
    assert "arena" in erro.message

out "263 ok"`, lang: 'df', title: `exercicios/45-observabilidade/263_perfil_e_coletor.df` },
  {"p": "`Arcane.Bench` responde \"quanto tempo leva\" com uma **média**. É o que quase toda ferramenta de benchmark faz, e é onde quase toda decisão de performance erra:"},
  {"list": ["**a média esconde a cauda**, e é a cauda que o usuário sente. Cem"]},
  {"p": "requisições de 10 ms e uma de 1000 ms dão média 20 ms — e quem pegou a última esperou um segundo;"},
  {"list": ["**duas médias diferentes podem ser a mesma coisa com ruído**, e sem"]},
  {"p": "teste estatístico não há como saber;"},
  {"list": ["**um número sozinho não responde \"piorou desde a semana passada?\"**."]},
  {"h3": "Percentis, e por que sem interpolar"},
  {"p": "`P.medir` devolve a distribuição: `p50`, `p90`, `p95`, `p99`, `p999`, `min`, `max`, `media`, `desvio` e `vazao`."},
  {"p": "O **aquecimento é separado e declarado**. As primeiras execuções medem cache frio, import preguiçoso e alocação inicial: misturá-las com o resto não é medir o programa, é medir a **partida**."},
  {"p": "E o percentil sai da amostra **por posto**, não de uma interpolação. Interpolar inventa um valor que não aconteceu — num P99 de latência o que se quer é uma medida que **existiu**."},
  {"h3": "O teste que importa"},
  {"p": "**Comparar uma ação com ela mesma não pode dar \"3% mais rápida\".** É o que separa medição de superstição."},
  { code: `igual := P.comparar(consulta, consulta, {"amostras": 40})
assert igual["mais_rapido"] is "empate"`, lang: 'df' },
  {"p": "A conta é o **Mann-Whitney U**, e não o teste t. Tempo de execução não é normal: tem cauda longa à direita, piso duro à esquerda (nada roda em tempo negativo) e picos de escalonamento. Um teste t supõe normalidade e responde com confiança sobre uma suposição falsa. O U não supõe nada sobre a forma — ele compara **ordens** —, e a correção de empates importa quando o relógio tem resolução grossa."},
  {"p": "E as duas medições são **intercaladas**: medir A inteiro e depois B inteiro faz uma queda de clock no meio virar \"B é mais lenta\". Alternar espalha a deriva da máquina pelos dois lados."},
  {"p": "`p_valor` diz **se** há diferença; `sobreposicao` diz **quanto** — é o tamanho do efeito, e é o que o `p` não diz."},
  {"h3": "Regressão, e duas escolhas que mantêm o CI utilizável"},
  {"list": ["**A primeira medida nunca reprova.** Sem base guardada não há"]},
  {"p": "regressão, só um começo. Reprovar ali faria todo CI novo nascer vermelho, e a primeira coisa que se faz com um CI vermelho por desenho é desligá-lo."},
  {"list": ["**A tolerância é obrigatória.** Sem ela, todo CI fica vermelho por"]},
  {"p": "ruído de máquina — o que dá no mesmo."},
  {"h3": "O que nenhum perfil de CPU mostra"},
  {"p": "**Pausa do coletor**: é o que transforma um P50 bom num P99 ruim, e não aparece em medida que olhe só o tempo total. `gc.callbacks` entrega o começo e o fim de cada coleta — é a medida na fonte."},
  {"p": "**Contenção de trava**: a thread bloqueada **não gasta CPU nenhuma**. Ela aparece como latência que ninguém explica, e a única forma de vê-la é medir na própria trava. A distinção entre \"peguei na hora\" e \"esperei\" é feita por uma tentativa sem bloqueio antes da aquisição real — sem ela, toda aquisição contaria como espera."},
  {"h3": "O coletor, e a distinção que quase todo mundo erra"},
  {"p": "No CPython quem libera é a **contagem de referência**, e ela roda na hora. O **coletor** existe só para o **ciclo**: `a` apontando para `b` que aponta para `a`."},
  {"p": "**Desligar o coletor não vaza memória em geral** — só deixa o ciclo para trás. É por isso que desligá-lo num trecho curto e sensível a latência é técnica segura, e não gambiarra."},
  {"p": "`Mem.sem_gc` religa **mesmo se o corpo falhar**. Não é detalhe: deixar o coletor desligado por causa de um erro é muito pior que a pausa que se queria evitar, e o programa seguiria assim até terminar sem nada denunciando."},
  {"p": "`Mem.gc_congelar` tira o que **já vive** das varreduras para sempre — o que um servidor faz depois da carga e antes do primeiro pedido."},
  {"h3": "Arena"},
  {"p": "**Não é um allocator**: quem aloca continua sendo o Python, e não há como trocá-lo por dentro. O que a arena troca é o **padrão de uso** — em vez de criar e descartar por volta, um lote é preparado, emprestado e devolvido."},
  {"table": {"head": ["Decisão", "Por quê"], "rows": [["ela **cresce** quando acaba, e **conta**", "travar seria pior; crescer calado esconderia que foi dimensionada errada"], ["devolver o que não veio dela é **recusado**", "o lote cresceria com estranhos, e o próximo `pegar` entregaria um deles"], ["`limpar` solta o lote inteiro numa chamada", "é o tempo de vida de arena da literatura"]]}},
  {"p": "**O ganho aparece quando o objeto é caro de montar**, não quando é um vault de três chaves. Meça antes com `P.comparar`, e só mantenha se a diferença for **significativa**."},
  {"h3": "O que NÃO se aplica"},
  {"list": ["**allocator global, bump, slab, `#[no_std]`**: quem aloca é o CPython."]},
  {"p": "Um \"allocator\" em Python puro seria uma camada *sobre* o alocador real — mais lenta, e chamada de allocator por engano."},
  {"list": ["**contadores de hardware, cache miss, branch miss**: o CPython não os"]},
  {"p": "expõe, e a conta num interpretador de árvore diria pouco."},
  {"list": ["**mark-and-sweep, GC concorrente ou paralelo**: o coletor é o do"]},
  {"p": "CPython, e trocá-lo não é decisão desta linguagem."},
  {"list": ["**PGO e LTO**: a parte 8 já mediu que compilar mais nós rende **1,01×**"]},
  {"p": "em código real. Um PGO otimizaria a constante errada."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/45-observabilidade/263_perfil_e_coletor.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '263-medir-com-rigor-e-o-coletor-sob-controle', text: "263 · medir com rigor, e o coletor sob controle", level: 2 as const }, { id: 'percentis-e-por-que-sem-interpolar', text: "Percentis, e por que sem interpolar", level: 3 as const }, { id: 'o-teste-que-importa', text: "O teste que importa", level: 3 as const }, { id: 'regressao-e-duas-escolhas-que-mantem-o-ci-utilizavel', text: "Regressão, e duas escolhas que mantêm o CI utilizável", level: 3 as const }, { id: 'o-que-nenhum-perfil-de-cpu-mostra', text: "O que nenhum perfil de CPU mostra", level: 3 as const }, { id: 'o-coletor-e-a-distincao-que-quase-todo-mundo-erra', text: "O coletor, e a distinção que quase todo mundo erra", level: 3 as const }, { id: 'arena', text: "Arena", level: 3 as const }, { id: 'o-que-nao-se-aplica', text: "O que NÃO se aplica", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"45 · Observabilidade e memória"}
      description={"1 exercícios: ."}
      href={"/docs/exercicios/45-observabilidade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
