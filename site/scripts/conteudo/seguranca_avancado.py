# -*- coding: utf-8 -*-
"""Segurança da informação — as dez páginas que faltavam.

As onze páginas de `seguranca_informacao.py` cobrem o currículo: CIA,
autenticação, autorização, criptografia, detecção. Estas descem na
prática: o OWASP mapeado para a linguagem, a API, os cabeçalhos da web,
os segredos, o log, a LGPD, a anonimização, a integridade, a cadeia de
suprimentos e a resposta a incidente.

Duas delas vêm com módulo novo na linguagem — `Arcane.Privacidade` e
`Arcane.Integridade` — e todo bloco `df` aqui roda.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/seguranca/owasp",
"title": "OWASP Top 10 na linguagem",
"description": "As dez categorias de 2021, e o que a linguagem, a biblioteca e as ferramentas fazem com cada uma.",
"blocos": [
 {"p": "O OWASP Top 10 é a lista das categorias de falha que mais aparecem em aplicações web. Ela não é um checklist — é um mapa de onde procurar. Para cada categoria, o que existe aqui para ajudar, e o que continua sendo decisão de quem escreve."},
 {"table": {"head": ["Categoria (2021)", "O que existe aqui", "O que continua sendo seu"], "rows": [
   ["**A01** Controle de acesso quebrado", "`Arcane.Politica` — negar por padrão, negar vence permitir, a decisão diz quem decidiu", "conferir o **dono** do objeto em cada rota (ver [API](/docs/seguranca/api))"],
   ["**A02** Falhas criptográficas", "scrypt em `hash_password`, ChaCha20-Poly1305, `Arcane.Chaves` com rotação", "não inventar esquema; TLS no proxy"],
   ["**A03** Injeção", "`?` no SQL, escape por destino, templates que escapam, `escapar_shell`", "não montar SQL com `$\"…\"`"],
   ["**A04** Design inseguro", "`Arcane.Dominio` com invariantes cobradas", "modelar ameaças antes — [STRIDE](/docs/seguranca/ameacas)"],
   ["**A05** Configuração insegura", "`Kiln.secure_headers()`, `dataforge devops doctor`", "ligar HSTS quando o TLS existir"],
   ["**A06** Componentes vulneráveis", "lockfile com sha256, SBOM, `dataforge outdated`", "atualizar — [Cadeia](/docs/seguranca/cadeia)"],
   ["**A07** Falhas de autenticação", "`tentativas` (bloqueio progressivo), TOTP, `forca_da_senha`, `vazada`", "a mesma resposta para usuário e senha errados"],
   ["**A08** Integridade de software e dados", "`Arcane.Integridade`, tarball reprodutível, webhook assinado", "assinar o que se publica"],
   ["**A09** Falhas de log e monitoramento", "`auditoria` encadeada, `escapar_log`, `Arcane.Deteccao`", "alguém olhar os alertas"],
   ["**A10** SSRF", "`url_segura` resolve o nome antes de responder", "usar o IP que ela devolve"]]}},
 {"code": """adopt Arcane.Seguranca as S

// A03 — o nome que vira SQL, o texto que vira shell, a celula que vira formula
assert S.escapar_csv("=HYPERLINK(\\"x\\")").startswith("'")
assert "\\n" not in S.escapar_log("ok\\nFALSO login admin")

// A07 — quanto vale esta senha?
assert S.forca_da_senha("123456")["nota"] smaller S.forca_da_senha("cavalo-bateria-grampo-azul")["nota"]

// A10 — o endereco interno e recusado ANTES da requisicao, e levanta:
// devolver "nao" deixaria quem esqueceu de conferir seguir adiante.
monitor:
    S.url_segura("http://127.0.0.1/admin")
    assert no
handle Error as e:
    out e.message
