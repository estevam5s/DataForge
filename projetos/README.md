# Projetos

Três programas completos que juntam as bibliotecas do registro. Não são
exercícios: cada um tem estrutura de projeto, testes e um `forge.toml` com
dependências reais.

```bash
cd projetos/gestor-tarefas
dataforge install
dataforge test tests/
dataforge run src/main.df -- listar
```

| Projeto | O que faz | Bibliotecas |
|---------|-----------|-------------|
| [gestor-tarefas](gestor-tarefas/) | CLI de tarefas com prazos e persistência | argumentos, tabela, datas, cofre, colecao, registro |
| [analise-vendas](analise-vendas/) | Lê CSV e produz relatório estatístico | estatistica, colecao, tabela, moeda, datas, progresso |
| [api-links](api-links/) | Encurtador de URL com servidor HTTP | validador, cache, registro, aleatorio, cofre, estado |

## O que cada um mostra

**gestor-tarefas** — a estrutura de uma CLI: `argumentos` gera a ajuda da mesma
declaração que faz a leitura, `cofre` monta a configuração em camadas, e o
repositório fica isolado atrás de uma interface para que trocar JSON por SQLite
seja mexer num arquivo só.

**analise-vendas** — o pipeline de dados: converter na entrada (e falhar cedo se
algo não converte), calcular, e apresentar. O relatório avisa quando o desvio
padrão passa de metade da média, porque aí o ticket médio não descreve as vendas
— e diz quando o r² da tendência é baixo demais para confiar nela.

**api-links** — separar regra de negócio de transporte. Toda a lógica está em
`encurtador.df`, testada em milissegundos; `main.df` é uma casca fina de HTTP. É
o que torna 11 testes de comportamento viáveis sem subir servidor.

## Rodando os três

```bash
for p in gestor-tarefas analise-vendas api-links; do
  (cd "projetos/$p" && dataforge install >/dev/null && dataforge test tests/)
done
```
