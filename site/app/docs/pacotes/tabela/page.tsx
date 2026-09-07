import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "tabela",
  description: "Tabelas de texto para o terminal: bordas, alinhamento, cores, barras e sparklines.",
};

const blocos: Bloco[] = [
  { code: `dataforge add tabela`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"], ["Exporta", "14 símbolos"]]}},
  {"h2": "Por que existe"},
  {"p": "Alinhar colunas à mão funciona até a primeira célula colorida: os códigos ANSI contam como caracteres e a tabela entorta. Aqui a largura ignora o que não é visível."},
  {"h2": "Uso"},
  { code: `adopt tabela as Tb
out Tb.render([["Ana", 30], ["Bruno", 25]], ["Nome", "Idade"])

┌───────┬───────┐
│ Nome  │ Idade │
├───────┼───────┤
│ Ana   │    30 │
│ Bruno │    25 │
└───────┴───────┘`, lang: 'df' },
  {"h2": "API"},
  {"p": "O que `relay` exporta — 14 símbolos:"},
  { code: `contar_colunas(linhas)
medir_colunas(linhas, n_colunas)
colunas_numericas(linhas, n_colunas)
render(linhas, cabecalho := void, estilo := "simples")
de_records(itens, campos := void, estilo := "simples")
barra(valor, maximo, largura := 24, cheio := "█", vazio := "░")
sparkline(valores)
caixa(texto, titulo := "", estilo := "simples", largura := 0)
lista(itens, marcador := "•", recuo := 2)
colorir(texto, cor)
encher(texto, largura, direita := no)
largura_visivel(texto)
ESTILOS
CORES`, lang: 'df' },
  {"h2": "Instalar"},
  { code: `dataforge add tabela
dataforge add tabela@1.0.0
dataforge add tabela@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'uso', text: "Uso", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"tabela"}
      description={"Tabelas de texto para o terminal: bordas, alinhamento, cores, barras e sparklines."}
      href={"/docs/pacotes/tabela"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
