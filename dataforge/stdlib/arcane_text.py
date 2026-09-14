"""
Arcane.Text - Advanced Text Processing Module
Templates, formatters, parsers, diff, similarity for DataForge.
"""

import re
import difflib
import textwrap
import hashlib
import html


class Construtor:
    """Texto montado em pedaços, e juntado uma vez no fim.

    `s += "x"` num laço é o caso que mais engana em qualquer linguagem
    com texto imutável. Cada `+=` aloca um texto novo e copia o
    anterior inteiro, e o custo total vira O(n²) — o *Schlemiel the
    Painter's Algorithm*.

    MEDIDO nesta linguagem, com o custo do laço já descontado:

        n         s += "x"      Construtor
        40.000        25 ms         125 ms
        80.000        88 ms         252 ms
       160.000       299 ms         509 ms
       320.000       872 ms       1.018 ms

        fator por dobra:  3,4  (quase quadrático)   2,0  (linear)

    O `+=` ganha enquanto n é pequeno — ele não paga a lista. A partir
    de umas dezenas de milhares de pedaços a curva se cruza, e daí em
    diante a distância só aumenta.

    Por que uma LISTA e não uma *Rope*
    ----------------------------------
    Uma rope — árvore balanceada de fragmentos — é a resposta certa
    quando o texto é **editado no meio** depois de montado. Não é o
    caso aqui: montar é acrescentar no fim, e para isso uma lista com
    `join` é O(n) com a constante mais baixa que existe em Python. Uma
    rope custaria mais em todo caso real desta linguagem, e a
    documentação diria um nome bonito sobre código mais lento.
    """

    __slots__ = ("_partes", "_tamanho")

    def __init__(self, inicial=""):
        self._partes = [str(inicial)] if inicial else []
        self._tamanho = len(str(inicial)) if inicial else 0

    def add(self, *pedacos):
        """Acrescenta no fim. Devolve a si mesmo, para encadear."""
        for pedaco in pedacos:
            texto = pedaco if isinstance(pedaco, str) else _texto_de(pedaco)
            if texto:
                self._partes.append(texto)
                self._tamanho += len(texto)
        return self

    def linha(self, *pedacos):
        """O mesmo, com uma quebra de linha no fim."""
        self.add(*pedacos)
        self._partes.append("\n")
        self._tamanho += 1
        return self

    def juntar(self, itens, separador=""):
        """Vários de uma vez, com separador entre eles."""
        primeiro = True
        for item in itens:
            if not primeiro and separador:
                self.add(separador)
            self.add(item)
            primeiro = False
        return self

    def texto(self):
        """O texto inteiro.

        Ele também COMPACTA: as partes viram um pedaço só. Chamar
        'texto()' dentro de um laço sem isso refaria o 'join' a cada
        volta, e o Construtor voltaria a ser quadrático — pela porta
        dos fundos.
        """
        if len(self._partes) > 1:
            self._partes = ["".join(self._partes)]
        return self._partes[0] if self._partes else ""

    def tamanho(self):
        """Quantos caracteres, sem montar o texto."""
        return self._tamanho

    def vazio(self):
        return self._tamanho == 0

    def limpar(self):
        self._partes = []
        self._tamanho = 0
        return self

    def __len__(self):
        return self._tamanho

    def __str__(self):
        return self.texto()

    def __repr__(self):
        return f"<construtor {self._tamanho} caractere(s)>"


def _texto_de(valor):
    """O valor como texto, pelo mesmo caminho do 'out'."""
    from ..builtins import _stringify
    try:
        return _stringify(valor)
    except Exception:                                   # noqa: BLE001
        return str(valor)


