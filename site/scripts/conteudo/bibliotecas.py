# -*- coding: utf-8 -*-
"""Construir, versionar e publicar uma biblioteca."""

PAGINAS = [
{
"href": "/docs/bibliotecas",
"title": "Escrever uma biblioteca",
"description": "Do primeiro arquivo ao pacote publicado — estrutura, contrato, versão, testes e registro.",
"blocos": [
 {"p": "Uma biblioteca é um projeto com uma diferença que muda tudo: **outra pessoa vai depender dela**. O que num programa é detalhe interno — o nome de uma ação, a ordem de um parâmetro, o formato de um retorno — vira promessa."},
 {"p": "Esta seção é o caminho inteiro, na ordem em que ele acontece."},
 {"cards": [
   {"href": "/docs/bibliotecas/estrutura", "title": "1. Estrutura", "desc": "o esqueleto, o forge.toml e onde cada coisa mora"},
   {"href": "/docs/bibliotecas/contrato", "title": "2. O contrato", "desc": "o que o relay promete, e o que quebra quem depende de você"},
   {"href": "/docs/bibliotecas/testes", "title": "3. Testes de biblioteca", "desc": "testar pelo nome público, e não pelo caminho interno"},
   {"href": "/docs/bibliotecas/versao", "title": "4. Versão", "desc": "semver, o que cada número significa, e como o resolvedor lê"},
   {"href": "/docs/bibliotecas/publicar", "title": "5. Publicar", "desc": "empacotar, o registro estático, e o que vai dentro do tarball"},
   {"href": "/docs/bibliotecas/manutencao", "title": "6. Manter", "desc": "depreciar sem quebrar, e o que fazer numa mudança incompatível"}]},

 {"h2": "Em trinta segundos"},
 {"code": """dataforge init minha-lib && cd minha-lib

# escreva src/main.df, com 'relay' no fim
dataforge check .
dataforge test tests/

dataforge pack                      # gera dist/minha-lib-1.0.0.tar.gz
dataforge publish --registry=../registro
""", "lang": "bash"},

 {"h2": "As quatro bibliotecas deste repositório"},
 {"p": "Elas existem como referência de quem for escrever a sua — e como prova de que o gerenciador funciona ponta a ponta:"},
 {"table": {"head": ["Pacote", "O que faz"], "rows": [
   ["[`validador`](/docs/pacotes/validador)", "CPF, CNPJ, e-mail, CEP e esquema de formulário"],
   ["[`tabela`](/docs/pacotes/tabela)", "saída tabular para terminal"],
   ["[`datas`](/docs/pacotes/datas)", "datas em pt-BR, com feriados"],
   ["[`cofre`](/docs/pacotes/cofre)", "configuração em camadas"]]}},
 {"p": "As quatro somam 46 testes, e o código de cada uma é curto o bastante para ser lido inteiro."},

 {"h2": "O que distingue uma biblioteca de um programa"},
 {"table": {"head": ["", "Programa", "Biblioteca"], "rows": [
   ["quem decide a entrada", "você", "**quem usa**"],
   ["renomear uma ação", "um `grep` e pronto", "**quebra** todo mundo"],
   ["erro sem tratamento", "aparece para você", "aparece na aplicação de outra pessoa"],
   ["efeito no topo do arquivo", "aceitável", "**inaceitável** — roda no `adopt` de quem importa"],
   ["dependência nova", "sua escolha", "vira dependência de todos os seus usuários"],
   ["o teste", "prova que funciona", "**é** a documentação do contrato"]]}},
 {"callout": {"tipo": "atencao", "titulo": "A regra que resume as seis linhas", "texto": "Numa biblioteca, o mais caro não é escrever — é **mudar de ideia depois**. Tudo nesta seção existe para adiar o menos possível a hora de decidir o que é público."}},
]},

{
"href": "/docs/bibliotecas/estrutura",
"title": "Estrutura de uma biblioteca",
"description": "O esqueleto que o init cria, o que cada campo do forge.toml significa, e onde pôr cada coisa.",
"blocos": [
 {"code": """dataforge init minha-lib
cd minha-lib
""", "lang": "bash"},
 {"code": """minha-lib/
  forge.toml               o manifesto            (versionado)
  src/main.df              a entrada              (versionado)
  tests/principal_test.df  os testes              (versionado)
  forge.lock               o que foi instalado    (versionado)
  forge_modules/           as dependências        (NÃO versionado)
  dist/                    os tarballs gerados    (NÃO versionado)
""", "lang": "text"},

 {"h2": "O manifesto, campo a campo"},
 {"code": """[package]
name = "validador"
version = "1.0.0"
description = "Validação de dados: e-mail, CPF, CNPJ, CEP, telefone e senha."
authors = ["Seu Nome"]
license = "MIT"
entry = "src/main.df"
dataforge = ">=1.0"
keywords = ["validacao", "formulario", "cpf", "brasil"]

[dependencies]
texto = "^1.0"

[lint]
ignore = ["magic-number"]

[scripts]
test = "test tests/"
""", "lang": "toml", "title": "forge.toml"},
 {"table": {"head": ["Campo", "Para quê"], "rows": [
   ["`name`", "o nome do `adopt`. Minúsculas, sem espaço — e **não se muda depois**"],
   ["`version`", "semver. Ver [versão](/docs/bibliotecas/versao)"],
   ["`description`", "a linha que aparece no `dataforge search`"],
   ["`entry`", "o arquivo que `adopt minha-lib` carrega"],
   ["`dataforge`", "de qual versão da linguagem ela precisa"],
   ["`keywords`", "como alguém acha a sua biblioteca sem saber o nome"],
   ["`[dependencies]`", "o que ela pede, com faixa semver"],
   ["`[lint]`", "as regras que **este** projeto silencia, com o porquê em comentário"],
   ["`[scripts]`", "atalhos: `dataforge test` vira o que estiver aqui"]]}},

 {"h2": "Uma entrada, e o resto interno"},
 {"p": "O `entry` é a porta. Tudo o que não passa por ela é detalhe de implementação, e é assim que se consegue mudar o interior sem quebrar ninguém:"},
 {"code": """src/
  main.df          a porta — só 'adopt' e 'relay'
  cpf.df           a regra do CPF
  cnpj.df          a do CNPJ
  comum.df         o que os dois usam
""", "lang": "text"},
 {"code": """adopt ./cpf as Cpf
adopt ./cnpj as Cnpj

action cpf(texto):
    yield Cpf.validar(texto)

action cnpj(texto):
    yield Cnpj.validar(texto)

relay cpf, cnpj
""", "lang": "df", "title": "src/main.df"},
 {"p": "Quem usa escreve `V.cpf(\"...\")`. Que exista um `comum.df`, e o que tem dentro, não é problema de ninguém — e **pode mudar numa versão de correção**."},

 {"h2": "Nada de efeito no topo"},
 {"p": "O corpo de um módulo roda no `adopt` de quem importa. Numa biblioteca, isso significa: na hora em que a aplicação da outra pessoa inicia."},
 {"code": """// NÃO: isto abre conexão quando alguém te importa
conexao := Banco.abrir("dados.db")

action buscar(id):
    yield Banco.query(conexao, "SELECT …", [id])
""", "lang": "df"},
 {"code": """// SIM: quem usa decide quando, e com qual banco
action buscar(conexao, id):
    yield Banco.query(conexao, "SELECT …", [id])

relay buscar
""", "lang": "df"},
 {"p": "O sintoma do primeiro caso é caro e indireto: o teste de quem te usa fica lento, ou abre arquivo, ou falha em CI sem disco — e a causa está numa biblioteca que ele nem chamou ainda."},

 {"h2": "O README é parte do pacote"},
 {"p": "Três coisas que quem chega procura, nesta ordem: **o que isto faz** (uma frase), **como instalo** (uma linha), **um exemplo que roda** (cinco linhas). O resto pode esperar."},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/bibliotecas/contrato", "title": "O contrato", "desc": "o que o relay promete"},
   {"href": "/docs/cli/forge-toml", "title": "forge.toml", "desc": "a referência completa do manifesto"}]},
]},

