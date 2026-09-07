import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "04 · Textos",
  description: "10 exercícios: métodos, regex, templates, palíndromo e cifra de César.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 04`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["039", "**Strings basicas**", "monte, meca e indexe textos."], ["040", "**Caixa e limpeza**", "normalize um texto sujo vindo de um formulario."], ["041", "**Busca dentro de texto**", "descubra se e onde um trecho aparece."], ["042", "**split e join**", "converta um CSV de uma linha em cluster e volte para texto."], ["043", "**Substituicao e preenchimento**", "mascare um documento e alinhe uma coluna."], ["044", "**Palindromo**", "verifique se uma frase e palindromo ignorando espacos e caixa."], ["045", "**Contagem de palavras**", "conte palavras e ache a mais frequente."], ["046", "**Templates de texto**", "preencha um modelo com dados de um vault."], ["047", "**Expressoes regulares**", "valide e extraia dados com Arcane.Regex."], ["048", "**Cifra de Cesar**", "cifre e decifre um texto deslocando as letras."]]}},
  {"h2": "039 · Strings basicas"},
  {"p": "Monte, meca e indexe textos."},
  { code: `// Exercicio 039 — Strings basicas
// Enunciado: monte, meca e indexe textos.

nome := "DataForge"
out nome.length(), nome[0], nome[-1], nome[0:4]

assert nome.length() is 9, "tamanho"
assert nome[0] is "D", "primeiro caractere"
assert nome[-1] is "e", "ultimo caractere"
assert nome[0:4] is "Data", "fatia"
assert nome + " v3" is "DataForge v3", "concatenacao"
assert "ab".repeat(3) is "ababab", "repeticao"
`, title: `039_basico_strings.df` },
  {"h2": "040 · Caixa e limpeza"},
  {"p": "Normalize um texto sujo vindo de um formulario."},
  { code: `// Exercicio 040 — Caixa e limpeza
// Enunciado: normalize um texto sujo vindo de um formulario.

bruto := "   joao DA silva   "
limpo := bruto.trim()

out "'" + bruto + "'"
out "'" + limpo + "'"
out limpo.upper(), limpo.lower(), limpo.title()

assert limpo is "joao DA silva", "trim"
assert limpo.upper() is "JOAO DA SILVA", "upper"
assert limpo.lower() is "joao da silva", "lower"
assert limpo.title() is "Joao Da Silva", "title"
assert limpo.capitalize() is "Joao da silva", "capitalize"
`, title: `040_caixa_e_limpeza.df` },
  {"h2": "Os demais"},
  {"p": "Os outros 8 exercícios deste módulo estão em `exercicios/04-strings/`. Rode-os com o comando acima."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '039--strings-basicas', text: "039 · Strings basicas", level: 2 as const }, { id: '040--caixa-e-limpeza', text: "040 · Caixa e limpeza", level: 2 as const }, { id: 'os-demais', text: "Os demais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"04 · Textos"}
      description={"10 exercícios: métodos, regex, templates, palíndromo e cifra de César."}
      href={"/docs/exercicios/04-strings"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
