# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de seguranca.

A tabela de funcoes NAO esta aqui: ela sai do modulo a cada
geracao. Escrita a mao, ela envelhece sem ninguem ver.
"""

PROLOGO_TSX = [
    r'''{"p": "`Arcane.Crypto` tem as **primitivas** — resumo, HMAC, senha derivada, aleatório de verdade, ChaCha20-Poly1305, JWT. Este módulo é o que se faz com a entrada que veio **de fora**, e ele chama o `Crypto` em vez de reimplementá-lo: duas contas iguais escritas duas vezes divergem, e no dia em que divergirem será a de segurança que estará errada."}''',

    r'''{"h2": "Escapar é por destino, nunca “em geral”"}''',

    r'''{"p": "O que protege uma página HTML não protege uma linha de shell, e o que protege shell estraga um CSV. São doze destinos, e cada um tem a sua função — usar a errada é o mesmo que não usar nenhuma."}''',

    r'''{ code: `adopt Arcane.Seguranca as Seg

out Seg.escapar_html("<b>&'")
out Seg.escapar_js("</script>")
out Seg.escapar_csv("=HYPERLINK(\"http://mau\")")
out Seg.escapar_cabecalho("ok\r\nSet-Cookie: admin=1")
out Seg.escapar_log("ana\n2026-01-01 INFO login ok")

out Seg.limpar_html("<b>oi</b><script>mau()</script>")`, title: `os destinos` }''',

    r'''{"callout": {"tipo": "atencao", "titulo": "A injeção que quase ninguém escapa", "texto": "`escapar_csv` existe porque o Excel e o Sheets **executam** uma célula que começa com `=`, `+`, `-` ou `@`. Um nome de usuário `=HYPERLINK(...)` vira link ativo na planilha de quem exportou, e nada no arquivo denuncia. O mesmo vale para `escapar_log`: um `\\n` num campo acrescenta uma **linha inteira** ao log, e a investigação seguinte lê um evento que nunca aconteceu."}}''',

    r'''{"h2": "O segredo que se recusa a aparecer"}''',

    r'''{"p": "Um segredo vaza em log muito mais do que em commit, e vaza pelo caminho mais inocente que existe: alguém imprime o vault inteiro para depurar. `Segredo` é opaco para texto, para interpolação e para serialização."}''',

    r'''{ code: `adopt Arcane.Seguranca as Seg

chave := Seg.segredo("sk_live_exemplo_de_chave")

out chave
out $"usando {chave}"
out chave.revelar()

assert chave.igual("sk_live_exemplo_de_chave")`, title: `Segredo` }''',

    r'''{"p": "Ele **não** protege da memória nem de quem chama `revelar()`. O que ele faz é transformar um vazamento acidental numa linha explícita, que aparece na revisão de código."}''',

    r'''{"h2": "Varredura de segredo, e o que a faz calar"}''',

    r'''{"p": "Ela acha por **formato** — `ghp_`, `sk_live_`, `AKIA`, bloco de chave privada, token do PyPI —, e por isso acha o que quem escreveu esqueceu, que é o único tipo que importa. O que ela **não** acusa custou mais que o que ela acusa:"}''',

    r'''{"table": {"head": ["Cala sobre", "Porque"], "rows": [
      ["um valor que se anuncia como exemplo", "`\"123456:AAHexemplo\"` num exercício que **ensina** a não escrever token no arquivo. Uma varredura que acusa o material didático do próprio projeto é desligada no mesmo dia — e junto com ela vão os achados de verdade."],
      ["JWT com papel `anon`", "A chave `anon` do Supabase vai no pacote do navegador **de propósito**: quem protege a linha é o RLS. A `service_role` ignora o RLS e é comprometimento total. As duas têm o mesmo formato, e só o conteúdo as separa — então o papel é lido de dentro do próprio token."],
      ["credencial de `localhost`", "`postgres://forge:forge@localhost` num teste é a forma normal de escrever um teste. Os domínios reservados (RFC 2606) entram pela mesma porta."],
      ["`// df: permitir segredo-no-codigo`", "O escape do analisador, e ele vale em **qualquer** arquivo — um segredo de brinquedo mora tanto num teste em Python quanto num exemplo em Markdown."]
    ]}}''',

    r'''{ code: `adopt Arcane.Seguranca as Seg

fonte := "chave := \"ghp_abcdefghijklmnopqrstuvwxyz0123456789\""

achados := Seg.procurar_segredos(fonte)
cycle a in achados:
    out $"{a['tipo']} na linha {a['linha']}: {a['trecho']}"

out Seg.redigir(fonte)`, title: `procurar e redigir` }''',

    r'''{"callout": {"tipo": "dica", "titulo": "A linha de comando", "texto": "`dataforge seguranca .` roda isto sobre o projeto inteiro, e não só sobre os `.df`: ele lê `.env`, `.json`, `.toml`, `.yml`, `.sh` e `.ts` também, porque um segredo vaza do arquivo de configuração muito mais do que do código. Com `--strict` ele reprova a esteira de CI; com `--json` ele vira entrada de outra ferramenta."}}''',

    r'''{"h2": "Entrada hostil"}''',

    r'''{"p": "Quatro perguntas que uma aplicação faz sobre todo valor que chega de fora, e que quase sempre são respondidas com uma comparação de texto que não basta."}''',

    r'''{"table": {"head": ["Função", "O ataque que ela fecha"], "rows": [
      ["`url_segura`", "**SSRF.** Um campo “URL do seu webhook” com `http://169.254.169.254/latest/meta-data/` faz o *seu* servidor buscar as credenciais da instância e devolvê-las na resposta. O pedido sai de dentro, então o firewall não vê nada de errado."],
      ["`caminho_seguro`", "**Travessia.** `realpath` antes de comparar: sem isso, um link simbólico dentro da pasta aponta para fora e a comparação de texto aprova."],
      ["`redirecionamento_seguro`", "**Redirecionamento aberto.** `/sair?proximo=//banco-falso.exemplo` sai do seu site com a barra de endereço mostrando o seu nome até o último instante."],
      ["`json_seguro`", "**Negação de serviço com 50 KB.** Um `[[[[[…]]]]]` de dez mil níveis estoura a pilha de quem lê, e o leitor padrão aceita."]
    ]}}''',

    r'''{"callout": {"tipo": "atencao", "titulo": "Bloquear por texto não funciona", "texto": "`localtest.me` resolve para `127.0.0.1`, e quem ataca controla o DNS do domínio dele. A única pergunta que vale é **para onde o nome resolve** — e é por isso que `host_privado` resolve antes de responder. Uma corrida continua possível (o DNS pode mudar entre a conferência e a busca); `url_segura` devolve o `ip` já resolvido para quem precisar fechar isso."}}''',

    r'''{"h2": "Segundo fator, e o token com prazo"}''',

    r'''{ code: `adopt Arcane.Seguranca as Seg

// Os vetores do RFC 4226
assert Seg.hotp("GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ", 0) is "755224"
assert Seg.hotp("GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ", 1) is "287082"

segredo := Seg.totp_segredo()
codigo := Seg.totp_agora(segredo)
assert Seg.totp_conferir(segredo, codigo)

out Seg.totp_uri(segredo, "ana@loja.com", emissor := "Loja")`, title: `TOTP` }''',

    r'''{"callout": {"tipo": "atencao", "titulo": "O propósito do token não é detalhe", "texto": "Sem ele, o token que confirma um e-mail **serve para trocar a senha** — os dois são assinados com a mesma chave. Ele entra no que é assinado, então um token de outro propósito não confere. E `ler_assinado` confere a assinatura **antes** do prazo: a data de dentro do token é dado de quem o mandou até a assinatura fechar."}}''',

    r'''{ code: `adopt Arcane.Seguranca as Seg

chave := Seg.chave_de_assinatura()

t := Seg.assinar({"usuario": 7}, chave, proposito := "trocar-senha")

monitor:
    Seg.ler_assinado(t, chave, prazo := 900, proposito := "confirmar-email")
handle SignatureError as e:
    out "recusado: o proposito e outro"

lido := Seg.ler_assinado(t, chave, prazo := 900, proposito := "trocar-senha")
out lido["valor"]["usuario"]`, title: `token assinado` }''',

    r'''{"h2": "Senha: a nota não serve, a lista serve"}''',

    r'''{"p": "“Senha fraca” não diz o que fazer. `forca_da_senha` devolve `problemas`, e `politica` devolve `faltando` — é isso que vai para a tela. `exigir_politica` levanta com a lista em `e.nota`, para quem escreve o caminho feliz."}''',

    r'''{"callout": {"tipo": "nota", "titulo": "`vazada` fala com a rede, e isso está no nome", "texto": "Ela manda os **cinco primeiros** caracteres do SHA-1 da senha, nunca a senha: é o k-anonimato do Have I Been Pwned, e o serviço devolve centenas de resumos que começam com aquele prefixo. Ela devolve **-1** em vez de levantar quando a rede falha — uma política de senha que para de funcionar porque um serviço de terceiro caiu impede cadastro por um motivo que não é de segurança."}}''',

    r'''{"h2": "Auditoria que não pode ser editada sem deixar marca"}''',

    r'''{"p": "Cada registro carrega o resumo do anterior. Isso não impede editar o arquivo — nada num arquivo local impede. O que ele dá é **evidência**: alterar ou apagar uma linha faz a próxima deixar de fechar, e `conferir()` diz em qual. Para que a evidência valha, a trilha tem de ser copiada para fora da máquina que a escreve."}''',

    r'''{ code: `adopt Arcane.Seguranca as Seg

livro := Seg.auditoria("auditoria.log")

livro.registrar("login", {"quem": "ana"})
livro.registrar("pagou", {"valor": 100})

r := livro.conferir()
out $"{r['registros']} registros, cadeia fecha: {r['ok']}"`, title: `trilha encadeada` }''',

    r'''{"p": "Os dados de cada evento passam por `redigir` antes de serem gravados: uma trilha de auditoria é exatamente o tipo de arquivo que acaba anexado a um chamado."}''',

    r'''{"h2": "O que este módulo não faz"}''',

    r'''{"table": {"head": ["Não há", "Porque"], "rows": [
      ["TLS e certificado", "É do `ssl` do Python e de quem está na frente do servidor (nginx, Caddy). Uma camada própria seria um subconjunto pior de algo que já existe e já é auditado."],
      ["Argon2", "Em Python puro ele seria lento o bastante para ter de rodar com parâmetros fracos — o que o torna **pior** que o `scrypt` do `hashlib`, e não melhor. `Crypto.hash_password` usa o que o Python tem."],
      ["CSRF, cabeçalhos e limite de corpo HTTP", "O [Kiln](/docs/kiln) já responde isso como **middleware**, preso ao ciclo de um pedido. Duas respostas à mesma pergunta divergem."],
      ["Limite de taxa entre processos", "`limitador` é por processo e em memória. Num servidor com vários processos o limite efetivo é N vezes maior; limite compartilhado pede um banco ou um Redis, e este módulo não pretende ser nenhum dos dois."]
    ]}}''',

    r'''{"p": "Guia com contexto e prática: [Criptografia](/docs/tecnicas/criptografia). As primitivas: [Arcane.Crypto](/docs/biblioteca/crypto)."}''',
]
