# -*- coding: utf-8 -*-
"""Bibliotecas — mais nove páginas: como uma API evolui.

As dezesseis páginas anteriores cobrem escrever, testar e publicar. Estas
cobrem o que acontece DEPOIS da primeira versão: marcar o que vai sumir,
o que ainda pode mudar, contar o que mudou, escolher licença e
dependências, escrever mensagens que servem a quem não leu o código, e
migrar quem usa. Vêm com `Arcane.Evolucao`, que é a peça que faltava.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/bibliotecas/obsolescencia",
"title": "Marcar o que vai sumir",
"description": "Arcane.Evolucao.obsoleta — a ação continua funcionando, e quem a chama é avisado uma vez.",
"blocos": [
 {"p": "Remover uma ação de uma versão para a outra quebra quem a usa no dia da atualização. O caminho é avisar **antes**: numa versão menor, a ação continua funcionando e avisa; numa versão maior, ela sai. Quem prestou atenção ao aviso já migrou."},
 {"code": """adopt Arcane.Evolucao as Ev

action calcular_total(itens):
    yield sum(itens)

mark @Ev.obsoleta("o nome dizia menos do que faz", desde := "1.4", use := "calcular_total")
action total(itens):
    yield calcular_total(itens)

cycle i in range(0, 3):
    assert total([1, 2]) is 3       // funciona — e avisa UMA vez

a := Ev.avisos()
assert len(a) is 1 and a[0]["acao"] is "total"
out a[0]["mensagem"]""", "lang": "df"},
 {"code": """$ dataforge run app.df
aviso: 'total' esta obsoleta desde a 1.4: o nome dizia menos do que faz. Use 'calcular_total'.""", "lang": "text"},
 {"h2": "Três decisões"},
 {"table": {"head": ["Decisão", "Sem ela"], "rows": [
   ["o aviso sai **uma vez por ação**", "uma ação obsoleta num laço de um milhão imprimiria um milhão de linhas — e o aviso que se repete é o aviso que se aprende a filtrar"],
   ["o aviso vai para a **saída de erro**", "um programa cuja saída é lida por outro (CSV, JSON) teria um aviso no meio dos dados"],
   ["`DF_OBSOLETOS=erro` reprova", "o aviso impresso não para nada; no CI, ele precisa reprovar"]]}},
 {"code": """DF_OBSOLETOS=erro dataforge test        # no CI: o uso obsoleto reprova
