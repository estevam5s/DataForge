# 227 — Chamada entre serviços que não mente

## O terceiro estado

Uma chamada de ação tem dois desfechos: devolve, ou levanta. Uma chamada de
**rede** tem três, e o terceiro é o que quebra sistemas:

| Desfecho | Como se vê |
|---|---|
| funcionou | `ok` é `yes`, `status` 2xx |
| falhou, e se sabe | `ok` é `no`, `status` 4xx/5xx |
| **não se sabe** | `ok` é `no`, `status` **0** |

O `status 0` é o caso honesto: o pedido pode ter chegado e a resposta ter se
perdido; pode estar a caminho ainda; pode ter sido processado duas vezes. Um
cliente que colapsa esse caso em "falhou" faz o programa acima dele repetir
uma cobrança.

É por isso que `Malha` devolve um **vault** em vez de levantar. Quem chama um
serviço precisa decidir o que fazer com cada um dos três, e um `monitor` em
volta de cada chamada não distinguiria os dois últimos.

## Por que um cliente por serviço, e não por chamada

```dataforge
Malha.registrar("estoque", "http://estoque:8080", {…})
cliente := Malha.de("estoque")
assert Malha.de("estoque") is cliente     // o MESMO objeto
```

O disjuntor e as métricas vivem **no cliente**. Um cliente novo a cada chamada
esqueceria que o serviço está caído — o que é exatamente a informação que
impede a avalanche.

## Retry: só o que é seguro

`Malha` repete por dois critérios, e os dois importam:

| Repete | Não repete |
|---|---|
| `status 0` (não chegou) | 4xx — o pedido está errado, repetir dá o mesmo erro com mais latência |
| 502, 503, 504 | 400, 401, 403, 404, 422 |
| 429, respeitando `Retry-After` | 500 sem `Retry-After`? **repete** — pode ser transitório |
| GET, HEAD, PUT, DELETE (idempotentes) | POST e PATCH, **a menos que** venha `chave :=` |

A última linha é a regra que separa um cliente correto de um perigoso. `POST
/cobrancas` repetido cobra duas vezes. Com `chave := "pedido-8f2a"` o servidor
tem como reconhecer o pedido repetido, e só então repetir é seguro:

```dataforge
cliente.post("/reservas", {"sku": "CAF-500"}, chave := "pedido-8f2a")
```

A chave viaja em `Idempotency-Key`. **Quem garante a idempotência é o
servidor**, não o cliente — a chave só dá a ele o meio.

## O disjuntor, e a conta que engana

```
    fechado   ────falhas demais────▶  aberto
       ▲                               │
       │                          espera passou
    sucesso                            │
       │                               ▼
       └──────────────────────  entreaberto
                                (deixa UM passar)
```

Sem disjuntor, um serviço que cai **leva** os que dependem dele: cada pedido
espera o prazo inteiro antes de falhar, as threads acabam, e o que estava de pé
cai também. E o serviço caído nunca se recupera, porque nunca para de receber.

O `entreaberto` existe para a volta: com cem threads esperando, abrir tudo de
uma vez derruba o serviço no instante em que ele volta.

**A conta que engana** — o disjuntor conta cada **tentativa**, não cada
chamada:

```dataforge
cliente := Malha.cliente(base, {"tentativas": 4, "disjuntor": {"falhas": 3}})
r := cliente.get("/quebrado")
assert r["tentativas"] is 4
assert cliente.disjuntor.estado is "aberto"   // a PRIMEIRA chamada abriu
```

Quatro tentativas contra um limite de três: uma chamada só já abre. Ao calibrar,
o limite precisa ser lido como "tentativas até desistir", e `cliente.disjuntor.falhas`
mostra o número de verdade.

**Um 4xx não abre o disjuntor.** Não é falha do serviço — o pedido está errado.
Contar isso abriria o disjuntor por um bug de quem chama, e derrubaria uma
dependência sadia.

## O rastro atravessa a fronteira

Sem um identificador que viaja com o pedido, investigar um incidente em cinco
serviços é cruzar horário de log — o que é impossível quando dois pedidos
acontecem no mesmo segundo.

```dataforge
Malha.comecar_contexto(void, "pedidos", {"tenant": "acme"})
cliente.get("/estoque/CAF-500")    // vai com 'X-Request-Id' e 'X-Ctx-Tenant'
Malha.terminar_contexto()
```

A metade que se esquece é a **borda**: o serviço que recebe precisa *continuar*
o rastro que chegou, e não começar um novo.

```dataforge
middleware:
    Malha.propagar(request, "estoque")
```

Sem isso, cada serviço inicia um rastro próprio e a corrente se quebra
exatamente no ponto onde ela serviria.

## Qual o próximo problema

Este exercício cobre o cliente. O que ele **não** resolve está em `228`:
duas escritas em serviços diferentes que precisam acontecer juntas — e não
podem, porque não há transação que atravesse a rede.
