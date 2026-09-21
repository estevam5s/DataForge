# -*- coding: utf-8 -*-
"""Segurança da informação — o currículo, e o veredito de cada item.

Esta seção é deliberadamente **conceitual e honesta ao mesmo tempo**.
Cada conceito aparece explicado como um profissional de segurança o
usa, e logo abaixo vem a resposta que ESTA linguagem dá — com código
que roda, ou com a frase "não existe aqui" e o motivo.

A regra do repositório vale inteira: não se inventa que existe. Uma
página de segurança que promete WebAuthn e não tem é pior que uma que
diz que não tem — a primeira manda alguém construir autenticação em
cima de algo que não está lá.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/seguranca/mapa",
"title": "Segurança da informação: o mapa",
"description": "O currículo completo — da tríade CIA ao bloqueio progressivo — com o que a linguagem responde para cada item, e o que ela não responde.",
"blocos": [
 {"p": "Segurança da informação não é uma biblioteca que se adota: é um conjunto de **decisões** que atravessam a linguagem, o código, o processo e a operação. Esta seção percorre o currículo inteiro e, para cada conceito, responde três coisas: **o que é**, **como o DataForge o atende**, e **o que ele não atende** — com o motivo."},

 {"callout": {"tipo": "atencao", "titulo": "Por que o veredito negativo está aqui", "texto": "Uma documentação de segurança que lista o que a ferramenta **não** faz é mais útil que uma que só lista o que faz. A segunda leva alguém a construir autenticação em cima de algo que não existe, e a descobrir no dia do incidente. Cada página aqui traz a linha *o que não existe*, e ela vem de `Arcane.Ecossistema.o_que_nao_existe()` ou está escrita com o motivo ao lado."}},

 {"h2": "O mapa"},

 {"table": {"head": ["Frente", "O que ela cobre", "Onde"], "rows": [
   ["**Princípios**", "CIA, autenticação, autorização, responsabilização, não-repúdio, privilégio mínimo, defesa em profundidade, zero trust, seguro por desenho e por padrão", "[Princípios](/docs/seguranca/principios)"],
   ["**Ameaças**", "modelagem de ameaças (STRIDE), superfície de ataque, fronteiras de confiança e de segurança, gestão de risco, políticas", "[Ameaças e risco](/docs/seguranca/ameacas)"],
   ["**A linguagem**", "segurança de tipos, de memória, limites de índice, ausência segura, dados imutáveis, padrões seguros", "[O que a linguagem garante](/docs/seguranca/linguagem)"],
   ["**A entrada**", "validação, codificação de saída, serialização e desserialização seguras", "[Entrada e saída](/docs/seguranca/entrada)"],
   ["**Identidade**", "senha, hashing, MFA, TOTP, WebAuthn, OAuth, OIDC, SAML, LDAP, JWT, tokens, sessão", "[Autenticação](/docs/seguranca/autenticacao)"],
   ["**Permissão**", "autorização, RBAC, capacidades, módulos, dependências, sandbox", "[Autorização e capacidades](/docs/seguranca/autorizacao)"],
   ["**Ataques**", "força bruta, *credential stuffing*, bloqueio de conta, atrasos progressivos, limite de taxa", "[Ataques a credenciais](/docs/seguranca/ataques)"],
   ["**Ferramentas**", "detecção de segredos, linter de segurança, análise estática, verificações em execução, auditoria", "[As ferramentas](/docs/seguranca/ferramentas)"]]}},

 {"callout": {"tipo": "dica", "titulo": "A página irmã", "texto": "[Segurança](/docs/seguranca) responde uma pergunta diferente e complementar: **o que a linguagem e as ferramentas já garantem por construção** — injeção de SQL, XSS nos templates, travessia em pacotes, integridade do registro, TLS — e como relatar uma vulnerabilidade. Esta seção aqui é o currículo; aquela é o inventário das garantias."}},

 {"h2": "A tríade CIA, em uma tela"},

 {"p": "Todo o resto é meio para estes três fins. Um controle que não serve a nenhum deles é cerimônia."},

 {"table": {"head": ["", "A pergunta", "A resposta da linguagem"], "rows": [
   ["**Confidencialidade**", "quem *não* deveria ver, não vê?", "`Crypto.cifrar` (ChaCha20-Poly1305), `Seg.segredo`, `Seg.redigir`, `Seg.mascarar_pii`"],
   ["**Integridade**", "o dado é o mesmo que foi gravado?", "`Crypto.hmac`, `Seg.assinar`, `Seg.auditoria` (cadeia encadeada), a etiqueta do AEAD"],
   ["**Disponibilidade**", "quem deveria usar, consegue?", "`Seg.limitador`, `Kiln.limite_de_corpo`, `Seg.json_seguro`, o teto da fila do `Arcane.Laco`"]]}},

 {"code": """adopt Arcane.Crypto as Crypto
adopt Arcane.Seguranca as Seg
adopt Arcane.Bytes as Bytes

// CONFIDENCIALIDADE: o texto cifrado nao revela o conteudo.
// 'cifrar' e 'decifrar' trabalham em Bytes, e nao em texto.
cofre := Crypto.cifrar("saldo: 12345", "uma senha forte")
assert "12345" not in Crypto.hex_encode(cofre)

// INTEGRIDADE: a etiqueta do AEAD vem de graca junto com a cifra.
// Senha errada — ou um byte trocado — e RECUSA, e nao "texto
// ilegivel": e a diferenca entre saber e adivinhar.
assert Bytes.para_texto(Crypto.decifrar(cofre, "uma senha forte")) is "saldo: 12345"

monitor:
    Crypto.decifrar(cofre, "senha errada")
    assert no
handle Error as e:
    out "recusado: a etiqueta nao fecha"

// DISPONIBILIDADE: o limite e o que impede um cliente derrubar todos.
limite := Seg.limitador(100, periodo := 60.0)
assert limite.permitir("cliente-7")""", "lang": "df"},

 {"h2": "Os quatro que sustentam uma conta"},

 {"table": {"head": ["", "A pergunta", "Como se responde aqui"], "rows": [
   ["**Autenticação**", "quem é você?", "senha derivada com `scrypt`, TOTP, token assinado com propósito"],
   ["**Autorização**", "você pode fazer isto?", "RBAC na aplicação, `Arcane.Capacidade` no módulo, `V.exigir_permissao` na tela"],
   ["**Responsabilização**", "quem fez, e quando?", "`Seg.auditoria` — uma linha por evento, com o resumo da anterior"],
   ["**Não-repúdio**", "dá para provar que foi você?", "assinatura com chave que só o autor tem. Um HMAC **não** dá isso: quem confere também consegue forjar"]]}},

 {"callout": {"tipo": "atencao", "titulo": "HMAC não é não-repúdio, e a diferença importa", "texto": "`Crypto.hmac` e `Seg.assinar` usam uma chave **simétrica**: as duas pontas têm a mesma, então quem verifica também consegue produzir. Isso prova **integridade e origem entre duas partes que confiam uma na outra** — e não serve como prova perante um terceiro. Não-repúdio de verdade pede assinatura **assimétrica** (a chave privada só do autor), e isso **não existe** nesta biblioteca: não há RSA nem curva elíptica em Python puro aqui. Quando o requisito for jurídico, use um serviço de assinatura."}},

 {"h2": "O que não existe — a lista curta"},

 {"table": {"head": ["Não há", "Porque", "O que fazer"], "rows": [
   ["WebAuthn, passkeys, FIDO2", "exige CBOR, COSE, atestação e um navegador do outro lado — é um protocolo, não uma função", "um provedor de identidade na frente"],
   ["OAuth 2.0 / OIDC / SAML / LDAP **completos**", "são integrações com sistemas externos, não primitivas. O que existe são as **peças locais**: `Seg.pkce`, `Seg.estado_de_oauth`, `Crypto.jwt_verificar`", "[Autenticação](/docs/seguranca/autenticacao)"],
   ["Argon2id", "em Python puro rodaria lento a ponto de exigir parâmetros fracos — pior que o `scrypt` do `hashlib`, e não melhor", "`Crypto.hash_password` usa scrypt"],
   ["Assinatura assimétrica (RSA, ECDSA, Ed25519)", "implementá-las em Python puro é lento e é exatamente onde um erro de implementação vira falha silenciosa", "`ssl` do Python, ou um HSM/KMS"],
   ["TLS no Kiln", "ele roda sobre o `http.server`; TLS é do nginx ou do Caddy na frente", "[Kiln em produção](/docs/kiln/producao)"]]}},

 {"h2": "Privacidade não é o mesmo que segurança"},

 {"p": "Segurança pergunta *quem pode acessar*. Privacidade pergunta *se esse dado deveria existir*. Um sistema pode ser impecável na primeira e ilegal na segunda — e a LGPD cobra a segunda."},

 {"table": {"head": ["Princípio", "O que ele obriga", "A peça"], "rows": [
   ["**Minimização**", "não coletar o que não se usa", "nenhuma ferramenta substitui a decisão; é de desenho"],
   ["**Privacidade por padrão**", "o estado inicial é o mais restritivo", "`Seg.limpar_html` com lista de permitidos, `Kiln.cabecalhos_seguros`"],
   ["**Mascaramento**", "o log e o relatório não carregam o dado pessoal", "`Seg.mascarar_pii` (CPF, CNPJ, cartão com Luhn, e-mail, telefone)"],
   ["**Descarte**", "apagar de verdade quando o prazo vence", "`Crypto.apagar_seguro`, e a política de retenção que ninguém automatiza por você"]]}},

 {"code": """adopt Arcane.Seguranca as Seg

// Um corpo de pedido inteiro indo para o log — o caminho mais
// comum de um vazamento, e o mais inocente.
corpo := \"\"\"{"cpf": "123.456.789-09", "email": "ana.silva@exemplo.com",
 "cartao": "4111111111111111", "pedido": 1234567890123456}\"\"\"

limpo := Seg.mascarar_pii(corpo)

assert "123.456.789-09" not in limpo
assert "ana.silva" not in limpo
assert "4111111111111111" not in limpo

// O numero do pedido NAO passa no Luhn, entao continua legivel:
// sem isso, todo numero de 16 digitos virava cartao e o relatorio
// ficava ilegivel — um falso positivo que faz desligar a mascara.
assert "1234567890123456" in limpo

