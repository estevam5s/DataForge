import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "tabela",
  description: "Tabelas, molduras, barras e sparklines para o terminal.",
};

const blocos: Bloco[] = [
  { code: `dataforge add tabela`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"]]}},
  {"h2": "Por que existe"},
  {"p": "Alinhar colunas à mão com `pad_end` funciona até a primeira célula colorida: os códigos ANSI contam como caracteres e a tabela entorta. Aqui a largura ignora o que não é visível."},
  {"h2": "Exemplo"},
  { code: `adopt tabela as Tb

out Tb.render([
    ["Arcane.Math", 45, 98.2],
    ["Arcane.Text", 68, 95.0]
], ["Módulo", "Símbolos", "Cobertura"])

// ┌─────────────┬──────────┬───────────┐
// │ Módulo      │ Símbolos │ Cobertura │
// ├─────────────┼──────────┼───────────┤
// │ Arcane.Math │       45 │      98.2 │
// │ Arcane.Text │       68 │      95.0 │
// └─────────────┴──────────┴───────────┘

out Tb.barra(45, 68, 20)               // █████████████░░░░░░░
out Tb.sparkline([3, 7, 12, 9, 18])    // ▁▃▅▄█
out Tb.caixa("tudo verde", "Status")`, lang: 'df' },
  {"h2": "API"},
  {"table": {"head": ["Função", "O que faz"], "rows": [["`render(linhas, cabecalho, estilo)`", "a tabela"], ["`de_records(itens, campos)`", "tabela a partir de vaults"], ["`barra(valor, max, largura)`", "barra proporcional"], ["`sparkline(valores)`", "gráfico de uma linha"], ["`caixa(texto, titulo, estilo)`", "bloco emoldurado"], ["`lista(itens, marcador)`", "lista com marcador"], ["`colorir(texto, cor)`", "cor ANSI"], ["`largura_visivel(texto)`", "largura ignorando ANSI"], ["`ESTILOS`", "simples, dupla, grossa, ascii, markdown"]]}},
  {"h2": "Instalar"},
  { code: `dataforge add tabela
dataforge add tabela@1.0.0
dataforge add tabela@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'exemplo', text: "Exemplo", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"tabela"}
      description={"Tabelas, molduras, barras e sparklines para o terminal."}
      href={"/docs/pacotes/tabela"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
