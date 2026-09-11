import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Decoradores",
  description: "mark @nome — envolver uma ação sem alterar seu corpo.",
};

const blocos: Bloco[] = [
  {"h2": "A forma"},
  { code: `action com_log(fn):
    action envolvida(x):
        out $"  [log] chamada com {x}"
        yield fn(x)
    yield envolvida

mark @com_log
action triplo(x):
    yield x * 3

out triplo(5)` },
  { code: `  [log] chamada com 5
15`, lang: 'text', title: `saída` },
  {"p": "Um decorador é uma ação que **recebe** a ação decorada e **devolve** a substituta. `mark @nome` faz a troca."},
  {"h2": "Empilhar"},
  { code: `mark @medir_tempo
mark @com_log
action processar(dados):
    yield transformar(dados)` },
  {"p": "O mais **próximo** da ação é aplicado primeiro. Aqui: `com_log` envolve `processar`, e `medir_tempo` envolve o resultado."},
  {"h2": "Com argumentos"},
  { code: `action repetir(vezes):
    action decorador(fn):
        action envolvida(x):
            resultado := void
            cycle _ in range(0, vezes):
                resultado := fn(x)
            yield resultado
        yield envolvida
    yield decorador

mark @repetir(3)
action tentar(x):
    out $"tentando {x}"
    yield x` },
  {"p": "Com argumentos, o decorador é chamado primeiro com eles, e o resultado recebe a ação. São três níveis de aninhamento — por isso decoradores com argumentos merecem um comentário explicando o que fazem."},
  {"h2": "Casos úteis"},
  {"h3": "Cache"},
  { code: `action cachear(fn):
    memoria := {}
    action envolvida(x):
        chave := str(x)
        given memoria.has(chave):
            yield memoria[chave]
        valor := fn(x)
        memoria[chave] := valor
        yield valor
    yield envolvida

mark @cachear
action calculo_pesado(n):
    yield n ** 3` },
  {"h3": "Validação"},
  { code: `action exige_positivo(fn):
    action envolvida(n):
        guard n bigger 0, $"esperava um numero positivo, veio {n}"
        yield fn(n)
    yield envolvida

mark @exige_positivo
action raiz(n):
    yield sqrt(n)` },
  {"h3": "Cronometrar"},
  { code: `adopt Arcane.Time as Time

action medir(fn):
    action envolvida(x):
        crono := Time.stopwatch()
        crono.start()
        resultado := fn(x)
        out $"  levou {round(crono.stop() * 1000, 2)} ms"
        yield resultado
    yield envolvida` },
  {"h2": "Quando não usar"},
  {"p": "Um decorador esconde comportamento. Isso é bom para preocupações transversais — log, cache, tempo, autorização — e ruim para lógica de negócio, que fica invisível em quem lê a ação."},
  {"callout": {"tipo": "nota", "texto": "Se o decorador muda o **resultado** da ação de forma não óbvia, provavelmente deveria ser uma chamada explícita."}},
];

const headings = [{ id: 'a-forma', text: "A forma", level: 2 as const }, { id: 'empilhar', text: "Empilhar", level: 2 as const }, { id: 'com-argumentos', text: "Com argumentos", level: 2 as const }, { id: 'casos-uteis', text: "Casos úteis", level: 2 as const }, { id: 'cache', text: "Cache", level: 3 as const }, { id: 'validacao', text: "Validação", level: 3 as const }, { id: 'cronometrar', text: "Cronometrar", level: 3 as const }, { id: 'quando-nao-usar', text: "Quando não usar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Decoradores"}
      description={"mark @nome — envolver uma ação sem alterar seu corpo."}
      href={"/docs/fundamentos/decoradores"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