out limpo""", "lang": "df"},

 {"h2": "Por onde começar"},

 {"cards": [
   {"href": "/docs/seguranca/principios", "title": "Princípios", "desc": "CIA, privilégio mínimo, defesa em profundidade, zero trust."},
   {"href": "/docs/seguranca/ameacas", "title": "Ameaças e risco", "desc": "STRIDE, superfície de ataque, fronteiras de confiança."},
   {"href": "/docs/seguranca/linguagem", "title": "O que a linguagem garante", "desc": "Tipos, memória, limites, ausência — e o que ela não garante."},
   {"href": "/docs/seguranca/entrada", "title": "Entrada e saída", "desc": "Validar na entrada, codificar na saída, desserializar com lista."},
   {"href": "/docs/seguranca/autenticacao", "title": "Autenticação", "desc": "Senha, scrypt, MFA, TOTP, OAuth, JWT, sessão."},
   {"href": "/docs/seguranca/autorizacao", "title": "Autorização e capacidades", "desc": "RBAC, a fronteira de autoridade, dependências."},
   {"href": "/docs/seguranca/ataques", "title": "Ataques a credenciais", "desc": "Força bruta, credential stuffing, bloqueio progressivo."},
   {"href": "/docs/seguranca/ferramentas", "title": "As ferramentas", "desc": "Segredos, linter, análise estática, auditoria."},
   {"href": "/docs/seguranca", "title": "Garantias por construção", "desc": "Injeção, XSS, pacotes, TLS — e como relatar uma falha."}]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/seguranca/principios",
"title": "Princípios",
"description": "CIA, autenticação, autorização, responsabilização, não-repúdio, privilégio mínimo, defesa em profundidade, zero trust, seguro por desenho e por padrão.",
"blocos": [
 {"p": "Os princípios existem porque controles isolados envelhecem e as perguntas não. Quando um requisito novo aparece, é a eles que se volta para decidir."},

 {"h2": "Confidencialidade, integridade, disponibilidade"},

 {"p": "A **tríade CIA** é o enquadramento mais antigo e o mais útil: todo controle serve a pelo menos um dos três, e um controle que não serve a nenhum é cerimônia."},

 {"table": {"head": ["", "Falha típica", "Na prática, aqui"], "rows": [
   ["**Confidencialidade**", "vazamento, log com dado pessoal, chave no repositório", "cifrar em repouso, `Seg.segredo`, `dataforge seguranca`"],
   ["**Integridade**", "dado alterado sem marca, log forjado", "AEAD, `Seg.auditoria`, `Seg.escapar_log`"],
   ["**Disponibilidade**", "negação de serviço, exaustão de memória", "`Seg.limitador`, `Seg.json_seguro`, limite de corpo"]]}},

 {"callout": {"tipo": "dica", "titulo": "Os três brigam entre si", "texto": "Cifrar tudo prejudica disponibilidade (a chave vira ponto único de falha). Replicar para disponibilidade aumenta a superfície de confidencialidade. Bloquear a conta após três erros protege contra força bruta e **cria** uma negação de serviço contra o usuário legítimo — quem ataca passa a errar de propósito para trancar a conta alheia. Por isso [atraso progressivo](/docs/seguranca/ataques) é preferível a bloqueio duro. Segurança é sempre uma escolha entre os três, e escolher sem nomear o que se perdeu é como a maioria dos sistemas fica frágil."}},

 {"h2": "Autenticação, autorização, responsabilização, não-repúdio"},

 {"p": "Quatro perguntas diferentes, confundidas o tempo todo. Um sistema que autentica muito bem e não autoriza direito entrega o banco inteiro a um usuário legítimo."},

 {"code": """adopt Arcane.Crypto as Crypto
adopt Arcane.Seguranca as Seg
adopt Arcane.OS as OS

// 1. AUTENTICACAO — quem e voce?
guardada := Crypto.hash_password("uma senha bem forte 2026")
assert Crypto.verify_password("uma senha bem forte 2026", guardada)

// 2. AUTORIZACAO — voce pode fazer isto?
steady PERMISSOES := {
    "leitor": ["ler"],
    "editor": ["ler", "escrever"],
    "admin":  ["ler", "escrever", "apagar"]
}

action pode(papel, acao):
    yield acao in (PERMISSOES[papel] ?? [])

assert pode("editor", "escrever")
assert pode("editor", "apagar") is no

// 3. RESPONSABILIZACAO — quem fez, e quando?
livro := Seg.auditoria($"{OS.temp_dir()}/df-princ-{randint(100000, 999999)}.log")
livro.registrar("apagou_pedido", {"pedido": 42}, quem := "ana")
assert livro.conferir()["ok"]

// 4. NAO-REPUDIO — da para provar que foi voce?
// Com chave simetrica isto prova a origem ENTRE AS DUAS PARTES,
// e nao perante um terceiro: quem confere tambem consegue forjar.
chave := Seg.chave_de_assinatura()
recibo := Seg.assinar({"pedido": 42, "por": "ana"}, chave,
    proposito := "recibo")
assert Seg.ler_assinado(recibo, chave, proposito := "recibo")["valor"]["por"] is "ana"

