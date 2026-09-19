// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "47 · Superfície e alvos",
  description: "1 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 47`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[265](#265-a-superficie-como-contrato-e-o-alvo-como-restricao)", "**a superficie como contrato, e o alvo como restricao**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "265 · a superficie como contrato, e o alvo como restricao"},
  { code: `// Numa linguagem compilada, quebrar a ABI e trocar o layout de uma
// struct ou a convencao de chamada, e o sintoma e cruel: o programa
// CARREGA e corrompe memoria, longe da causa.
//
// Aqui nao ha layout binario a quebrar — e existe EXATAMENTE o mesmo
// problema, com outro nome. A superficie de um modulo e o contrato
// dele, e o sintoma tambem e o mesmo: nao e erro de quem publicou, e
// erro de quem consome, depois.

adopt Arcane.Abi as Abi
adopt Arcane.Alvo as Alvo
adopt Arcane.Capacidade as Cap
adopt Arcane.IO as IO
adopt Arcane.OS as OS

pasta := $"{OS.temp_dir()}/df-265-{randint(100000, 999999)}"
IO.mkdir(pasta)

V1 := "action somar(a: Integer, b: Integer) -> Integer:\\n" +
      "    yield a + b\\n\\n" +
      "action saudar(nome: String) -> String:\\n" +
      "    yield nome\\n\\n" +
      "record Ponto:\\n" +
      "    x: Integer\\n" +
      "    y: Integer\\n\\n" +
      "action interna():\\n" +
      "    yield 1\\n\\n" +
      "relay somar, saudar, Ponto\\n"

antes := $"{pasta}/v1.df"
IO.write(antes, V1)

// ── a superficie respeita o relay ──
// Um modulo que DECLARA o que exporta esta dizendo que o resto e
// interno — e o que e interno nao e contrato.
s := Abi.superficie(antes)
assert sorted(keys(s)) is ["Ponto", "saudar", "somar"]
assert "interna" not in s

assert s["somar"]["especie"] is "acao"
assert s["somar"]["parametros"] is ["a", "b"]
assert s["somar"]["tipos"]["a"] is "Integer"
assert s["somar"]["retorno"] is "Integer"
assert sorted(s["Ponto"]["campos"]) is ["x", "y"]

// ── nada mudou: correcao ──
igual := $"{pasta}/igual.df"
IO.write(igual, V1)
assert Abi.comparar(antes, igual)["veredito"] is "correcao"

// ── so acrescimo: menor ──
maisUm := $"{pasta}/mais.df"
IO.write(maisUm, V1.replace("relay somar, saudar, Ponto",
                            "action dobrar(n):\\n    yield n * 2\\n\\n" +
                            "relay somar, saudar, Ponto, dobrar"))
r := Abi.comparar(antes, maisUm)
assert r["veredito"] is "menor"
assert r["quebras"] is []
assert r["compativeis"][0]["tipo"] is "simbolo-novo"

// ── tirar um simbolo: maior ──
semSaudar := $"{pasta}/sem.df"
IO.write(semSaudar, V1.replace("relay somar, saudar, Ponto",
                               "relay somar, Ponto"))
q := Abi.comparar(antes, semSaudar)
assert q["veredito"] is "maior"
assert q["quebras"][0]["tipo"] is "simbolo-removido"
assert q["quebras"][0]["nome"] is "saudar"
// cada quebra diz o que fazer, e nao so o que houve
assert len(q["quebras"][0]["dica"]) bigger 15

// ── exigir mais um argumento: maior ──
maisArg := $"{pasta}/arg.df"
IO.write(maisArg, V1.replace("action somar(a: Integer, b: Integer)",
                             "action somar(a: Integer, b: Integer, c: Integer)"))
assert Abi.veredito(antes, maisArg) is "maior"

// mas um parametro OPCIONAL novo nao quebra: quem chamava com dois
// continua chamando com dois
opcional := $"{pasta}/opc.df"
IO.write(opcional, V1.replace("action somar(a: Integer, b: Integer)",
                              "action somar(a: Integer, b: Integer, c := 0)"))
assert Abi.veredito(antes, opcional) is "menor"
assert Abi.compativel(antes, opcional)

// ── renomear um parametro: maior ──
// E a regra que uma ferramenta feita para C nao precisaria ter: nesta
// linguagem a chamada com NOME existe, entao o nome do parametro e
// contrato, e nao so a posicao.
renomeado := $"{pasta}/ren.df"
IO.write(renomeado, V1.replace("action somar(a: Integer, b: Integer)",
                               "action somar(x: Integer, b: Integer)"))
quebras := Abi.quebras(antes, renomeado)
assert len([k cycle k in quebras given k["tipo"] is "parametro-renomeado"]) is 1

// ── trocar o retorno: maior ──
// O tipo de retorno ATRAVESSA a fronteira do adopt: quem usava o valor
// perde a conferencia, ou e acusado.
retorno := $"{pasta}/ret.df"
IO.write(retorno, V1.replace("-> Integer:\\n    yield a + b", "-> Float:\\n    yield a + b"))
assert len([k cycle k in Abi.quebras(antes, retorno)
            given k["tipo"] is "retorno-trocado"]) is 1

// ── o terceiro balde: o que a superficie NAO decide ──
// Acrescentar campo a um record quebra SE ele nao tiver padrao. A
// superficie le a declaracao sem executa-la e nao sabe qual dos dois e.
// Acusar quebra reprovaria um release correto; calar deixaria passar um
// que quebra. O honesto e um terceiro balde.
campoNovo := $"{pasta}/campo.df"
IO.write(campoNovo, V1.replace("    y: Integer\\n", "    y: Integer\\n    z: Integer\\n"))
c := Abi.comparar(antes, campoNovo)
assert c["atencao"][0]["tipo"] is "campo-novo-em-record"
assert len([k cycle k in c["quebras"] given k["nome"] is "Ponto"]) is 0

// ── uma superficie que nao compila NAO JULGA ──
// Um falso alarme aqui reprova um release que esta certo.
quebrado := $"{pasta}/quebrado.df"
IO.write(quebrado, "action mal(:\\n")
d := Abi.comparar(antes, quebrado)
assert d["veredito"] is "desconhecido"
assert d["motivo"] isnt ""

// ── o mapa de simbolos: o analogo do mapa do ligador ──
prog := $"{pasta}/prog.df"
IO.write(prog, "adopt Arcane.Math as M\\n\\n" +
               "action calcular(n):\\n" +
               "    yield M.sqrt(n) + len(\\"abc\\") + fantasma\\n")

origem := {e["nome"]: e["origem"] cycle e in Abi.mapa(prog)}
assert origem["M"] is "modulo"
assert origem["len"] is "embutido"
assert origem["calcular"] is "local"
assert origem["fantasma"] is "desconhecido"   // NINGUEM prove este nome

// ── PARTE 19: onde este programa roda ──
comProcesso := $"{pasta}/servidor.df"
IO.write(comProcesso, "adopt Arcane.Process as P\\nadopt Arcane.IO as F\\nout 1\\n")

// as exigencias saem dos adopt, com a linha
exigencias := Alvo.exigencias(comProcesso)
assert sorted([e["capacidade"] cycle e in exigencias]) is ["arquivos", "processo"]
assert exigencias[0]["linha"] bigger 0

// e o vocabulario e o MESMO do Arcane.Capacidade: dois vocabularios
// divergiriam no primeiro modulo novo
assert Cap.exige("Arcane.Process") is "processo"

// no servidor roda; numa aba, nao
assert Alvo.conferir(comProcesso, "servidor")["roda"]
aba := Alvo.conferir(comProcesso, "navegador")
assert not aba["roda"]
assert len(aba["problemas"]) is 2

// e cada ausencia vem com o MOTIVO, nao so com um "nao"
assert "SharedArrayBuffer" in Alvo.porque("navegador", "threads")
assert "soquete cru" in Alvo.porque("navegador", "rede")
assert Alvo.porque("servidor", "rede") is ""   // ele tem

// um programa puro roda em todo lugar
puro := $"{pasta}/puro.df"
IO.write(puro, "adopt Arcane.Math as M\\nout M.sqrt(4)\\n")
assert Alvo.exigencias(puro) is []
cycle nome in keys(Alvo.alvos()):
    assert Alvo.conferir(puro, nome)["roda"]

// um alvo inventado e recusado COM A LISTA
monitor:
    Alvo.conferir(puro, "nintendo")
    assert no
handle RuntimeError as e:
    assert "nintendo" in e.message
    assert "navegador" in e.message

// ── e a leitura e ESTATICA, e o modulo diz isso ──
// Um "roda" quer dizer "nao achei impedimento por esta via", e nao
// "vai funcionar".
limites := Alvo.limites()
assert len(limites) bigger_eq 3
assert "adopt" in join(" ", limites)

IO.remove_tree(pasta)
out "265 ok"`, lang: 'df', title: `exercicios/47-abi-e-alvos/265_superficie_e_alvos.df` },
  {"p": "Numa linguagem compilada, quebrar a **ABI** é trocar o layout de uma struct ou a convenção de chamada. O sintoma é cruel: o programa **carrega** e corrompe memória, longe da causa e sem nada denunciar."},
  {"p": "Aqui não há layout binário a quebrar. E existe **exatamente o mesmo problema**, com outro nome."},
  {"table": {"head": ["Na linguagem compilada", "Aqui"], "rows": [["símbolo removido do `.so`", "símbolo tirado do `relay`"], ["assinatura trocada", "aridade, nome ou tipo de parâmetro trocado"], ["layout de struct mudado", "campo acrescentado a um `record`"], ["`soname` bump", "versão **maior** no `forge.toml`"]]}},
  {"p": "**O sintoma também é o mesmo**: não é um erro de compilação de quem publicou. O módulo novo compila, os testes dele passam, o pacote sobe. O erro acontece na máquina de **quem consome**, depois — e a pessoa que vai depurar não é a que causou."},
  {"h3": "O que é contrato"},
  {"p": "A superfície respeita o `relay`. Um módulo que **declara** o que exporta está dizendo que o resto é interno — e o que é interno não é contrato, então mexer nele não quebra ninguém."},
  {"h3": "As regras que quebram"},
  {"table": {"head": ["Regra", "Por quê"], "rows": [["`simbolo-removido`", "quem o adotava para de compilar"], ["`especie-trocada`", "uma ação virou record: toda forma de uso muda"], ["`aridade-incompativel`", "uma chamada que era válida deixou de ser"], ["`parametro-renomeado`", "**a chamada com nome existe aqui**"], ["`tipo-de-parametro`", "quem passava o tipo antigo passa a ser recusado"], ["`retorno-trocado`", "o retorno **atravessa** a fronteira do `adopt`"], ["`campo-removido`", "todo acesso ao campo vira erro"]]}},
  {"p": "`parametro-renomeado` é a regra que uma ferramenta feita para C **não precisaria ter**. Em C o argumento é posicional e o nome não sai do cabeçalho; aqui `somar(a := 1, b := 2)` existe, então trocar `a` por `x` quebra — e quebra em silêncio, porque o `check` de quem consome acusa um nome que a pessoa nunca escreveu errado."},
  {"h3": "O terceiro balde"},
  {"p": "Acrescentar um campo a um `record` quebra `Ponto(3, 4)` **se o campo não tiver padrão**. Se tiver, é compatível. A superfície lê a declaração sem executá-la e **não sabe qual dos dois é**."},
  {"p": "Acusar quebra reprovaria um release correto; calar deixaria passar um que quebra. O honesto é um **terceiro balde** — em destaque no relatório, e que `--estrito` transforma em quebra para quem prefere o alarme."},
  {"p": "Pelo mesmo motivo, **uma superfície que não compila não julga**: `veredito` devolve `desconhecido` com o motivo. Um falso alarme aqui reprova um release que está certo — e a segunda vez que isso acontece, a conferência inteira é desligada."},
  {"h3": "O mapa de símbolos"},
  {"p": "Num projeto de duzentos arquivos, *\"de onde vem este nome?\"* é a pergunta que mais custa a responder à mão. Um ligador escreve isso num arquivo de mapa; aqui ele sai do mesmo caminho que o `check` usa."},
  {"p": "A linha que paga o mapa é `desconhecido`: um nome que nenhum `adopt`, nenhuma declaração local e nenhum embutido provê é, quase sempre, um erro de digitação, um `adopt` apagado, ou um nome que vem de um arquivo vizinho que este não importa."},
  {"h3": "Parte 19 — onde este programa roda"},
  {"p": "*Roda no navegador? numa função serverless? num WASI?* A resposta dependia de alguém conhecer de cor o que cada ambiente suporta."},
  {"p": "Seis alvos: `servidor`, `cli`, `navegador`, `wasi`, `funcao`, `embarcado`. E cada ausência vem com **o motivo**, não só com um `não`: threads no navegador dependem de `SharedArrayBuffer` e isolamento de origem; soquete cru não existe numa aba; o WASI não tem `fork`."},
  {"p": "**O vocabulário é o mesmo** de `Arcane.Capacidade`. Lá as capacidades são cobradas em execução; aqui são lidas antes de rodar. É a mesma pergunta feita de dois lados — e usar dois vocabulários faria as duas respostas divergirem no primeiro módulo novo."},
  {"h3": "O limite, dito em voz alta"},
  {"p": "**A leitura é estática, e sai dos `adopt` de um arquivo.**"},
  {"list": ["um módulo alcançado **indiretamente** não aparece;", "`adopt Python.x` conta como `python` e para aí;", "um `roda` quer dizer **\"não achei impedimento por esta via\"**, e não"]},
  {"p": "\"vai funcionar\"."},
  {"h3": "WebAssembly, com precisão"},
  {"p": "**Compilar para WASM** é produzir um `.wasm` com as funções da sua linguagem — e isso **não existe** aqui. **Rodar em WASM** é rodar o interpretador dentro de um runtime WASM — e isso **funciona**, pelo Pyodide, que compila o CPython para WebAssembly."},
  {"p": "Quem chama a segunda de \"DataForge compila para WASM\" está descrevendo outra coisa, e a diferença aparece no tamanho do artefato: o interpretador inteiro vai junto, alguns megabytes antes da primeira linha."},
  {"p": "Emitir um `.wasm` parcial \"só para dizer que emite\" seria uma caixa que se marca: ele não rodaria nenhum programa do repositório. A parte 8 já mostrou o que acontece quando se mede em vez de supor — a otimização que \"devia\" render, rendeu **1,01×**."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/47-abi-e-alvos/265_superficie_e_alvos.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '265-a-superficie-como-contrato-e-o-alvo-como-restricao', text: "265 · a superficie como contrato, e o alvo como restricao", level: 2 as const }, { id: 'o-que-e-contrato', text: "O que é contrato", level: 3 as const }, { id: 'as-regras-que-quebram', text: "As regras que quebram", level: 3 as const }, { id: 'o-terceiro-balde', text: "O terceiro balde", level: 3 as const }, { id: 'o-mapa-de-simbolos', text: "O mapa de símbolos", level: 3 as const }, { id: 'parte-19-onde-este-programa-roda', text: "Parte 19 — onde este programa roda", level: 3 as const }, { id: 'o-limite-dito-em-voz-alta', text: "O limite, dito em voz alta", level: 3 as const }, { id: 'webassembly-com-precisao', text: "WebAssembly, com precisão", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"47 · Superfície e alvos"}
      description={"1 exercícios: ."}
      href={"/docs/exercicios/47-abi-e-alvos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