out "quatro categorias, conferidas\"""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "A varredura acha o que está escrito", "texto": "`dataforge seguranca` aplica regras sintáticas — SQL concatenado, shell com interpolação, MD5 para assinatura — e acha segredo pelo formato. Ela não prova que a aplicação é segura: acha o que está **escrito** de um jeito perigoso, que é a classe de falha mais barata de corrigir."}},
 {"p": "Continue em [Segurança de API](/docs/seguranca/api) e [Web](/docs/seguranca/web)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/seguranca/api",
"title": "Segurança de API",
"description": "O OWASP API Top 10, e o BOLA — a falha mais comum de uma API — escrita e corrigida.",
"blocos": [
 {"p": "A falha número um de API não é injeção nem criptografia: é **autorização por objeto** (BOLA). A rota confere que o usuário está logado, e não que o pedido `/pedidos/43` é **dele**. Trocar o número na URL mostra o pedido de outra pessoa."},
 {"code": """adopt Kiln

pedidos := {
    "42": {"id": "42", "dono": "ana", "total": 120},
    "43": {"id": "43", "dono": "bia", "total": 900}
}

// Quem e o usuario sai do TOKEN, e nunca do corpo ou da query.
// O Kiln entrega os cabecalhos em minusculas, como o HTTP/2 os escreve.
action usuario_de(cabecalhos):
    yield {"t-ana": "ana", "t-bia": "bia"}[cabecalhos["authorization"] ?? ""] ?? void

server api on 0:
    route GET "/pedidos/:id":
        quem := usuario_de(headers)
        given quem is void:
            respond 401 json {"erro": "entre primeiro"}
        p := pedidos[params["id"]] ?? void
        // 404 tambem para o pedido de OUTRA pessoa: 403 confirmaria que existe.
        given p is void or p["dono"] isnt quem:
            respond 404 json {"erro": "pedido nao encontrado"}
        respond json p

assert Kiln.test(api, "GET", "/pedidos/42", void, {"Authorization": "t-ana"})["status"] is 200
assert Kiln.test(api, "GET", "/pedidos/43", void, {"Authorization": "t-ana"})["status"] is 404
assert Kiln.test(api, "GET", "/pedidos/42")["status"] is 401
out "BOLA fechado: o dono e conferido por objeto\"""", "lang": "df"},
 {"h2": "O OWASP API Top 10 (2023)"},
 {"table": {"head": ["Categoria", "A pergunta em cada rota"], "rows": [
   ["API1 — autorização por objeto (BOLA)", "este objeto é **deste** usuário?"],
   ["API2 — autenticação quebrada", "o token é conferido, tem prazo, e o erro não diz qual parte errou?"],
   ["API3 — autorização por propriedade", "o corpo pode mudar `papel` ou `saldo`? — aceite uma lista de campos"],
   ["API4 — consumo sem limite", "há `rate_limit`, `body_limit` e paginação com teto?"],
   ["API5 — autorização por função", "a rota de administração confere o papel, e não só o login?"],
   ["API6 — fluxos de negócio sensíveis", "comprar 500 ingressos por script é possível?"],
   ["API7 — SSRF", "a URL que o cliente manda passa por `url_segura`?"],
   ["API8 — configuração insegura", "`secure_headers`, CORS com origem nomeada, erro sem traceback"],
   ["API9 — inventário", "há uma rota esquecida de uma versão antiga? `dataforge api` lista todas"],
   ["API10 — consumo inseguro de APIs", "a resposta do terceiro é validada como entrada de fora?"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Mass assignment (API3)", "texto": "`atualizar(usuario, body)` com o corpo inteiro deixa o cliente mandar `{\"papel\": \"admin\"}`. A correção é a mesma da minimização de dados: uma lista de **permitidos** — `Privacidade.minimizar(body, [\"nome\", \"email\"])` — e não de proibidos."}},
 {"p": "Continue em [Web](/docs/seguranca/web) e [Autorização](/docs/seguranca/autorizacao)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/seguranca/web",
"title": "Segurança na web",
"description": "Cabeçalhos, CSP, CORS, CSRF, cookie, limite de taxa e de corpo — o que o Kiln liga e o que é decisão sua.",
"blocos": [
 {"p": "O navegador tem defesas poderosas — e **nenhuma** vem ligada. Elas dependem de cabeçalhos que o servidor manda. O Kiln traz cada uma como middleware, e a lista abaixo é o mínimo de um site público."},
 {"code": """adopt Kiln

server site on 0:
    middleware Kiln.rate_limit(60, 60)        // 60 pedidos por minuto, por IP
    middleware Kiln.body_limit(1048576)       // 1 MB de corpo, no maximo
    after Kiln.secure_headers()               // nosniff, frame, CSP, referrer
    route GET "/":
        respond json {"ok": yes}

r := Kiln.test(site, "GET", "/")
assert r["headers"]["X-Frame-Options"] is "DENY"
assert r["headers"]["X-Content-Type-Options"] is "nosniff"
assert "default-src 'self'" in r["headers"]["Content-Security-Policy"]
out "os cabecalhos sairam\"""", "lang": "df"},
 {"table": {"head": ["Defesa", "No Kiln", "Contra"], "rows": [
   ["`X-Frame-Options` / `frame-ancestors`", "`secure_headers(frame := …)`", "clickjacking: sua página num `<iframe>` de outro"],
   ["`Content-Security-Policy`", "`secure_headers(csp := …)`", "o XSS que escapou do escape — o script injetado não roda"],
   ["`X-Content-Type-Options: nosniff`", "ligado", "um `.txt` com HTML executado como página"],
   ["`Strict-Transport-Security`", "`secure_headers(hsts := yes)`", "o primeiro acesso por http interceptado"],
   ["CORS com origem **nomeada**", "`Kiln.cors([\"https://app.exemplo.com\"])`", "outro site lendo a resposta com o cookie do usuário"],
   ["CSRF", "`Kiln.csrf(segredo)` + `csrf_token`", "o formulário de outro site postando no seu"],
   ["cookie `HttpOnly`, `SameSite`, `Secure`", "`Kiln.cookie(…)` — `HttpOnly` e `Lax` por padrão", "o script que lê a sessão; o POST de outra origem"],
   ["limite de taxa e de corpo", "`rate_limit`, `body_limit`", "força bruta; o corpo de 2 GB que derruba o processo"]]}},
 {"callout": {"tipo": "atencao", "titulo": "HSTS desligado por padrão — de propósito", "texto": "Ele diz ao navegador *“só me acesse por https pelos próximos meses”*, e o navegador **obedece** mesmo que o https ainda não exista. Mandado cedo demais, tira o site do ar para quem já o visitou, sem como voltar atrás a tempo. Ligue quando o certificado estiver de pé."}},
 {"callout": {"tipo": "atencao", "titulo": "`cors(\"*\")` com credenciais", "texto": "Origem `*` é para API pública e sem cookie. Com sessão, a origem precisa ser nomeada — senão qualquer site que o usuário abrir lê as respostas como se fosse ele."}},
 {"p": "O `rate_limit` conta **por processo**: com três réplicas, o limite real é o triplo. Ver [Kiln em produção](/docs/kiln/producao)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/seguranca/segredos",
"title": "Gestão de segredos",
"description": "Onde o segredo mora, como ele não aparece em log, como é achado no código — e o que fazer quando vaza.",
"blocos": [
 {"p": "Um segredo tem quatro momentos: onde ele **mora**, como ele **passa** pelo programa, como ele **não aparece** onde não devia, e o que se faz quando ele **vaza**. Cada um tem uma ferramenta aqui."},
 {"table": {"head": ["Momento", "Onde", "Ferramenta"], "rows": [
   ["mora", "variável de ambiente, cofre do provedor, KMS — **nunca** o repositório", "`OS.env`, `.env` no `.gitignore`"],
   ["passa", "dentro de um `Segredo`, que não se imprime", "`Seguranca.segredo(valor)` → `revelar()`"],
   ["não aparece", "log, erro, relatório", "`redigir(texto)`, `mascarar_no_log` no CI"],
   ["vaza", "commit, log público, print de tela", "`procurar_segredos`, `dataforge seguranca` — e **rotacionar**"]]}},
 {"code": """adopt Arcane.Seguranca as S

s := S.segredo("sk_live_" + "x" * 24, "stripe")
out s                          // nao aparece
assert "sk_live" not in str(s)
assert s.revelar().startswith("sk_live")   // so onde for preciso — e aparece na revisao

log := "conectando com postgres://app:s3nh4-forte@db:5432/loja"
limpo := S.redigir(log)
out limpo
assert "s3nh4-forte" not in limpo

achados := S.procurar_segredos("chave := \\"ghp_" + "R8tK2mQ9vX4pL7nZ3wB6yH1cJ5dF0sG8aE2u" + "\\"")
assert len(achados) is 1
out $"achado: {achados[0]['tipo']} na linha {achados[0]['linha']}\"""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Um segredo commitado é um segredo vazado", "texto": "Apagar no commit seguinte não o tira do histórico, e um repositório público é espelhado em minutos. A única resposta é **rotacionar**: gerar outro, trocar onde é usado, revogar o velho. `Arcane.Chaves` foi desenhado para que rotacionar não quebre o que a chave velha cifrou."}},
 {"p": "Antes do commit: [pre-commit](/docs/devops/ambiente-de-dev). O ciclo da chave: [Criptografia e chaves](/docs/seguranca/criptografia)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/seguranca/logs",
"title": "Log seguro e auditoria",
"description": "O log que não pode ser forjado, que não guarda dado pessoal, e a trilha de auditoria que denuncia a linha apagada.",
"blocos": [
 {"p": "O log tem dois inimigos opostos: o que **falta** (o incidente sem rastro) e o que **sobra** (o CPF, a senha, o token gravados em texto). E um terceiro, mais sutil: o log **forjado**, em que um campo com quebra de linha acrescenta um evento que nunca aconteceu."},
 {"code": """adopt Arcane.Seguranca as S
adopt Arcane.OS as OS
adopt Arcane.IO as IO

// 1. Forjar: um nome de usuario com '\\n' acrescentaria uma linha inteira.
nome := "ana\\n2026-09-22 INFO login ok usuario=admin"
linha := $"login falhou usuario={S.escapar_log(nome)}"
assert len(linha.lines()) is 1

// 2. Sobrar: o dado pessoal sai mascarado.
evento := "pedido de ana@exemplo.com, cpf 529.982.247-25"
out S.mascarar_pii(evento)
assert "529.982.247-25" not in S.mascarar_pii(evento)

// 3. Apagar: a auditoria e encadeada — cada registro leva o resumo do anterior.
pasta := $"{OS.temp_dir()}/df-aud-{randint(100000, 999999)}"
IO.mkdir(pasta)
a := S.auditoria($"{pasta}/trilha.log")
a.registrar("login", {"usuario": "ana"}, "ana")
a.registrar("exportou", {"linhas": 120}, "ana")
assert a.conferir()["ok"]
IO.remove_tree(pasta)
out "log de uma linha, sem PII, e a trilha integra\"""", "lang": "df"},
 {"table": {"head": ["Registre", "Não registre"], "rows": [
   ["quem, o quê, quando, de onde, o resultado", "senha, token, número de cartão, CPF inteiro"],
   ["a falha de autenticação e de autorização", "o corpo inteiro do pedido"],
   ["a mudança de permissão e de configuração", "o dado de saúde, o dado de criança"],
   ["o id da requisição, para cruzar serviços", "a chave de sessão"]]}},
 {"callout": {"tipo": "nota", "titulo": "Encadeada não é imutável", "texto": "Cada registro da `auditoria` carrega o resumo do anterior: apagar ou editar uma linha no meio quebra a corrente, e `conferir()` diz onde. Quem apaga o arquivo **inteiro** não é detectado por ele — por isso a trilha vai também para fora da máquina (um coletor, um bucket com retenção)."}},
 {"p": "Continue em [Detecção](/docs/seguranca/deteccao) e [Incidentes](/docs/seguranca/incidentes)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/seguranca/privacidade",
"title": "LGPD na prática",
"description": "Finalidade, necessidade, consentimento, retenção e os direitos do titular — como operações sobre dado, com Arcane.Privacidade.",
"blocos": [
 {"p": "A LGPD fala em princípios — finalidade, adequação, necessidade, transparência, segurança (art. 6º). No código eles viram perguntas concretas: **para que** este dado é usado, **quais campos** a finalidade precisa, **até quando** ele pode ficar, e **onde** ele mora quando o titular pede para ver ou apagar. `Arcane.Privacidade` torna cada resposta registrável."},
 {"callout": {"tipo": "atencao", "titulo": "Não é parecer jurídico", "texto": "Este módulo não decide a base legal de um tratamento nem substitui o encarregado (DPO). Ele torna as decisões **registráveis e conferíveis** — que é o que se pede num incidente ou numa fiscalização."}},
 {"h2": "Consentimento por finalidade"},
 {"code": """adopt Arcane.Privacidade as P

c := P.consentimentos()
c.conceder("ana", "nota-fiscal", "1", 100)
c.conceder("ana", "marketing", "1", 100)
c.revogar("ana", "marketing", 500)

// Uma finalidade nao autoriza outra.
assert c.pode("ana", "nota-fiscal", "", 600)
assert not c.pode("ana", "pesquisa", "", 600)

// A revogacao vale dali em diante — e o passado continua respondivel.
assert c.pode("ana", "marketing", "", 300)
assert not c.pode("ana", "marketing", "", 600)
assert len(c.historico("ana")) is 3
out c.finalidades("ana")""", "lang": "df"},
 {"h2": "Necessidade e retenção"},
 {"code": """adopt Arcane.Privacidade as P

clientes := [
    {"id": 1, "nome": "Ana", "cpf": "529.982.247-25", "cidade": "Recife", "criado": "2019-01-10"},
    {"id": 2, "nome": "Bia", "cpf": "111.444.777-35", "cidade": "Natal", "criado": "2026-08-01"}
]

// O relatorio de vendas por cidade nao precisa de nome nem de CPF.
relatorio := P.minimizar(clientes, ["id", "cidade"])
assert "cpf" not in relatorio[0]

// Cinco anos de retencao: o que passou do prazo, e o que nao diz quando nasceu.
agora := 1790000000
vencidos := P.vencidos(clientes, "criado", 5 * 365, agora)
assert len(vencidos) is 1 and vencidos[0]["id"] is 1
out $"{len(vencidos)} registro(s) a eliminar\"""", "lang": "df"},
 {"h2": "Acesso e eliminação — em todo lugar"},
 {"code": """adopt Arcane.Privacidade as P

banco := {"ana": {"email": "ana@exemplo.com"}}
newsletter := ["ana@exemplo.com"]

t := P.titulares()
t.registrar("banco", lambda tit: banco[tit] ?? void, lambda tit: pop(banco, tit))
t.registrar("newsletter",
    lambda tit: [e cycle e in newsletter given e.startswith(tit)],
    lambda tit: newsletter.remove("ana@exemplo.com"))

copia := t.exportar("ana")
assert copia["completo"] and copia["dados"]["banco"]["email"] is "ana@exemplo.com"

r := t.esquecer("ana")
assert r["completo"] and r["apagados"] is ["banco", "newsletter"]
assert "ana" not in banco and len(newsletter) is 0
out "acesso e eliminacao em todo lugar registrado\"""", "lang": "df"},
 {"table": {"head": ["Decisão", "Sem ela"], "rows": [
   ["consentimento **por finalidade**, com versão do termo", "o aceite da nota fiscal vira autorização de marketing"],
   ["a revogação acrescenta, não apaga", "não se prova que havia consentimento no dia do envio"],
   ["minimizar por lista de **permitidos**", "o campo novo (o CPF de ontem) sai no relatório sem ninguém decidir"],
   ["o registro **sem data** é vencido", "o que não diz quando nasceu fica para sempre"],
   ["o pedido do titular relata **falhas**", "o dado apagado em nove de onze lugares, e a resposta *“feito”*"]]}},
 {"p": "Continue em [Anonimização](/docs/seguranca/anonimizacao) e [Arcane.Privacidade](/docs/biblioteca/privacidade)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/seguranca/anonimizacao",
"title": "Pseudonimizar, anonimizar, medir",
"description": "Por que um hash de CPF não protege, o que é k-anonimato, e a contagem com privacidade diferencial.",
"blocos": [
 {"p": "Três técnicas que o código costuma confundir, e a lei não: **pseudonimizar** troca o identificador por um apelido que só volta com uma chave (o dado continua pessoal); **anonimizar** remove a possibilidade de reidentificar (o dado deixa de ser pessoal — art. 12); e **publicar agregados** com ruído protege quem está nos números."},
 {"h2": "O hash sem chave não protege"},
 {"code": """adopt Arcane.Privacidade as P
adopt Arcane.Crypto as Crypto

cpf := "529.982.247-25"

// ERRADO: sha256 do CPF. Sao so 10^9 CPFs — um laptop calcula todos numa tarde.
fraco := Crypto.sha256(cpf)

// CERTO: HMAC com uma chave que mora FORA da base, por finalidade.
chave := "vem-do-ambiente-e-nao-da-base-x"
vendas := P.pseudonimizar(cpf, chave, "vendas")
rh := P.pseudonimizar(cpf, chave, "rh")
assert vendas is P.pseudonimizar(cpf, chave, "vendas")   // estavel: as juncoes funcionam
assert vendas isnt rh                                     // cruzar os dois exige a chave
out vendas""", "lang": "df"},
 {"h2": "Tirar o nome não anonimiza"},
 {"code": """adopt Arcane.Privacidade as P

atendimentos := [
    {"cep": "01310-100", "idade": 34, "diagnostico": "A"},
    {"cep": "01310-200", "idade": 36, "diagnostico": "B"},
    {"cep": "04567-000", "idade": 52, "diagnostico": "C"},
    {"cep": "04567-111", "idade": 58, "diagnostico": "B"}
]

antes := P.k_anonimato(atendimentos, ["cep", "idade"])
out $"k = {antes['k']}: alguem esta sozinho numa combinacao"
assert antes["k"] is 1

generalizado := atendimentos >> morph a: {
    "cep": P.generalizar(a["cep"], "cep", 2),
    "idade": P.generalizar(a["idade"], "idade", 2),
    "diagnostico": a["diagnostico"]}
depois := P.k_anonimato(generalizado, ["cep", "idade"])
assert depois["k"] is 2
out $"depois de generalizar: k = {depois['k']}\"""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "k-anonimato não basta sozinho", "texto": "Se os dois do mesmo grupo têm o **mesmo** diagnóstico, saber o grupo revela o diagnóstico (ataque de homogeneidade). k-anonimato mede a primeira porta; a diversidade do atributo sensível dentro de cada grupo é a segunda — confira as duas antes de publicar."}},
 {"h2": "Publicar uma contagem"},
 {"code": """adopt Arcane.Privacidade as P

// "3 casos no bairro" identifica os tres. Com ruido de Laplace, a presenca
// ou ausencia de UMA pessoa muda pouco o numero publicado.
publicado := P.contagem_privada(3, 0.5)
assert publicado bigger_eq 0
out $"publicado: {publicado} (o valor real nao sai)\"""", "lang": "df"},
 {"table": {"head": ["ε (epsilon)", "Protege", "Erra"], "rows": [
   ["0,1", "muito", "muito"], ["1", "bem", "pouco"], ["5", "pouco", "quase nada"]]}},
 {"p": "Cada publicação **gasta** privacidade: publicar a mesma contagem cem vezes com ruído novo deixa a média revelar o valor. Publique uma vez, e guarde o número publicado."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/seguranca/integridade",
"title": "Integridade",
"description": "SRI para o script de CDN, o manifesto de uma pasta, e o manifesto assinado que denuncia a troca conjunta.",
"blocos": [
 {"p": "Integridade é o \"I\" da tríade, e o menos implementado: quase todo sistema cifra, poucos conferem. `Arcane.Integridade` responde três perguntas: o script da CDN é o que eu aprovei? a pasta de produção mudou desde o deploy? e quem trocou um arquivo trocou também o manifesto?"},
 {"h2": "SRI — o script de terceiro"},
 {"code": """adopt Arcane.Integridade as I

js := "alert('Hello, world.');"
valor := I.sri(js)
out $"<script src=\\"https://cdn.exemplo.com/a.js\\" integrity=\\"{valor}\\" crossorigin=\\"anonymous\\"></script>"

// O exemplo da MDN — o mesmo valor que o navegador calcula.
assert valor is "sha384-H8BRh8j48O9oYatfu5AZzq6A9RINhZO5H16dQZngK7T62em8MUt1FLm52t+eX6xO"
assert not I.conferir_sri(js + " ", valor)""", "lang": "df"},
 {"h2": "O manifesto de uma pasta"},
 {"code": """adopt Arcane.Integridade as I
adopt Arcane.IO as IO
adopt Arcane.OS as OS

app := $"{OS.temp_dir()}/df-int-{randint(100000, 999999)}"
IO.mkdir(app)
IO.write($"{app}/main.df", "out 1")
IO.write($"{app}/config.toml", "porta = 8080")

chave := "mora-fora-desta-maquina-000"
assinado := I.assinar_manifesto(I.manifesto(app), chave)

// ... depois do deploy, alguem mexe:
IO.write($"{app}/main.df", "out 2")
IO.write($"{app}/porta-dos-fundos.df", "out 3")

r := I.conferir_manifesto(app, assinado["arquivos"])
out r
assert r["alterados"] is ["main.df"] and r["acrescentados"] is ["porta-dos-fundos.df"]

// E quem troca o arquivo e o manifesto JUNTOS e pego pela assinatura.
forjado := assinado with {}
forjado["arquivos"] := I.manifesto(app)
assert not I.verificar_manifesto(forjado, chave)
IO.remove_tree(app)""", "lang": "df"},
 {"table": {"head": ["Decisão", "Sem ela"], "rows": [
   ["caminho relativo e com `/`", "o manifesto do Windows não confere no Linux"],
   ["link simbólico não é seguido", "o manifesto descreve arquivos de fora da pasta"],
   ["a assinatura usa uma chave que mora **fora**", "quem troca o arquivo troca o manifesto junto, e ele continua batendo"],
   ["comparação em tempo constante", "a assinatura é descoberta pelo tempo de resposta"]]}},
 {"p": "Continue em [Cadeia de suprimentos](/docs/seguranca/cadeia) e [Arcane.Integridade](/docs/biblioteca/integridade)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/seguranca/cadeia",
"title": "Cadeia de suprimentos",
"description": "Do pacote que se instala à imagem que se publica — o que é conferido, e em que ponto.",
"blocos": [
 {"p": "A cadeia de suprimentos é tudo que entra no seu programa sem ter sido escrito por você: pacotes, *actions* do CI, a imagem base, o próprio interpretador. Um ataque a ela alcança todo mundo que confia no elo — por isso cada elo precisa de uma conferência, e não de confiança."},
 {"table": {"head": ["Elo", "A conferência", "Onde"], "rows": [
   ["o pacote instalado", "o sha256 do `forge.lock` é comparado com o que chegou", "`dataforge install`"],
   ["o pacote publicado", "tarball **reprodutível** (`mtime=0`, uid/gid zerados)", "`dataforge pack`"],
   ["a extração", "recusa `../` e link simbólico (*Zip Slip*)", "`dataforge add`"],
   ["as *actions* do CI", "fixar por **SHA do commit**, e não por tag", "o workflow"],
   ["a imagem base", "atualizada pelo Dependabot; `USER` sem privilégio", "`dataforge devops github`"],
   ["o inventário", "SBOM em CycloneDX", "`dataforge devops sbom`"],
   ["o artefato em produção", "manifesto assinado da pasta", "`Arcane.Integridade`"],
   ["o que o código pode fazer", "o `adopt` fora da lista é recusado", "`Arcane.Capacidade`"]]}},
 {"code": """uses: actions/checkout@v4                                       # a tag pode ser MOVIDA
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # o commit nao""", "lang": "yaml"},
 {"callout": {"tipo": "atencao", "titulo": "A tag de uma action pode mudar de dono", "texto": "Uma tag aponta para o commit que o dono da action quiser, quando ele quiser — e uma conta comprometida move `v4` para um commit malicioso em todos os repositórios que o usam. O SHA não se move. O Dependabot atualiza os SHAs fixados, então fixar não significa ficar para trás."}},
 {"code": """dataforge install              # confere o sha256 de cada pacote contra o lock
dataforge outdated             # o que tem versao nova
dataforge devops sbom          # o inventario, para o scanner da empresa
dataforge seguranca . --strict # o segredo que entraria junto no pacote""", "lang": "bash"},
 {"p": "Continue em [Integridade](/docs/seguranca/integridade) e [O lockfile](/docs/modulos/lockfile)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/seguranca/incidentes",
"title": "Resposta a incidentes",
"description": "As fases do NIST, o que preservar antes de consertar, e a comunicação que a LGPD exige.",
"blocos": [
 {"p": "Um incidente é a pior hora para decidir como responder a um incidente. As fases abaixo seguem o guia do NIST (SP 800-61), e a regra que atravessa todas é a mesma: **preserve antes de consertar** — reiniciar a máquina apaga a memória, e reinstalar apaga o disco que provava o que aconteceu."},
 {"table": {"head": ["Fase", "O que se faz", "Com o quê, aqui"], "rows": [
   ["**Preparação**", "quem é chamado, onde está o log, qual é a chave de emergência", "`auditoria` fora da máquina; manifesto assinado de cada deploy"],
   ["**Detecção e análise**", "o alerta, e a pergunta *“é real?”*", "`Arcane.Deteccao`: o alerta traz os eventos"],
   ["**Contenção**", "parar o dano sem destruir a evidência", "revogar tokens, girar chaves, tirar do balanceador"],
   ["**Erradicação**", "tirar o que o atacante deixou", "`conferir_manifesto`: o que foi acrescentado e alterado"],
   ["**Recuperação**", "voltar a um estado conhecido", "reimplantar do artefato assinado, e não da máquina"],
   ["**Lições**", "o que teria detectado antes", "uma regra nova no motor de detecção"]]}},
 {"h2": "A primeira hora"},
 {"code": """adopt Arcane.Integridade as I
adopt Arcane.IO as IO
adopt Arcane.OS as OS

// 1. Fotografar antes de mexer: o manifesto do estado ATUAL e a evidencia.
servidor := $"{OS.temp_dir()}/df-inc-{randint(100000, 999999)}"
IO.mkdir(servidor)
IO.write($"{servidor}/app.df", "out 1")
IO.write($"{servidor}/.cache-x.df", "adopt Python.os")   // o que alguem deixou

esperado := {"app.df": I.manifesto(servidor)["app.df"]}   // o do deploy
agora := I.manifesto(servidor)
evidencia := to_json(agora)                                // guardado FORA daqui

r := I.conferir_manifesto(servidor, esperado)
out $"acrescentado desde o deploy: {r['acrescentados']}"
assert r["acrescentados"] is [".cache-x.df"]
IO.remove_tree(servidor)""", "lang": "df"},
 {"h2": "Comunicar"},
 {"p": "Um incidente com dado pessoal que possa gerar risco ou dano relevante ao titular precisa ser comunicado à **ANPD** e aos **titulares** (LGPD, art. 48). O regulamento da ANPD sobre comunicação de incidentes fixa o prazo em **três dias úteis** a partir do conhecimento — e pede o que foi afetado, quantos titulares, as medidas tomadas e o contato do encarregado."},
 {"table": {"head": ["A comunicação precisa dizer", "De onde vem"], "rows": [
   ["quais dados, e de quantos titulares", "`Privacidade.titulares()` — onde cada dado mora"],
   ["quando começou e quando foi percebido", "a trilha de `auditoria`, e o alerta"],
   ["o que foi feito para conter", "o registro da contenção"],
   ["o que o titular deve fazer", "trocar a senha, desconfiar de contato"]]}},
 {"callout": {"tipo": "dica", "titulo": "O ensaio", "texto": "Uma resposta que só existe num documento falha no primeiro incidente. Ensaie uma vez por semestre: alguém apaga um arquivo de produção de mentira, e o time precisa descobrir o quê, quando e por quem — só com o que está registrado."}},
 {"p": "Volte ao [mapa de segurança](/docs/seguranca/mapa)."},
]},
]
