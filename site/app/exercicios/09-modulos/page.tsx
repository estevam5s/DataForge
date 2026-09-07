import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "09 · Módulos",
  description: "12 exercícios: `adopt` local e da stdlib, Math, Analytics, IO e SQLite.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 09`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["099", "**adopt de um modulo local**", "importe um arquivo .df vizinho e use suas acoes."], ["100", "**Import inexistente**", "comprove que importar um modulo que nao existe dispara erro."], ["101", "**Arcane.Math**", "use funcoes matematicas da biblioteca padrao."], ["102", "**Estatistica descritiva**", "calcule medidas de posicao e dispersao."], ["103", "**Arcane.Analytics**", "explore correlacao, percentis e outliers."], ["104", "**Regressao linear**", "ajuste uma reta e faca previsoes."], ["105", "**Dados tabulares**", "agrupe e resuma registros com Arcane.Analytics."], ["106", "**Arcane.IO**", "escreva, leia e apague um arquivo temporario."], ["107", "**JSON**", "serialize e desserialize estruturas."], ["108", "**Arcane.Database**", "crie uma tabela em memoria, insira e consulte."], ["109", "**Arcane.Text**", "formate um relatorio em caixa e tabela."], ["110", "**Arcane.Test**", "escreva asserts de biblioteca para uma funcao."]]}},
  {"h2": "099 · adopt de um modulo local"},
  {"p": "Importe um arquivo .df vizinho e use suas acoes."},
  { code: `// Exercicio 099 — adopt de um modulo local
// Enunciado: importe um arquivo .df vizinho e use suas acoes.

adopt geometria as geo

out "PI       =", geo.PI
out "circulo  =", round(geo.area_circulo(2), 4)
out "retangulo=", geo.area_retangulo(3, 4)

assert round(geo.area_circulo(1), 5) is 3.14159, "area do circulo"
assert geo.area_retangulo(3, 4) is 12, "area do retangulo"
assert round(geo.perimetro_circulo(1), 5) is 6.28319, "perimetro"
`, title: `099_adopt_local.df` },
  {"h2": "100 · Import inexistente"},
  {"p": "Comprove que importar um modulo que nao existe dispara erro."},
  { code: `// Exercicio 100 — Import inexistente
// Enunciado: comprove que importar um modulo que nao existe dispara erro.

falhou := no
monitor:
    adopt Arcane.NaoExiste as inexistente
    out inexistente
handle e:
    falhou := yes
    out "erro esperado:", e.type

assert falhou is yes, "modulo inexistente dispara ImportError"

adopt Arcane.Math as M
assert M.sqrt(9) is 3.0, "modulo valido funciona"
out "Math.sqrt(9) =", M.sqrt(9)
`, title: `100_adopt_erro.df` },
  {"h2": "Os demais"},
  {"p": "Os outros 10 exercícios deste módulo estão em `exercicios/09-modulos/`. Rode-os com o comando acima."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '099--adopt-de-um-modulo-local', text: "099 · adopt de um modulo local", level: 2 as const }, { id: '100--import-inexistente', text: "100 · Import inexistente", level: 2 as const }, { id: 'os-demais', text: "Os demais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"09 · Módulos"}
      description={"12 exercícios: `adopt` local e da stdlib, Math, Analytics, IO e SQLite."}
      href={"/exercicios/09-modulos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
