# Exercício 205 — Modelos e validação

## Enunciado

Declare um modelo, e deixe que ele recuse dado inválido.

## Conceitos

Um modelo descreve a tabela **e** o que vale nela:

```dataforge
Usuario := Forge.modelo("Usuario", {
    "email": {"tipo": "Texto", "obrigatorio": yes, "unico": yes,
              "validacoes": ["email"]},
    "idade": {"tipo": "Inteiro", "validacoes": [["minimo", 0], ["maximo", 130]]}
}, {"conexao": db})
```

O nome da tabela sai do plural: `Usuario` → `usuarios`.

## O que observar

**A validação junta TODOS os problemas.** Um formulário que aponta um erro por
vez faz o usuário submeter cinco vezes para descobrir cinco problemas.
`e.campos` traz um item por problema.

**Os tipos voltam convertidos.** SQLite guarda booleano como 0 e 1. Sem a
conversão de volta, `given usuario["ativo"]:` seria **sempre verdadeiro** — 0 é
um inteiro, e a comparação nunca falharia visivelmente. Erros assim vivem meses.

**Campo desconhecido é recusado.** Um `nomee` digitado errado viraria uma coluna
fantasma que nada lê.

## Armadilhas

- `buscar` devolve `void` quando não acha; `buscar_ou_erro` levanta
  `RecordNotFoundError`. Use o primeiro quando a ausência é prevista.
- `marcas_de_tempo` acrescenta `criado_em` e `atualizado_em` — mas só se você
  migrar depois de declará-las.

## Relacionados

- [206 — Relações](206_relacoes_sem_n_mais_um.md)
- [207 — Migrações](207_migracoes.md)