out "os quatro, e o quarto com a ressalva escrita\"""", "lang": "df"},

 {"h2": "Privilégio mínimo"},

 {"p": "Cada parte recebe exatamente a autoridade de que precisa, e por exatamente o tempo em que precisa. É o princípio que mais reduz o **estrago** de uma falha — ele não impede a invasão, ele limita o que ela alcança."},

 {"table": {"head": ["Onde aplicar", "Como"], "rows": [
   ["no módulo", "`Arcane.Capacidade` recusa o `adopt` do que não está na lista"],
   ["no banco", "a conta da aplicação não é a dona do esquema; `service_role` fica fora do bundle"],
   ["no token", "propósito e prazo — um token de confirmar e-mail não troca senha"],
   ["no contêiner", "`USER forge` no Dockerfile, e é o que `dataforge devops` gera"],
   ["no arquivo", "`Seg.caminho_seguro(base, pedido)` — a pasta base é a autoridade"]]}},

 {"code": """adopt Arcane.Capacidade as Cap

// A autoridade AMBIENTE e o que se recorta: o 'adopt' de um modulo
// fora da lista e recusado pelo NOME da capacidade que falta.
permitido := Cap.limites()
out $"o que este arquivo alcanca: {len(permitido)} capacidade(s)"

// E o que ela NAO faz, dito no proprio modulo: ela nao tira o que
// ja foi ENTREGUE. Numa linguagem de capacidade, poder e o que se
// PASSA, nao o que esta no ar — e e por isso que bloquear o 'adopt'
// e a fronteira certa, e nao uma meia-medida.""", "lang": "df"},

 {"h2": "Defesa em profundidade"},

 {"p": "Nenhum controle é confiável sozinho. A pergunta que define o desenho é: **quando esta camada falhar, o que segura?**"},

 {"table": {"head": ["Camada", "Exemplo", "O que ela ainda deixa passar"], "rows": [
   ["1. Validar na entrada", "`Seg.numero_seguro(pagina, 1, 1000)`", "um valor válido e malicioso"],
   ["2. Consulta parametrizada", "`db.query(sql, [valor])`", "nada de SQL — mas o dado vai para a tela"],
   ["3. Codificar na saída", "`Seg.escapar_html`", "nada de XSS — mas o navegador pode carregar de fora"],
   ["4. Cabeçalhos", "CSP, `X-Content-Type-Options`", "um bug de lógica de autorização"],
   ["5. Autorização por recurso", "o dono do pedido é quem o lê", "uma credencial roubada"],
   ["6. Auditoria", "`Seg.auditoria`", "nada — mas agora dá para investigar"]]}},

 {"callout": {"tipo": "atencao", "titulo": "Escapar não substitui parametrizar", "texto": "`Seg.escapar_sql_like` cuida do `%` e do `_` de um `LIKE`, e **não é defesa contra injeção**: o valor continua tendo de ir por parâmetro. A função existe para que uma busca por `\"50%\"` não vire uma busca por *\"50 seguido de qualquer coisa\"* — que é um bug de resultado, não de segurança."}},

 {"h2": "Zero trust"},

 {"p": "O modelo antigo era um perímetro: dentro da rede, confia-se. **Zero trust** parte de que não há dentro — toda requisição é autenticada, autorizada e registrada, venha de onde vier."},

 {"table": {"head": ["Regra", "O que ela quebra do modelo antigo"], "rows": [
   ["nunca confie na rede de origem", "“é interno” deixa de ser argumento"],
   ["autentique **cada** requisição", "a sessão longa e implícita dá lugar a token curto"],
   ["autorize por recurso, e não por papel só", "ser `admin` não basta: é `admin` **daquele** tenant"],
   ["presuma violação", "o log e a auditoria não são opcionais"]]}},

 {"callout": {"tipo": "dica", "titulo": "Onde isso aparece na linguagem", "texto": "`Seg.url_segura` é zero trust aplicado a uma URL: ela **resolve o nome** antes de responder, porque `localtest.me` resolve para `127.0.0.1` e quem ataca controla o DNS do domínio dele. A pergunta não é *como o endereço se parece*, é *para onde ele aponta* — a mesma troca que o zero trust faz com a rede."}},

 {"h2": "Seguro por desenho, e seguro por padrão"},

 {"p": "São coisas diferentes, e a segunda é a que mais rende. **Por desenho** é a arquitetura escolhida para tornar a falha impossível; **por padrão** é o estado inicial ser o mais restritivo — o que protege quem nunca leu a documentação."},

 {"table": {"head": ["Decisão", "Por desenho ou por padrão", "O que ela evita"], "rows": [
   ["`record` é imutável, ponto", "desenho", "um valor compartilhado mudar sob os pés de quem o leu"],
   ["`limpar_html` usa lista de **permitidos**", "desenho", "a lista de proibidos que esqueceu `<svg onload>`"],
   ["`Seg.segredo` imprime `***`", "padrão", "o vault inteiro impresso para depurar"],
   ["a grade da Vitrine já vem paginada", "padrão", "uma listagem sem teto travar o painel"],
   ["`POST` não é repetido sem chave de idempotência", "padrão", "a cobrança em dobro de uma retentativa"],
   ["`Kiln` responde 404 de verdade, não 200", "padrão", "um monitor achando que está tudo bem"]]}},

 {"callout": {"tipo": "atencao", "titulo": "O padrão inseguro mais caro da linguagem, nomeado", "texto": "A linguagem **não sincroniza sozinha**. Duas threads escrevendo na mesma variável perdem atualizações — medido: **40.425 de 80.000**, em silêncio. Isso vale para toda rota do Kiln, onde a concorrência é invisível para quem escreve. O `check` avisa (`escrita-concorrente`), e o aviso é o controle: não há como a linguagem decidir por você onde pôr o mutex sem proibir o uso correto. Veja [Concorrência](/docs/tecnicas/concorrencia)."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/seguranca/ameacas",
"title": "Ameaças e risco",
"description": "Modelagem de ameaças com STRIDE, superfície de ataque, fronteiras de confiança e de segurança, gestão de risco e políticas.",
"blocos": [
 {"p": "Modelar ameaças é responder quatro perguntas, nesta ordem: **o que estamos construindo**, **o que pode dar errado**, **o que vamos fazer**, e **fizemos um bom trabalho?** Pular a primeira é o erro mais comum — sem o desenho do sistema, a lista de ameaças vira uma lista de medos."},

 {"h2": "STRIDE"},

 {"p": "Seis categorias que cobrem praticamente tudo o que se faz contra um sistema. O valor delas é serem **exaustivas o bastante** para a reunião terminar."},

 {"table": {"head": ["", "A ameaça", "A propriedade que ela viola", "A resposta aqui"], "rows": [
   ["**S**poofing", "fingir ser outro", "autenticação", "`hash_password` com scrypt, TOTP, token assinado"],
   ["**T**ampering", "alterar dado em trânsito ou em repouso", "integridade", "AEAD, HMAC, `Seg.auditoria`"],
   ["**R**epudiation", "negar ter feito", "não-repúdio", "trilha encadeada — e a ressalva sobre chave simétrica"],
   ["**I**nformation disclosure", "ver o que não devia", "confidencialidade", "`Seg.segredo`, `redigir`, `mascarar_pii`"],
   ["**D**enial of service", "impedir o uso legítimo", "disponibilidade", "`limitador`, `json_seguro`, limite de corpo"],
   ["**E**levation of privilege", "virar admin sem ser", "autorização", "RBAC por recurso, `Arcane.Capacidade`"]]}},

 {"h2": "Superfície de ataque"},

 {"p": "É a soma de todos os pontos por onde um dado de fora entra no sistema. Reduzi-la é a única medida que melhora **todas** as outras ao mesmo tempo — o que não existe não pode ser atacado."},

 {"table": {"head": ["Ponto de entrada", "O que costuma escapar", "A peça"], "rows": [
   ["parâmetro de rota e query", "faixa não conferida, tipo assumido", "`Seg.numero_seguro`"],
   ["corpo do pedido", "JSON fundo demais, corpo gigante", "`Seg.json_seguro`, `Kiln.limite_de_corpo`"],
   ["cabeçalho", "`Host` e `X-Forwarded-For` tratados como verdade", "conferir contra uma lista"],
   ["upload", "nome com `..`, extensão, tamanho", "`Kiln.salvar_upload`, `Seg.nome_de_arquivo_seguro`"],
   ["URL fornecida pelo usuário", "SSRF para a rede interna", "`Seg.url_segura`"],
   ["redirecionamento", "`?proximo=` para fora do site", "`Seg.redirecionamento_seguro`"],
   ["arquivo de configuração", "segredo commitado", "`dataforge seguranca`"],
   ["dependência", "pacote trocado numa versão publicada", "`forge.lock` com sha256"]]}},

 {"code": """adopt Arcane.Seguranca as Seg

// A superficie de uma rota, em quatro linhas. Cada uma fecha um
// ponto que um pedido de fora alcanca.
action listar(query):
    pagina := Seg.numero_seguro(query["pagina"] ?? "1", 1, 10000)
    por_pagina := Seg.numero_seguro(query["tamanho"] ?? "20", 1, 100)
    busca := Seg.sem_controle(query["q"] ?? "")
    yield {"pagina": pagina, "tamanho": por_pagina, "busca": busca}

assert listar({"pagina": "3"})["pagina"] is 3
assert listar({})["tamanho"] is 20

// '?tamanho=999999999' derruba a listagem, e passa por qualquer
// conversao que nao confira a faixa.
monitor:
    listar({"tamanho": "999999999"})
    assert no
handle UnsafeInputError as e:
    out "recusado antes de chegar ao banco\"""", "lang": "df"},

 {"h2": "Fronteira de confiança, fronteira de segurança"},

 {"p": "São conceitos diferentes e a confusão entre eles custa caro. Uma **fronteira de confiança** é onde o nível de confiança muda — o dado atravessa e passa a ser suspeito. Uma **fronteira de segurança** é onde existe um mecanismo que **obriga** a separação."},

 {"table": {"head": ["Fronteira", "Tipo", "O que ela garante"], "rows": [
   ["navegador → servidor", "confiança **e** segurança", "processos e máquinas diferentes"],
   ["processo → processo", "ambas", "o sistema operacional isola a memória"],
   ["`Arcane.Capacidade`", "**só de confiança**", "recusa o `adopt`; não tira o que já foi entregue"],
   ["thread → thread", "**nenhuma**", "memória compartilhada; nada isola"],
   ["validação de entrada", "**só de confiança**", "depende de quem escreveu chamar a função"]]}},

 {"callout": {"tipo": "atencao", "titulo": "Tratar uma de confiança como de segurança é a falha clássica", "texto": "`Arcane.Capacidade` bloqueia a **autoridade ambiente** — o `adopt` de um módulo fora da lista — e o próprio módulo diz isso em execução, por `limites()`. Ele **não é um sandbox**: código malicioso que já recebeu um objeto de arquivo continua usando-o. Um módulo chamado *Sandbox* que prometesse contenção seria usado onde não pode, e a descoberta viria por incidente. Contenção de verdade é processo separado, contêiner ou VM."}},

 {"h2": "Gestão de risco"},

 {"p": "Risco é **probabilidade × impacto**, e o ponto de fazer a conta é ordenar — não há orçamento para tratar tudo. As quatro respostas possíveis são sempre as mesmas."},

 {"table": {"head": ["Resposta", "Quando", "Exemplo"], "rows": [
   ["**Mitigar**", "o controle custa menos que o dano esperado", "limite de taxa no login"],
   ["**Transferir**", "outro faz melhor e responde por isso", "TLS no Caddy; pagamentos num PSP"],
   ["**Evitar**", "a funcionalidade não paga o risco", "não guardar o número do cartão"],
   ["**Aceitar**", "residual pequeno, e **registrado**", "o `.deb` não é assinado; está escrito"]]}},

 {"callout": {"tipo": "dica", "titulo": "Aceitar é uma decisão, não um silêncio", "texto": "A diferença entre risco aceito e risco esquecido é **um registro com data e nome**. Este repositório faz isso no código: `Arcane.Ecossistema.o_que_nao_existe()` lista os cinco componentes ausentes com o motivo, e `Arcane.Principios` traz os dez princípios com veredito — cinco cumpridos, quatro parciais, um que não se aplica. Um relatório que aprovasse os dez seria a prova de que ninguém o leu."}},

 {"h2": "Políticas"},

 {"p": "Uma política que ninguém consegue verificar é um documento. As que funcionam viram **verificação automática** — e o lugar delas é a esteira de CI."},

 {"code": """// Uma politica executavel: a esteira reprova o que a
// politica proibe, e ninguem precisa lembrar de conferir.

// 1. Nenhum segredo entra no repositorio.
//    $ dataforge seguranca . --strict

// 2. O analisador nao deixa passar erro.
//    $ dataforge check . --strict

// 3. Estilo e higiene.
//    $ dataforge lint .

// 4. A suite inteira, com piso de cobertura.
//    $ dataforge test tests/ --cobertura --minimo=80

// 5. A superficie nao quebrou sem o bump correspondente.
//    $ dataforge abi antes.df depois.df""", "lang": "df"},

 {"table": {"head": ["Política", "O comando que a cobra"], "rows": [
   ["segredo nunca entra no repositório", "`dataforge seguranca . --strict`"],
   ["nenhum erro do analisador", "`dataforge check . --strict`"],
   ["cobertura mínima", "`dataforge test --cobertura --minimo=80`"],
   ["a versão sobe quando a superfície quebra", "`dataforge abi`"],
   ["as dependências são as do lockfile", "`dataforge install`"]]}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/seguranca/linguagem",
"title": "O que a linguagem garante",
"description": "Segurança de tipos, de memória, limites de índice, ausência segura, dados imutáveis e padrões seguros — com a medida, e com o que fica de fora.",
"blocos": [
 {"p": "Boa parte da segurança de um sistema é decidida antes de qualquer biblioteca: pelo que a **linguagem** torna impossível. Esta página é o inventário honesto disso — o que é garantido, o que é verificado, e o que continua por conta de quem escreve."},

 {"h2": "Segurança de memória"},

 {"p": "A classe de falha mais cara da história do software — estouro de buffer, uso após liberação, ponteiro pendurado — **não existe aqui**, e não por mérito da linguagem: o interpretador roda sobre o CPython, que gerencia a memória. Não há aritmética de ponteiro no caminho comum, não há `free`, e todo acesso a coleção é conferido."},

 {"table": {"head": ["Classe de falha", "Estado", "Porque"], "rows": [
   ["estouro de buffer", "**impossível** no caminho comum", "coleções crescem; índice é conferido"],
   ["uso após liberação", "**impossível**", "não há liberação manual"],
   ["ponteiro pendurado", "**impossível**", "a contagem de referências segura o objeto"],
   ["dupla liberação", "**impossível**", "idem"],
   ["corrida de dados", "**possível**", "threads compartilham memória e nada é automático"]]}},

 {"callout": {"tipo": "atencao", "titulo": "Há duas portas para fora dessa garantia, e as duas são explícitas", "texto": "`Arcane.C` (FFI) chama biblioteca nativa: dali para frente a segurança de memória é a do C, e um ponteiro errado derruba o processo. E `Arcane.Estrutura` trabalha sobre blocos de bytes — ali há ponteiro, aritmética e `liberar()`. As duas **conferem os limites** e recusam o nulo (`BufferOverflowError`, `NullPointerError`, `DanglingPointerError`), mas quem as usa saiu do jardim murado de propósito. Segurança de memória por gestão automática é o padrão; sair dela é uma escolha escrita no código."}},

 {"code": """adopt Arcane.Estrutura as Est

bloco := Est.bloco(16)

// O limite e conferido — e o erro tem NOME, e nao um valor de lixo.
monitor:
    Cabecalho := Est.definir("Cabecalho", [["a", "u64"], ["b", "u64"],
        ["c", "u64"]], ordem := "rede")
    Cabecalho.ler(bloco)
    assert no
handle BufferOverflowError as e:
    out "recusado: o registro nao cabe no bloco"

// E o ponteiro nulo tambem:
p := Est.nulo()
monitor:
    p.ler()
    assert no
handle NullPointerError as e:
    out "recusado: ponteiro nulo\"""", "lang": "df"},

 {"h2": "Segurança de tipos"},

 {"p": "A linguagem é **dinamicamente tipada com verificação estática opcional**. A distinção importa: o tipo não é apagado em execução — ele é conferido —, e o `check` prova antes de rodar o que consegue provar."},

 {"table": {"head": ["Confere", "Quando", "Código"], "rows": [
   ["tipo declarado de variável e parâmetro", "execução **e** `check`", "`x: Integer := \"a\"`"],
   ["aridade da chamada, inclusive entre arquivos", "`check`", "`P.criar(1, 2, 3)`"],
   ["campo que não existe num record ou instância", "`check`, com sugestão", "`p.clientte`"],
   ["índice fora do alcance num literal fixo", "`check`", "`indice-fora-do-alcance`"],
   ["chave ausente num vault literal", "`check`, com sugestão", "`chave-ausente`"],
   ["limite de um genérico `<T extends X>`", "ambos", "`generic-bound`"],
   ["refinamento de um `type … where`", "toda fronteira", "`tipo-refinado`"]]}},

 {"code": """// O refinamento vale em TODA fronteira — declaracao, parametro,
// retorno e campo. Um tipo que so valesse na criacao seria uma
// sugestao, e nao um tipo.
type Positivo := Integer where valor bigger 0

action dividir(total: Integer, partes: Positivo) -> Integer:
    yield total ~/ partes

assert dividir(10, 2) is 5

monitor:
    dividir(10, 0)
    assert no
handle Error as e:
    out "recusado na fronteira: 0 nao e Positivo"

// E o tipo OPACO e o que impede confundir dois textos. A regra
// vale na CRIACAO, entao um valor invalido nunca existe:
opaque type Cpf := String where len(valor) is 11

cpf := Cpf("12345678909")
assert cpf isnt void

monitor:
    Cpf("123")
    assert no
handle Error as e:
    out "recusado: um Cpf tem 11 digitos"

out "o tipo opaco separa dois textos que parecem iguais\"""", "lang": "df"},

 {"callout": {"tipo": "atencao", "titulo": "O que o analisador NÃO prova", "texto": "Ele é **otimista de propósito**: quando não consegue provar que algo está errado, fica calado. Um falso alarme ensina a ignorar mensagens, e um analisador ignorado não protege nada. Então ele cala sobre valor que vem de fora, sobre objeto sem anotação, sobre o que atravessa um decorador, e dentro de `monitor`/`retry` os erros viram aviso. **Isso não é segurança de tipos à moda de Rust** — é verificação parcial, e a diferença precisa estar clara para quem desenha o sistema."}},

 {"h2": "Ausência segura"},

 {"p": "`void` é um valor, não um ponteiro nulo — e ler um campo de `void` levanta `NullReferenceError`, com linha e coluna, em vez de corromper qualquer coisa. Os dois operadores que evitam o `given` defensivo são os mesmos do resto do mundo."},

 {"code": """v := {"nome": "Ana"}

// '??' da o padrao quando o valor e void.
assert (v["idade"] ?? 0) is 0

// '?.' para a cadeia em vez de levantar.
endereco := void
assert endereco?.cidade is void

// E a distincao que o analisador conhece: depois de conferir,
// o tipo deixa de incluir void.
given v["nome"] isnt void:
    assert len(v["nome"]) is 3

out "ausencia tratada, e nao adivinhada\"""", "lang": "df"},

 {"callout": {"tipo": "dica", "titulo": "A armadilha que o `??` esconde numa rota", "texto": "`query[\"x\"]` **sem** `??` dá 500 numa rota do Kiln: a query, o corpo e os cabeçalhos vêm de fora, a chave pode não vir, e indexar um vault sem a chave é erro. `params` é a exceção — se a rota casou, o parâmetro existe. É a diferença entre dado que você controla e dado que chegou pela rede, e ela aparece no código como um `??`."}},

 {"h2": "Dados imutáveis"},

 {"p": "Imutabilidade é um controle de segurança, e não só de estilo: um valor que não muda não pode ser alterado por outra parte do programa depois de conferido — o padrão *TOCTOU* (conferir e usar) simplesmente não acontece."},

 {"table": {"head": ["Forma", "O que ela garante"], "rows": [
   ["`steady`", "o nome não é reatribuído"],
   ["`record`", "campos imutáveis, igualdade estrutural, `with` devolve cópia"],
   ["`freeze(xs)`", "um cluster que não muda"],
   ["`Objetos.congelar(obj)`", "a instância recusa escrita"],
   ["`Dom.valor(...)`", "objeto de valor com a regra cobrada na criação"]]}},

 {"code": """record Permissao:
    papel: String
    acao: String

p := Permissao("editor", "escrever")

// Conferido uma vez, vale para sempre: nada muda o objeto depois.
monitor:
    p.papel := "admin"
    assert no
handle Error as e:
    out "recusado: record e imutavel"

// 'with' devolve um NOVO — o original continua o que era.
elevada := p with {"papel": "admin"}
assert p.papel is "editor"
assert elevada.papel is "admin\"""", "lang": "df"},

 {"h2": "Padrões seguros — a lista"},

 {"table": {"head": ["Padrão", "A alternativa insegura que ele evita"], "rows": [
   ["a indentação só aceita espaço", "o mesmo arquivo com significados diferentes"],
   ["`//` é comentário; divisão inteira é `~/`", "ambiguidade em código lido às pressas"],
   ["`record` é imutável por padrão", "compartilhar estado sem perceber"],
   ["campo com padrão mutável é **copiado** no `spawn`", "todas as instâncias dividirem a mesma lista"],
   ["`monitor` sem `handle` **não** engole o erro", "a falha sumir silenciosamente"],
   ["`defer` **não** engole erro", "um arquivo não fechado terminar com código 0"],
   ["`parallel` levanta o erro da tarefa que falhou", "um CI verde com metade do trabalho perdida"],
   ["`Crypto.hash_password` usa scrypt", "SHA-256 puro numa senha"],
   ["o `check` avisa sobre escrita concorrente", "perder atualizações em silêncio"]]}},

 {"h2": "Limites e recursos"},

 {"p": "A disponibilidade tem controles próprios na linguagem, e eles existem porque o caso comum é acidente e não ataque."},

 {"table": {"head": ["Limite", "O que ele impede"], "rows": [
   ["teto de mil quadros de chamada", "recursão infinita comer a pilha (e `yield f(…)` vira salto)"],
   ["`Seg.json_seguro`", "aninhamento fundo estourar a pilha do leitor"],
   ["`Kiln.limite_de_corpo`", "um corpo gigante consumir a memória"],
   ["teto na fila do `Arcane.Laco`", "fonte mais rápida que o consumo morrer por memória"],
   ["`Arcane.Inicio.limite_da_pilha`", "o teto real da thread, e não o presumido"]]}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/seguranca/entrada",
"title": "Entrada e saída",
"description": "Validação de entrada, codificação de saída e serialização segura — as três que respondem pela maioria das falhas exploradas.",
"blocos": [
 {"p": "A maior parte das falhas exploradas na prática cabe em uma frase: **dado de fora tratado como código**. As três defesas são independentes e nenhuma substitui as outras."},

 {"h2": "Validar na entrada"},

 {"p": "Validação responde *este valor é aceitável?* — e a resposta certa a um valor inaceitável é **recusar**, não consertar. Consertar cria o segundo problema: duas versões do mesmo dado, e a conferência feita sobre a errada."},

 {"table": {"head": ["Conferir", "A função", "O que passa despercebido sem ela"], "rows": [
   ["número e faixa", "`Seg.numero_seguro`", "`?pagina=-1`, `?tamanho=999999999`"],
   ["JSON", "`Seg.json_seguro`", "dez mil níveis de aninhamento"],
   ["URL de fora", "`Seg.url_segura`", "SSRF para `169.254.169.254`"],
   ["caminho de arquivo", "`Seg.caminho_seguro`", "`../../etc/passwd`, e o link simbólico"],
   ["nome de arquivo", "`Seg.nome_de_arquivo_seguro`", "`CON.txt`, e a marca que inverte a leitura"],
   ["destino de redirecionamento", "`Seg.redirecionamento_seguro`", "`//banco-falso.exemplo`"],
   ["texto", "`Seg.sem_controle`", "caracteres invisíveis de direção de escrita"],
   ["esquema de formulário", "`Kiln.validar`, `Lavra.validar`", "campo ausente tratado como vazio"]]}},

 {"code": """adopt Arcane.Seguranca as Seg

// Travessia: o 'realpath' antes de comparar e o que fecha o buraco.
// Sem ele, um link simbolico dentro da pasta aponta para fora e a
// comparacao de texto aprova.
monitor:
    Seg.caminho_seguro("/tmp/uploads", "../../etc/passwd")
    assert no
handle UnsafeInputError as e:
    out "travessia recusada"

// E o byte nulo, que e a forma classica de truncar o nome DEPOIS
// da conferencia de extensao.
monitor:
    Seg.caminho_seguro("/tmp/uploads", "foto.png\\u0000.php")
    assert no
handle Error as e:
    out "byte nulo recusado"

// Nome de arquivo: '..' some, e o nome reservado do Windows ganha
// prefixo — criar 'CON.txt' falha la e funciona aqui.
assert Seg.nome_de_arquivo_seguro("../../etc/passwd") is "passwd"
assert Seg.nome_de_arquivo_seguro("CON.txt") is "_CON.txt\"""", "lang": "df"},

 {"callout": {"tipo": "atencao", "titulo": "Lista de permitidos, sempre", "texto": "Uma lista de proibidos é uma aposta de que se pensou em tudo, e a história do XSS é a lista dos que não pensaram: `<svg onload>`, `<math>`, `javascript:` com tabulação no meio, entidade HTML dentro do atributo. A lista de permitidos erra para o lado de **perder uma tag legítima** — que é um bug visível, relatado no mesmo dia. É por isso que `Seg.limpar_html` recebe as tags que passam, e não as que não passam."}},

 {"h2": "Codificar na saída"},

 {"p": "Codificação responde *para onde este texto vai?* — e a resposta muda a função. O que protege uma página HTML não protege uma linha de shell, e o que protege shell estraga um CSV."},

 {"table": {"head": ["Destino", "Função", "O que ela fecha"], "rows": [
   ["corpo HTML", "`escapar_html`", "XSS refletido e armazenado"],
   ["atributo HTML", "`escapar_atributo`", "atributo sem aspas, onde o espaço é o fim do valor"],
   ["dentro de `<script>`", "`escapar_js`", "`</script>` no meio de uma string fechando a tag"],
   ["URL", "`escapar_url`", "parâmetro que vira outro parâmetro"],
   ["linha de shell", "`escapar_shell`", "injeção de comando"],
   ["`LIKE` do SQL", "`escapar_sql_like`", "`%` do usuário virando curinga *(não é defesa contra injeção)*"],
   ["célula de planilha", "`escapar_csv`", "injeção de fórmula"],
   ["cabeçalho HTTP", "`escapar_cabecalho`", "injeção de cabeçalho por CRLF"],
   ["linha de log", "`escapar_log`", "log forjado"],
   ["expressão regular", "`escapar_regex`", "padrão do usuário virando metacaractere"]]}},

 {"code": """adopt Arcane.Seguranca as Seg

// 1. O caso que mais engana: o texto do usuario vai DENTRO de um
//    <script>. Escapar aspas nao resolve — '</script>' fecha a tag
//    antes de o JavaScript ser lido, e o resto da pagina vira codigo.
perigoso := "</script><script>roubar()</script>"
assert "</script>" not in Seg.escapar_js(perigoso)

// 2. A injecao que quase ninguem escapa: o Excel EXECUTA a celula
//    que comeca com '=', '+', '-' ou '@'.
assert Seg.escapar_csv("=HYPERLINK(\\"http://mau\\")")[0:1] is "'"
assert Seg.escapar_csv("Ana Souza") is "Ana Souza"

// 3. O log forjado: um '\\n' num campo acrescenta uma LINHA inteira,
//    e a investigacao seguinte le um evento que nunca aconteceu.
forjado := "ana\\n2026-01-01 INFO admin apagou tudo"
assert "\\n" not in Seg.escapar_log(forjado)

// 4. E o cabecalho, onde o CRLF injeta outro cabecalho.
assert Seg.escapar_cabecalho("/painel\\r\\nSet-Cookie: admin=1") is "/painelSet-Cookie: admin=1"

out "quatro destinos, quatro funcoes\"""", "lang": "df"},

 {"h2": "Serializar e desserializar"},

 {"p": "Desserialização insegura é a falha que mais surpreende, porque a operação parece passiva. Em linguagens onde o formato carrega **tipos** — `pickle` do Python, a serialização nativa do Java —, ler um arquivo é executar código."},

 {"callout": {"tipo": "dica", "titulo": "Aqui essa classe não existe, e o motivo é o formato", "texto": "`Arcane.Serialization` e `Objetos.de_json` trabalham com **JSON**, que carrega dados e não tipos. Não há construtor a invocar na leitura, então não há execução a sequestrar. A ponte para o Python (`adopt Python.pickle`) reabre a porta — e ali a responsabilidade volta a ser de quem escreveu."}},

 {"p": "O que **continua** sendo sua responsabilidade é a **forma** do que chegou: JSON válido não quer dizer JSON esperado."},

 {"code": """adopt Arcane.Seguranca as Seg
adopt Arcane.Objetos as Obj

record Pedido:
    id: Integer
    total: Integer

// 1. Teto de tamanho, profundidade e numero de chaves ANTES de ler.
//    Um '[[[[[...]]]]]' de dez mil niveis estoura a pilha de quem le,
//    e o leitor padrao aceita: e negacao de servico com 50 KB.
cru := Seg.json_seguro("{\\"id\\": 7, \\"total\\": 199}")

// 2. O dado NUNCA escolhe o tipo. A lista de tipos e argumento,
//    e as invariantes sao conferidas na chegada.
pedido := Obj.de_vault(cru, [Pedido])
assert pedido.id is 7

// 3. E o inverso, para gravar.
assert Obj.para_vault(pedido)["total"] is 199

out "o formato nao executa, e a forma e conferida\"""", "lang": "df"},

 {"table": {"head": ["Regra", "Porque"], "rows": [
   ["o dado nunca escolhe a classe", "`Objetos.de_vault` exige a lista de tipos como argumento"],
   ["`setup` não roda na desserialização", "construtor é código; a chegada não o invoca"],
   ["as invariantes são conferidas na chegada", "um objeto inválido nunca existe"],
   ["tamanho e profundidade antes de interpretar", "a defesa tem de vir antes do trabalho"]]}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/seguranca/autenticacao",
"title": "Autenticação",
"description": "Senha e hashing (scrypt, PBKDF2, bcrypt, Argon2id), MFA, 2FA, TOTP, WebAuthn e passkeys, OAuth 2.0, OIDC, SAML, LDAP, JWT, tokens e sessão — com o veredito de cada um.",
"blocos": [
 {"p": "Autenticação responde **quem é você**. Esta página percorre os mecanismos usados na indústria e diz, para cada um, o que a linguagem entrega — e o que ela não entrega."},

 {"h2": "Senha: o hashing"},

 {"p": "Guardar senha é guardar um **derivado lento e salgado** dela. A lentidão é o recurso: ela não incomoda quem faz um login e inviabiliza quem faz bilhões."},

 {"table": {"head": ["Algoritmo", "Estado aqui", "O veredito"], "rows": [
   ["**scrypt**", "**o padrão**, `Crypto.hash_password`", "*memory-hard*: exige ~32 MB por tentativa, e memória é o que a GPU não tem em abundância por núcleo"],
   ["**PBKDF2-SHA256**", "disponível, `algoritmo := \"pbkdf2\"`", "só encadeia hash — barato de acelerar em GPU. Fica para compatibilidade e para senhas antigas"],
   ["**Argon2id**", "**não existe**", "seria o melhor; em Python puro rodaria lento a ponto de exigir parâmetros fracos, o que o torna *pior* que o scrypt"],
   ["**bcrypt**", "**não existe**", "exige uma implementação de Blowfish; o `hashlib` não a traz, e escrevê-la em Python é o tipo de código criptográfico que não se deve escrever"]]}},

 {"code": """adopt Arcane.Crypto as Crypto

// O sal e sorteado e vai DENTRO da string guardada: guarde-a inteira.
guardada := Crypto.hash_password("uma senha bem forte 2026")

out guardada[0:24]              // scrypt$32768$8$1$...

assert Crypto.verify_password("uma senha bem forte 2026", guardada)
assert Crypto.verify_password("outra senha", guardada) is no

// Duas vezes a MESMA senha dao strings diferentes — e o sal e o
// motivo: sem ele, senhas iguais teriam o mesmo resumo, e uma
// tabela pronta quebraria todas de uma vez.
assert Crypto.hash_password("igual") isnt Crypto.hash_password("igual")""", "lang": "df"},

 {"h3": "Rotação: o único momento em que dá para atualizar"},

 {"p": "Sem isto, um banco fica para sempre no algoritmo com que nasceu — ninguém sabe quais linhas estão velhas, e não há momento em que a senha em claro esteja disponível para regravar. Exceto **um**: o login bem-sucedido."},

 {"code": """adopt Arcane.Crypto as Crypto

action entrar(senha, guardada):
    given Crypto.verify_password(senha, guardada) is no:
        yield {"ok": no}

    // Aqui — e so aqui — a senha em claro existe e ja foi conferida.
    given Crypto.precisa_rehash(guardada):
        yield {"ok": yes, "regravar": Crypto.hash_password(senha)}

    yield {"ok": yes}

// Uma senha guardada no formato antigo continua entrando...
antiga := Crypto.hash_password("segredo do usuario", algoritmo := "pbkdf2")
r := entrar("segredo do usuario", antiga)
assert r["ok"]
// ...e sai do login ja no formato novo.
assert "regravar" in keys(r)

out "o formato antigo entra, e e atualizado na saida\"""", "lang": "df"},

 {"callout": {"tipo": "atencao", "titulo": "Por que `verify_password` ainda aceita o formato antigo", "texto": "Um banco tem senhas guardadas de antes da troca de algoritmo. Se a conferência só entendesse o formato novo, o dia da atualização seria **o dia em que ninguém consegue entrar** — e a saída de emergência seria mandar todo mundo redefinir a senha. O formato é auto-descritivo: o primeiro campo diz qual é, e os parâmetros vêm junto. É o que torna a próxima troca barata."}},

 {"h3": "Força, política e vazamento"},

 {"p": "“Senha fraca” não diz o que fazer. O que vai para a tela é a **lista do que falta**."},

 {"code": """adopt Arcane.Seguranca as Seg

fraca := Seg.forca_da_senha("Abcdef1!")
out $"{fraca['rotulo']} ({fraca['nota']}/100)"
cycle problema in fraca["problemas"]:
    out $"   - {problema}"

// A politica devolve; 'exigir_politica' levanta com a lista em
// 'e.nota', para quem escreve o caminho feliz.
r := Seg.politica("Tr0vao#Azul7291!x")
assert r["ok"]

// E a entropia, que e uma medida do TEXTO e nao de como ele foi
// escolhido: por isso ela e um dos criterios, e nunca o unico.
out $"entropia: {r['entropia']} bits\"""", "lang": "df"},

 {"callout": {"tipo": "nota", "titulo": "Verificar vazamento sem entregar a senha", "texto": "`Seg.vazada(senha)` consulta o *Have I Been Pwned* mandando os **cinco primeiros** caracteres do SHA-1 — nunca a senha. O serviço devolve centenas de resumos que começam com aquele prefixo, e a comparação é local: ele não tem como saber qual das centenas era a sua. É o k-anonimato, e é uma chamada de **rede** — está no nome da função. Ela devolve `-1` em vez de levantar quando a rede falha: uma política de senha que para de funcionar porque um serviço de terceiro caiu impede cadastro por um motivo que não é de segurança. Para conferir offline: `prefixo_vazamento` + `conferir_vazamento`."}},

 {"callout": {"tipo": "atencao", "titulo": "Rotação periódica de senha é má prática", "texto": "Obrigar a troca a cada 90 dias é contraproducente, e o **NIST SP 800-63B** recomenda contra desde 2017: as pessoas respondem com `Senha1!`, `Senha2!`, `Senha3!` — previsível e pior que a original. Troque **por evento**: vazamento conhecido, suspeita de comprometimento, saída de um administrador. O que `precisa_rehash` faz é outra coisa: rotacionar o **algoritmo**, sem incomodar ninguém."}},

 {"h2": "Múltiplos fatores"},

 {"p": "Um fator é algo que você **sabe** (senha), **tem** (telefone, chave física) ou **é** (biometria). MFA exige de categorias diferentes — duas senhas não são dois fatores."},

 {"table": {"head": ["Fator", "Estado aqui", "Observação"], "rows": [
   ["**TOTP** (app autenticador)", "**existe**, RFC 6238 completo", "o segundo fator com melhor relação custo/benefício"],
   ["**HOTP** (por contador)", "**existe**, RFC 4226", "base do TOTP; serve para token físico de contador"],
   ["**Códigos de recuperação**", "**existe**", "devolve o código **e** o resumo — guarde só o resumo"],
   ["**SMS**", "não há integração", "desaconselhado: *SIM swap* e interceptação de SS7"],
   ["**WebAuthn / passkeys / FIDO2**", "**não existe**", "é um protocolo com CBOR, COSE e atestação, não uma função"],
   ["**Chave física (YubiKey)**", "**não existe**", "chega por WebAuthn"]]}},

 {"code": """adopt Arcane.Seguranca as Seg

// Os vetores do RFC 4226. Uma implementacao de OTP que nao os
// reproduz esta errada mesmo que "funcione": o autenticador do
// usuario vai discordar dela.
assert Seg.hotp("GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ", 0) is "755224"
assert Seg.hotp("GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ", 1) is "287082"

// O cadastro: sorteie o segredo, mostre o QR, e guarde o segredo
// CIFRADO — ele vale tanto quanto a senha.
segredo := Seg.totp_segredo()
out Seg.totp_uri(segredo, "ana@loja.com", emissor := "Minha Loja")

// A conferencia aceita a janela vizinha: o relogio do telefone anda
// alguns segundos fora, e um codigo digitado no segundo 29 chega no
// 31. Sem tolerancia, uma fracao real dos logins legitimos falha —
// e o usuario aprende a desligar o segundo fator.
codigo := Seg.totp_agora(segredo)
assert Seg.totp_conferir(segredo, codigo)
assert Seg.totp_conferir(segredo, "000000") is no

// E os codigos de recuperacao, para quem perdeu o telefone.
r := Seg.codigos_de_recuperacao(10)
out $"{len(r['codigos'])} codigos; guarde apenas os {len(r['resumos'])} resumos\"""", "lang": "df"},

 {"callout": {"tipo": "atencao", "titulo": "Três detalhes que decidem se o TOTP protege", "texto": "**1.** A comparação é em tempo constante — comparar código com `is` vaza, pelo tempo, quantos dígitos iniciais estavam certos. **2.** O código usado precisa ser **marcado como usado**: sem isso, quem intercepta tem 30 segundos para reusá-lo. Isso é estado da sua aplicação, e a biblioteca não pode fazer por você. **3.** O segredo guardado em claro no banco anula tudo — quem ler a tabela gera os códigos."}},

 {"h2": "WebAuthn e passkeys — o veredito"},

 {"p": "São hoje o mecanismo mais forte disponível: a chave privada nunca sai do dispositivo, e a assinatura é ligada ao **domínio**, o que torna o phishing estruturalmente impossível."},

 {"callout": {"tipo": "atencao", "titulo": "Não existe nesta biblioteca, e o motivo", "texto": "WebAuthn não é uma função: é um protocolo entre navegador, autenticador e servidor, com CBOR, COSE, cadeias de atestação e verificação de assinatura **assimétrica** (ES256, RS256). Duas dessas peças — a criptografia assimétrica e o parser CBOR — não existem aqui, e escrevê-las em Python puro é exatamente o tipo de código criptográfico que não se deve escrever à mão. **O que fazer:** ponha um provedor de identidade na frente (Auth0, Keycloak, Clerk, Supabase Auth) e receba o resultado como [OIDC](/docs/seguranca/autenticacao) — e aí as peças que existem aqui (`pkce`, `estado_de_oauth`, `jwt_verificar`) são as que você usa."}},

 {"h2": "OAuth 2.0, OIDC, SAML, LDAP"},

 {"p": "São **integrações** com sistemas externos, e não primitivas. O que a biblioteca traz são as peças **locais** de cada fluxo — as que envolvem criptografia e que são justamente onde as implementações erram."},

 {"table": {"head": ["Protocolo", "Para quê", "Estado aqui"], "rows": [
   ["**OAuth 2.0**", "autoriz**ação** delegada — acesso a um recurso", "as peças locais: `pkce`, `estado_de_oauth`; o HTTP é `Arcane.Malha`"],
   ["**OpenID Connect**", "autentic**ação** sobre OAuth — quem é a pessoa", "a verificação do `id_token` é `Crypto.jwt_verificar` *(HS\\*; para RS256 é preciso um serviço)*"],
   ["**SAML**", "SSO corporativo em XML", "**não existe** — exige XML-DSig e canonicalização, cheios de armadilhas"],
   ["**LDAP / Active Directory**", "diretório corporativo", "**não existe** — é um protocolo binário próprio"]]}},

 {"callout": {"tipo": "dica", "titulo": "OAuth autoriza; OIDC autentica", "texto": "É a confusão mais cara desta área. OAuth 2.0 entrega um *access token*: ele diz **o que pode ser feito**, e não quem é a pessoa. Usar um access token como prova de identidade é a falha conhecida por *confused deputy* — o token foi emitido para outro aplicativo e você o aceita como login. Quem responde “quem é” é o `id_token` do OIDC, e ele precisa ser **verificado**: assinatura, emissor (`iss`), destinatário (`aud`), prazo (`exp`) e o `nonce` que você mandou."}},

 {"code": """adopt Arcane.Seguranca as Seg

// PKCE (RFC 7636) — o que o OAuth 2.0 exige hoje, e a peca que a
// biblioteca entrega. O 'code' volta pela URL do navegador; num app
// de celular ou numa SPA nao existe segredo do cliente para provar
// quem e, e quem interceptar o codigo o troca por um token.
par := Seg.pkce()

// Ao PEDIR o codigo, manda-se o desafio (o SHA-256 do verificador).
out $"code_challenge={par['desafio'][0:16]}... method={par['metodo']}"

// Ao TROCAR o codigo, manda-se o verificador. So quem sorteou o tem.
assert Seg.conferir_pkce(par["verificador"], par["desafio"])
assert Seg.conferir_pkce("outro-verificador-que-nao-e-o-certo-123456", par["desafio"]) is no

// E o 'state', que e a defesa de CSRF do fluxo: sem ele, um atacante
// inicia o proprio fluxo e faz a vitima completa-lo — a conta dela
// acaba ligada a conta dele no provedor.
estado := Seg.estado_de_oauth()
// guarde na sessao, e CONFIRA na volta. Guardar e nao conferir e o
// defeito mais comum deste fluxo.
assert len(estado) bigger 20

out "as pecas locais do OAuth, e a rede fica com o Arcane.Malha\"""", "lang": "df"},

 {"callout": {"tipo": "atencao", "titulo": "`plain` não é uma opção", "texto": "O RFC 7636 define dois métodos de PKCE: `S256` e `plain`. O `plain` manda o verificador **como** desafio — o que não protege de nada, porque quem intercepta a primeira ida já tem os dois. Ele existe no RFC por compatibilidade com clientes antigos, e não é oferecido aqui."}},

 {"h2": "JWT"},

 {"p": "Um JWT é um objeto JSON assinado. Ele é útil quando o receptor precisa validar **sem consultar um banco** — e é exatamente por isso que ele é difícil de revogar."},

 {"code": """adopt Arcane.Crypto as Crypto

chave := Crypto.random_hex(32)

token := Crypto.jwt_assinar({"sub": "ana", "papel": "editor"}, chave,
    expira_em := 900)

// O ALGORITMO E DECIDIDO POR QUEM VERIFICA, e nao pelo token.
// Essa e a falha classica do JWT: aceitar o 'alg' que vem dentro
// permite 'alg: none' — e o token passa a ser texto assinado por
// ninguem. Aqui o algoritmo e argumento da verificacao.
r := Crypto.jwt_verificar(token, chave, algoritmo := "HS256")
assert r["valido"]
assert r["carga"]["sub"] is "ana"

// 'jwt_ler' le SEM verificar — para inspecionar, nunca para decidir.
out Crypto.jwt_ler(token)["papel"]

// Ele DEVOLVE o veredito em vez de levantar: o motivo entra no log,
// e quem chama decide o que responder ao cliente.
outra := Crypto.jwt_verificar(token, "outra chave", algoritmo := "HS256")
assert outra["valido"] is no
out $"recusado: {outra['motivo']}\"""", "lang": "df"},

 {"table": {"head": ["A armadilha", "Como se fecha aqui"], "rows": [
   ["`alg: none`", "o algoritmo é **argumento de quem verifica**, nunca lido do token"],
   ["confusão HS256/RS256", "idem — não há como o token escolher"],
   ["token que não expira", "`expira_em` é conferido na verificação"],
   ["revogação", "**não tem solução no formato**: use prazo curto + *refresh*"],
   ["dado sensível no corpo", "o corpo é base64, **não** é cifrado — qualquer um lê"]]}},

 {"h2": "Tokens e sessão"},

 {"table": {"head": ["Tipo", "Vida", "Onde guardar", "Como revogar"], "rows": [
   ["**acesso**", "5–15 min", "memória do cliente", "não se revoga: expira"],
   ["**refresh**", "dias/semanas", "cookie `HttpOnly`", "no banco — e **rotacione a cada uso**"],
   ["**sessão**", "horas", "cookie `HttpOnly`", "apagar do armazém"],
   ["**API key**", "longa", "cofre do cliente", "no banco, por prefixo"],
   ["**de uso único** (e-mail, senha)", "minutos", "não se guarda", "propósito + prazo, e marcar usado"]]}},

 {"code": """adopt Arcane.Seguranca as Seg

chave := Seg.chave_de_assinatura()

// Um link de redefinir senha: proposito E prazo. Sem o proposito, o
// token que confirma um e-mail SERVE para trocar a senha — os dois
// sao assinados com a mesma chave.
link := Seg.assinar({"usuario": 42}, chave, proposito := "trocar-senha")

monitor:
    Seg.ler_assinado(link, chave, prazo := 900, proposito := "confirmar-email")
    assert no
handle SignatureError as e:
    out "recusado: o proposito e outro"

lido := Seg.ler_assinado(link, chave, prazo := 900, proposito := "trocar-senha")
assert lido["valor"]["usuario"] is 42

// E a URL assinada, para download temporario: mudar QUALQUER
// parametro invalida a assinatura.
u := Seg.assinar_url("https://loja.com/baixar?id=9", chave, prazo := 60)
assert Seg.conferir_url(u, chave)["ok"]""", "lang": "df"},

 {"callout": {"tipo": "atencao", "titulo": "A ordem da verificação não é detalhe", "texto": "`ler_assinado` confere a **assinatura antes do prazo**. Conferir o prazo primeiro significa ler o corpo de um token que ainda não se sabe se é legítimo — e a data de dentro dele é dado de quem o mandou até a assinatura fechar. E `ExpiredTokenError` é separado de `SignatureError` de propósito: no primeiro caso o link era legítimo e caducou, e a ação certa é oferecer outro; num token adulterado, oferecer outro seria ajudar quem tenta."}},

 {"h3": "O cookie de sessão"},

 {"table": {"head": ["Atributo", "Porque"], "rows": [
   ["`HttpOnly`", "o JavaScript não lê — um XSS deixa de virar roubo de sessão"],
   ["`Secure`", "não viaja em HTTP puro"],
   ["`SameSite=Lax`", "não vai numa requisição de outro site (defesa de CSRF)"],
   ["`Path=/`, sem `Domain`", "não vaza para subdomínio de terceiro"],
   ["id novo **após o login**", "impede fixação de sessão"]]}},

 {"callout": {"tipo": "dica", "titulo": "Fixação de sessão, e como a Vitrine a fecha", "texto": "O ataque: o atacante planta um id de sessão no navegador da vítima **antes** do login; se o servidor reaproveitar aquele id, os dois passam a compartilhar a sessão autenticada. Na Vitrine, um id desconhecido vira **sessão nova**, e só id de 32 hexadecimais chega ao armazém — o segundo detalhe também impede que `../x` vire nome de arquivo no armazém em disco."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/seguranca/autorizacao",
"title": "Autorização e capacidades",
"description": "RBAC, autorização por recurso, a fronteira de autoridade do Arcane.Capacidade, segurança de dependências e os limites do sandbox.",
"blocos": [
 {"p": "Autenticação diz **quem** é. Autorização diz **o que pode**. A segunda é onde mora a maioria das falhas exploradas na prática, e é a menos testada — porque exige pensar no usuário legítimo agindo fora do seu papel."},

 {"h2": "A falha mais comum: autorização por objeto"},

 {"p": "Conferir o **papel** e esquecer o **dono** é a vulnerabilidade mais frequente em aplicações web. O usuário está autenticado, tem o papel certo, e lê o pedido de outra pessoa trocando o número na URL."},

 {"code": """// ERRADO: confere o papel, e nao o dono.
action ver_pedido_errado(usuario, id):
    given usuario["papel"] isnt "cliente":
        trigger "sem permissao"
    yield buscar(id)          // qualquer id, de qualquer um

// CERTO: a consulta carrega o dono. A autorizacao vira uma
// condicao do WHERE, e nao um 'given' que alguem pode esquecer.
action ver_pedido(usuario, id):
    pedido := buscar_do_dono(id, usuario["id"])
    given pedido is void:
        // 404, e nao 403: dizer "existe, mas nao e seu" ja entrega
        // que aquele id existe.
        trigger "nao encontrado"
    yield pedido

action buscar(id):
    yield {"id": id, "dono": 99}

action buscar_do_dono(id, dono):
    p := buscar(id)
    yield p given p["dono"] is dono otherwise void

monitor:
    ver_pedido({"id": 7, "papel": "cliente"}, 1234)
    assert no
handle Error as e:
    out "o pedido de outro dono nao e alcancavel\"""", "lang": "df"},

 {"callout": {"tipo": "atencao", "titulo": "403 ou 404?", "texto": "Responder **403 Forbidden** a um recurso que existe e não é seu confirma que ele existe — e isso já é informação. Para recursos cujo identificador é sequencial ou adivinhável, **404** é a resposta certa: quem não pode ver não descobre nem que existe. Use 403 quando a existência do recurso já é pública e o que falta é permissão."}},

 {"h2": "RBAC"},

 {"p": "Papéis são a forma mais usada, e funcionam bem quando as permissões são **do sistema**. Quando dependem do dado (*este* pedido, *este* tenant), papel sozinho não basta — a checagem tem de descer ao recurso."},

 {"code": """steady PERMISSOES := {
    "leitor": ["pedido:ler"],
    "editor": ["pedido:ler", "pedido:escrever"],
    "admin":  ["pedido:ler", "pedido:escrever", "pedido:apagar",
               "usuario:gerir"]
}

action pode(papel, permissao):
    yield permissao in (PERMISSOES[papel] ?? [])

// O padrao e NEGAR: um papel desconhecido nao ganha nada. A lista
// vazia do '??' e o que garante isso — sem ela, indexar um vault
// sem a chave levantaria, e um 'monitor' mal colocado viraria um
// 'permitido'.
assert pode("admin", "usuario:gerir")
assert pode("leitor", "pedido:apagar") is no
assert pode("papel-que-nao-existe", "pedido:ler") is no

// E a separacao de funcoes: quem aprova nao e quem solicita.
action aprovar(solicitante, aprovador, valor):
    given solicitante is aprovador:
        trigger "quem solicita nao aprova"
    given pode(aprovador["papel"], "pedido:escrever") is no:
        trigger "sem permissao"
    yield {"aprovado": yes, "valor": valor}

monitor:
    ana := {"id": 1, "papel": "editor"}
    aprovar(ana, ana, 10000)
    assert no
handle Error as e:
    out $"recusado: {e.message}\"""", "lang": "df"},

 {"h2": "Capacidades: a outra escola"},

 {"p": "No modelo de **capacidade**, poder não é consultado numa tabela — é **passado**. Quem tem a referência ao recurso pode usá-lo, e quem não tem não consegue nem nomeá-lo. Isso elimina por construção a confusão do *deputado confuso*, em que um componente privilegiado é enganado a agir em nome de outro."},

 {"code": """adopt Arcane.Capacidade as Cap

// 'limites()' devolve a lista em EXECUCAO. Um modulo que
// prometesse contencao sem dizer o que alcanca seria usado onde
// nao pode, e a descoberta viria por incidente.
out $"capacidades deste arquivo: {len(Cap.limites())}"

// A fronteira e o 'adopt': um modulo fora da lista e recusado pelo
// NOME da capacidade que falta — e nao com "erro de import".""", "lang": "df"},

 {"callout": {"tipo": "atencao", "titulo": "O que a capacidade NÃO é — e está no próprio módulo", "texto": "Ela bloqueia a **autoridade ambiente** (o `adopt`), e **não tira o que já foi entregue**. Isso não é limitação de implementação: é o modelo. Numa linguagem de capacidade, poder é o que se **passa**, não o que está no ar — e por isso bloquear o `adopt` é a fronteira certa. Mas a consequência precisa estar clara: **não é um sandbox**. Código que já recebeu um objeto de arquivo continua usando-o. Contenção real é processo separado, contêiner ou VM."}},

 {"h2": "Sandbox — o veredito"},

 {"table": {"head": ["Nível", "Existe aqui?", "O que ele realmente contém"], "rows": [
   ["`Arcane.Capacidade`", "**sim**", "o `adopt`; não contém código já autorizado"],
   ["Restrição por processo", "**parcial** — `P.map_processos`", "isola memória; não isola disco nem rede"],
   ["Contêiner", "**gerado**, não executado", "`dataforge devops` escreve o Dockerfile com `USER forge`"],
   ["VM / microVM", "**não existe**", "é infraestrutura"],
   ["Executar código não confiável", "**não faça**", "não há mecanismo que torne isso seguro aqui"]]}},

 {"callout": {"tipo": "atencao", "titulo": "Não execute código de terceiros no seu processo", "texto": "Não há, nesta linguagem, um modo de execução que torne seguro rodar um `.df` que você não escreveu. Se o requisito for esse — um *playground*, uma automação enviada por usuário —, a contenção tem de vir de fora: contêiner descartável, sem rede, com limite de CPU e memória, e com prazo. Qualquer coisa aquém disso é uma aposta."}},

 {"h2": "Segurança de dependências"},

 {"p": "A cadeia de suprimentos é hoje um dos vetores mais explorados: o código que você não escreveu roda com a mesma autoridade do que você escreveu."},

 {"table": {"head": ["Controle", "Como aqui"], "rows": [
   ["**zero dependência no runtime**", "`dataforge/` usa só a stdlib do Python — a superfície de terceiros é **zero**"],
   ["lockfile **lido**", "`forge.lock` fixa a versão e o sha256, e `install` o honra"],
   ["integridade conferida", "o sha256 do lock é comparado com o que chegou — é o ataque do tarball trocado"],
   ["conflito de versão é **erro**", "duas cópias em versões diferentes geram bug irreproduzível"],
   ["extração recusa `../` e link simbólico", "um pacote não escreve fora da própria pasta"],
   ["tarball reprodutível", "`mtime=0`, uid/gid zerados — sem isso o sha256 mudaria a cada empacotamento e a verificação não significaria nada"],
   ["SBOM", "`dataforge devops sbom`"]]}},

 {"callout": {"tipo": "dica", "titulo": "Um lockfile que ninguém lê não trava nada", "texto": "O `forge.lock` era versionado, carregava o sha256 de cada pacote — e **nenhum caminho de instalação o consultava**. Duas pessoas clonando o mesmo projeto em dias diferentes recebiam árvores diferentes, e a “verificação de integridade” conferia um download contra ele mesmo. Hoje `install` instala o que o lock fixa, `update` reescreve, e `add` move só o que está sendo adicionado. Vale conferir isso em qualquer gerenciador que você use."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/seguranca/ataques",
"title": "Ataques a credenciais",
"description": "Força bruta, credential stuffing, pulverização de senha, bloqueio de conta, atrasos progressivos e limite de taxa — com o que cada defesa quebra.",
"blocos": [
 {"p": "As três formas de atacar um login são diferentes, e a defesa que serve a uma não serve às outras. Confundi-las é como um sistema fica com bloqueio de conta e continua sendo invadido."},

 {"table": {"head": ["Ataque", "O que o atacante tem", "A forma", "O que o detecta"], "rows": [
   ["**Força bruta**", "um usuário", "muitas senhas nele", "tentativas por **conta**"],
   ["**Credential stuffing**", "listas vazadas de usuário+senha", "uma tentativa em cada conta", "taxa por **IP** e por dispositivo"],
   ["**Pulverização**", "muitos usuários", "uma senha comum em todos", "taxa **global** de falhas"]]}},

 {"callout": {"tipo": "atencao", "titulo": "Por que bloquear a conta não resolve — e cria um problema", "texto": "Bloquear após N erros protege contra força bruta e **cria uma negação de serviço**: quem ataca passa a errar de propósito para trancar a conta alheia. Contra *credential stuffing* ele não faz nada — lá é **uma** tentativa por conta, e o limite nunca é atingido. A defesa que cobre os três é **atraso progressivo por conta** somado a **limite de taxa por origem**."}},

 {"h2": "Atraso progressivo"},

 {"p": "A espera dobra a cada bloqueio, até um teto. Um limite fixo é contornado esperando o período; o crescimento torna a força bruta cara sem nunca trancar de vez quem só errou a senha."},

 {"code": """adopt Arcane.Seguranca as Seg

// Depois de 3 falhas, espera 30s. Depois de mais 3, 60s. Depois,
// 120s — ate o teto. 'sucesso()' zera: sem isso, quem erra duas
// vezes por mes fica perto do bloqueio para sempre.
porta := Seg.tentativas(limite := 3, base := 30.0, teto := 3600.0)

cycle i from 1 to 2:
    r := porta.falha("ana@loja.com")
    out $"   falha {i}: faltam {r['restantes']} tentativa(s)"

terceira := porta.falha("ana@loja.com")
assert terceira["bloqueado"]
out $"   bloqueado por {terceira['segundos']}s"

// E o estado e POR CHAVE: outra conta nao e afetada.
assert porta.bloqueado("bruno@loja.com") is no

// O login certo zera a contagem.
porta.sucesso("ana@loja.com")
assert porta.bloqueado("ana@loja.com") is no

out "progressivo por conta, e nao um bloqueio duro\"""", "lang": "df"},

 {"h2": "Limite de taxa"},

 {"p": "O limitador usa **balde de fichas**: o balde enche continuamente, e não de uma vez por janela. Com janela fixa, um cliente gasta o limite no último segundo de uma e no primeiro da seguinte — o dobro do limite num instante, que é exatamente o que se queria evitar."},

 {"code": """adopt Arcane.Seguranca as Seg

// 5 tentativas por minuto, por origem.
porta := Seg.limitador(5, periodo := 60.0)

cycle i from 1 to 5:
    assert porta.permitir("203.0.113.7")

assert porta.permitir("203.0.113.7") is no

// 'espera' e o valor que vai no cabecalho 'Retry-After'.
out $"   Retry-After: {porta.espera('203.0.113.7')}s"

// Outra origem nao e afetada — a chave e o que separa.
assert porta.permitir("198.51.100.4")""", "lang": "df"},

 {"callout": {"tipo": "atencao", "titulo": "O limitador é por processo, e isso muda a conta", "texto": "Ele vive na memória. Num servidor com quatro processos, cada um tem o seu balde, e **o limite efetivo é quatro vezes maior**. Para limite compartilhado é preciso um armazém comum (Redis, banco), e este módulo não pretende ser nenhum dos dois — mas quem calibra o número precisa saber disso, senão o limite que está escrito não é o que acontece."}},

 {"h2": "A camada completa de um login"},

 {"code": """adopt Arcane.Seguranca as Seg
adopt Arcane.Crypto as Crypto

steady POR_IP := Seg.limitador(20, periodo := 60.0)
steady POR_CONTA := Seg.tentativas(limite := 5, base := 30.0)

action entrar(email, senha, ip, guardada):
    // 1. Taxa por origem — pega credential stuffing e pulverizacao.
    given POR_IP.permitir(ip) is no:
        yield {"ok": no, "motivo": "muitas tentativas", "espere": POR_IP.espera(ip)}

    // 2. Atraso progressivo por conta — pega forca bruta.
    given POR_CONTA.bloqueado(email):
        yield {"ok": no, "motivo": "conta temporariamente bloqueada",
               "espere": POR_CONTA.falta(email)}

    // 3. A conferencia em si, em tempo constante por dentro.
    given Crypto.verify_password(senha, guardada) is no:
        POR_CONTA.falha(email)
        // A MESMA mensagem para usuario inexistente e senha errada:
        // distingui-las entrega quais contas existem.
        yield {"ok": no, "motivo": "usuario ou senha invalidos"}

    POR_CONTA.sucesso(email)
    yield {"ok": yes}

guardada := Crypto.hash_password("uma senha bem forte 2026")

assert entrar("ana@loja.com", "errada", "203.0.113.7", guardada)["ok"] is no
assert entrar("ana@loja.com", "uma senha bem forte 2026", "203.0.113.7", guardada)["ok"]

out "taxa por origem, atraso por conta, mensagem unica\"""", "lang": "df"},

 {"h2": "Enumeração de usuários"},

 {"p": "Se “usuário não existe” e “senha incorreta” são respostas diferentes, o atacante descobre **quais contas existem** antes de tentar qualquer senha — e passa a usar as listas vazadas só onde elas valem."},

 {"table": {"head": ["Onde vaza", "Como fechar"], "rows": [
   ["mensagem de erro do login", "a mesma frase para os dois casos"],
   ["**tempo** de resposta", "derive a senha mesmo quando o usuário não existe"],
   ["cadastro (“e-mail já usado”)", "responda sempre igual e informe por e-mail"],
   ["redefinição de senha", "“se houver conta, enviamos um link”"],
   ["código HTTP diferente", "o mesmo 401 nos dois casos"]]}},

 {"callout": {"tipo": "dica", "titulo": "O vazamento por tempo é o que quase todo mundo esquece", "texto": "Se o usuário não existe, o código costuma voltar **sem** derivar a senha — e a resposta chega em 1 ms em vez de 45 ms. Isso é tão informativo quanto a mensagem. A correção é conferir contra um hash descartável quando a conta não existe, de modo que os dois caminhos custem o mesmo."}},

 {"h2": "Outras defesas, e o veredito"},

 {"table": {"head": ["Defesa", "Estado aqui", "Observação"], "rows": [
   ["senha vazada recusada no cadastro", "**existe** — `Seg.vazada`", "k-anonimato; a senha não sai da máquina"],
   ["CAPTCHA", "**não existe**", "é serviço de terceiro; ponha-o depois de N falhas, não antes"],
   ["MFA", "**existe** — TOTP", "a defesa que sobrevive à senha vazada"],
   ["impressão digital de dispositivo", "**não existe**", "tem implicação de privacidade; avalie antes"],
   ["alerta de login novo", "seu e-mail + `Seg.auditoria`", "detecção, e não prevenção"],
   ["bloqueio por geografia", "**não existe**", "alta taxa de falso positivo"]]}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/seguranca/ferramentas",
"title": "As ferramentas",
"description": "Detecção de segredos, linter de segurança, análise estática, verificações em execução e trilha de auditoria — o que cada uma pega, e o que ela não pega.",
"blocos": [
 {"p": "Uma ferramenta de segurança vale pelo que ela **pega** e pelo que ela **não acusa por engano**. A segunda metade decide se ela continua ligada: um alarme falso no caminho comum ensina a ignorar a saída, e uma ferramenta ignorada não protege nada."},

 {"h2": "`dataforge seguranca`"},

 {"p": "Duas varreduras sobre cada arquivo: **segredos por formato** e **dez regras sintáticas**. Ela lê `.df`, `.env`, `.json`, `.toml`, `.yml`, `.sh`, `.ts` e `.md` — um segredo vaza do arquivo de configuração muito mais do que do código."},

 {"code": """// $ dataforge seguranca .
//
// ALTO  src/config.df:12:14  [segredo-no-codigo]
//         Stripe escrito no arquivo (sk_l************).
//         dica: Leia de 'OS.env' e ROTACIONE a chave que ja esteve aqui.
//
// MEDIO src/relatorio.df:88:5  [md5-ou-sha1]
//         MD5 e SHA-1 estao quebrados para assinatura.
//         dica: Use 'sha256'. Para senha, 'hash_password'.
//
// 2 achado(s) em 143 arquivo(s) — 1 de gravidade alta

// --strict        reprova a esteira de CI
// --json          vira entrada de outra ferramenta
// --so=alto       esconde os medios""", "lang": "df"},

 {"table": {"head": ["Regra", "Gravidade", "O que ela acusa"], "rows": [
   ["`segredo-no-codigo`", "alto", "chave de API, token ou bloco de chave privada no arquivo"],
   ["`sql-concatenado`", "alto", "SQL montado com interpolação ou concatenação"],
   ["`shell-com-texto`", "alto", "linha de shell montada com interpolação"],
   ["`senha-sem-derivacao`", "alto", "senha guardada com resumo simples"],
   ["`verificacao-desligada`", "alto", "`verificar := no` no caminho de produção"],
   ["`md5-ou-sha1`", "médio", "MD5 e SHA-1 para assinatura"],
   ["`html-sem-escape`", "médio", "HTML montado com interpolação"],
   ["`aleatorio-fraco`", "médio", "`randint` para token, senha ou chave"],
   ["`comparacao-de-segredo`", "médio", "comparar segredo com `is` vaza tempo"],
   ["`caminho-de-fora`", "médio", "caminho montado com valor que veio de fora"]]}},

 {"callout": {"tipo": "atencao", "titulo": "O que a varredura CALA, e por quê", "texto": "Sem três silêncios ela apontava **19 vezes** neste repositório, e as 19 eram falso alarme — inclusive os exercícios que *ensinam* a não escrever token no arquivo. Ela cala sobre: **(1)** valor que se anuncia como exemplo (`\"123456:AAHexemplo\"`); **(2)** **JWT com papel `anon`** — a chave `anon` do Supabase vai no pacote do navegador de propósito, e só o conteúdo a separa da `service_role`, então o papel é lido de dentro do próprio token; **(3)** credencial de `localhost` e dos domínios reservados da RFC 2606."}},

 {"code": """adopt Arcane.Seguranca as Seg

// A mesma varredura, chamada de dentro de um programa — e util num
// gancho de pre-commit ou antes de gravar um log.
fonte := "chave := \\"ghp_abcdefghijklmnopqrstuvwxyz0123456789\\""

achados := Seg.procurar_segredos(fonte)
assert len(achados) is 1
out $"{achados[0]['tipo']} na linha {achados[0]['linha']}: {achados[0]['trecho']}"

// O trecho ja vem MASCARADO: um relatorio de vazamento que imprime
// o segredo inteiro e mais um lugar onde ele esta.
assert "abcdefghijkl" not in achados[0]["trecho"]

// E 'redigir' devolve o texto com os segredos trocados no lugar,
// para gravar um corpo de pedido no log sem que o log vire o
// proximo vazamento.
assert "abcdefghijkl" not in Seg.redigir(fonte)""", "lang": "df"},

 {"callout": {"tipo": "dica", "titulo": "O escape, quando o achado é deliberado", "texto": "`// df: permitir segredo-no-codigo` na linha, ou na de cima, silencia **aquela** regra ali — e vale em qualquer arquivo, não só num `.df`. A regra tem de ser **nomeada**: um `permitir` solto esconderia o próximo achado, que ninguém pediu para esconder. Um analisador sem escape obriga a escolher entre conviver com o alarme e desligar tudo, e a segunda é o que acontece."}},

 {"h2": "Análise estática"},

 {"table": {"head": ["Comando", "O que ele pega que importa para segurança"], "rows": [
   ["`dataforge check`", "nome, aridade e tipo — **inclusive entre arquivos**; campo inexistente com sugestão"],
   ["`dataforge check --strict`", "avisos viram erros; é o que vai na esteira"],
   ["`dataforge lint`", "variável escrita e nunca lida, ramo redundante"],
   ["`dataforge seguranca`", "as duas varreduras acima"],
   ["`dataforge oop`", "acoplamento e coesão — complexidade é onde a falha se esconde"],
   ["`dataforge deps`", "o grafo de imports, e o ciclo"]]}},

 {"callout": {"tipo": "atencao", "titulo": "O aviso que é o único bug caro que nem o check nem o lint mencionavam", "texto": "`escrita-concorrente`: o `check` avisa quando um `thread`, `parallel` **ou `route`** escreve num nome que vem de fora. **A rota é o caso que mais importa** — o Kiln usa `ThreadingHTTPServer`, cada pedido roda numa thread, e ali a concorrência é *invisível* para quem escreve. Medido: seis pedidos simultâneos numa rota que lê, espera e escreve entregaram **1 de 6**."}},

 {"h2": "Verificações em execução"},

 {"p": "O que a análise estática não consegue provar continua sendo conferido quando o programa roda — e o erro tem nome, linha e dica."},

 {"table": {"head": ["Confere", "O erro"], "rows": [
   ["tipo declarado, em toda fronteira", "`TypeError`"],
   ["índice fora do alcance", "`IndexError`"],
   ["chave que não existe", "`KeyError`"],
   ["membro de `void`", "`NullReferenceError`"],
   ["refinamento de um `type … where`", "o erro nomeia o tipo, não a base"],
   ["invariante de um agregado", "`InvariantError`, e o comando é desfeito"],
   ["limite de bloco e ponteiro nulo", "`BufferOverflowError`, `NullPointerError`"],
   ["entrada hostil recusada", "`UnsafeInputError`"]]}},

 {"h2": "Trilha de auditoria"},

 {"p": "Responsabilização exige um registro que não possa ser alterado sem deixar marca. A trilha encadeia o resumo do registro anterior em cada registro."},

 {"code": """adopt Arcane.Seguranca as Seg
adopt Arcane.OS as OS
adopt Arcane.IO as IO

caminho := $"{OS.temp_dir()}/df-auditoria-{randint(100000, 999999)}.log"
livro := Seg.auditoria(caminho)

livro.registrar("login", {"ip": "203.0.113.7"}, quem := "ana")
livro.registrar("apagou_pedido", {"pedido": 42}, quem := "ana")
livro.registrar("exportou_relatorio", {"linhas": 1200}, quem := "bruno")

r := livro.conferir()
assert r["ok"]
out $"{r['registros']} registros, cadeia fecha"

// Os dados passam por 'redigir' ANTES de serem gravados: uma trilha
// de auditoria e exatamente o tipo de arquivo que acaba anexado a
// um chamado.
livro.registrar("deploy", {"token": "ghp_abcdefghijklmnopqrstuvwxyz01"})
cycle linha in livro.ler():
    assert "abcdefghijkl" not in str(linha)

out "o segredo nao entra nem na propria auditoria"

IO.delete(caminho)""", "lang": "df"},

 {"callout": {"tipo": "atencao", "titulo": "A cadeia dá evidência, e não impedimento", "texto": "Nada num arquivo local impede alguém com acesso de editá-lo. O que a cadeia dá é que **alterar ou apagar uma linha faz a próxima deixar de fechar**, e `conferir()` diz em qual. Para que a evidência valha, a trilha tem de ser copiada para **fora da máquina que a escreve** — e isso está aqui, na documentação, porque o código não tem como garantir."}},

 {"h2": "A esteira completa"},

 {"code": """// .github/workflows/ci.yml — as cinco que reprovam de verdade
//
//   dataforge check . --strict
//   dataforge lint .
//   dataforge seguranca . --strict
//   dataforge test tests/ --cobertura --minimo=80
//   dataforge devops doctor
//
// E o gancho local, que pega antes de o segredo sair da maquina:
//
//   # .git/hooks/pre-commit
//   #!/bin/sh
//   dataforge seguranca . --strict || exit 1""", "lang": "df"},

 {"callout": {"tipo": "dica", "titulo": "O gancho local não substitui a esteira", "texto": "Um gancho de pré-commit pode ser pulado com `--no-verify`, e é pulado. Ele existe para dar a resposta **rápida** a quem está escrevendo; quem **reprova** é o CI, que não tem como ser pulado. Os dois rodam o mesmo comando de propósito: se divergirem, o local passa a aprovar o que o remoto recusa, e a confiança no primeiro acaba."}},
]},
]