{
"href": "/docs/bibliotecas/contrato",
"title": "O contrato de uma biblioteca",
"description": "O que o relay promete, o que a assinatura promete, e o que quebra quem depende de você.",
"blocos": [
 {"p": "O contrato de uma biblioteca é tudo o que alguém pode escrever hoje e esperar que continue funcionando amanhã. Ele é maior do que parece — e a maior parte dele nunca foi escrita em lugar nenhum."},

 {"h2": "O que entra no contrato"},
 {"table": {"head": ["Faz parte", "Não faz"], "rows": [
   ["os nomes no `relay`", "o que não está nele"],
   ["quantos parâmetros cada ação recebe", "o nome dos arquivos internos"],
   ["o que ela devolve, e de que tipo", "a ordem das ações no arquivo"],
   ["o **tipo** do erro que ela levanta", "o texto exato da mensagem de erro"],
   ["os campos de um `record` exportado", "um campo cujo nome começa com `_`"],
   ["os membros de um `enum` exportado", "a implementação de qualquer método"]]}},
 {"callout": {"tipo": "nota", "titulo": "O tipo do erro está no contrato", "texto": "Quem usa escreve `handle ValidationError`. Trocar o tipo levantado por outro quebra esse `handle` — e quebra em silêncio, porque o erro simplesmente deixa de ser capturado e sobe. Mudar o **texto** da mensagem é seguro; mudar o **tipo** não é."}},

 {"h2": "Escreva o `relay` cedo"},
 {"p": "Enquanto não há `relay`, **tudo** é público — e cada coisa que alguém descobre e passa a usar vira contrato sem você saber. O `relay` é o momento em que você decide, e quanto mais cedo, menor o estrago."},
 {"code": """// no fim de src/main.df
relay cpf, cnpj, email, cep, Resultado
""", "lang": "df"},
 {"p": "A partir daí o analisador ajuda: `V.interna()` passa a ser acusado **antes de rodar**, na máquina de quem usa."},

 {"h2": "Assine o que você promete"},
 {"p": "Os tipos declarados atravessam o `adopt`. Uma ação sem anotação promete menos, e o `check` de quem usa fica cego:"},
 {"code": """action formatar(valor, casas):          // promete pouco
    yield round(valor, casas)

action formatar(valor: Float, casas: Integer := 2) -> Float:
    yield round(valor, casas)
""", "lang": "df"},
 {"p": "Com a segunda forma, `V.formatar(\"12\", 2)` é acusado na máquina de quem chamou, com a linha certa — e a mensagem cita **o seu arquivo** como origem da declaração."},

 {"h2": "Erros: levante o seu, não o de dentro"},
 {"p": "Se a sua biblioteca deixa vazar o erro do `Arcane.Database` que ela usa por dentro, o banco virou parte do seu contrato — e trocá-lo numa versão de correção quebraria quem tratava aquele erro."},
 {"code": """action buscar(id: Integer) -> Vault:
    monitor:
        yield consultar(id)
    handle Error as e:
        // o erro do domínio, com a causa preservada
        trigger $"nao foi possivel buscar o registro {id}"
""", "lang": "df"},
 {"p": "A causa do erro original continua acessível em `.causa`, e o relatório desenha as duas camadas: quem usa vê o que a sua biblioteca prometeu **e** o que de fato aconteceu."},

 {"h2": "O que um valor devolvido promete"},
 {"p": "Devolver um `record` promete os campos dele; devolver um `Vault` promete as chaves — e um vault é mais fácil de mudar por engano. Para um retorno estável, prefira `record`:"},
 {"code": """record Resultado:
    valido: Boolean
    motivo: String := ""

action cpf(texto: String) -> Resultado:
    given len(texto) smaller 11:
        yield Resultado(no, "o CPF precisa de 11 dígitos")
    yield Resultado(yes)

relay cpf, Resultado
""", "lang": "df"},
 {"p": "Acrescentar um campo **com padrão** a um record é compatível; remover ou renomear um não é. E o `record` exportado precisa ir no `relay`: sem ele, quem usa recebe o valor e não consegue nomear o tipo."},

 {"h2": "A lista de conferência antes da 1.0.0"},
 {"list": [
   "Todo nome público está num `relay`?",
   "Toda ação pública tem tipos nos parâmetros e no retorno?",
   "Todo erro que sai da biblioteca é **seu**, e não de uma dependência?",
   "O topo dos arquivos não faz nada além de declarar?",
   "Os testes exercitam a biblioteca pelo nome público (`adopt minha-lib`)?",
   "O README tem um exemplo que roda?"]},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/bibliotecas/testes", "title": "Testes de biblioteca", "desc": "testar pelo nome público"},
   {"href": "/docs/bibliotecas/versao", "title": "Versão", "desc": "o que cada número promete"}]},
]},
{
"href": "/docs/bibliotecas/testes",
"title": "Testes de biblioteca",
"description": "Testar pelo nome público, e por que o caminho relativo esconde exatamente o bug que importa.",
"blocos": [
 {"p": "O teste de uma biblioteca tem um trabalho a mais que o de um programa: **ele é o primeiro usuário**. Se ele chega ao código por um caminho que nenhum usuário usaria, ele deixa de testar a única coisa que só ele pode testar — a fronteira."},

 {"h2": "Importe pelo nome, não pelo caminho"},
 {"code": """adopt ../src/main as V        // NÃO: nenhum usuário escreve isto
adopt minha-lib as V          // SIM: é assim que ela será usada
""", "lang": "df"},
 {"p": "A segunda forma exercita a resolução de verdade: o `entry` do manifesto, o `relay`, o nome do pacote. A primeira pula tudo isso e testa arquivos soltos."},
 {"callout": {"tipo": "atencao", "titulo": "Isto já quebrou aqui", "texto": "As suítes dos **vinte** pacotes deste repositório falhavam porque um pacote não sabia se importar pelo próprio nome — e a CI não apanhava, porque ela não rodava `dataforge test` dentro de `packages/`. O teste que passa pelo caminho relativo teria continuado verde."}},

 {"h2": "A forma de um teste"},
 {"code": """adopt Arcane.Crucible as C

action cpf(texto):
    yield len(texto) is 11

crucible "cpf":
    trial "aceita um CPF com 11 digitos":
        expect cpf("52998224725") is yes

    trial "recusa o numero de digitos errado":
        expect cpf("123") is no

C.run()
""", "lang": "df", "title": "tests/cpf_test.df"},
 {"code": """dataforge test tests/
""", "lang": "bash"},

 {"h2": "Teste o contrato, e não a implementação"},
 {"table": {"head": ["Teste isto", "Não isto"], "rows": [
   ["o que uma ação pública devolve", "o valor de uma variável interna"],
   ["o **tipo** do erro levantado", "o texto exato da mensagem"],
   ["que o campo `valido` existe", "a ordem dos campos do record"],
   ["o comportamento na borda (vazio, zero, negativo)", "o caminho que o código toma por dentro"]]}},
 {"p": "A regra prática: um teste que quebra quando você **melhora** a implementação sem mudar o comportamento é um teste que está no lugar errado."},

 {"h2": "As bordas que uma biblioteca precisa cobrir"},
 {"list": [
   "**Vazio** — texto vazio, cluster `[]`, vault `{}`. É o que mais chega de formulário.",
   "**Void** — quem usa vai passar `void` um dia, e a mensagem precisa dizer o que fazer.",
   "**O tipo errado** — um número onde se espera texto. Com anotação de tipo, o `check` pega antes; sem ela, o teste é a única defesa.",
   "**O limite** — o maior valor aceito, e o primeiro recusado.",
   "**A repetição** — chamar duas vezes devolve o mesmo? Se não, há estado escondido."]},

 {"h2": "Cobertura, e o número que mente"},
 {"code": """dataforge test tests/ --cobertura --minimo=80
""", "lang": "bash"},
 {"p": "Uma ação **nunca chamada** aparece com 0%, e não com 20% — a linha da declaração não conta, o corpo conta. E um arquivo que nenhum teste toca aparece no relatório com 0% em vez de sumir dele: sumir é o que faz uma cobertura de 95% conviver com metade do sistema sem teste."},
 {"p": "`forge_modules/` fica de fora da descoberta. Sem isso, um projeto com 13 testes relatava **89**, e a suíte ficava vermelha por falha de uma biblioteca que ninguém escreveu."},

 {"h2": "Instantâneo, para saída grande"},
 {"p": "Quando o que se testa é um texto longo — um relatório, um HTML, um CSV —, comparar à mão é inviável. O instantâneo grava na primeira vez e compara nas seguintes; `DF_ATUALIZAR_SNAPSHOT=1` aceita a mudança."},
 {"p": "Atualizar por padrão seria pior que não ter instantâneo: o teste passaria a concordar com qualquer mudança, inclusive a errada."},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/crucible", "title": "Crucible", "desc": "o corredor de testes inteiro"},
   {"href": "/docs/tecnicas/cobertura", "title": "Cobertura", "desc": "os dois jeitos de o número mentir"},
   {"href": "/docs/bibliotecas/versao", "title": "Versão", "desc": "o próximo passo"}]},
]},

