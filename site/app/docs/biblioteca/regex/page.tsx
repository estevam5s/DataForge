import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Regex",
  description: "Expressões regulares e validadores brasileiros.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Regex as Regex

texto := "contato: ana@exemplo.com, tel (48) 99999-1234"

out Regex.extract_emails(texto)
out Regex.extract_numbers(texto)
out Regex.is_email("ana@exemplo.com")
out Regex.is_cpf("529.982.247-25")
out Regex.replace_all("\\\\d", "#", "abc123")`, title: `exemplo` },
  {"h2": "Constantes"},
  {"table": {"head": ["Nome", "Valor"], "rows": [["`DOTALL`", "`re.DOTALL`"], ["`IGNORECASE`", "`re.IGNORECASE`"], ["`MULTILINE`", "`re.MULTILINE`"], ["`patterns`", "`{'email': '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\\\.…`"]]}},
  {"h2": "Funções (28)"},
  {"table": {"head": ["Assinatura"], "rows": [["`clean_whitespace(string)`"], ["`compile(pattern, flags=0)`"], ["`count(pattern, string, flags=0)`"], ["`escape(string)`"], ["`extract(pattern, string, flags=0)`"], ["`extract_emails(string)`"], ["`extract_numbers(string)`"], ["`extract_urls(string)`"], ["`extract_words(string)`"], ["`findall(pattern, string, flags=0)`"], ["`finditer(pattern, string, flags=0)`"], ["`is_cnpj(string)`"], ["`is_cpf(string)`"], ["`is_date(string)`"], ["`is_email(string)`"], ["`is_ipv4(string)`"], ["`is_phone(string)`"], ["`is_url(string)`"], ["`mask(string, pattern, mask_char='*')`"], ["`match(pattern, string, flags=0)`"], ["`remove_html(string)`"], ["`replace_all(pattern, repl, string)`"], ["`search(pattern, string, flags=0)`"], ["`split(pattern, string, maxsplit=0, flags=0)`"], ["`sub(pattern, repl, string, count=0, flags=0)`"], ["`subn(pattern, repl, string, count=0, flags=0)`"], ["`test(pattern, string, flags=0)`"], ["`word_count(string)`"]]}},
];

const headings = [{ id: 'constantes', text: "Constantes", level: 2 as const }, { id: 'funcoes-28', text: "Funções (28)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Regex"}
      description={"Expressões regulares e validadores brasileiros."}
      href={"/docs/biblioteca/regex"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
