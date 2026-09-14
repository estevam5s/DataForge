# Supabase — banco do painel

Três arquivos, aplicados em ordem. São **idempotentes**: rodar duas vezes
não quebra nada.

```bash
python3 scripts/supabase_aplicar.py            # aplica tudo
python3 scripts/supabase_aplicar.py 01         # só o esquema
python3 scripts/supabase_aplicar.py --estado   # o que já existe lá
```

Ou cole o conteúdo no SQL Editor do Supabase, na ordem `01 → 05`.

| Arquivo | O que traz |
|---|---|
| `01_esquema.sql` | 10 tabelas, 25 políticas de RLS, gatilhos, a visão do placar |
| `02_agendamentos.sql` | pg_cron, 6 tarefas, fila de envios, log de execuções |
| `03_solucoes.sql` | esconde a solução de referência de quem ainda não resolveu |
| `04_downloads.sql` | quantos instalaram, de onde, sem guardar IP |
| `05_feedback_e_bibliotecas.sql` | o feedback do painel e os pacotes que a comunidade envia |

## As credenciais

O script lê `.supabase.local` na raiz do repositório — **gitignored**:

```
SUPABASE_URL=https://SEU-PROJETO.supabase.co
SUPABASE_SERVICE_ROLE=eyJ…
SUPABASE_ACCESS_TOKEN=sbp_…
SUPABASE_PROJECT_REF=SEU-PROJETO
```

E o site lê `site/.env.local`, também gitignored:

```
NEXT_PUBLIC_SUPABASE_URL=https://SEU-PROJETO.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ…
```

**A `service_role` nunca entra no site.** Ela ignora RLS: quem a tem lê e
escreve tudo. Ela vive só aqui, para aplicar migração. A `anon` é pública
por natureza — vai no bundle, e quem protege os dados é a RLS.

## As tabelas

| Tabela | Quem lê | Quem escreve |
|---|---|---|
| `perfis` | todos | o dono (menos o próprio papel) e admin |
| `projetos`, `trechos` | dono, público ou admin | o dono |
| `anotacoes`, `progresso` | só o dono | só o dono |
| `problemas` | todos (os publicados) | só admin |
| `submissoes` | dono e admin | o dono — **sem update nem delete** |
| `resolucoes` | dono e admin | o dono |
| `eventos` | só admin | qualquer um insere o seu |
| `metricas_diarias` | só admin | as tarefas agendadas |
| `agendamentos`, `execucoes_agendamento` | só admin | só admin |
| `envios` | destinatário e admin | só admin |

Três decisões que valem lembrar:

1. **`e_admin()` é `SECURITY DEFINER`.** A política de `perfis` consulta
   `perfis`; sem isso, a checagem dispararia a própria política e o
   Postgres abortaria com *infinite recursion detected*.

2. **O dono não pode mudar o próprio papel.** A política de update exige
   que `papel` continue igual ao que já está gravado — senão bastaria um
   `UPDATE` para qualquer um virar admin.

3. **Submissão não se edita nem se apaga.** É histórico. Sem política de
   update/delete, ambos ficam negados por padrão.

4. **O Postgres não faz RLS por coluna.** A política de select libera a
   linha inteira — e a linha de `problemas` tem a resposta. Por isso a
   prática lê a view `problemas_publicos`, que lista as colunas
   explicitamente, a tabela crua fica fechada a admin, e a solução sai
   por `solucao_de(uuid)`, que só a entrega a quem já resolveu.

   Esta era uma falha de verdade: o comentário do `01` afirmava que a
   RLS escondia a coluna, e não escondia. Qualquer um com a chave anon
   lia a resposta de todos os problemas.

## As tarefas agendadas

| Nome | Quando (UTC) | Faz |
|---|---|---|
| `processar_envios` | a cada 30 min | prepara a fila de envios |
| `pulso_horario` | de hora em hora | fotografia de uso |
| `metricas_diarias` | 3h10 | consolida o dia anterior |
| `zerar_ofensivas` | 3h05 | zera quem passou um dia sem praticar |
| `limpar_historico` | 4h30 | apaga eventos com mais de 90 dias |
| `resumo_semanal` | segunda, 12h | enfileira o resumo da semana |

A tabela `agendamentos` descreve; o `pg_cron` dispara. Mudar a expressão
pelo painel reagenda na hora — um gatilho chama `sincronizar_cron()`.

Para rodar uma à mão:

```sql
select public.rodar_agendamento('metricas_diarias');
```

O executor valida o nome da função contra uma lista fixa antes de chamar.
Sem essa lista, o campo `funcao` seria injeção de SQL com passo de admin.

## Promover alguém a admin

Pelo SQL Editor (a primeira vez não tem como ser pelo painel — ainda não
há admin para promover):

```sql
update public.perfis set papel = 'admin'
 where id = (select id from auth.users where email = 'voce@exemplo.com');
```

Depois disso, o painel em `/painel/admin/usuarios` faz o resto.

## Os problemas de prática

Vêm de `problemas/catalogo.py`. Toda solução de referência é verificada
contra todos os casos antes de publicar:

```bash
python3 scripts/gerar_problemas.py --testar   # só verifica
python3 scripts/gerar_problemas.py            # verifica e publica
```

Um problema cuja própria solução não passa nunca chega ao banco — e
descobrir isso pelo usuário seria tarde demais.

## As duas portas de escrita do 05

`feedback` e `bibliotecas_enviadas` **não têm política de INSERT**. A
escrita passa só por `enviar_feedback()` e `enviar_biblioteca()`, que são
`security definer` — e é isso que permite validar antes de gravar.

Uma tabela aberta a `authenticated` vira lixeira no dia em que alguém
descobre o endpoint. E o limite por janela (5 feedbacks por hora, 3
bibliotecas por dia) precisa viver no banco: no cliente ele é decoração,
porque quem manda o POST escolhe se executa o JavaScript da página.

As validações estão escritas **duas vezes de propósito** — no `CHECK` da
tabela e no começo da função. O `CHECK` protege o dado; a função produz a
mensagem. Sem ela, quem escreve um assunto de dois caracteres recebe
`new row for relation "feedback" violates check constraint
"feedback_assunto_check"`, que fala da restrição e não do que fazer.

Verificado ponta a ponta, com usuário de verdade:

| | |
|---|---|
| anônimo escreve feedback | recusado |
| autor lê o feedback de outro | 0 linhas |
| 6º feedback na mesma hora | recusado, com a dica de esperar |
| nome de pacote `../escapar` | recusado, dizendo a forma aceita |
| tarball `http://` | recusado, dizendo por quê |
| outra pessoa reusa um nome já publicado | recusado, nomeando o dono |
| usuário comum aprova um pacote | recusado |
| pacote pendente no registro público | não aparece |
