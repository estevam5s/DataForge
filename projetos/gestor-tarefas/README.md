# gestor-tarefas

Gestor de tarefas de linha de comando.

```bash
dataforge install
dataforge run src/main.df -- adicionar "Comprar pão" --prioridade 3 --prazo 2026-09-15
dataforge run src/main.df -- listar
dataforge run src/main.df -- listar --pendentes
dataforge run src/main.df -- concluir 1
dataforge run src/main.df -- resumo
```

```
┌───┬───┬─────────────────────────┬────────┬───────────────────────┐
│   │ # │ Tarefa                  │ Prior. │ Prazo                 │
├───┼───┼─────────────────────────┼────────┼───────────────────────┤
│   │ 1 │ Escrever a documentação │ alta   │ 2026-09-15            │
│ ✓ │ 2 │ Revisar os testes       │ media  │ —                     │
│   │ 3 │ Comprar café            │ baixa  │ 2026-09-01 (atrasada) │
└───┴───┴─────────────────────────┴────────┴───────────────────────┘
```

## Estrutura

| Arquivo | Responsabilidade |
|---------|------------------|
| `src/tarefa.df` | o modelo — um `record`, porque duas tarefas iguais são a mesma |
| `src/repositorio.df` | persistência em JSON, isolada atrás de uma interface |
| `src/main.df` | CLI e apresentação |

## Decisões

**Tarefa é record, não blueprint.** O que muda é a lista que as contém; a tarefa
em si é um valor. Concluir uma cria uma cópia com `with`, e o original fica
intacto — o que torna impossível alterar uma tarefa por engano em outro ponto do
código.

**O repositório absorve arquivo corrompido.** Um JSON quebrado avisa e começa
vazio, sem apagar o original. Derrubar o programa por causa de um arquivo que
alguém editou à mão seria pior que seguir.

**Configuração em camadas.** Padrão, arquivo, ambiente e argumentos, nessa ordem
de precedência. `cofre` guarda de onde veio cada valor, o que responde a pergunta
que se faz às três da manhã.