{
"href": "/docs/bibliotecas/versao",
"title": "Versão e compatibilidade",
"description": "Semver na prática: o que cada número promete, como o resolvedor lê a faixa, e por que conflito é erro.",
"blocos": [
 {"p": "A versão de uma biblioteca é uma **promessa legível por máquina**. Ela responde a uma pergunta só: *posso atualizar sem ler o changelog?*"},
 {"code": """1.4.2
│ │ └── correção   — consertou algo, sem mudar o contrato
│ └──── menor      — acrescentou algo, sem quebrar o que havia
└────── maior      — quebrou alguma coisa
""", "lang": "text"},

 {"h2": "O que cabe em cada número"},
 {"table": {"head": ["Mudança", "Sobe"], "rows": [
   ["corrigir um cálculo errado", "correção (`1.4.2` → `1.4.3`)"],
   ["melhorar a mensagem de um erro", "correção"],
   ["trocar a implementação interna", "correção"],
   ["**acrescentar** uma ação ao `relay`", "menor (`1.4.2` → `1.5.0`)"],
   ["acrescentar um parâmetro **com padrão**", "menor"],
   ["acrescentar um campo com padrão a um record", "menor"],
   ["renomear ou remover algo público", "**maior** (`1.4.2` → `2.0.0`)"],
   ["trocar o **tipo** de um erro levantado", "**maior**"],
   ["tornar obrigatório um parâmetro que era opcional", "**maior**"],
   ["mudar o que uma ação devolve", "**maior**"]]}},
 {"callout": {"tipo": "atencao", "titulo": "As três linhas de baixo são as esquecidas", "texto": "Trocar o tipo do erro quebra em silêncio — o `handle` de quem usa para de capturar e o erro sobe. Mudar o retorno de `Vault` para `record` quebra toda leitura por chave. Nenhuma das duas parece \"quebrar\" enquanto se escreve."}},

 {"h2": "A faixa, do lado de quem depende"},
 {"code": """[dependencies]
validador = "^1.2.0"      # >=1.2.0 e <2.0.0   — aceita correção e menor
tabela    = "~1.2.0"      # >=1.2.0 e <1.3.0   — só correção
datas     = "1.2.3"       # exatamente essa
cofre     = ">=1.0 <3.0"  # comparadores, combináveis
texto     = "*"           # qualquer uma
""", "lang": "toml"},
 {"p": "`^` é o padrão razoável: ele confia no semver de quem publicou. `~` é para quando essa confiança ainda não existe, e a versão exata é para quando existe um motivo escrito."},

 {"h2": "Antes de 1.0.0"},
 {"p": "Enquanto o maior é `0`, o contrato ainda está sendo decidido, e a convenção é que o **menor** carrega as quebras: `0.3.0` pode quebrar `0.2.0`. Publicar `1.0.0` é a declaração de que o contrato está de pé — e é a partir dali que ele custa caro para mudar."},

 {"h2": "Conflito é erro, e não aviso"},
 {"p": "Se dois pacotes pedem faixas incompatíveis do mesmo terceiro, `dataforge install` **falha**, dizendo quem pediu o quê. A alternativa — instalar duas cópias em versões diferentes — produz o pior tipo de bug: dois `record` com o mesmo nome e campos distintos circulando no mesmo programa, e um `with` que recusa o próprio resultado."},

 {"h2": "O lockfile"},
 {"table": {"head": ["Arquivo", "Guarda", "Versionar?"], "rows": [
   ["`forge.toml`", "o que você **pediu** (faixas)", "sim"],
   ["`forge.lock`", "o que foi **instalado** (versões exatas + sha256)", "sim"],
   ["`forge_modules/`", "os arquivos", "não"]]}},
 {"p": "O lock é o que faz a instalação de hoje ser igual à de três meses atrás — e o `sha256` é o que faz \"a mesma versão\" significar \"os mesmos bytes\"."},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/bibliotecas/publicar", "title": "Publicar", "desc": "empacotar e mandar para o registro"},
   {"href": "/docs/pacotes", "title": "O gerenciador", "desc": "add, install, search e o resolvedor"}]},
]},

