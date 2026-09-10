import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "04 · Strings",
  description: "10 exercícios: interpolação, métodos de texto, formatação e regex.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 04`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["039", "**Strings basicas**", "monte, meca e indexe textos."], ["040", "**Caixa e limpeza**", "normalize um texto sujo vindo de um formulario."], ["041", "**Busca dentro de texto**", "descubra se e onde um trecho aparece."], ["042", "**split e join**", "converta um CSV de uma linha em cluster e volte para texto."], ["043", "**Substituicao e preenchimento**", "mascare um documento e alinhe uma coluna."], ["044", "**Palindromo**", "verifique se uma frase e palindromo ignorando espacos e caixa."], ["045", "**Contagem de palavras**", "conte palavras e ache a mais frequente."], ["046", "**Templates de texto**", "preencha um modelo com dados de um vault."], ["047", "**Expressoes regulares**", "valide e extraia dados com Arcane.Regex."], ["048", "**Cifra de Cesar**", "cifre e decifre um texto deslocando as letras."]]}},
  {"p": "Rode um isolado com `dataforge run exercicios/04-strings/039_basico_strings.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"04 · Strings"}
      description={"10 exercícios: interpolação, métodos de texto, formatação e regex."}
      href={"/docs/exercicios/04-strings"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
