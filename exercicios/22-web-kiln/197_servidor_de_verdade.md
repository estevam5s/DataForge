# Exercicio 197 — Subir o servidor de verdade

## Enunciado

Acenda o forno, faça pedidos pela rede e apague.

## Conceitos

Três formas de rodar, para três momentos:

| Forma | Faz | Quando |
|-------|-----|--------|
| `Kiln.test(app, verbo, caminho)` | executa a rota, sem socket | teste |
| `Kiln.serve(app, porta)` | sobe em segundo plano, devolve a porta | script, teste de integração |
| `ignite app on 8080` | sobe e bloqueia até Ctrl-C | produção |

```dataforge
porta := Kiln.serve(contador, 0)     // 0 = o sistema escolhe uma livre
// … faz pedidos …
Kiln.stop(contador)
```

## O que observar

**Porta 0 deixa o sistema escolher.** Numa suíte de testes, porta fixa dá
conflito quando dois testes rodam juntos — ou quando você esqueceu um servidor
no ar. `Kiln.serve` devolve a porta que saiu.

**O estado do programa sobrevive entre pedidos.** A variável `visitas` é do
programa, não do pedido: três chamadas a `/contar` dão 3. Isso vale para
qualquer estado em memória — e some quando o processo reinicia.

**`Kiln.stats` conta o que aconteceu**: pedidos, erros, rotas e tempo no ar.

**Cada pedido roda numa thread.** Dois pedidos simultâneos que escrevem na
mesma variável podem perder atualizações — a linguagem não sincroniza threads.

## Erros comuns

- Usar `ignite` num teste. Ele bloqueia, e o teste nunca termina.
- Esquecer `Kiln.stop`. A porta fica ocupada até o processo morrer.
- Guardar sessão em memória e rodar vários processos. Cada um tem a sua, e o
  visitante desloga a cada pedido.