{
"href": "/docs/bibliotecas/publicar",
"title": "Publicar um pacote",
"description": "Empacotar, o que entra no tarball, o registro estático — e por que o pacote é reprodutível.",
"blocos": [
 {"p": "Publicar é dois passos: **empacotar** (gerar o tarball) e **enviar** (copiar para um registro). Os dois são comandos, e o registro não é um servidor."},

 {"h2": "Empacotar"},
 {"code": """dataforge check .
dataforge test tests/
dataforge pack
""", "lang": "bash"},
 {"code": """  dist/minha-lib-1.0.0.tar.gz   14.2 KB
  sha256: 9eb3d7de7b8581abf905ad93c978514af39b65253ede72ee82d262c8fe7761d0
""", "lang": "text"},
 {"p": "**O tarball é reprodutível**: `mtime` zerado, uid e gid zerados. Sem isso o sha256 mudaria a cada empacotamento, e a verificação de integridade não significaria nada — dois downloads da mesma versão não teriam como ser comparados."},

 {"h2": "O que entra, e o que não"},
 {"table": {"head": ["Entra", "Fica de fora"], "rows": [
   ["`forge.toml`", "`forge_modules/`"],
   ["o `entry` e tudo o que ele alcança", "`dist/`"],
   ["`src/`", "`.git/`"],
   ["`tests/`", "arquivos fora do projeto"],
   ["`README.md`, `LICENSE`", "o que o `.gitignore` já exclui"]]}},
 {"callout": {"tipo": "dica", "titulo": "Confira antes de publicar", "texto": "`tar tzf dist/minha-lib-1.0.0.tar.gz` lista o que vai dentro. É o momento de descobrir um `.env` ou um dump de banco — depois de publicado, o conteúdo saiu da sua máquina."}},

 {"h2": "O registro é uma pasta"},
 {"p": "Não há servidor a manter: um registro é uma pasta com `index.json` e `pacotes/*.tar.gz`, servida por qualquer host estático."},
 {"code": """registro/
  index.json
  pacotes/
    validador-1.0.0.tar.gz
    tabela-1.1.0.tar.gz
""", "lang": "text"},
 {"code": """dataforge publish --registry=../registro
""", "lang": "bash"},
 {"p": "O do projeto vive em `site/public/registry/` e vai ao ar junto com o site. Publicar numa pasta e versioná-la é um registro privado completo — o que uma empresa precisa para compartilhar bibliotecas internas sem infraestrutura."},

 {"h2": "A extração recusa o que sai da pasta"},
 {"p": "Um pacote não pode escrever fora do lugar dele. A extração recusa caminho com `../` e recusa link simbólico — as duas formas clássicas de um tarball malicioso sobrescrever um arquivo do sistema."},

 {"h2": "Do outro lado: instalar"},
 {"code": """dataforge add validador             # a última versão
dataforge add validador@1.2.0       # uma exata
dataforge install                   # resolve o forge.toml inteiro
dataforge list                      # o que está instalado
dataforge remove validador
""", "lang": "bash"},
 {"p": "O cache fica em `~/.dataforge/cache/`, entre projetos: instalar a mesma versão num segundo projeto não baixa de novo."},

 {"h2": "A lista antes de publicar"},
 {"list": [
   "`dataforge check .` limpo",
   "`dataforge test tests/` verde, importando **pelo nome do pacote**",
   "`version` subida, segundo o [semver](/docs/bibliotecas/versao)",
   "README com um exemplo que roda",
   "`tar tzf` conferido — nada de segredo, nada de `dist/`",
   "o CHANGELOG diz o que mudou, e o que quebrou"], "ordered": True},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/bibliotecas/manutencao", "title": "Manter", "desc": "depreciar sem quebrar"},
   {"href": "/docs/pacotes/publicar", "title": "Referência do publish", "desc": "as opções do comando"}]},
]},