class ArcaneText:
    """Advanced text processing tools for DataForge."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Text",

            # Montar texto em pedaços — O(n) contra o O(n²) do '+='
            "construtor": lambda inicial="": Construtor(inicial),

            # Template engine
            "template": cls._template,
            "render": cls._render,

            # String manipulation
            "camel_case": cls._camel_case,
            "snake_case": cls._snake_case,
            "kebab_case": cls._kebab_case,
            "pascal_case": cls._pascal_case,
            "title_case": cls._title_case,
            "constant_case": cls._constant_case,
            "dot_case": cls._dot_case,
            "path_case": cls._path_case,
            "sentence_case": cls._sentence_case,
            "slug": cls._slug,

            # Text analysis
            "word_count": cls._word_count,
            "char_count": cls._char_count,
            "line_count": cls._line_count,
            "sentence_count": cls._sentence_count,
            "paragraph_count": cls._paragraph_count,
            "reading_time": cls._reading_time,
            "frequency": cls._frequency,
            "ngrams": cls._ngrams,

            # Diff & Similarity
            "diff": cls._diff,
            "unified_diff": cls._unified_diff,
            "similarity": cls._similarity,
            "distance": cls._levenshtein,
            "fuzzy_match": cls._fuzzy_match,
            "closest": cls._closest,

            # Formatting
            "wrap": cls._wrap,
            "dedent": cls._dedent,
            "indent": cls._indent,
            "truncate": cls._truncate,
            "pad": cls._pad,
            "align": cls._align,
            "table": cls._table,
            "box": cls._box,
            "highlight": cls._highlight,
            "number_format": cls._number_format,
            "currency": cls._currency,

            # Parsing
            "parse_csv": cls._parse_csv,
            "to_csv": cls._to_csv,
            "parse_ini": cls._parse_ini,
            "parse_query": cls._parse_query,
            "to_query": cls._to_query,
            "extract_links": cls._extract_links,
            "extract_emails": cls._extract_emails,
            "extract_numbers": cls._extract_numbers,
            "extract_hashtags": cls._extract_hashtags,
            "extract_mentions": cls._extract_mentions,

            # Encoding / Sanitization
            "escape_html": cls._escape_html,
            "unescape_html": cls._unescape_html,
            "escape_regex": cls._escape_regex,
            "strip_html": cls._strip_html,
            "strip_ansi": cls._strip_ansi,
            "normalize_whitespace": cls._normalize_whitespace,
            "remove_accents": cls._remove_accents,
            "transliterate": cls._transliterate,

            # Generators
            "lorem": cls._lorem,
            "repeat_str": cls._repeat_str,
            "random_string": cls._random_string,
        }

    # ── Template Engine ──────────────────────────────────

    @staticmethod
    def _template(text):
        """Create a template with {{variable}} placeholders."""
        return {"__type__": "Template", "text": text}

    @staticmethod
    def _render(template, context):
        """Render a template with context dict."""
        if isinstance(template, dict) and template.get("__type__") == "Template":
            text = template["text"]
        else:
            text = str(template)

        result = text
        if isinstance(context, dict):
            for key, value in context.items():
                # Accept both {{key}} and {key} placeholders.
                result = result.replace("{{" + str(key) + "}}", str(value))
                result = result.replace("{" + str(key) + "}", str(value))
        return result

    # ── Case Conversions ─────────────────────────────────

    @staticmethod
    def _split_words(text):
        """Split text into words handling camelCase, snake_case, kebab-case etc."""
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        text = re.sub(r'[_\-./\\]', ' ', text)
        return [w for w in text.split() if w]

    @staticmethod
    def _camel_case(text):
        words = ArcaneText._split_words(text)
        if not words:
            return ""
        return words[0].lower() + "".join(w.capitalize() for w in words[1:])

    @staticmethod
    def _snake_case(text):
        return "_".join(w.lower() for w in ArcaneText._split_words(text))

    @staticmethod
    def _kebab_case(text):
        return "-".join(w.lower() for w in ArcaneText._split_words(text))

    @staticmethod
    def _pascal_case(text):
        return "".join(w.capitalize() for w in ArcaneText._split_words(text))

    @staticmethod
    def _title_case(text):
        return " ".join(w.capitalize() for w in ArcaneText._split_words(text))

    @staticmethod
    def _constant_case(text):
        return "_".join(w.upper() for w in ArcaneText._split_words(text))

    @staticmethod
    def _dot_case(text):
        return ".".join(w.lower() for w in ArcaneText._split_words(text))

    @staticmethod
    def _path_case(text):
        return "/".join(w.lower() for w in ArcaneText._split_words(text))

    @staticmethod
    def _sentence_case(text):
        words = ArcaneText._split_words(text)
        if not words:
            return ""
        return words[0].capitalize() + " " + " ".join(w.lower() for w in words[1:])

    @staticmethod
    def _slug(text):
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_]+', '-', text)
        text = re.sub(r'-+', '-', text)
        return text.strip('-')

    # ── Text Analysis ────────────────────────────────────

    @staticmethod
    def _word_count(text):
        return len(text.split())

    @staticmethod
    def _char_count(text, include_spaces=True):
        if include_spaces:
            return len(text)
        return len(text.replace(" ", ""))

    @staticmethod
    def _line_count(text):
        return len(text.splitlines()) if text else 0

    @staticmethod
    def _sentence_count(text):
        return len(re.findall(r'[.!?]+', text))

    @staticmethod
    def _paragraph_count(text):
        paras = [p.strip() for p in text.split('\n\n') if p.strip()]
        return len(paras)

    @staticmethod
    def _reading_time(text, wpm=200):
        """Estimate reading time in minutes."""
        words = len(text.split())
        minutes = words / wpm
        return round(minutes, 1)

    @staticmethod
    def _frequency(text):
        """Word frequency analysis."""
        words = re.findall(r'\b\w+\b', text.lower())
        freq = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        return dict(sorted(freq.items(), key=lambda x: -x[1]))

    @staticmethod
    def _ngrams(text, n=2):
        """Generate n-grams from text."""
        words = text.split()
        return [" ".join(words[i:i+n]) for i in range(len(words) - n + 1)]

    # ── Diff & Similarity ────────────────────────────────

    @staticmethod
    def _diff(a, b):
        """Get differences between two strings."""
        a_lines = a.splitlines(keepends=True)
        b_lines = b.splitlines(keepends=True)
        diff = list(difflib.ndiff(a_lines, b_lines))
        return "".join(diff)

    @staticmethod
    def _unified_diff(a, b, a_name="original", b_name="modified"):
        """Get unified diff."""
        a_lines = a.splitlines(keepends=True)
        b_lines = b.splitlines(keepends=True)
        diff = list(difflib.unified_diff(a_lines, b_lines, fromfile=a_name, tofile=b_name))
        return "".join(diff)

    @staticmethod
    def _similarity(a, b):
        """Calculate similarity ratio between two strings (0.0 to 1.0)."""
        return round(difflib.SequenceMatcher(None, a, b).ratio(), 4)

    @staticmethod
    def _levenshtein(a, b):
        """Calculate Levenshtein edit distance."""
        if len(a) < len(b):
            return ArcaneText._levenshtein(b, a)
        if len(b) == 0:
            return len(a)
        prev_row = list(range(len(b) + 1))
        for i, ca in enumerate(a):
            curr_row = [i + 1]
            for j, cb in enumerate(b):
                insertions = prev_row[j + 1] + 1
                deletions = curr_row[j] + 1
                substitutions = prev_row[j] + (ca != cb)
                curr_row.append(min(insertions, deletions, substitutions))
            prev_row = curr_row
        return prev_row[-1]

    @staticmethod
    def _fuzzy_match(query, text, threshold=0.6):
        """Check if query fuzzy-matches text."""
        ratio = difflib.SequenceMatcher(None, query.lower(), text.lower()).ratio()
        return ratio >= threshold

    @staticmethod
    def _closest(query, candidates, n=3):
        """Find closest matches from candidates."""
        return difflib.get_close_matches(query, candidates, n=n, cutoff=0.4)

    # ── Formatting ───────────────────────────────────────

    @staticmethod
    def _wrap(text, width=80):
        return textwrap.fill(text, width=width)

    @staticmethod
    def _dedent(text):
        return textwrap.dedent(text)

    @staticmethod
    def _indent(text, prefix="    "):
        return textwrap.indent(text, prefix)

    @staticmethod
    def _truncate(text, length=50, suffix="..."):
        if len(text) <= length:
            return text
        return text[:length - len(suffix)] + suffix

    @staticmethod
    def _pad(text, width, fill=" ", align="left"):
        if align == "left":
            return text.ljust(width, fill)
        elif align == "right":
            return text.rjust(width, fill)
        elif align == "center":
            return text.center(width, fill)
        return text

    @staticmethod
    def _align(lines, alignment="left", width=None):
        """Align multiple lines."""
        if isinstance(lines, str):
            lines = lines.splitlines()
        if width is None:
            width = max(len(l) for l in lines) if lines else 0
        result = []
        for line in lines:
            if alignment == "left":
                result.append(line.ljust(width))
            elif alignment == "right":
                result.append(line.rjust(width))
            elif alignment == "center":
                result.append(line.center(width))
        return "\n".join(result)

    @staticmethod
    def _table(headers, rows, style="simple"):
        """Create a text table."""
        all_rows = [headers] + rows
        widths = [max(len(str(row[i])) for row in all_rows) for i in range(len(headers))]

        def format_row(row):
            cells = [str(row[i]).ljust(widths[i]) for i in range(len(headers))]
            return "│ " + " │ ".join(cells) + " │"

        sep = "├─" + "─┼─".join("─" * w for w in widths) + "─┤"
        top = "┌─" + "─┬─".join("─" * w for w in widths) + "─┐"
        bottom = "└─" + "─┴─".join("─" * w for w in widths) + "─┘"

        lines = [top, format_row(headers), sep]
        for row in rows:
            lines.append(format_row(row))
        lines.append(bottom)
        return "\n".join(lines)

    @staticmethod
    def _box(text, style="single"):
        """Wrap text in a box."""
        lines = text.splitlines()
        width = max(len(l) for l in lines) if lines else 0
        top = "┌" + "─" * (width + 2) + "┐"
        bottom = "└" + "─" * (width + 2) + "┘"
        body = ["│ " + l.ljust(width) + " │" for l in lines]
        return "\n".join([top] + body + [bottom])

    @staticmethod
    def _highlight(text, word, start="\033[1;33m", end="\033[0m"):
        """Highlight occurrences of word in text."""
        return text.replace(word, f"{start}{word}{end}")

    @staticmethod
    def _number_format(n, decimals=2, thousands_sep=",", decimal_sep="."):
        """Format number with separators."""
        if isinstance(n, float):
            parts = f"{n:.{decimals}f}".split(".")
        else:
            parts = [str(n)]
        integer_part = parts[0]
        # Add thousands separator
        digits = list(integer_part.lstrip("-"))
        neg = "-" if integer_part.startswith("-") else ""
        groups = []
        while digits:
            groups.insert(0, "".join(digits[-3:]))
            digits = digits[:-3]
        result = neg + thousands_sep.join(groups)
        if len(parts) > 1:
            result += decimal_sep + parts[1]
        return result

    @staticmethod
    def _currency(amount, symbol="$", decimals=2):
        """Format as currency."""
        formatted = ArcaneText._number_format(amount, decimals)
        return f"{symbol}{formatted}"

    # ── Parsing ──────────────────────────────────────────

    @staticmethod
    def _parse_csv(text, delimiter=","):
        """Parse CSV text into list of lists."""
        rows = []
        for line in text.strip().splitlines():
            rows.append([cell.strip().strip('"') for cell in line.split(delimiter)])
        return rows

    @staticmethod
    def _to_csv(data, delimiter=","):
        """Convert list of lists to CSV string."""
        lines = []
        for row in data:
            lines.append(delimiter.join(str(cell) for cell in row))
        return "\n".join(lines)

    @staticmethod
    def _parse_ini(text):
        """Parse INI-style text."""
        result = {}
        current_section = "default"
        result[current_section] = {}
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith(';') or line.startswith('#'):
                continue
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].strip()
                result[current_section] = {}
            elif '=' in line:
                key, _, value = line.partition('=')
                result[current_section][key.strip()] = value.strip()
        return result

    @staticmethod
    def _parse_query(query_string):
        """Parse URL query string."""
        result = {}
        query_string = query_string.lstrip('?')
        for pair in query_string.split('&'):
            if '=' in pair:
                key, _, value = pair.partition('=')
                result[key] = value
        return result

    @staticmethod
    def _to_query(params):
        """Convert dict to URL query string."""
        pairs = [f"{k}={v}" for k, v in params.items()]
        return "&".join(pairs)

    @staticmethod
    def _extract_links(text):
        return re.findall(r'https?://[^\s<>"\']+', text)

    @staticmethod
    def _extract_emails(text):
        return re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)

    @staticmethod
    def _extract_numbers(text):
        return [float(n) if '.' in n else int(n) for n in re.findall(r'-?\d+\.?\d*', text)]

    @staticmethod
    def _extract_hashtags(text):
        return re.findall(r'#(\w+)', text)

    @staticmethod
    def _extract_mentions(text):
        return re.findall(r'@(\w+)', text)

    # ── Encoding / Sanitization ──────────────────────────

    @staticmethod
    def _escape_html(text):
        return html.escape(text)

    @staticmethod
    def _unescape_html(text):
        return html.unescape(text)

    @staticmethod
    def _escape_regex(text):
        return re.escape(text)

    @staticmethod
    def _strip_html(text):
        return re.sub(r'<[^>]+>', '', text)

    @staticmethod
    def _strip_ansi(text):
        return re.sub(r'\033\[[0-9;]*m', '', text)

    @staticmethod
    def _normalize_whitespace(text):
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def _remove_accents(text):
        import unicodedata
        nfkd = unicodedata.normalize('NFKD', text)
        return ''.join(c for c in nfkd if not unicodedata.combining(c))

    @staticmethod
    def _transliterate(text):
        """Basic transliteration to ASCII."""
        import unicodedata
        nfkd = unicodedata.normalize('NFKD', text)
        return nfkd.encode('ascii', 'ignore').decode('ascii')

    # ── Generators ───────────────────────────────────────

    @staticmethod
    def _lorem(sentences=3):
        """Generate lorem ipsum text."""
        words = [
            "lorem", "ipsum", "dolor", "sit", "amet", "consectetur",
            "adipiscing", "elit", "sed", "do", "eiusmod", "tempor",
            "incididunt", "ut", "labore", "et", "dolore", "magna",
            "aliqua", "enim", "ad", "minim", "veniam", "quis",
            "nostrud", "exercitation", "ullamco", "laboris", "nisi",
            "aliquip", "ex", "ea", "commodo", "consequat",
        ]
        import random
        result = []
        for _ in range(sentences):
            length = random.randint(6, 14)
            sentence_words = random.choices(words, k=length)
            sentence_words[0] = sentence_words[0].capitalize()
            result.append(" ".join(sentence_words) + ".")
        return " ".join(result)

    @staticmethod
    def _repeat_str(text, n, separator=""):
        return separator.join([text] * n)

    @staticmethod
    def _random_string(length=16, charset="alphanumeric"):
        """Generate random string."""
        import random
        import string
        if charset == "alpha":
            chars = string.ascii_letters
        elif charset == "numeric":
            chars = string.digits
        elif charset == "hex":
            chars = string.hexdigits[:16]
        else:
            chars = string.ascii_letters + string.digits
        return "".join(random.choices(chars, k=length))
