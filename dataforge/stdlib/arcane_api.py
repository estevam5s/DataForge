"""Arcane.API — a API do Kiln vista de fora: OpenAPI, Insomnia, curl.

Por que isto existe
-------------------
O Kiln já é um framework REST completo — `route`, `resource`, `cors`,
`auth`, `rate_limit`, paginação. O que faltava era o outro lado: quem
vai **consumir** a API precisa saber o que ela oferece, e hoje isso se
descobre lendo o código-fonte do servidor.

Escrever a documentação à mão resolve por uma semana. Depois ela
diverge — e uma documentação de API errada é pior que nenhuma, porque
quem a lê não tem como saber.

Então ela é **derivada das rotas registradas**. O servidor é a fonte da
verdade; isto é uma projeção dele.

    adopt Arcane.API as API

    out API.openapi(servidor, {"titulo": "Minha API"})
    IO.write("insomnia.json", API.insomnia(servidor))
    out API.curl(servidor)

O que cada formato serve
------------------------
| | Para |
|---|---|
| `openapi` | Swagger UI, geradores de cliente, validação de contrato |
| `insomnia` | importar direto no Insomnia, com uma requisição por rota |
| `postman` | idem, na coleção v2.1 |
| `curl` | copiar e colar no terminal, ou pôr num README |
| `markdown` | a tabela de rotas para a documentação do projeto |

Os limites, ditos
-----------------
O Kiln não declara tipos de corpo nem de resposta — `respond json {…}`
monta o vault na hora. Então o esquema de entrada e saída **não é
inferido**: o que sai é a rota, o método, os parâmetros de caminho e o
que se declarar à mão em `Kiln.validar`.

Inventar um esquema a partir de um exemplo daria uma documentação com
aparência de completa e conteúdo adivinhado. Preferimos uma menor e
verdadeira.
"""

import json as _json


def _rotas_de(app):
    """As rotas registradas, com os nomes dos parâmetros.

    Aceita tanto o objeto do servidor quanto a lista que
    `Kiln.routes` já devolve — quem chama não deveria precisar saber
    qual das duas tem em mãos.
    """
    if isinstance(app, list):
        return app
    rotas = getattr(app, "rotas", None)
    if rotas is None:
        from ..errors import TypeError_
        raise TypeError_(
            "isto nao e um servidor Kiln.", 0, 0,
            nota="passe o nome declarado em 'server <nome> on <porta>:'",
            dica='API.openapi(meu_servidor)',
            doc="tecnicas/api")
    return [{"method": r.metodo, "path": r.padrao, "params": list(r.nomes)}
            for r in rotas]


def _caminho_openapi(padrao):
    """`/itens/:id` vira `/itens/{id}` — o OpenAPI usa chaves."""
    partes = []
    for pedaco in padrao.split("/"):
        if pedaco.startswith(":"):
            partes.append("{" + pedaco[1:] + "}")
        elif pedaco.startswith("<") and pedaco.endswith(">"):
            partes.append("{" + pedaco[1:-1] + "}")
        else:
            partes.append(pedaco)
    return "/".join(partes)


def _resumo(metodo, padrao, params):
    """Uma frase curta para a rota, a partir do que ela é.

    `GET /itens` → "Lista itens". `GET /itens/:id` → "Um item".
    É palpite, mas é palpite ÓBVIO e editável — melhor que um campo
    vazio que ninguém preenche.
    """
    pedacos = [p for p in padrao.strip("/").split("/")
               if p and not p.startswith((":", "<"))]
    recurso = pedacos[-1] if pedacos else "raiz"
    tem_id = bool(params)

    verbos = {
        "GET": f"Um {recurso}" if tem_id else f"Lista {recurso}",
        "POST": f"Cria {recurso}",
        "PUT": f"Substitui {recurso}",
        "PATCH": f"Altera {recurso}",
        "DELETE": f"Remove {recurso}",
        "HEAD": f"Cabecalhos de {recurso}",
        "OPTIONS": f"Metodos de {recurso}",
    }
    return verbos.get(metodo.upper(), f"{metodo} {padrao}")


