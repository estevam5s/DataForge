// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "07 · Erros",
  description: "10 exercícios: monitor/handle/ensure, trigger, retry e defer.",
};

const blocos: Bloco[] = [
  {"p": "Nível: **Primeiros passos** · monitor/handle/ensure, trigger, retry e defer · [todos os módulos](/docs/exercicios)"},
  { code: `python3 exercicios/run_all.py 07`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[077](#077-monitor-handle)", "**monitor / handle**", "capture uma divisao por zero sem derrubar o programa."], ["[078](#078-ensure-finally)", "**ensure (finally)**", "garanta que a limpeza rode com ou sem erro."], ["[079](#079-trigger-lancar-erro)", "**trigger (lancar erro)**", "valide a entrada de uma acao lancando erros descritivos."], ["[080](#080-handle-tipado)", "**handle tipado**", "capture apenas um tipo de erro e deixe os outros passarem."], ["[081](#081-monitor-sem-handle-propaga)", "**monitor sem handle propaga**", "comprove que um monitor com apenas ensure nao engole o erro."], ["[082](#082-guard-e-validate)", "**guard e validate**", "compare as duas formas de pre-condicao."], ["[083](#083-retry)", "**retry**", "repita uma operacao instavel ate ter sucesso."], ["[084](#084-propagate)", "**propagate**", "registre o erro e repasse para o chamador."], ["[085](#085-assert)", "**assert**", "use assert como verificacao interna e capture a falha."], ["[086](#086-pilha-de-erros-e-recuperacao)", "**Pilha de erros e recuperacao**", "converta valores com fallback em varias camadas."]]}},
  {"h2": "077 · monitor / handle"},
  {"p": "**Enunciado.** capture uma divisao por zero sem derrubar o programa."},
  { code: `resultado := void
monitor:
    resultado := 10 / 0
handle e:
    out "capturado:", e
    resultado := -1

out "continuou, resultado =", resultado
assert resultado is -1, "o handle rodou"`, lang: 'df', title: `exercicios/07-erros/077_monitor_handle.df` },
  {"h2": "078 · ensure (finally)"},
  {"p": "**Enunciado.** garanta que a limpeza rode com ou sem erro."},
  { code: `log := []

action com_falha():
    monitor:
        log.append("inicio")
        trigger "falhou"
    handle e:
        log.append("tratou")
    ensure:
        log.append("limpou")

action sem_falha():
    monitor:
        log.append("ok")
    handle e:
        log.append("nao deveria")
    ensure:
        log.append("limpou2")

com_falha()
sem_falha()
out log

assert log is ["inicio", "tratou", "limpou", "ok", "limpou2"], "ensure sempre roda"`, lang: 'df', title: `exercicios/07-erros/078_ensure.df` },
  {"h2": "079 · trigger (lancar erro)"},
  {"p": "**Enunciado.** valide a entrada de uma acao lancando erros descritivos."},
  { code: `action idade_valida(n):
    given typeof(n) isnt "Integer":
        trigger "idade precisa ser Integer"
    given n smaller 0:
        trigger "idade nao pode ser negativa"
    given n bigger 150:
        trigger "idade improvavel"
    yield n

erros := []
cycle entrada in ["x", -5, 200, 30]:
    monitor:
        out "ok:", idade_valida(entrada)
    handle e:
        erros.append(e.message)
        out "erro:", e

assert len(erros) is 3, "tres entradas invalidas"
assert erros[0] is "idade precisa ser Integer", "tipo"
assert erros[1] is "idade nao pode ser negativa", "negativa"`, lang: 'df', title: `exercicios/07-erros/079_trigger.df` },
  {"h2": "080 · handle tipado"},
  {"p": "**Enunciado.** capture apenas um tipo de erro e deixe os outros passarem."},
  { code: `capturou_runtime := no
monitor:
    x := 1 / 0
handle RuntimeError as e:
    capturou_runtime := yes
    out "runtime:", e.type, "-", e.message

assert capturou_runtime is yes, "capturou RuntimeError"

escapou := no
monitor:
    monitor:
        trigger "erro do usuario"
    handle RuntimeError as e:
        out "nao deveria capturar aqui"
handle externo:
    escapou := yes
    out "escapou para o handler externo:", externo.type

assert escapou is yes, "TriggerError nao casa com RuntimeError"`, lang: 'df', title: `exercicios/07-erros/080_handle_tipado.df` },
  {"h2": "081 · monitor sem handle propaga"},
  {"p": "**Enunciado.** comprove que um monitor com apenas ensure nao engole o erro."},
  { code: `log := []
propagou := no

monitor:
    monitor:
        log.append("tentou")
        trigger "erro interno"
    ensure:
        log.append("limpou")
handle e:
    propagou := yes
    log.append("externo tratou")

out log
assert propagou is yes, "o erro chegou ao handler externo"
assert log is ["tentou", "limpou", "externo tratou"], "ordem de execucao"`, lang: 'df', title: `exercicios/07-erros/081_monitor_sem_handle.df` },
  {"h2": "082 · guard e validate"},
  {"p": "**Enunciado.** compare as duas formas de pre-condicao."},
  { code: `action com_guard(n):
    guard n bigger 0, "guard: n precisa ser positivo"
    yield n * 2

action com_validate(n):
    validate n bigger 0, "validate: n precisa ser positivo"
    yield n * 3

msgs := []
cycle acao in [com_guard, com_validate]:
    monitor:
        acao(-1)
    handle e:
        msgs.append(e.message)

out msgs
assert com_guard(5) is 10, "guard passa"
assert com_validate(5) is 15, "validate passa"
assert msgs[0] is "guard: n precisa ser positivo", "guard dispara"
assert msgs[1] is "validate: n precisa ser positivo", "validate dispara"`, lang: 'df', title: `exercicios/07-erros/082_guard_validate.df` },
  {"h2": "083 · retry"},
  {"p": "**Enunciado.** repita uma operacao instavel ate ter sucesso."},
  { code: `tentativas := {"n": 0}

retry 5:
    tentativas["n"] := tentativas["n"] + 1
    given tentativas["n"] smaller 3:
        trigger "instabilidade temporaria"
    out "sucesso na tentativa", tentativas["n"]
handle e:
    out "desistiu apos as tentativas:", e

assert tentativas["n"] is 3, "precisou de 3 tentativas"

falhas := {"n": 0}
capturou := no
retry 2:
    falhas["n"] := falhas["n"] + 1
    trigger "sempre falha"
handle e:
    capturou := yes
    out "handler final:", e

assert falhas["n"] is 2, "tentou 2 vezes"
assert capturou is yes, "o handler final rodou"`, lang: 'df', title: `exercicios/07-erros/083_retry.df` },
  {"h2": "084 · propagate"},
  {"p": "**Enunciado.** registre o erro e repasse para o chamador."},
  { code: `log := []

action camada_baixa():
    trigger "falha de disco"

action camada_media():
    monitor:
        camada_baixa()
    handle e:
        log.append("media viu: " + e.message)
        propagate e.message

chegou := no
monitor:
    camada_media()
handle e:
    chegou := yes
    log.append("topo viu: " + e.message)

out log
assert chegou is yes, "o erro subiu ate o topo"
assert log is ["media viu: falha de disco", "topo viu: falha de disco"], "propagacao registrada"`, lang: 'df', title: `exercicios/07-erros/084_propagate.df` },
  {"h2": "085 · assert"},
  {"p": "**Enunciado.** use assert como verificacao interna e capture a falha."},
  { code: `action media(nums):
    assert len(nums) bigger 0, "a lista nao pode ser vazia"
    yield sum(nums) / len(nums)

out media([2, 4, 6])
assert media([2, 4, 6]) is 4.0, "media"

falhou := no
monitor:
    media([])
handle e:
    falhou := yes
    out "assert disparou:", e

assert falhou is yes, "assert com lista vazia dispara"`, lang: 'df', title: `exercicios/07-erros/085_assert.df` },
  {"h2": "086 · Pilha de erros e recuperacao"},
  {"p": "**Enunciado.** converta valores com fallback em varias camadas."},
  { code: `action para_inteiro(texto, padrao := 0):
    monitor:
        yield cast texto as Integer
    handle e:
        yield padrao

entradas := ["10", "abc", "42", ""]
convertidos := []
cycle t in entradas:
    convertidos.append(para_inteiro(t, -1))

out convertidos
assert convertidos is [10, -1, 42, -1], "conversao com fallback"

// erro dentro de laco nao interrompe as demais iteracoes
processados := 0
cycle n in [1, 0, 2, 0, 3]:
    monitor:
        x := 10 / n
        processados += 1
    handle e:
        skip
assert processados is 3, "tres divisoes validas"
out "processados:", processados`, lang: 'df', title: `exercicios/07-erros/086_erros_aninhados.df` },
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/07-erros/077_monitor_handle.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '077-monitor-handle', text: "077 · monitor / handle", level: 2 as const }, { id: '078-ensure-finally', text: "078 · ensure (finally)", level: 2 as const }, { id: '079-trigger-lancar-erro', text: "079 · trigger (lancar erro)", level: 2 as const }, { id: '080-handle-tipado', text: "080 · handle tipado", level: 2 as const }, { id: '081-monitor-sem-handle-propaga', text: "081 · monitor sem handle propaga", level: 2 as const }, { id: '082-guard-e-validate', text: "082 · guard e validate", level: 2 as const }, { id: '083-retry', text: "083 · retry", level: 2 as const }, { id: '084-propagate', text: "084 · propagate", level: 2 as const }, { id: '085-assert', text: "085 · assert", level: 2 as const }, { id: '086-pilha-de-erros-e-recuperacao', text: "086 · Pilha de erros e recuperacao", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"07 · Erros"}
      description={"10 exercícios: monitor/handle/ensure, trigger, retry e defer."}
      href={"/docs/exercicios/07-erros"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
