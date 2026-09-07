import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "moeda",
  description: "Dinheiro sem erro de ponto flutuante: centavos inteiros, câmbio e formatação BRL.",
};

const blocos: Bloco[] = [
  { code: `dataforge add moeda`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"], ["Exporta", "24 símbolos"]]}},
  {"h2": "Por que existe"},
  {"p": "`0.1 + 0.2` não dá `0.3` em ponto flutuante. Com dinheiro isso vira centavo perdido, e centavo perdido vira conferência de fechamento. Aqui tudo é inteiro de centavos."},
  {"h2": "Uso"},
  { code: `adopt moeda as M
preco := M.de_reais(19.90)
total := M.multiplicar(preco, 3)
out M.formatar(total)          // R$ 59,70`, lang: 'df' },
  {"h2": "API"},
  {"p": "O que `relay` exporta — 24 símbolos:"},
  { code: `record Dinheiro
SIMBOLOS
meio_acima(x)
de_centavos(centavos, simbolo := "BRL")
de_reais(valor, simbolo := "BRL")
de_texto(texto, simbolo := "BRL")
em_reais(d)
somar(a, b)
subtrair(a, b)
multiplicar(d, fator)
dividir(d, divisor)
conferir_moeda(a, b)
repartir(d, partes)
repartir_por_peso(d, pesos)
percentual(d, taxa)
com_desconto(d, taxa)
com_acrescimo(d, taxa)
e_zero(d)
e_negativo(d)
comparar(a, b)
maior(a, b)
total(lista)
formatar(d, com_simbolo := yes)
converter(d, para, taxa)`, lang: 'df' },
  {"h2": "Instalar"},
  { code: `dataforge add moeda
dataforge add moeda@1.0.0
dataforge add moeda@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'uso', text: "Uso", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"moeda"}
      description={"Dinheiro sem erro de ponto flutuante: centavos inteiros, câmbio e formatação BRL."}
      href={"/docs/pacotes/moeda"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
