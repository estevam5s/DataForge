# Exercicio 173 — Erros e retentativas

## Enunciado

Trate falhas temporárias com `retry`, espera crescente e propagação controlada.

## `retry`

```dataforge
retry 5:
    resultado := chamada_instavel()
    out resultado
handle e:
    out $"desistiu: {e}"
```

Tenta o bloco até 5 vezes. Se alguma tentativa der certo, o `retry` termina ali.
Se todas falharem, o `handle` roda com o **último** erro.

## Nem todo erro merece retry

Esta é a distinção que separa retry útil de retry inútil:

| Tipo | Exemplos | Repetir? |
|------|----------|----------|
| **Temporário** | timeout, serviço indisponível, conexão recusada | sim |
| **Permanente** | senha inválida, 404, dado malformado | não |

Repetir um erro permanente é desperdício garantido: a senha não vai ficar válida
na terceira tentativa. Pior, atrasa a mensagem de erro que o usuário precisa ver.

```dataforge
action classificar_erro(mensagem):
    temporarios := ["timeout", "indisponivel", "conexao recusada"]
    cycle t in temporarios:
        given t in mensagem:
            yield "tentar de novo"
    yield "desistir"
```

## Espera crescente

Repetir imediatamente contra um serviço sobrecarregado piora a sobrecarga. A
prática correta é dobrar a espera:

```dataforge
espera := {"ms": 10}
// falha → espera 10ms → falha → espera 20ms → falha → espera 40ms
espera["ms"] := espera["ms"] * 2
```

Isso tem nome — *exponential backoff* — e é o que evita que N clientes em retry
derrubem um serviço que estava só se recuperando.

## Registrar e repassar

```dataforge
action camada_media():
    monitor:
        camada_baixa()
    handle e:
        registro.error("falha na camada baixa", {"motivo": e.message})
        propagate e.message
```

`propagate` relança depois de registrar. A camada do meio **anota o que sabe** —
contexto que o topo não teria — mas não decide o que fazer. Essa decisão pertence
a quem tem visão do todo.

O anti-padrão oposto é engolir:

```dataforge
handle e:
    registro.error("falhou")     // e agora? o chamador acha que deu certo
```

## Regra de ouro

**Trate o erro onde você pode fazer algo a respeito.** Nas camadas intermediárias,
registre e repasse.

## Saída esperada

```
── com retry ──
  sucesso na tentativa 3

── falhando sempre ──
  apos 3 tentativas: indisponivel

── com espera crescente ──
  tentativa 1 falhou, esperando 10ms
  tentativa 2 falhou, esperando 20ms
  conectado

── logando e propagando ──
23:59:01 ERROR [rede] falha na camada baixa motivo=disco cheio
  o topo recebeu: disco cheio

── decidindo sobre retry ──
  timeout ao conectar        -> tentar de novo
  senha invalida             -> desistir
  servico indisponivel       -> tentar de novo
  404 nao encontrado         -> desistir
```

## Experimente

- Escreva `retry_inteligente(acao, n)` que só repete erros temporários.
- Acrescente um limite total de tempo além do número de tentativas.
