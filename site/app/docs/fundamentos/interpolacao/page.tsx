import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Interpolação",
  description: "Strings com $ que embutem expressões, e como formatar saída legível.",
};

const blocos: Bloco[] = [
  {"h2": "A forma"},
  { code: `nome := "Ana"
idade := 30

out $"Ola {nome}, voce tem {idade} anos"` },
  {"p": "O prefixo `$` liga a interpolação. Sem ele, `{nome}` sai literalmente."},
  {"table": {"head": ["Linguagem", "Equivalente"], "rows": [["Python", "`f\"Ola, {nome}\"`"], ["JavaScript", "`` `Ola, ${nome}` ``"], ["C#", "`$\"Ola, {nome}\"`"], ["Kotlin", "`\"Ola, $nome\"`"]]}},
  {"h2": "Por que o $ é obrigatório"},
  { code: `out "{nome}"      # sai literalmente: {nome}
out $"{nome}"     # sai: Ana` },
  {"p": "Isso preserva código existente e permite escrever JSON, regex e templates de outros sistemas sem escapar nada."},
  {"h2": "O que cabe dentro"},
  {"p": "Qualquer expressão:"},
  { code: `out $"{idade + 1}"                                  # aritmética
out $"{moeda(saldo)}"                               # chamada de ação
out $"{usuario["tags"][0]}"                         # índices e chaves
out $"{"par" given n % 2 is 0 otherwise "impar"}"   # ternário
out $"{[x * 2 cycle x in nums]}"                    # compreensão` },
  {"p": "Inclusive strings com aspas duplas dentro — o lexer acompanha o aninhamento."},
  {"h2": "Formatação segue a linguagem"},
  { code: `out $"{yes} {no} {void}"     # "yes no void", não "True False None"` },
  {"p": "Os valores usam as mesmas regras de `out`: um record com `toString` usa o seu `toString`, uma lista sai como `[1, 2, 3]`."},
  {"h2": "Chaves literais"},
  { code: `out $"{{isso e literal}} e {nome} e interpolado"
# {isso e literal} e Ana e interpolado` },
  {"h2": "Multilinha"},
  { code: `out $"""
Relatorio de {mes}
{"-".repeat(30)}
Total: {total}
"""` },
  {"h2": "Alinhar colunas"},
  {"p": "`pad_end` para texto, `pad_start` para número:"},
  { code: `cycle p in produtos:
    out $"{p.nome.pad_end(12)}{str(p.qtd).pad_start(5)}{str(p.preco).pad_start(10)}"` },
  { code: `Mouse          15      80.0
Teclado         3     200.0`, lang: 'text', title: `saída` },
  {"h2": "Comparando com concatenação"},
  { code: `antigo := "Ola, " + nome + "! Voce tem " + str(idade) + " anos."
novo := $"Ola, {nome}! Voce tem {idade} anos."` },
  {"p": "A segunda tem menos ruído, menos `+` e nenhum `str()`. As duas produzem exatamente o mesmo texto."},
  {"callout": {"tipo": "nota", "texto": "`$\"{}\"` com chaves vazias é erro do lexer: `Empty interpolation: '{}' needs an expression`. Melhor falhar do que produzir texto vazio em silêncio."}},
];

const headings = [{ id: 'a-forma', text: "A forma", level: 2 as const }, { id: 'por-que-o--e-obrigatorio', text: "Por que o $ é obrigatório", level: 2 as const }, { id: 'o-que-cabe-dentro', text: "O que cabe dentro", level: 2 as const }, { id: 'formatacao-segue-a-linguagem', text: "Formatação segue a linguagem", level: 2 as const }, { id: 'chaves-literais', text: "Chaves literais", level: 2 as const }, { id: 'multilinha', text: "Multilinha", level: 2 as const }, { id: 'alinhar-colunas', text: "Alinhar colunas", level: 2 as const }, { id: 'comparando-com-concatenacao', text: "Comparando com concatenação", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Interpolação"}
      description={"Strings com $ que embutem expressões, e como formatar saída legível."}
      href={"/docs/fundamentos/interpolacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
