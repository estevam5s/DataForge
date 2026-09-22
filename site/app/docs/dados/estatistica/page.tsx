// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Estatística descritiva",
  description: "descrever, correlação, discretizar e contar valores — e a média que mente com a cauda.",
};

const blocos: Bloco[] = [
  {"p": "`descrever` responde as perguntas de sempre de uma vez — contagem, média, desvio, mínimo, quartis, máximo — por coluna numérica. É o primeiro número a olhar depois do perfil."},
  { code: `adopt Arcane.Quadro as Q

salarios := Q.de_colunas({"salario": [2000, 2100, 2200, 2300, 2400, 50000]})
out salarios.descrever().texto()

// A media diz 10.166; a mediana, 2.250. Um salario puxa a media para cima.
assert mean(salarios.coluna("salario")) bigger 10000
assert median(salarios.coluna("salario")) is 2250`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "A média esconde a cauda", "texto": "Seis salários, cinco perto de 2.200 e um de 50.000: a média é 10.166 — um salário que ninguém ganha. Com cauda longa (renda, tempo de resposta, preço de imóvel), reporte a **mediana** e os percentis. É a mesma razão por que o `Arcane.Perfil` mede P50/P95/P99 e não a média."}},
  { code: `adopt Arcane.Quadro as Q

q := Q.de_vaults([
    {"horas": 1, "nota": 5}, {"horas": 2, "nota": 6},
    {"horas": 3, "nota": 7}, {"horas": 4, "nota": 9}])
c := q.correlacao()
out c.texto()

faixas := Q.de_colunas({"idade": [15, 22, 37, 41, 68]}).discretizar("idade", 3)
out faixas.texto()

cores := Q.de_colunas({"cor": ["azul", "verde", "azul", "azul"]}).contar_valores("cor")
out cores.texto()`, lang: 'df' },
  {"p": "Correlação não é causa: horas de estudo e nota andam juntas aqui, e isso não diz qual puxa qual — nem se um terceiro fator puxa as duas."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Estatística descritiva"}
      description={"descrever, correlação, discretizar e contar valores — e a média que mente com a cauda."}
      href={"/docs/dados/estatistica"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
