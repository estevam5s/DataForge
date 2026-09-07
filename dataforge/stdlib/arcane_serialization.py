"""
Arcane.Serialization — JSON, CSV, INI, TOML-simples, XML e formato binário.

Converte entre estruturas do DataForge e formatos de texto. As funções de
leitura são tolerantes: devolvem um resultado com 'ok' em vez de estourar,
quando a variante '_safe' é usada.
"""

import base64
import csv
import io
import json
import pickle
import xml.etree.ElementTree as ET
from configparser import ConfigParser


class ArcaneSerialization:
    """Serialização e desserialização de dados."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Serialization",

            # ── JSON ──
            "to_json": cls._to_json,
            "from_json": cls._from_json,
            "from_json_safe": cls._from_json_safe,
            "json_pretty": lambda d, indent=2: json.dumps(
                d, ensure_ascii=False, indent=indent, default=str),
            "json_lines": cls._json_lines,
            "from_json_lines": cls._from_json_lines,
            "is_valid_json": cls._is_valid_json,
            "json_path": cls._json_path,

            # ── CSV ──
            "to_csv": cls._to_csv,
            "from_csv": cls._from_csv,
            "csv_to_records": cls._csv_to_records,
            "records_to_csv": cls._records_to_csv,

            # ── INI ──
            "to_ini": cls._to_ini,
            "from_ini": cls._from_ini,

            # ── TOML simples ──
            "to_toml": cls._to_toml,
            "from_toml": cls._from_toml,

            # ── XML ──
            "to_xml": cls._to_xml,
            "from_xml": cls._from_xml,

            # ── Binário ──
            "to_bytes": lambda d: list(pickle.dumps(d)),
            "from_bytes": lambda b: pickle.loads(bytes(b)),
            "to_base64": lambda d: base64.b64encode(
                json.dumps(d, default=str).encode()).decode(),
            "from_base64": lambda t: json.loads(base64.b64decode(t).decode()),

            # ── Utilidades ──
            "deep_copy": lambda d: json.loads(json.dumps(d, default=str)),
            "flatten": cls._flatten,
            "unflatten": cls._unflatten,
            "formats": lambda: ["json", "jsonl", "csv", "ini", "toml", "xml",
                                "bytes", "base64"],
        }

    # ── JSON ──

    @staticmethod
    def _to_json(dados, indent=None, ordenar=False):
        return json.dumps(dados, ensure_ascii=False, indent=indent,
                          sort_keys=bool(ordenar), default=str)

    @staticmethod
    def _from_json(texto):
        return json.loads(texto)

    @staticmethod
    def _from_json_safe(texto, padrao=None):
        try:
            return {"ok": True, "value": json.loads(texto), "error": ""}
        except (json.JSONDecodeError, TypeError) as e:
            return {"ok": False, "value": padrao, "error": str(e)}

    @staticmethod
    def _is_valid_json(texto):
        try:
            json.loads(texto)
            return True
        except (json.JSONDecodeError, TypeError):
            return False

    @staticmethod
    def _json_lines(registros):
        return "\n".join(json.dumps(r, ensure_ascii=False, default=str)
                         for r in registros)

    @staticmethod
    def _from_json_lines(texto):
        return [json.loads(linha) for linha in texto.splitlines() if linha.strip()]

    @staticmethod
    def _json_path(dados, caminho, padrao=None):
        """Busca por caminho pontuado: 'usuario.endereco.cidade' ou 'itens.0.nome'."""
        atual = dados
        for parte in str(caminho).split("."):
            if isinstance(atual, dict):
                if parte not in atual:
                    return padrao
                atual = atual[parte]
            elif isinstance(atual, (list, tuple)):
                try:
                    atual = atual[int(parte)]
                except (ValueError, IndexError):
                    return padrao
            else:
                return padrao
        return atual

    # ── CSV ──

    @staticmethod
    def _to_csv(linhas, delimitador=",", cabecalho=None):
        buffer = io.StringIO()
        escritor = csv.writer(buffer, delimiter=delimitador, lineterminator="\n")
        if cabecalho:
            escritor.writerow(cabecalho)
        for linha in linhas:
            escritor.writerow(linha)
        return buffer.getvalue()

    @staticmethod
    def _from_csv(texto, delimitador=",", tem_cabecalho=False):
        leitor = csv.reader(io.StringIO(texto), delimiter=delimitador)
        linhas = [list(l) for l in leitor if l]
        if tem_cabecalho and linhas:
            return {"header": linhas[0], "rows": linhas[1:]}
        return linhas

    @staticmethod
    def _csv_to_records(texto, delimitador=","):
        leitor = csv.DictReader(io.StringIO(texto), delimiter=delimitador)
        return [dict(linha) for linha in leitor]

    @staticmethod
    def _records_to_csv(registros, delimitador=","):
        if not registros:
            return ""
        campos = list(registros[0].keys())
        buffer = io.StringIO()
        escritor = csv.DictWriter(buffer, fieldnames=campos,
                                  delimiter=delimitador, lineterminator="\n")
        escritor.writeheader()
        for registro in registros:
            escritor.writerow({c: registro.get(c, "") for c in campos})
        return buffer.getvalue()

    # ── INI ──

    @staticmethod
    def _to_ini(dados):
        parser = ConfigParser()
        for secao, valores in dados.items():
            parser[str(secao)] = {str(k): str(v) for k, v in valores.items()}
        buffer = io.StringIO()
        parser.write(buffer)
        return buffer.getvalue()

    @staticmethod
    def _from_ini(texto):
        parser = ConfigParser()
        parser.read_string(texto)
        return {secao: dict(parser[secao]) for secao in parser.sections()}

    # ── TOML simples ──

    @staticmethod
    def _to_toml(dados):
        linhas = []
        simples = {k: v for k, v in dados.items() if not isinstance(v, dict)}
        tabelas = {k: v for k, v in dados.items() if isinstance(v, dict)}
        for chave, valor in simples.items():
            linhas.append(f"{chave} = {ArcaneSerialization._toml_valor(valor)}")
        for nome, tabela in tabelas.items():
            linhas.append("")
            linhas.append(f"[{nome}]")
            for chave, valor in tabela.items():
                linhas.append(f"{chave} = {ArcaneSerialization._toml_valor(valor)}")
        return "\n".join(linhas) + "\n"

    @staticmethod
    def _toml_valor(valor):
        if isinstance(valor, bool):
            return "true" if valor else "false"
        if isinstance(valor, (int, float)):
            return str(valor)
        if isinstance(valor, (list, tuple)):
            return "[" + ", ".join(ArcaneSerialization._toml_valor(v) for v in valor) + "]"
        return json.dumps(str(valor), ensure_ascii=False)

    @staticmethod
    def _from_toml(texto):
        """Leitor de um subconjunto de TOML: tabelas, escalares e listas simples."""
        try:
            import tomllib
            return tomllib.loads(texto)
        except (ImportError, Exception):
            pass
        resultado, atual = {}, None
        for linha in texto.splitlines():
            limpa = linha.split("#")[0].strip()
            if not limpa:
                continue
            if limpa.startswith("[") and limpa.endswith("]"):
                atual = limpa[1:-1].strip()
                resultado[atual] = {}
                continue
            if "=" not in limpa:
                continue
            chave, _, bruto = limpa.partition("=")
            valor = ArcaneSerialization._parse_toml_valor(bruto.strip())
            destino = resultado[atual] if atual else resultado
            destino[chave.strip()] = valor
        return resultado

    @staticmethod
    def _parse_toml_valor(bruto):
        if bruto.startswith("[") and bruto.endswith("]"):
            interno = bruto[1:-1].strip()
            if not interno:
                return []
            return [ArcaneSerialization._parse_toml_valor(p.strip())
                    for p in interno.split(",") if p.strip()]
        if bruto in ("true", "false"):
            return bruto == "true"
        if (bruto.startswith('"') and bruto.endswith('"')) or \
           (bruto.startswith("'") and bruto.endswith("'")):
            return bruto[1:-1]
        try:
            return int(bruto)
        except ValueError:
            pass
        try:
            return float(bruto)
        except ValueError:
            return bruto

    # ── XML ──

    @staticmethod
    def _to_xml(dados, raiz="root"):
        def construir(pai, valor):
            if isinstance(valor, dict):
                for chave, sub in valor.items():
                    filho = ET.SubElement(pai, str(chave))
                    construir(filho, sub)
            elif isinstance(valor, (list, tuple)):
                for sub in valor:
                    filho = ET.SubElement(pai, "item")
                    construir(filho, sub)
            else:
                pai.text = str(valor)

        elemento = ET.Element(raiz)
        construir(elemento, dados)
        return ET.tostring(elemento, encoding="unicode")

    @staticmethod
    def _from_xml(texto):
        def ler(elemento):
            filhos = list(elemento)
            if not filhos:
                return elemento.text or ""
            if all(f.tag == "item" for f in filhos):
                return [ler(f) for f in filhos]
            return {f.tag: ler(f) for f in filhos}
        return ler(ET.fromstring(texto))

    # ── Utilidades ──

    @staticmethod
    def _flatten(dados, separador=".", prefixo=""):
        saida = {}
        for chave, valor in dados.items():
            caminho = f"{prefixo}{separador}{chave}" if prefixo else str(chave)
            if isinstance(valor, dict):
                saida.update(ArcaneSerialization._flatten(valor, separador, caminho))
            else:
                saida[caminho] = valor
        return saida

    @staticmethod
    def _unflatten(plano, separador="."):
        saida = {}
        for caminho, valor in plano.items():
            partes = str(caminho).split(separador)
            atual = saida
            for parte in partes[:-1]:
                atual = atual.setdefault(parte, {})
            atual[partes[-1]] = valor
        return saida
