// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/regex.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Regex",
  description: "Expressões regulares e validadores brasileiros (CPF, CNPJ, telefone).",
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
  {"table": {"head": ["Nome", "Valor"], "rows": [["`DOTALL`", "`16`"], ["`IGNORECASE`", "`2`"], ["`MULTILINE`", "`8`"], ["`patterns`", "`{\"email\": \"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\\\.[a-zA-Z]{2,…`"]]}},
  {"h2": "Funções (42)"},
  {"table": {"head": ["Assinatura"], "rows": [["`between(pattern_start, pattern_end, string, flags=0)`"], ["`clean_whitespace(string)`"], ["`compile(pattern, flags=0)`"], ["`count(pattern, string, flags=0)`"], ["`escape(string)`"], ["`explain(pattern)`"], ["`extract(pattern, string, flags=0)`"], ["`extract_emails(string)`"], ["`extract_numbers(string)`"], ["`extract_urls(string)`"], ["`extract_words(string)`"], ["`findall(pattern, string, flags=0)`"], ["`finditer(pattern, string, flags=0)`"], ["`findnamed(pattern, string, flags=0)`"], ["`fullmatch(pattern, string, flags=0)`"], ["`group_names(pattern)`"], ["`highlight(pattern, string, before='[', after=']', flags=0)`"], ["`is_cnpj(string)`"], ["`is_cpf(string)`"], ["`is_date(string)`"], ["`is_email(string)`"], ["`is_exactly(pattern, string, flags=0)`"], ["`is_ipv4(string)`"], ["`is_phone(string)`"], ["`is_url(string)`"], ["`mask(string, pattern, mask_char='*')`"], ["`match(pattern, string, flags=0)`"], ["`named(pattern, string, flags=0)`"], ["`positions(pattern, string, flags=0)`"], ["`remove_html(string)`"], ["`replace_all(pattern, repl, string)`"], ["`replace_map(pattern, table, string, flags=0)`"], ["`risk(pattern)`"], ["`safe_search(pattern, string, ms=100, flags=0)`"], ["`search(pattern, string, flags=0)`"], ["`split(pattern, string, maxsplit=0, flags=0)`"], ["`split_keep(pattern, string, flags=0)`"], ["`sub(pattern, repl, string, count=0, flags=0)`"], ["`sub_with(pattern, action, string, count=0, flags=0)`"], ["`subn(pattern, repl, string, count=0, flags=0)`"], ["`test(pattern, string, flags=0)`"], ["`word_count(string)`"]]}},
];

const headings = [{ id: 'constantes', text: "Constantes", level: 2 as const }, { id: 'funcoes-42', text: "Funções (42)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Regex"}
      description={"Expressões regulares e validadores brasileiros (CPF, CNPJ, telefone)."}
      href={"/docs/biblioteca/regex"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
