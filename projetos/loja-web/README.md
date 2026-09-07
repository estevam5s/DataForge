# loja-web

Um site completo em DataForge: páginas HTML, API REST no mesmo processo,
sessão com cookie, banco SQLite e exportação para Excel — sem nenhuma
dependência externa.

```bash
cd projetos/loja-web
dataforge test tests/            # 29 testes
dataforge run src/main.df        # http://127.0.0.1:8080
dataforge run src/main.df -- 3000
```

Login para experimentar: `ferreiro` / `bigorna`.

## As rotas

| Rota | Devolve |
|------|---------|
| `GET /` | catálogo em HTML, com filtro por categoria |
| `GET /produto/:id` | ficha do produto (404 com página se não existir) |
| `GET /relatorio` | totais e valor em estoque por categoria |
| `GET /relatorio.xlsx` | o mesmo relatório, com fórmulas vivas |
| `GET /entrar`, `POST /entrar`, `GET /sair` | sessão |
| `GET /admin` | exige login |
| `GET /static/*` | CSS |
| `/api/produtos` | GET, POST, PUT, DELETE — JSON |
| `/api/categorias` | GET |

A API é um segundo `server`, montado sob `/api` com `Kiln.mount`. As duas
aplicações compartilham o processo e a conexão com o banco.

## Os arquivos

```
src/banco.df     tudo o que toca SQL — trocar SQLite é mexer aqui só
src/paginas.df   o que o visitante vê; devolve HTML pronto
src/app.df       as rotas; monta e NÃO sobe nada
src/main.df      lê a porta e acende
views/           templates
www/             CSS
tests/           29 testes, sem abrir socket
```

**`app.df` monta e `main.df` acende.** A separação não é enfeite: um teste
que importasse o `main` subiria o servidor e nunca terminaria.

## O que este projeto mostra

**Testar rota é tão barato quanto testar função.** `Kiln.test` executa o
pedido direto na aplicação, sem socket. Os 29 testes rodam em 0,06s — e é
isso que faz alguém realmente escrevê-los.

**A planilha é gerada na hora, do mesmo dado da tela.** O `/relatorio.xlsx`
não é um arquivo guardado: é montado no pedido, com as fórmulas que o Excel
resolve ao abrir. Quem recebe pode mexer nos números e ver o total mudar.

**O caminho é relativo ao programa, não a quem o chamou.** `OS.beside("..")`
resolve a raiz do projeto a partir do arquivo em execução — sem isso, rodar
de duas pastas diferentes carrega templates diferentes.

## Três armadilhas que este projeto atravessou

1. **`query["x"]` sem `??` dá 500.** A query é do visitante: a chave pode não
   vir, e indexar um vault sem a chave é erro. O mesmo vale para `body`.
2. **Cada pedido roda numa thread.** Uma conexão SQLite comum recusa ser usada
   em outra thread; o `Arcane.Database` serializa o acesso para que isso
   funcione. Um teste que roda tudo na mesma thread **não** pega esse bug — só
   subir o servidor de verdade pegou.
3. **`>> distill a, v: a + v 0 / len(x)` divide o zero**, não a soma. O valor
   inicial vem depois do corpo. O relatório mostrava a soma como se fosse a
   média, e nada na tela denunciava.
