// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/reativo_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Dados que chegam depois",
  description: "R.recurso: carregando, pronto ou erro — e a resposta velha que chega por último e não pode vencer.",
};

const blocos: Bloco[] = [
  {"p": "Toda tela que busca dados fora tem três estados: **carregando** (o spinner), **pronto** (o dado) e **erro** (a mensagem). `R.recurso` guarda os três num sinal, e busca de novo quando a fonte muda."},
  { code: `adopt Arcane.Reativo as R

busca := R.sinal("café")

action buscar(termo):
    sleep(20)                                   // a rede
    yield [$"{termo} torrado", $"{termo} moído"]

resultados := R.recurso(buscar, busca)
assert resultados.aguardar(2)["valor"] is ["café torrado", "café moído"]

busca.escrever("chá")
final := resultados.aguardar(2)
assert final["estado"] is "pronto" and final["valor"][0] is "chá torrado"`, lang: 'df' },
  {"h2": "A resposta velha"},
  {"p": "A pessoa digita \"ca\" e depois \"café\". A busca de \"ca\" é mais lenta e chega **por último** — e sem cuidado a tela mostra o resultado da pergunta velha, com \"café\" escrito na caixa. Cada busca do recurso leva um número de geração, e a resposta de uma geração passada é **descartada**:"},
  { code: `adopt Arcane.Reativo as R

termo := R.sinal("ca")

action buscar(t):
    sleep(300 given t is "ca" otherwise 30)     // a primeira é a lenta
    yield $"resultados de {t}"

r := R.recurso(buscar, termo)
termo.escrever("café")
assert r.aguardar(2)["valor"] is "resultados de café"
sleep(400)                                      // a lenta chega agora…
assert r.ler()["valor"] is "resultados de café" // …e não vence
assert r.descartadas() is 1`, lang: 'df' },
  {"h2": "O erro é um estado, não uma exceção"},
  { code: `adopt Arcane.Reativo as R

r := R.recurso(lambda => 1 / 0)
estado := r.aguardar(2)
assert estado["estado"] is "erro"
out estado["erro"]`, lang: 'df' },
  {"p": "A tela decide lendo `r.estado()`, que é um **sinal**: um derivado ou efeito que o lê redesenha quando a busca termina. `aguardar` existe para teste e para script — numa interface, ninguém espera; quem reage é o efeito."},
];

const headings = [{ id: 'a-resposta-velha', text: "A resposta velha", level: 2 as const }, { id: 'o-erro-e-um-estado-nao-uma-excecao', text: "O erro é um estado, não uma exceção", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Dados que chegam depois"}
      description={"R.recurso: carregando, pronto ou erro — e a resposta velha que chega por último e não pode vencer."}
      href={"/docs/reativo/recursos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