class ArcaneAPI:
    """A API do Kiln, exportada para quem vai consumi-la."""

    def __new__(cls):
        return {
            "__name__": "Arcane.API",

            # ── Exportar ──
            "openapi": cls._openapi,
            "insomnia": cls._insomnia,
            "postman": cls._postman,
            "curl": cls._curl,
            "markdown": cls._markdown,

            # ── Inspecionar ──
            "rotas": cls._rotas,
            "resumo": cls._resumo_da_api,
        }

    # ── Inspecionar ──────────────────────────────────────────

    @staticmethod
    def _rotas(app):
        """As rotas, como cluster de vaults."""
        return _rotas_de(app)

    @staticmethod
    def _resumo_da_api(app):
        """Quantas rotas, por método — para um `out` rápido."""
        rotas = _rotas_de(app)
        por_metodo = {}
        for r in rotas:
            por_metodo[r["method"]] = por_metodo.get(r["method"], 0) + 1
        return {
            "rotas": len(rotas),
            "metodos": por_metodo,
            "com_parametro": sum(1 for r in rotas if r["params"]),
        }

    # ── OpenAPI ──────────────────────────────────────────────

    @staticmethod
    def _openapi(app, config=None):
        """OpenAPI 3.1, como texto JSON.

        É o formato que o Swagger UI lê, que gera cliente em vinte
        linguagens, e que um validador de contrato consome. Se for para
        exportar um formato só, é este.
        """
        config = dict(config or {})
        rotas = _rotas_de(app)

        caminhos = {}
        for rota in rotas:
            caminho = _caminho_openapi(rota["path"])
            metodo = rota["method"].lower()
            operacao = {
                "summary": _resumo(rota["method"], rota["path"],
                                   rota["params"]),
                "responses": {
                    "200": {"description": "ok"},
                    "404": {"description": "nao encontrado"},
                    "500": {"description": "erro interno"},
                },
            }
            if rota["params"]:
                operacao["parameters"] = [
                    {"name": nome, "in": "path", "required": True,
                     "schema": {"type": "string"}}
                    for nome in rota["params"]
                ]
            if metodo in ("post", "put", "patch"):
                operacao["requestBody"] = {
                    "required": True,
                    "content": {"application/json": {
                        "schema": {"type": "object"}}},
                }
            caminhos.setdefault(caminho, {})[metodo] = operacao

        documento = {
            "openapi": "3.1.0",
            "info": {
                "title": config.get("titulo", "API DataForge"),
                "version": str(config.get("versao", "1.0.0")),
                "description": config.get("descricao",
                                          "Gerado de um servidor Kiln."),
            },
            "servers": [{"url": config.get("base", "http://127.0.0.1:8080")}],
            "paths": caminhos,
        }
        return _json.dumps(documento, indent=2, ensure_ascii=False)

    # ── Insomnia ─────────────────────────────────────────────

    @staticmethod
    def _insomnia(app, config=None):
        """Coleção do Insomnia v4, como texto JSON.

        Importar isto no Insomnia dá **uma requisição por rota**, já com
        o método, a URL e um corpo de exemplo onde faz sentido. Os
        parâmetros de caminho viram `{{ id }}`, que o Insomnia reconhece
        como variável de ambiente.
        """
        config = dict(config or {})
        rotas = _rotas_de(app)
        base = config.get("base", "http://127.0.0.1:8080")
        nome = config.get("titulo", "API DataForge")

        recursos = [{
            "_id": "wrk_dataforge",
            "_type": "workspace",
            "name": nome,
            "description": config.get(
                "descricao", "Gerado por 'Arcane.API' a partir das rotas."),
        }, {
            "_id": "env_base",
            "_type": "environment",
            "parentId": "wrk_dataforge",
            "name": "Base",
            "data": {"base": base},
        }]

        for i, rota in enumerate(rotas):
            url = rota["path"]
            for nome_param in rota["params"]:
                url = url.replace(f":{nome_param}", "{{ " + nome_param + " }}")

            pedido = {
                "_id": f"req_{i}",
                "_type": "request",
                "parentId": "wrk_dataforge",
                "name": _resumo(rota["method"], rota["path"], rota["params"]),
                "method": rota["method"].upper(),
                "url": "{{ base }}" + url,
                "headers": [{"name": "Content-Type",
                             "value": "application/json"}],
                "sort": i * 100,
            }
            if rota["method"].upper() in ("POST", "PUT", "PATCH"):
                pedido["body"] = {
                    "mimeType": "application/json",
                    "text": "{\n  \n}",
                }
            recursos.append(pedido)

        return _json.dumps({
            "_type": "export",
            "__export_format": 4,
            "__export_source": "dataforge:arcane-api",
            "resources": recursos,
        }, indent=2, ensure_ascii=False)

    # ── Postman ──────────────────────────────────────────────

    @staticmethod
    def _postman(app, config=None):
        """Coleção do Postman v2.1, como texto JSON."""
        config = dict(config or {})
        rotas = _rotas_de(app)
        base = config.get("base", "http://127.0.0.1:8080")

        itens = []
        for rota in rotas:
            caminho = [p for p in rota["path"].strip("/").split("/") if p]
            caminho = [("{{" + p[1:] + "}}") if p.startswith(":") else p
                       for p in caminho]
            pedido = {
                "method": rota["method"].upper(),
                "header": [{"key": "Content-Type",
                            "value": "application/json"}],
                "url": {"raw": base + rota["path"],
                        "host": [base], "path": caminho},
            }
            if rota["method"].upper() in ("POST", "PUT", "PATCH"):
                pedido["body"] = {"mode": "raw", "raw": "{}"}
            itens.append({
                "name": _resumo(rota["method"], rota["path"], rota["params"]),
                "request": pedido,
            })

        return _json.dumps({
            "info": {
                "name": config.get("titulo", "API DataForge"),
                "schema": "https://schema.getpostman.com/json/"
                          "collection/v2.1.0/collection.json",
            },
            "item": itens,
        }, indent=2, ensure_ascii=False)

    # ── curl ─────────────────────────────────────────────────

    @staticmethod
    def _curl(app, config=None):
        """Um `curl` por rota, pronto para copiar.

        É o formato que mais se usa e o menos cerimonioso: cabe num
        README, num chamado de suporte, ou numa mensagem para quem está
        testando a API pela primeira vez.
        """
        config = dict(config or {})
        base = config.get("base", "http://127.0.0.1:8080")
        linhas = []

        for rota in _rotas_de(app):
            caminho = rota["path"]
            for nome in rota["params"]:
                caminho = caminho.replace(f":{nome}", f"<{nome}>")

            linhas.append(f"# {_resumo(rota['method'], rota['path'], rota['params'])}")
            metodo = rota["method"].upper()
            if metodo == "GET":
                linhas.append(f"curl {base}{caminho}")
            elif metodo in ("POST", "PUT", "PATCH"):
                linhas.append(
                    f"curl -X {metodo} {base}{caminho} \\\n"
                    f"  -H 'Content-Type: application/json' \\\n"
                    f"  -d '{{}}'")
            else:
                linhas.append(f"curl -X {metodo} {base}{caminho}")
            linhas.append("")

        return "\n".join(linhas).rstrip() + "\n"

    # ── Markdown ─────────────────────────────────────────────

    @staticmethod
    def _markdown(app, config=None):
        """A tabela de rotas, para o README do projeto."""
        config = dict(config or {})
        rotas = _rotas_de(app)
        base = config.get("base", "http://127.0.0.1:8080")

        linhas = [
            f"# {config.get('titulo', 'API')}",
            "",
            config.get("descricao", ""),
            "",
            f"Base: `{base}`",
            "",
            "| Método | Caminho | O que faz |",
            "|---|---|---|",
        ]
        for rota in rotas:
            linhas.append(
                f"| `{rota['method'].upper()}` | `{rota['path']}` | "
                f"{_resumo(rota['method'], rota['path'], rota['params'])} |")
        linhas += [
            "",
            "<sub>Gerado de `Arcane.API` a partir das rotas registradas — "
            "o servidor é a fonte da verdade.</sub>",
            "",
        ]
        return "\n".join(linhas)
