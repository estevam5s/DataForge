# Exercicio 194 — Páginas HTML com template

## Enunciado

Renderize uma página a partir de um template com laço e caso vazio.

## Conceitos

`views` diz onde ficam os templates; `render` lê um deles e devolve HTML:

```dataforge
server site on 8080:
    views "./paginas"

    route GET "/":
        render "lista.html" with {"titulo": "Forja", "produtos": produtos}
```

A sintaxe do template é pequena de propósito:

| Marca | Faz |
|-------|-----|
| `{{nome}}` | escreve o valor, **escapando HTML** |
| `{{&nome}}` | escreve sem escapar |
| `{{#lista}}…{{/lista}}` | repete para cada item |
| `{{^lista}}…{{/lista}}` | mostra quando a lista está vazia |
| `{{.}}` | o item atual, numa lista de valores simples |

Template que vira linguagem é código escondido onde ninguém procura. Lógica de
verdade fica no `.df`.

## O que observar

**O escape é o padrão, não a opção.** Um produto chamado `Bigorna <de aço>` sai
como `Bigorna &lt;de aço&gt;`. Isso fecha a porta para XSS por acidente — a
falha mais comum em página gerada por servidor. Para escrever HTML de
propósito, `{{&campo}}`, e a diferença de um caractere é o que torna a decisão
visível na revisão.

**`{{^lista}}` existe porque lista vazia é caso normal.** Sem ele, a página
vazia sai em branco e ninguém sabe se quebrou.

**`render` também encerra a rota**, como `respond`.

## Erros comuns

- Bloco aberto e nunca fechado (`{{#itens}}` sem `{{/itens}}`). O Kiln reclama
  com o nome do bloco em vez de renderizar metade da página.
- Esquecer o `views`. Sem a pasta declarada, `render` diz exatamente isso.
- Usar `{{&campo}}` com texto vindo do usuário. É abrir a porta que o escape
  fecha.
