# 386 — onde a sessão mora

A sessão na memória do processo some quando ele reinicia, e não
atravessa dois processos.

## Só o que MUDOU é gravado

Cada valor é codificado e comparado com a foto tirada ao abrir.
Gravar no `definir` perderia `itens.append(x)`, que não passa por ele.

## As três armadilhas que custaram

`PRAGMA journal_mode=WAL` ignora o `timeout` e dois processos subindo
juntos davam `database is locked`; um id desconhecido vira sessão
**nova**, senão o id plantado no cookie viraria sessão; e só id de 32
hexadecimais chega ao armazém, porque em arquivos o id é **nome de
arquivo**.

## E `encerrar_sessao` marca

Sem a marca, a gravação do fim do pedido recriava a sessão que acabou
de ser apagada.
