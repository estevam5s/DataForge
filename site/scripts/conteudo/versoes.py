"""Histórico de versões e segurança."""

PAGINAS = [
{
"href": "/docs/versoes",
"title": "Versões",
"description": "O que mudou, quando, e por quê.",
"blocos": [
 {"p": "DataForge segue [versionamento semântico](https://semver.org): `MAIOR.MENOR.CORREÇÃO`. Enquanto a linguagem está em 1.x, mudança que quebra código existente sobe o número do meio — e vem com o caminho de migração."},
 {"callout": {"tipo": "nota", "titulo": "A versão pública é 1.0.0", "texto": "Os números 3.x e 4.x que aparecem no histórico são de desenvolvimento, antes do primeiro lançamento. Quem instala hoje instala a 1.0.0."}},

 {"h2": "O que pode quebrar, e quando"},
 {"p": "**Acrescentar é livre. Tirar e renomear exigem uma versão maior.** Um símbolo novo não quebra ninguém; um símbolo que some quebra todo programa que o usava."},
 {"p": "Isso não é uma promessa em prosa: `doc/superficie.json` guarda a lista de tudo o que é público — as 81 palavras reservadas, as 228 funções embutidas, os 36 módulos e cada símbolo deles, os apelidos, os 49 comandos da CLI e os 177 códigos de erro. Um teste falha quando algo some dessa lista."},
 {"table": {"head": ["", "Quer dizer", "Exemplo"], "rows": [
   ["**1.x.y → 2.0.0**", "um programa válido pode parar de funcionar", "uma palavra reservada some; um módulo muda de nome"],
   ["**1.2.0 → 1.3.0**", "há capacidade nova, e o que existia continua", "um módulo novo; um parâmetro opcional novo"],
   ["**1.2.3 → 1.2.4**", "correção, sem interface nova", "um bug de arredondamento; uma mensagem melhor"]]}},
 {"callout": {"tipo": "atencao", "titulo": "O que NÃO está coberto", "texto": "O **texto** das mensagens de erro (o código `DF0301` é estável; a frase melhora — case pelo código). A representação em texto de um valor. Qualquer coisa dentro de `dataforge/`, que é implementação. Desempenho. E os pacotes que você alcança pela ponte, que não são nossos."}},
 {"p": "A política inteira está em [`doc/ESTABILIDADE.md`](https://github.com/estevam5s/DataForge/blob/main/doc/ESTABILIDADE.md), com o caminho que uma remoção percorre antes de acontecer."},

 {"h2": "1.0.0 — o lançamento"},
 {"p": "A primeira versão pública reúne tudo o que foi construído. O que ela traz:"},

 {"h3": "A linguagem"},
 {"list": [
   "**81 palavras reservadas**, lexer com INDENT/DEDENT, parser recursivo descendente, AST tipada, analisador estático e interpretador de árvore — todos próprios, em Python puro, **sem dependência de runtime**.",
   "**Orientação a objetos completa**: `blueprint`, `record` imutável, `trait`, herança, `private`/`protected` que valem de verdade, propriedades `get`/`set`, métodos estáticos, sobrecarga de operadores, `final` e `abstract` com contrato conferido na declaração.",
   "**Pattern matching estrutural** com `match`/`point`/`when`/`default`, sobre literais, sequências, vaults, records e membros de enum.",
   "**Generators preguiçosos** (`stream action` + `emit`), inclusive infinitos.",
   "**Pipelines** `>> sift / morph / distill`, compreensões, spread, desestruturação, interpolação `$\"{x}\"`, `??` e `?.`.",
   "**Decoradores** `@Nome` com pilha, argumentos nomeados e metadados legíveis por `Arcane.Meta`.",
   "**Generics** `<T>` aceitos pelo analisador — documentam a relação entre entrada e saída."]},

 {"h3": "Erros: 177 códigos"},
 {"p": "De 10 para 177, em 15 famílias. As classes e o catálogo nascem da **mesma tabela** — antes eram duas listas escritas à mão, e elas divergiam."},
 {"list": [
   "`handle` compara por **herança**: `handle RuntimeError` pega `DivisionByZeroError`.",
   "`handle KeyError:` agora **filtra**. Antes virava nome de variável e o bloco engolia qualquer erro em silêncio — com 177 tipos isso deixa de ser detalhe.",
   "Exceção do Python vira erro da linguagem. `[].min()` subia como `Internal Error` que nem `monitor` capturava.",
   "`e.campos`, `e.nota` e `e.dica` legíveis pelo programa.",
   "`dataforge erros` lista o catálogo; `explain` aceita o código **ou** o nome da classe."]},

 {"h3": "Crucible — o framework de testes"},
 {"p": "Dez palavras contextuais, 59 matchers, dublês, teste por propriedade com contraexemplo encolhido, benchmark com p95 e quatro formatos de relatório. Ver [Crucible](/docs/crucible)."},

 {"h3": "Forge — cinco bancos de dados"},
 {"p": "PostgreSQL, MySQL, MariaDB, MongoDB, Redis e SQLite — cada driver falando o protocolo por socket, **sem dependência**. Mais construtor de consultas que nunca põe valor no texto do SQL, e ORM com relações que custam duas consultas em vez de N+1. Ver [banco de dados](/docs/banco-de-dados)."},

 {"h3": "Kiln — o framework web"},
 {"p": "Dez palavras próprias, roteamento, middleware, sessão, templates com escape automático. Ver [Kiln](/docs/kiln)."},

 {"h3": "Análise de complexidade"},
 {"p": "`dataforge big-o` diz a classe de cada ação **e o porquê**, distinguindo divisão e conquista de recursão exponencial. Ver [Big-O](/docs/big-o)."},

 {"h3": "Ferramentas"},
 {"table": {"head": ["Comando", "Faz"], "rows": [
   ["`run`, `repl`, `watch`", "executar"],
   ["`check`, `lint`, `fmt`", "analisar e formatar"],
   ["`crucible`, `test`", "testar"],
   ["`big-o`, `custo`, `profile`, `bench`", "medir"],
   ["`erros`, `explain`", "entender um erro"],
   ["`new`, `init`, `info`", "criar projeto"],
   ["`add`, `install`, `pack`, `publish`", "pacotes"],
   ["`doc`, `stats`, `fix`, `editor`", "o resto"]]}},

 {"h3": "Ecossistema"},
 {"list": [
   "**22 módulos** `Arcane.*` na biblioteca padrão, com 753 símbolos",
   "**20 pacotes** no registro, escritos em DataForge",
   "**Extensão do VS Code** com 103 snippets, Big-O no editor, custo de import e painel de bancos",
   "**200 exercícios** e 42 exemplos, todos rodando",
   "**891 testes** automatizados"]},

 {"h2": "O caminho até aqui"},
 {"p": "As versões de desenvolvimento, e o que cada uma acrescentou:"},
 {"table": {"head": ["", "O que entrou"], "rows": [
   ["**4.2**", "Kiln (framework web), Arcane.Excel sem dependência, extensão do VS Code"],
   ["**4.1**", "OOP completa: visibilidade, propriedades, estáticos, operadores, abstratos, generics, decoradores"],
   ["**4.0**", "Records, enums, pattern matching, generators, interpolação, ternário, `??`, `?.`, analisador estático, gerenciador de pacotes, seis ferramentas de linha de comando"],
   ["**3.1**", "Módulos, `relay`, detecção de ciclos, stack traces"],
   ["**3.0**", "Blueprints, traits, herança, `monitor`/`handle`/`ensure`"]]}},

 {"h2": "Bugs corrigidos que valem registro"},
 {"p": "Os que mudaram o comportamento da linguagem, e não só uma mensagem:"},
 {"table": {"head": ["Sintoma", "Causa"], "rows": [
   ["`private` do pai recusado ao próprio pai", "a checagem olhava o blueprint da **instância**, não o de quem declarou o membro"],
   ["`[].min()` incapturável", "exceção do Python subia crua, sem virar erro da linguagem"],
   ["`handle KeyError:` engolia tudo", "o nome virava variável em vez de filtro"],
   ["`// 200, application/json` virava divisão", "comentário começando com número era lido como operando"],
   ["`// 10 — o dobro` virava divisão", "o travessão não marcava prosa"],
   ["campos mutáveis compartilhados entre instâncias", "o literal do padrão era avaliado uma vez, na declaração"],
   ["closures num laço viam o último valor", "o escopo era reaproveitado mesmo quando o corpo o capturava"],
   ["`profile` somava 207%", "recursão contada duas vezes; agora mede tempo **próprio**"],
   ["`-v` nunca ligava o modo verboso", "só flags com `--` eram reconhecidas; `-v` caía entre os alvos"],
   ["erros de sintaxe diziam `<stdin>`", "o nome do arquivo não chegava ao lexer e ao parser"]]}},
 {"p": "Cada um tem teste de regressão. A suíte só cresce."},

 {"h2": "O que ainda não existe"},
 {"p": "Declarado, para não haver surpresa:"},
 {"list": [
   "**LSP e depurador** — a extensão do VS Code analisa e roda, mas não há autocompletar sensível a contexto nem ponto de parada.",
   "**Bytecode** — é interpretador de árvore. Rápido o suficiente para o que a linguagem faz, e não para computação numérica pesada.",
   "**Sincronização entre threads** — sem mutex; a coordenação é por `channel`.",
   "**Exaustividade no `match`** — ele não avisa se um membro de enum ficou de fora.",
   "**`<T extends Comparable>`** — generics documentam, não restringem.",
   "**WebSocket e HTTP/2 no Kiln** — ele roda sobre o `http.server` do Python."]},
 {"p": "O plano completo está no [roadmap](/docs/roadmap)."},
]},

{
"href": "/docs/seguranca",
"title": "Segurança",
"description": "O que a linguagem garante por construção, e o que continua sendo sua responsabilidade.",
"blocos": [
 {"p": "Segurança não se acrescenta depois. Esta página lista o que o DataForge **garante por construção** — coisas que você não consegue errar mesmo querendo — e o que ele não pode garantir por você."},

 {"h2": "Injeção de SQL"},
 {"p": "**Garantido.** O construtor de consultas não tem como pôr um valor no texto da consulta: valores viram parâmetros, sempre."},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, "create table u (id integer primary key, nome text)")

malicioso := "'; drop table u; --"
Forge.de(db, "u").inserir({"nome": malicioso})

// a tabela continua lá — o valor foi tratado como dado
assert "u" in Forge.tabelas(db)""", "lang": "df"},
 {"p": "A lista de operadores também é **fechada**: `.onde(\"x\", operador, v)` só aceita os operadores conhecidos. Um operador vindo de variável seria outro caminho de injeção."},
 {"callout": {"tipo": "atencao", "titulo": "`onde_cru` é a saída de emergência", "texto": "Ela existe para o que o construtor não cobre — funções do banco, operadores geográficos. O SQL vai como escrito; **os valores continuam parâmetros**. Nunca concatene entrada do usuário no texto que você passa a ela."}},

 {"h2": "XSS nos templates"},
 {"p": "**Garantido por padrão.** O Kiln escapa toda interpolação de template:"},
 {"code": """// render "pagina.html" with {"nome": entrada_do_usuario}
//
// No template:  <p>{{ nome }}</p>
// Se 'nome' for '<script>alert(1)</script>', sai escapado — o
// navegador mostra o texto, não executa.""", "lang": "df"},
 {"p": "Escapar é o **padrão**, não uma opção a lembrar. Ver [Kiln: páginas](/docs/kiln/paginas)."},

 {"h2": "Travessia de caminho em pacotes"},
 {"p": "**Garantido.** A extração de um pacote recusa qualquer entrada com `../` ou link simbólico — um pacote não pode escrever fora da própria pasta."},
 {"p": "O tarball também é **reprodutível** (`mtime` zerado, uid/gid zerados): sem isso o sha256 mudaria a cada empacotamento, e a verificação de integridade não significaria nada."},

 {"h2": "Integridade dos pacotes"},
 {"p": "**Garantido.** Todo pacote instalado tem o sha256 registrado no `forge.lock`. Se o conteúdo mudar entre o registro e você, a instalação falha com `IntegrityError` (DF0507)."},
 {"code": """dataforge install --limpar-cache   # se suspeitar do cache local""", "lang": "bash"},

 {"h2": "Conflito de versão"},
 {"p": "**É erro, não aviso.** Se dois pacotes pedem faixas incompatíveis do mesmo terceiro, o resolvedor falha dizendo quem pediu o quê. Instalar duas cópias em versões diferentes gera bug irreproduzível."},

 {"h2": "TLS"},
 {"p": "**Verificado por padrão.** `Http.get` e as conexões de banco verificam o certificado. Desligar exige dizer isso explicitamente — e a documentação não ensina como, de propósito."},
 {"callout": {"tipo": "perigo", "titulo": "Não desligue a verificação de TLS", "texto": "Um certificado inválido significa que você não sabe com quem está falando. Corrija o certificado do servidor; desligar a verificação transforma um erro visível num problema silencioso."}},

 {"h2": "Senhas no editor"},
 {"p": "**A extensão do VS Code** guarda senhas de banco no cofre do sistema (`SecretStorage`), não no `settings.json` — que muita gente versiona sem perceber. A URL salva leva um marcador no lugar da senha."},

 {"h2": "O que continua sendo sua responsabilidade"},

 {"h3": "Segredos"},
 {"p": "A linguagem não tem como saber que um texto é uma senha. As regras valem aqui como em qualquer lugar:"},
 {"code": """adopt Forge

// certo: vem do ambiente
db := Forge.conectar(ambiente("DATABASE_URL") ?? ":memory:")

// errado: vai para o repositório junto com o código
// db := Forge.conectar("postgres://usuario:senha123@prod/app")""", "lang": "df"},
 {"list": [
   "Nunca escreva credencial no código — use `ambiente(\"NOME\")`.",
   "`.env` e `forge.local.toml` no `.gitignore`.",
   "Se um segredo vazou para o histórico do git, **rotacione**: apagar o commit não basta, ele já foi clonado."]},

 {"h3": "Validar o que vem de fora"},
 {"p": "O corpo, a query e os cabeçalhos de uma requisição vêm do cliente. Trate-os como hostis:"},
 {"code": """adopt Forge

db := Forge.conectar(":memory:")
Usuario := Forge.modelo("Usuario", {
    "id": {"tipo": "Serial"},
    "email": {"tipo": "Texto", "obrigatorio": yes, "validacoes": ["email"]},
    "idade": {"tipo": "Inteiro", "validacoes": [["minimo", 0], ["maximo", 130]]}
}, {"conexao": db})
Forge.migrar_tudo(db)

monitor:
    Usuario.criar({"email": "não-é-email", "idade": -5})
handle ValidationError as e:
    assert len(e.campos) is 2""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "`query[\"x\"]` sem `??` dá 500", "texto": "A chave pode não vir, e indexar um vault sem a chave é erro. `params` é a exceção — se a rota casou, o parâmetro existe."}},

 {"h3": "Autorização"},
 {"p": "Autenticação diz **quem** é; autorização diz **o que pode**. A segunda é regra de negócio, e nenhuma biblioteca a escreve por você:"},
 {"code": """// route DELETE "/pedidos/:id":
//     given req.sessao["usuario"] is void:
//         respond 401, {"erro": "não autenticado"}
//
//     pedido := buscar(params.id)
//     given pedido["usuario_id"] isnt req.sessao["usuario"]:
//         respond 403, {"erro": "não é seu"}
//
//     remover(params.id)
//     respond 204, \"\"""", "lang": "df"},
 {"p": "O erro clássico é conferir só a autenticação — e qualquer usuário logado apagar o pedido de qualquer outro."},

 {"h3": "Limite de requisições"},
 {"p": "O Kiln tem `rate_limit`, mas quem decide o limite é você. Sem ele, uma rota de login é um convite a força bruta."},

 {"h3": "Produção"},
 {"list": [
   "**Ponha um nginx ou Caddy na frente do Kiln.** Ele roda sobre o `http.server` do Python, que não foi feito para exposição direta.",
   "**Rode como usuário sem privilégio.** O `Dockerfile` do projeto já faz isso.",
   "**`dataforge check --strict` no CI.** O analisador acha erro de nome e de aridade antes do usuário achar."]},

 {"h2": "Relatar uma vulnerabilidade"},
 {"p": "Se você encontrou algo que permite executar código, ler arquivo fora do escopo, ou contornar as garantias desta página:"},
 {"list": [
   "**Não abra issue pública.** Ela é indexada em minutos.",
   "Escreva para o e-mail do mantenedor no [repositório](https://github.com/estevam5s/DataForge), com o que você fez e o que aconteceu.",
   "Um exemplo mínimo que reproduz vale mais que uma descrição longa."]},
 {"callout": {"tipo": "nota", "titulo": "O que não é vulnerabilidade", "texto": "`trigger` derruba o programa, `run` executa o arquivo que você mandou, e um `.df` malicioso faz o que qualquer script faz. A linguagem executa código — não há sandbox, e ela não promete um."}},

 {"h2": "Os erros que ajudam"},
 {"table": {"head": ["Código", "Sobre"], "rows": [
   ["`DF0507`", "pacote corrompido — o sha256 não bate"],
   ["`DF0508`", "pacote com caminho inseguro (`../` ou link simbólico)"],
   ["`DF1203`", "credenciais recusadas"],
   ["`DF1304`", "falha de TLS"],
   ["`DF1308`", "sessão inválida ou expirada"],
   ["`DF1311`", "origem não permitida (CORS)"],
   ["`DF1312`", "limite de requisições"],
   ["`DF1505`", "dado fora do esquema"]]}},
 {"p": "`dataforge explain DF0508` explica cada um."},
]},
]
