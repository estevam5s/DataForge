// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/concorrencia_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Padrões de concorrência",
  description: "Produtor-consumidor, pool de trabalhadores, espalhar e juntar — montados com as peças da biblioteca.",
};

const blocos: Bloco[] = [
  {"h2": "Pool de trabalhadores"},
  {"p": "N trabalhadores tirando tarefas de um canal: o número de trabalhadores limita quantas rodam ao mesmo tempo — o que protege o serviço externo que eles chamam."},
  { code: `adopt Arcane.Concurrent as P

fila := P.canal()
resultados := P.ator(lambda acc, r: acc + [r], [])

action trabalhador():
    persist yes:
        t := fila.receber()
        given t is void:
            halt
        resultados.enviar(t * t)

action alimentar():
    cycle i from 1 to 6:
        fila.enviar(i)
    fila.fechar()

parallel:
    alimentar()
    trabalhador()
    trabalhador()
    trabalhador()
assert sorted(resultados.parar()) is [1, 4, 9, 16, 25, 36]`, lang: 'df' },
  {"h2": "Espalhar e juntar"},
  {"p": "Muitas chamadas independentes ao mesmo tempo, e o resultado de todas na ordem da entrada — `P.map` faz os dois, com um teto de trabalhadores:"},
  { code: `adopt Arcane.Concurrent as P

action buscar_preco(item):
    sleep(10)                         // a rede
    yield len(item) * 10

precos := P.map(buscar_preco, ["café", "chá", "açúcar"], 3)
assert precos is [40, 30, 60]         // na ordem da entrada, não da chegada`, lang: 'df' },
  {"table": {"head": ["Padrão", "Peças"], "rows": [["produtor-consumidor", "`P.canal(n)` — a capacidade é a contrapressão"], ["pool de trabalhadores", "canal + N threads + um ator para os resultados"], ["espalhar e juntar", "`P.map(acao, itens, trabalhadores)`"], ["estado disputado", "`P.ator`"], ["várias escritas que andam juntas", "`Arcane.Stm`"]]}},
];

const headings = [{ id: 'pool-de-trabalhadores', text: "Pool de trabalhadores", level: 2 as const }, { id: 'espalhar-e-juntar', text: "Espalhar e juntar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Padrões de concorrência"}
      description={"Produtor-consumidor, pool de trabalhadores, espalhar e juntar — montados com as peças da biblioteca."}
      href={"/docs/concorrencia/padroes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