{
"href": "/docs/bibliotecas/manutencao",
"title": "Manter uma biblioteca",
"description": "Depreciar sem quebrar, o que fazer numa mudança incompatível, e como não abandonar quem depende de você.",
"blocos": [
 {"p": "A parte difícil de uma biblioteca começa depois do `1.0.0`. Tudo o que você publicou está rodando na máquina de alguém, e cada mudança tem de escolher entre **melhorar** e **não quebrar**."},

 {"h2": "Acrescentar é quase sempre seguro"},
 {"code": """// antes
action formatar(valor: Float) -> String:
    yield $"R$ {round(valor, 2)}"

// depois — menor, não maior: quem chamava com um argumento continua igual
action formatar(valor: Float, moeda: String := "R$") -> String:
    yield $"{moeda} {round(valor, 2)}"
""", "lang": "df"},
 {"p": "Parâmetro novo **com padrão**, campo novo **com padrão**, ação nova no `relay`: tudo isso é versão menor. A armadilha é o parâmetro novo **sem** padrão — e a linguagem recusa declará-lo depois de um com padrão, o que evita metade dos casos."},

 {"h2": "Depreciar: avise antes de remover"},
 {"p": "Remover na hora quebra; remover depois de um ciclo de aviso não. A sequência tem três etapas e leva uma versão maior:"},
 {"code": """// 1.5.0 — o novo nasce, o velho continua e avisa
action validar_cpf(texto: String) -> Boolean:
    yield len(texto) is 11

action cpf(texto: String) -> Boolean:
    // descontinuada em 1.5.0, sai na 2.0.0
    out "aviso: V.cpf virou V.validar_cpf; ela sai na 2.0.0"
    yield validar_cpf(texto)

relay validar_cpf, cpf
""", "lang": "df"},
 {"list": [
   "**1.5.0** — o nome novo aparece; o antigo continua funcionando e avisa.",
   "**1.x** seguintes — o CHANGELOG repete o aviso.",
   "**2.0.0** — o antigo sai, e a nota de versão diz exatamente o que fazer."], "ordered": True},
 {"p": "O aviso precisa dizer **o que usar no lugar**. Um \"descontinuado\" sem substituto só transfere o problema."},

 {"h2": "Quando a quebra é inevitável"},
 {"table": {"head": ["Faça", "Porque"], "rows": [
   ["suba o **maior**", "é a única sinalização que o resolvedor entende"],
   ["escreva o caminho de migração", "\"o que mudou\" sem \"o que fazer\" custa uma tarde a cada usuário"],
   ["mantenha a linha antiga viva por um tempo", "correção de segurança em `1.x` enquanto a `2.x` amadurece"],
   ["quebre **uma vez**, e não aos poucos", "três versões maiores em seis meses é pior que uma com três quebras"]]}},

 {"h2": "O CHANGELOG é para quem atualiza"},
 {"code": """## 2.0.0

### Quebrado
- `V.cpf` saiu. Use `V.validar_cpf`, que tem a mesma assinatura.
- `V.email` devolve um record em vez de Boolean:
      antes:  given V.email(x):
      agora:  given V.email(x).valido:

### Adicionado
- `V.cep`, com os dois formatos.
""", "lang": "text"},
 {"p": "A seção **Quebrado** vem primeiro e mostra as duas linhas — a de antes e a de agora. É o que transforma uma atualização numa busca-e-substitui em vez de uma investigação."},

 {"h2": "Segurança"},
 {"list": [
   "Uma correção de segurança sai como **correção** em todas as linhas ainda vivas, e não só na mais nova.",
   "A nota diz **o que estava exposto** e **desde quando** — sem isso ninguém sabe se foi afetado.",
   "Se um segredo vazou dentro de um tarball publicado, ele está comprometido: **rotacione**, e publique uma versão nova. Despublicar não desfaz o download de ninguém."]},

 {"h2": "Abandonar com honestidade"},
 {"p": "Uma biblioteca sem manutenção é comum e legítimo. O que faz diferença é dizer: uma linha no README — \"não tenho mantido isto; `outra-lib` faz o mesmo\" — economiza horas de quem estava prestes a adotá-la, e é mais útil que qualquer último commit."},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/bibliotecas/contrato", "title": "O contrato", "desc": "o que está em jogo em cada mudança"},
   {"href": "/docs/versoes", "title": "Versões e estabilidade", "desc": "como a própria linguagem trata isso"}]},
]},
]
