# -*- coding: utf-8 -*-
"""A API pública do site — a referência que faltava.

Sete JSONs estavam no ar, com CORS, servidos de `/api/*.json`, e não
havia uma linha documentando que existem. Uma API sem referência é uma
API que ninguém usa: quem chega não sabe o que pedir nem o que vem de
volta.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/api",
"title": "Referência da API",
"description": "Sete endpoints JSON com a linguagem inteira: sintaxe, 1349 símbolos, 45 comandos, 177 códigos de erro e o inventário. Gerados do código-fonte, com CORS aberto.",
"blocos": [
 {"p": "Tudo que esta documentação mostra está disponível como **JSON**, servido do próprio site, com `Access-Control-Allow-Origin: *`. Serve para gerar realce de sintaxe, autocompletar num editor que não fale LSP, uma folha de consulta, um bot, ou um site como este."},
 {"code": """curl -s https://dataforge-lang.vercel.app/api/index.json""", "lang": "bash"},
 {"code": """{
  "nome": "DataForge",
  "versao": "1.0.0",
  "descricao": "API pública da linguagem: sintaxe, biblioteca, comandos e conteúdos.",
  "documentacao": "https://dataforge-lang.vercel.app/docs",
  "rotas": {
    "sintaxe":    "/api/sintaxe.json",
    "embutidas":  "/api/embutidas.json",
    "modulos":    "/api/modulos.json",
    "comandos":   "/api/comandos.json",
    "erros":      "/api/erros.json",
    "conteudos":  "/api/conteudos.json"
  }
}""", "lang": "json"},

 {"callout": {"tipo": "nota", "titulo": "Nada aqui é escrito à mão", "texto": "Os sete arquivos saem de `scripts/gerar_api.py`, que lê `tokens.py`, `builtins.py`, a `stdlib/`, o `cli.py` e o catálogo de erros — o mesmo código que o interpretador executa. Um símbolo novo aparece na API na próxima geração; um removido desaparece. Não há uma segunda lista para divergir."}},

 {"h2": "Os sete endpoints"},
 {"table": {"head": ["Endpoint", "Tamanho", "O que traz"], "rows": [
   ["`/api/index.json`", "< 1 KB", "o índice — comece por aqui"],
   ["`/api/sintaxe.json`", "10 KB", "81 palavras reservadas, 19 contextuais, 19 operadores, os verbos HTTP e as regras que mais pegam"],
   ["`/api/embutidas.json`", "2 KB", "as 228 funções globais, sem `adopt`"],
   ["`/api/modulos.json`", "112 KB", "39 módulos e **1349 símbolos**, com assinatura e resumo de cada um"],
   ["`/api/comandos.json`", "22 KB", "45 comandos da CLI, em 7 grupos, com opções, exemplos e apelidos"],
   ["`/api/erros.json`", "68 KB", "177 códigos de erro, com explicação, exemplo que provoca e como corrigir"],
   ["`/api/conteudos.json`", "< 1 KB", "o inventário: exercícios por módulo, exemplos, pacotes, projetos"]]}},

 {"h2": "`/api/sintaxe.json`"},
 {"p": "É o que um realce de sintaxe precisa, e cada palavra vem com o **equivalente** na linguagem de onde a pessoa vem:"},
 {"code": """{
  "versao": "1.0.0",
  "extensao": ".df",
  "reservadas": [
    { "palavra": "action", "descricao": "declara uma função",
      "equivalente": "def / function" }
  ],
  "contextuais": [
    { "palavra": "abstract", "descricao": "sem implementação; obriga o herdeiro",
      "equivalente": "abstract", "onde": "corpo de blueprint" }
  ],
  "operadores": [
    { "simbolo": ":=", "descricao": "atribuição", "equivalente": "=" }
  ],
  "verbos_http": ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "ANY"],
  "regras": ["A indentação é de 4 espaços. Tab é erro de sintaxe.", "…"]
}""", "lang": "json"},
 {"p": "A distinção entre `reservadas` e `contextuais` importa para quem constrói ferramenta: as 81 primeiras **não podem ser nome de variável**; as 19 segundas podem, e só viram palavra-chave onde fazem sentido — `route`, `render` e `server` são nomes bons demais para tirar de quem escreve."},
 {"p": "O campo `onde` das contextuais diz exatamente em que contexto ela liga."},

 {"h2": "`/api/modulos.json`"},
 {"p": "O maior dos sete, e o que responde \"o que a biblioteca tem\":"},
 {"code": """{
  "versao": "1.0.0",
  "total_modulos": 39,
  "total_simbolos": 1349,
  "modulos": [
    {
      "nome": "Arcane.Vitrine",
      "apelidos": ["Painel", "Vitrine"],
      "total": 113,
      "simbolos": [
        { "nome": "abas", "assinatura": "(rotulos)",
          "resumo": "Abas. Devolve um cluster de áreas, uma por rótulo." }
      ]
    }
  ]
}""", "lang": "json"},
 {"p": "`apelidos` é o mesmo módulo por outro nome: `adopt Banco` e `adopt Arcane.Forge` carregam o **mesmo** objeto. Contá-los como módulos diferentes já fez o site anunciar 33 onde havia 29 — por isso a API traz o nome oficial e a lista de apelidos separada."},

 {"h2": "`/api/erros.json`"},
 {"p": "Cada um dos 177 códigos com o que provoca e o que resolve:"},
 {"code": """{
  "codigo": "DF0101",
  "titulo": "Indentacao inconsistente",
  "explicacao": "DataForge usa indentação para delimitar blocos, e aceita apenas espaços…",
  "exemplo": "given x bigger 0:\\n    out \\"com espacos\\"\\n\\tout \\"com tab\\"",
  "solucao": "Configure o editor para inserir espaços no lugar de tab…",
  "doc": "primeiros-passos"
}""", "lang": "json"},
 {"p": "O campo `exemplo` é código que **provoca** aquele erro, e o `doc` é o caminho relativo da página que explica o assunto — `https://dataforge-lang.vercel.app/docs/` + `doc`."},
 {"p": "É o mesmo catálogo que o `dataforge explain DF0101` imprime no terminal."},

 {"h2": "`/api/comandos.json`"},
 {"code": """{
  "grupo": "Projeto",
  "comandos": [
    {
      "nome": "init",
      "uso": "dataforge init [pasta]",
      "resumo": "Cria forge.toml e o esqueleto do projeto",
      "detalhe": "Escreve o manifesto, a pasta src/ com um main.df e a tests/…",
      "opcoes": [],
      "exemplos": [
        { "comando": "dataforge init", "nota": "aqui mesmo" },
        { "comando": "dataforge init meu-app", "nota": "numa pasta nova" }
      ],
      "apelidos": [],
      "veja": ["new", "info"]
    }
  ]
}""", "lang": "json"},
 {"p": "`veja` liga os comandos entre si — é o que permite montar uma navegação sem decidir à mão o que é relacionado a quê."},

 {"h2": "Usar: três exemplos que rodam"},
 {"h3": "Em DataForge"},
 {"code": """adopt Arcane.Web as Web
adopt Arcane.Serialization as Serde

// 'Arcane.Web' e o CLIENTE; 'Arcane.Http' e o servidor.
r := Web.get("https://dataforge-lang.vercel.app/api/sintaxe.json")
dados := Serde.from_json(r["body"])

out $"{len(dados["reservadas"])} palavras reservadas"

// Cada uma traz o equivalente na linguagem de onde a pessoa vem
cycle p in dados["reservadas"]:
    given p["equivalente"] is not "":
        out $"  {p["palavra"]} ← {p["equivalente"]}\"""", "lang": "df"},

 {"h3": "No terminal, com jq"},
 {"code": """# quantos símbolos tem cada módulo, do maior para o menor
curl -s https://dataforge-lang.vercel.app/api/modulos.json \\
  | jq -r '.modulos | sort_by(-.total) | .[] | "\\(.total)\\t\\(.nome)"' \\
  | head

# o que fazer com um erro específico
curl -s https://dataforge-lang.vercel.app/api/erros.json \\
  | jq -r '.codigos[] | select(.codigo == "DF0401") | .solucao'

# toda opção de um comando
curl -s https://dataforge-lang.vercel.app/api/comandos.json \\
  | jq -r '.grupos[].comandos[] | select(.nome == "check") | .opcoes[]'""", "lang": "bash"},

 {"h3": "Em JavaScript, do navegador"},
 {"code": """const base = 'https://dataforge-lang.vercel.app/api';

// O CORS é aberto: dá para chamar de qualquer origem.
const { reservadas, operadores } = await fetch(`${base}/sintaxe.json`)
  .then((r) => r.json());

// Um realce de sintaxe mínimo, com a lista sempre em dia.
const palavras = new RegExp(`\\\\b(${reservadas.map((p) => p.palavra).join('|')})\\\\b`, 'g');
const colorido = codigo.replace(palavras, '<b>$1</b>');""", "lang": "javascript"},

 {"h2": "Contrato"},
 {"table": {"head": ["", ""], "rows": [
   ["**Método**", "`GET`. Não há escrita — é um site estático."],
   ["**Autenticação**", "nenhuma. Os dados são públicos e não há cota."],
   ["**CORS**", "`Access-Control-Allow-Origin: *` em todos os sete."],
   ["**Codificação**", "UTF-8, e o `Content-Type` diz `charset=utf-8`."],
   ["**Cache**", "revalidação a cada pedido. Um deploy publica dados novos na hora."],
   ["**Versão**", "todo arquivo traz `versao` na raiz — compare com a sua antes de confiar no formato."]]}},

 {"callout": {"tipo": "atencao", "titulo": "O que pode mudar sem aviso", "texto": "Os **valores** mudam a cada versão da linguagem: um símbolo novo, um erro renomeado, um comando acrescentado. Isso é o ponto da API. O que não muda sem subir a `versao` é o **formato**: os nomes dos campos e a forma de cada objeto. Se você depende de um campo, leia `versao` e trate a divergência."}},

 {"h2": "O registro de pacotes é outro endereço"},
 {"p": "`/registry/index.json` é o registro que o `dataforge add` consulta — não faz parte desta API, e tem contrato próprio."},
 {"code": """curl -s https://dataforge-lang.vercel.app/registry/index.json | jq '.pacotes | keys'""", "lang": "bash"},
 {"p": "Ele é uma pasta com `index.json` e `pacotes/*.tar.gz`, servida por qualquer host: **não há servidor a manter**. Os detalhes em [Pacotes](/docs/pacotes/registro)."},

 {"h2": "E o OpenAPI, que é outra coisa"},
 {"p": "Esta página é a API **do site**. Se você quer o contrato de uma API que você escreveu em DataForge, o `Arcane.API` gera OpenAPI 3.1, coleção do Postman, do Insomnia, comandos `curl` e Markdown — tudo derivado das rotas registradas no seu servidor Kiln."},
 {"code": """adopt Arcane.API as API

doc := API.openapi(minha_api, {"titulo": "Loja", "versao": "2.0"})""", "lang": "df"},
 {"p": "Em [OpenAPI, Insomnia e Postman](/docs/tecnicas/api)."},

 {"h2": "Onde continuar"},
 {"cards": [
   {"href": "/docs/tecnicas/api", "title": "OpenAPI", "desc": "O contrato da SUA API, gerado das rotas do Kiln."},
   {"href": "/docs/biblioteca", "title": "Biblioteca Arcane", "meta": "1349 símbolos", "desc": "O mesmo que /api/modulos.json, para ler."},
   {"href": "/docs/erros", "title": "Códigos de erro", "meta": "177", "desc": "O mesmo que /api/erros.json."},
   {"href": "/docs/pacotes/registro", "title": "O registro", "desc": "Como publicar um pacote, e por que ele é estático."}]},
]},
]
