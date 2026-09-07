import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Text",
  description: "Manipulação de texto, tabelas, caixas e conversão de caixa.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Text as Text

out Text.box("Relatorio")
out Text.slug("Ola Mundo DataForge!")
out Text.snake_case("MinhaVariavelLegal")
out Text.truncate("frase bem longa demais", 10)
out Text.number_format(1234567.891, 2)

cabecalho := ["Produto", "Qtd"]
linhas := [["Mouse", "12"], ["Teclado", "5"]]
out Text.table(cabecalho, linhas)`, title: `exemplo` },
  {"h2": "Funções (58)"},
  {"table": {"head": ["Assinatura"], "rows": [["`align(lines, alignment='left', width=None)`"], ["`box(text, style='single')`"], ["`camel_case(text)`"], ["`char_count(text, include_spaces=True)`"], ["`closest(query, candidates, n=3)`"], ["`constant_case(text)`"], ["`currency(amount, symbol='$', decimals=2)`"], ["`dedent(text)`"], ["`diff(a, b)`"], ["`distance(a, b)`"], ["`dot_case(text)`"], ["`escape_html(text)`"], ["`escape_regex(text)`"], ["`extract_emails(text)`"], ["`extract_hashtags(text)`"], ["`extract_links(text)`"], ["`extract_mentions(text)`"], ["`extract_numbers(text)`"], ["`frequency(text)`"], ["`fuzzy_match(query, text, threshold=0.6)`"], ["`highlight(text, word, start='\\x1b[1;33m', end='\\x1b[0m')`"], ["`indent(text, prefix='    ')`"], ["`kebab_case(text)`"], ["`line_count(text)`"], ["`lorem(sentences=3)`"], ["`ngrams(text, n=2)`"], ["`normalize_whitespace(text)`"], ["`number_format(n, decimals=2, thousands_sep=',', decimal_sep='.')`"], ["`pad(text, width, fill=' ', align='left')`"], ["`paragraph_count(text)`"], ["`parse_csv(text, delimiter=',')`"], ["`parse_ini(text)`"], ["`parse_query(query_string)`"], ["`pascal_case(text)`"], ["`path_case(text)`"], ["`random_string(length=16, charset='alphanumeric')`"], ["`reading_time(text, wpm=200)`"], ["`remove_accents(text)`"], ["`render(template, context)`"], ["`repeat_str(text, n, separator='')`"], ["`sentence_case(text)`"], ["`sentence_count(text)`"], ["`similarity(a, b)`"], ["`slug(text)`"], ["`snake_case(text)`"], ["`strip_ansi(text)`"], ["`strip_html(text)`"], ["`table(headers, rows, style='simple')`"], ["`template(text)`"], ["`title_case(text)`"], ["`to_csv(data, delimiter=',')`"], ["`to_query(params)`"], ["`transliterate(text)`"], ["`truncate(text, length=50, suffix='...')`"], ["`unescape_html(text)`"], ["`unified_diff(a, b, a_name='original', b_name='modified')`"], ["`word_count(text)`"], ["`wrap(text, width=80)`"]]}},
];

const headings = [{ id: 'funcoes-58', text: "Funções (58)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Text"}
      description={"Manipulação de texto, tabelas, caixas e conversão de caixa."}
      href={"/biblioteca/text"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