DF_OBSOLETOS=silencio dataforge run app.df   # quando nao da para mudar agora""", "lang": "bash"},
 {"h2": "O calendário"},
 {"table": {"head": ["Versão", "O que acontece com `total`"], "rows": [
   ["1.4 (menor)", "`calcular_total` nasce; `total` passa a avisar"],
   ["1.5, 1.6 (menores)", "continua avisando — tempo para migrar"],
   ["2.0 (maior)", "`total` sai; o CHANGELOG diz o que usar"]]}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/bibliotecas/experimental",
"title": "API experimental",
"description": "Marcar o que ainda pode mudar sem aviso de versão — e por que isso protege os dois lados.",
"blocos": [
 {"p": "Semver promete que uma versão menor não quebra nada. Isso é ótimo para quem usa e é uma prisão para quem escreve: a primeira versão de uma API raramente é a certa. `experimental` separa o que já é promessa do que ainda é rascunho."},
 {"code": """adopt Arcane.Evolucao as Ev

mark @Ev.experimental("a assinatura ainda vai mudar")
action prever_demanda(historico):
    yield sum(historico) / len(historico)

assert prever_demanda([10, 20, 30]) is 20.0
assert Ev.avisos()[0]["tipo"] is "experimental\"""", "lang": "df"},
 {"table": {"head": ["", "Obsoleta", "Experimental"], "rows": [
   ["diz", "*vai sumir*", "*pode mudar*"],
   ["`DF_OBSOLETOS=erro`", "reprova", "**não** reprova — usar o experimental é escolha legítima"],
   ["entra no `dataforge abi`", "sim, até sair", "declare no README que não entra na promessa"]]}},
 {"callout": {"tipo": "dica", "titulo": "Experimental tem prazo", "texto": "Uma API experimental há três versões não é experimental: é uma API que você não teve coragem de prometer. Ou ela vira estável, ou sai."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/bibliotecas/changelog",
"title": "O CHANGELOG",
"description": "O que escrever, em que ordem, e a seção que quase todo mundo esquece.",
"blocos": [
 {"p": "O CHANGELOG é para quem vai **atualizar**, e a pergunta dessa pessoa é uma só: *o que eu preciso mudar no meu código?*. Por isso ele é organizado pelo efeito, e não pela ordem dos commits."},
 {"code": """## 2.0.0

### Quebra — o que voce precisa mudar
- `total(itens)` foi removida. Use `calcular_total(itens)` — avisava desde a 1.4.

### Adicionado
- `calcular_frete(uf, peso)`.

### Corrigido
- `desconto` arredondava para baixo; agora arredonda para o mais proximo.

### Obsoleto — vai sair na 3.0
- `frete_fixo()`: use `calcular_frete`.""", "lang": "text", "title": "CHANGELOG.md"},
 {"table": {"head": ["Seção", "Porque ela existe"], "rows": [
   ["**Quebra** (primeiro)", "é o que impede a atualização; escondê-la no meio é o que faz alguém atualizar e quebrar produção"],
   ["Adicionado", "o que se ganha"],
   ["Corrigido", "o comportamento que mudou — uma correção é uma mudança para quem dependia do defeito"],
   ["**Obsoleto**", "a seção esquecida: é ela que dá tempo de migrar"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Uma correção também quebra", "texto": "Se `desconto` arredondava errado há dois anos, alguém tem um relatório que depende do número errado. A correção entra no CHANGELOG dizendo **o que mudou no resultado** — e não só *“corrigido bug”*."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/bibliotecas/licenca",
"title": "Licença",
"description": "Por que uma biblioteca sem licença não pode ser usada, e o que cada família permite.",
"blocos": [
 {"p": "Código sem licença é, por padrão, **todos os direitos reservados**: ninguém pode usar, copiar ou modificar legalmente, por mais pública que seja a página. Uma biblioteca sem licença é uma biblioteca que uma empresa não pode adotar."},
 {"code": """[project]
name = "placa"
version = "1.0.0"
license = "MIT"            # o identificador SPDX""", "lang": "toml", "title": "forge.toml"},
 {"table": {"head": ["Família", "Exemplos", "Quem usa pode…", "Exige"], "rows": [
   ["permissiva", "MIT, BSD, Apache-2.0", "usar em código fechado", "manter o aviso de copyright"],
   ["copyleft fraca", "MPL-2.0, LGPL", "usar em código fechado", "publicar mudanças **no arquivo** da biblioteca"],
   ["copyleft forte", "GPL-3.0", "usar", "publicar o programa inteiro que a inclui"],
   ["rede", "AGPL-3.0", "usar", "publicar o código mesmo quando só oferecido como serviço"]]}},
 {"callout": {"tipo": "nota", "titulo": "Isto não é parecer jurídico", "texto": "A tabela é o resumo que ajuda a escolher. Para um caso específico — uma dependência com licença diferente da sua, um cliente com política própria —, consulte quem responde por isso na sua organização."}},
 {"p": "A linguagem é MIT; os pacotes deste repositório também. Apache-2.0 acrescenta uma concessão explícita de patente, o que algumas empresas exigem."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/bibliotecas/dependencias",
"title": "Escolher dependências",
"description": "Cada dependência é uma promessa que você faz em nome de outra pessoa — as perguntas antes de adicionar.",
"blocos": [
 {"p": "Uma dependência entra em uma linha e sai em uma semana de trabalho. Quem instala a sua biblioteca herda **todas** as dependências dela, e as dependências delas. Antes de adicionar, cinco perguntas."},
 {"table": {"head": ["Pergunta", "Porque"], "rows": [
   ["a biblioteca padrão já faz?", "`Arcane.*` vem junto e não tem versão para conflitar"],
   ["dá para escrever em 50 linhas?", "50 linhas suas não quebram numa atualização de terceiro"],
   ["quem mantém, e há quanto tempo não há commit?", "uma dependência abandonada é uma vulnerabilidade adiada"],
   ["qual a faixa de versão?", "`^1.2` aceita 1.x; `*` aceita a 2.0 que quebra tudo"],
   ["ela depende do Python (`adopt Python.x`)?", "o `forge.toml` não sabe instalar isso — declare no README"]]}},
 {"code": """dataforge add validador@^1.0    # faixa: 1.x, a partir da 1.0
dataforge why tabela             # por que isto esta instalado
dataforge tree                   # a arvore inteira, com as transitivas
dataforge outdated               # o que tem versao nova""", "lang": "bash"},
 {"callout": {"tipo": "atencao", "titulo": "Conflito de faixa é erro, e não aviso", "texto": "Se duas dependências pedem faixas incompatíveis do mesmo terceiro, `dataforge add` recusa e diz quem pediu o quê. Instalar as duas versões lado a lado geraria um bug irreproduzível: o mesmo tipo existindo duas vezes."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/bibliotecas/mensagens",
"title": "Mensagens para quem não leu o código",
"description": "O erro de uma biblioteca é lido por quem a usa — o que ele precisa dizer, e o que nunca dizer.",
"blocos": [
 {"p": "A mensagem de erro da sua biblioteca aparece no terminal de alguém que nunca abriu o seu código. Ela precisa dizer **o que aconteceu**, **com qual valor**, e **o que fazer** — nessa ordem."},
 {"code": """action validar_cep(cep):
    digitos := "".join([c cycle c in str(cep) given c.isdigit()])
    given len(digitos) isnt 8:
        trigger $"CEP '{cep}' tem {len(digitos)} digitos, e um CEP tem 8. Confira se nao faltou um zero a esquerda."
    yield digitos

monitor:
    validar_cep(1310100)
    assert no
handle Error as e:
    out e.message
    assert "tem 7 digitos" in e.message""", "lang": "df"},
 {"table": {"head": ["Ruim", "Bom"], "rows": [
   ["`CEP inválido`", "`CEP '1310100' tem 7 dígitos, e um CEP tem 8. Confira se não faltou um zero à esquerda.`"],
   ["`KeyError: 'nome'`", "`o cliente não tem 'nome'. Campos recebidos: email, idade.`"],
   ["`erro ao conectar`", "`não conectei em db:5432 em 30 s — o banco está no ar?`"]]}},
 {"h2": "O que nunca vai numa mensagem"},
 {"table": {"head": ["Nunca", "Porque"], "rows": [
   ["a senha, o token, a chave", "a mensagem vai para o log, e o log é lido por muita gente"],
   ["o CPF inteiro, o cartão", "`Seguranca.mascarar_pii` antes"],
   ["o traceback do Python", "fala de arquivos que quem usa nunca viu"],
   ["o nome de um tipo do Python (`list`, `dict`)", "a linguagem os chama de `Cluster` e `Vault`"]]}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/bibliotecas/estabilidade",
"title": "A promessa de estabilidade",
"description": "O que cada número de versão promete, escrito — e conferido pelo abi a cada release.",
"blocos": [
 {"p": "Semver é uma promessa, e uma promessa só vale se estiver escrita. Declare no README o que a sua biblioteca promete, e confira a cada release com `dataforge abi` — que diz qual número a mudança **exige**."},
 {"table": {"head": ["Sobe", "Quando", "Quem usa precisa…"], "rows": [
   ["**correção** (1.4.0 → 1.4.1)", "a superfície não mudou", "nada"],
   ["**menor** (1.4 → 1.5)", "só acréscimos: nome novo, parâmetro com padrão", "nada — e ganha o novo"],
   ["**maior** (1.x → 2.0)", "algo saiu, mudou de nome ou de assinatura", "ler a seção *Quebra* do CHANGELOG"]]}},
 {"code": """dataforge abi v1.4/src/main.df src/main.df
# veredito: menor
# e sai com codigo diferente de zero quando algo QUEBRA — no CI, antes da tag""", "lang": "bash"},
 {"table": {"head": ["Muda a superfície (é quebra)", "Não muda"], "rows": [
   ["remover ou renomear uma ação exportada", "renomear com `relay novo, novo as antigo`"],
   ["renomear um **parâmetro** — a chamada com nome existe", "renomear uma variável interna"],
   ["acrescentar parâmetro **sem** padrão", "acrescentar parâmetro **com** padrão"],
   ["mudar o tipo declarado de retorno", "mudar a implementação"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Antes da 1.0 não há promessa", "texto": "Em `0.x`, qualquer versão pode quebrar — é o que o número diz. Fique lá enquanto a API muda, e suba para a 1.0 quando puder prometer. Uma 1.0 que quebra a cada menor ensina a não confiar no número."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/bibliotecas/migracao",
"title": "Guia de migração",
"description": "Numa versão maior, o guia que diz a cada pessoa o que trocar — com a busca que acha cada uso.",
"blocos": [
 {"p": "Uma versão maior sem guia de migração deixa cada pessoa descobrir sozinha o que quebrou. O guia é uma tabela: o que era, o que é agora, e como achar cada uso no próprio código."},
 {"code": """# Migrar da 1.x para a 2.0

| Era (1.x)                 | Agora (2.0)                    | Achar                         |
|---------------------------|--------------------------------|-------------------------------|
| `total(itens)`            | `calcular_total(itens)`        | `grep -rn "\\.total(" src/`    |
| `frete(uf)`               | `calcular_frete(uf, peso := 1)` | `grep -rn "\\.frete(" src/`    |
| `Pedido.cliente` (texto)  | `Pedido.cliente` (record)       | `dataforge check` acusa        |""", "lang": "text", "title": "MIGRACAO.md"},
 {"list": [
   "Uma versão menor **antes**, com tudo que vai sair marcado com `obsoleta` — quem roda com `DF_OBSOLETOS=erro` acha cada uso sozinho.",
   "O guia lista cada quebra com o **como achar**: um `grep`, ou *“o `check` acusa”* quando o tipo mudou.",
   "Onde der, mantenha o nome velho por uma versão com `Evolucao.renomeada` — ele funciona e avisa.",
 ], "ordered": True},
 {"code": """adopt Arcane.Evolucao as Ev

action calcular_total(itens):
    yield sum(itens)

// O nome velho, por mais uma versao: funciona e avisa.
total := Ev.renomeada(calcular_total, "total", "2.0")
assert total([1, 2, 3]) is 6
assert Ev.avisos()[0]["acao"] is "total\"""", "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/bibliotecas/checklist",
"title": "Checklist de release",
"description": "As doze conferências antes de uma tag — e o comando que faz cada uma.",
"blocos": [
 {"p": "Uma lista que se segue é melhor que um cuidado que se tem. Estas doze saem do que já quebrou em releases de verdade — inclusive neste repositório."},
 {"table": {"head": ["#", "Conferir", "Com"], "rows": [
   ["1", "o formato", "`dataforge fmt . --check`"],
   ["2", "a análise, com avisos como erro", "`dataforge check . --strict`"],
   ["3", "os testes, com piso de cobertura", "`dataforge test --minimo=80`"],
   ["4", "nenhum uso obsoleto", "`DF_OBSOLETOS=erro dataforge test`"],
   ["5", "o número de versão que a mudança exige", "`dataforge abi anterior.df atual.df`"],
   ["6", "a versão do `forge.toml` igual à tag", "o workflow de release confere"],
   ["7", "o CHANGELOG com *Quebra* e *Obsoleto*", "leitura"],
   ["8", "nenhum segredo no pacote", "`dataforge seguranca . --strict`"],
   ["9", "o pacote instala numa pasta limpa", "`dataforge pack` + `dataforge add` noutra pasta"],
   ["10", "o teste importa pelo **nome** do pacote", "`adopt minha_lib`, e não `../src`"],
   ["11", "os exemplos do README rodam", "extrair e rodar"],
   ["12", "a licença declarada", "`license` no `forge.toml`"]]}},
 {"code": """dataforge fmt . --check && \\
dataforge check . --strict && \\
DF_OBSOLETOS=erro dataforge test --minimo=80 && \\
dataforge seguranca . --strict && \\
dataforge abi v_anterior/src/main.df src/main.df && \\
dataforge pack""", "lang": "bash"},
 {"callout": {"tipo": "dica", "titulo": "Automatize: `dataforge devops github`", "texto": "O workflow de release gerado confere a tag contra o `forge.toml`, roda os testes de novo e publica — ver [Release por tag](/docs/devops/release)."}},
]},
]
