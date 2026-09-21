"""
Arcane.Regex - Regular Expressions Module
Pattern matching, search, replace, and validation with regex.
"""

import re


class ArcaneRegex:
    """Regular expressions module for DataForge."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Regex",

            # Core operations
            "match": cls._match,
            "search": cls._search,
            "findall": cls._findall,
            "finditer": cls._finditer,
            "sub": cls._sub,
            "subn": cls._subn,
            "split": cls._split,
            "test": cls._test,
            "count": cls._count,
            "extract": cls._extract,

            # Compile
            "compile": cls._compile,

            # Common patterns (pre-built)
            "patterns": {
                "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                "url": r"https?://[^\s<>\"']+",
                "phone": r"\+?[\d\s\-\(\)]{7,15}",
                "ipv4": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
                "hex_color": r"#(?:[0-9a-fA-F]{3}){1,2}\b",
                "date_iso": r"\d{4}-\d{2}-\d{2}",
                "time_24h": r"(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?",
                "integer": r"-?\d+",
                "float_num": r"-?\d+\.?\d*",
                "word": r"\b\w+\b",
                "whitespace": r"\s+",
                "alpha": r"[a-zA-Z]+",
                "alphanumeric": r"[a-zA-Z0-9]+",
                "username": r"^[a-zA-Z0-9_]{3,20}$",
                "slug": r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
                "cpf": r"\d{3}\.\d{3}\.\d{3}-\d{2}",
                "cnpj": r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}",
                "cep": r"\d{5}-?\d{3}",
                "html_tag": r"<[^>]+>",
                "markdown_bold": r"\*\*(.+?)\*\*",
                "markdown_link": r"\[([^\]]+)\]\(([^\)]+)\)",
            },

            # Validators
            "is_email": cls._is_email,
            "is_url": cls._is_url,
            "is_phone": cls._is_phone,
            "is_ipv4": cls._is_ipv4,
            "is_date": cls._is_date,
            "is_cpf": cls._is_cpf,
            "is_cnpj": cls._is_cnpj,

            # Utilities
            "escape": cls._escape,
            "replace_all": cls._replace_all,
            "extract_numbers": cls._extract_numbers,
            "extract_words": cls._extract_words,
            **_extras(),
            "extract_emails": cls._extract_emails,
            "extract_urls": cls._extract_urls,
            "remove_html": cls._remove_html,
            "clean_whitespace": cls._clean_whitespace,
            "mask": cls._mask,
            "word_count": cls._word_count,

            # Flags
            "IGNORECASE": re.IGNORECASE,
            "MULTILINE": re.MULTILINE,
            "DOTALL": re.DOTALL,
        }

    @staticmethod
    def _match(pattern, string, flags=0):
        m = re.match(pattern, string, flags)
        if m:
            return {
                "matched": True,
                "value": m.group(),
                "groups": list(m.groups()),
                # 'groups' continua vindo por POSICAO — havia codigo
                # lendo dali. 'named' e o acrescimo: sem ele, escrever
                # '(?P<ano>…)' era decoracao, porque o nome compilava e
                # o resultado nao o carregava.
                "named": dict(m.groupdict()),
                "span": list(m.span()),
                "start": m.start(),
                "end": m.end(),
            }
        return {"matched": False, "value": "", "groups": [], "named": {},
                "span": [], "start": -1, "end": -1}

    @staticmethod
    def _search(pattern, string, flags=0):
        m = re.search(pattern, string, flags)
        if m:
            return {
                "matched": True,
                "value": m.group(),
                "groups": list(m.groups()),
                # 'groups' continua vindo por POSICAO — havia codigo
                # lendo dali. 'named' e o acrescimo: sem ele, escrever
                # '(?P<ano>…)' era decoracao, porque o nome compilava e
                # o resultado nao o carregava.
                "named": dict(m.groupdict()),
                "span": list(m.span()),
                "start": m.start(),
                "end": m.end(),
            }
        return {"matched": False, "value": "", "groups": [], "named": {},
                "span": [], "start": -1, "end": -1}

    @staticmethod
    def _findall(pattern, string, flags=0):
        return re.findall(pattern, string, flags)

    @staticmethod
    def _finditer(pattern, string, flags=0):
        results = []
        for m in re.finditer(pattern, string, flags):
            results.append({
                "value": m.group(),
                "groups": list(m.groups()),
                "named": dict(m.groupdict()),
                "span": list(m.span()),
                "start": m.start(),
                "end": m.end(),
            })
        return results

    @staticmethod
    def _sub(pattern, repl, string, count=0, flags=0):
        return re.sub(pattern, repl, string, count=count, flags=flags)

    @staticmethod
    def _subn(pattern, repl, string, count=0, flags=0):
        result, n = re.subn(pattern, repl, string, count=count,
                            flags=flags)
        return {"result": result, "count": n}

    @staticmethod
    def _split(pattern, string, maxsplit=0, flags=0):
        return re.split(pattern, string, maxsplit=maxsplit,
                        flags=flags)

    @staticmethod
    def _test(pattern, string, flags=0):
        return bool(re.search(pattern, string, flags))

    @staticmethod
    def _count(pattern, string, flags=0):
        return len(re.findall(pattern, string, flags))

    @staticmethod
    def _extract(pattern, string, flags=0):
        m = re.search(pattern, string, flags)
        if m:
            return list(m.groups()) if m.groups() else [m.group()]
        return []

    @staticmethod
    def _compile(pattern, flags=0):
        """O padrao preso a um objeto, com TODAS as operacoes.

        Ele tinha cinco — `match`, `search`, `findall`, `sub`, `test` —
        e era a superficie mais pobre do modulo, justamente na forma
        que a doc recomenda para um padrao usado num laco. Quem
        compilava perdia `finditer`, os grupos nomeados, `fullmatch`,
        `split` e a contagem, e voltava a chamar a versao por texto —
        que e o contrario do motivo de compilar.

        A lista sai do modulo inteiro: uma segunda lista escrita a mao
        divergiria dele no primeiro simbolo novo.
        """
        re.compile(pattern, flags)          # falha aqui, e nao no uso
        inteiro = ArcaneRegex()
        preso = {
            "__type__": "CompiledRegex",
            "pattern": pattern,
            "flags": flags,
        }
        for nome in _COM_PADRAO_E_TEXTO:
            operacao = inteiro.get(nome)
            if operacao is None:
                continue
            preso[nome] = ArcaneRegex._prender(operacao, pattern, flags)
        return preso

    @staticmethod
    def _prender(operacao, pattern, flags):
        """Chama a operacao com o padrao na frente e a flag no fim."""
        def presa(*args, **kwargs):
            kwargs.setdefault("flags", flags)
            try:
                return operacao(pattern, *args, **kwargs)
            except TypeError:
                # Algumas nao aceitam 'flags' (replace_all, risk).
                kwargs.pop("flags", None)
                return operacao(pattern, *args, **kwargs)
        return presa

    @staticmethod
    def _is_email(string):
        return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", string))

    @staticmethod
    def _is_url(string):
        return bool(re.match(r"^https?://[^\s<>\"']+$", string))

    @staticmethod
    def _is_phone(string):
        return bool(re.match(r"^\+?[\d\s\-\(\)]{7,15}$", string))

    @staticmethod
    def _is_ipv4(string):
        return bool(re.match(r"^(?:\d{1,3}\.){3}\d{1,3}$", string))

    @staticmethod
    def _is_date(string):
        return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", string))

    @staticmethod
    def _is_cpf(string):
        return bool(re.match(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$", string))

    @staticmethod
    def _is_cnpj(string):
        return bool(re.match(r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$", string))

    @staticmethod
    def _escape(string):
        return re.escape(string)

    @staticmethod
    def _replace_all(pattern, repl, string):
        return re.sub(pattern, repl, string)

    @staticmethod
    def _extract_numbers(string):
        return [float(x) if '.' in x else int(x) for x in re.findall(r'-?\d+\.?\d*', string)]

    @staticmethod
    def _extract_words(string):
        return re.findall(r'\b[a-zA-ZÀ-ÿ]+\b', string)

    @staticmethod
    def _extract_emails(string):
        return re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', string)

    @staticmethod
    def _extract_urls(string):
        return re.findall(r'https?://[^\s<>"\']+', string)

    @staticmethod
    def _remove_html(string):
        return re.sub(r'<[^>]+>', '', string)

    @staticmethod
    def _clean_whitespace(string):
        return re.sub(r'\s+', ' ', string).strip()

    @staticmethod
    def _mask(string, pattern, mask_char="*"):
        def masker(m):
            return mask_char * len(m.group())
        return re.sub(pattern, masker, string)

    @staticmethod
    def _word_count(string):
        return len(re.findall(r'\b\w+\b', string))


#: As operacoes cujo PRIMEIRO argumento e o padrao. Sao essas que um
#: objeto compilado pode oferecer — as que recebem so um texto
#: (`is_email`, `clean_whitespace`) nao tem padrao a prender.
_COM_PADRAO_E_TEXTO = (
    "match", "search", "fullmatch", "findall", "finditer",
    "named", "findnamed", "group_names",
    "sub", "subn", "sub_with", "replace_map", "replace_all",
    "split", "split_keep", "count", "test", "is_exactly", "extract",
    "highlight", "positions", "explain", "risk", "safe_search",
)


def _extras():
    """A segunda metade do modulo, em 'arcane_regex_extra.py'.

    O import e aqui embaixo, e nao no topo: o arquivo de extras importa
    'errors' para levantar com a classe certa, e 'errors' nasce do
    catalogo — um import circular derrubaria a stdlib inteira na
    partida.
    """
    from .arcane_regex_extra import EXTRAS
    return EXTRAS
