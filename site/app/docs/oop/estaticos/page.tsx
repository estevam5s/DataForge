import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Métodos estáticos",
  description: "O que pertence à família, não à instância.",
};

const blocos: Bloco[] = [
  { code: `blueprint Temperatura:
    celsius: Float := 0.0

    static action de_fahrenheit(f):
        t := spawn Temperatura()
        t.celsius := (f - 32) * 5 / 9
        yield t

    static action congelamento():
        yield 0.0

    action em_fahrenheit():
        yield self.celsius * 9 / 5 + 32`, lang: 'df' },
  {"h2": "Construtor alternativo"},
  {"p": "É o uso mais comum: uma segunda forma de criar o objeto, com nome que diz o que ela faz."},
  { code: `gelo := Temperatura.de_fahrenheit(32)
config := Config.do_arquivo("app.json")
data := Data.de_iso("2026-09-07")`, lang: 'df' },
  {"p": "`Temperatura.de_fahrenheit(32)` é mais claro que um `setup` com um parâmetro `escala` que muda o significado do primeiro argumento."},
  {"h2": "Valor estático"},
  { code: `blueprint Contador:
    static total := 0            // compartilhado por todas as instâncias

    action setup():
        Contador.total += 1`, lang: 'df' },
  {"callout": {"tipo": "atencao", "texto": "Um valor estático é compartilhado: mudá-lo muda para todas as instâncias, inclusive as que já existem. É estado global com outro nome — use com a mesma cautela."}},
  {"h2": "Erro útil"},
  {"p": "Chamar um método de instância no blueprint mostra o `spawn` que falta, em vez de estourar `Undefined name: self` lá dentro:"},
  { code: `erro[DF0301]: 'Temperatura.em_fahrenheit()' is an instance method and needs an object.
    Spawn one first:
        obj := spawn Temperatura(…)
        obj.em_fahrenheit(…)
    Or declare it as 'static action em_fahrenheit(…)' if it does not use 'self'.`, lang: 'text' },
];

const headings = [{ id: 'construtor-alternativo', text: "Construtor alternativo", level: 2 as const }, { id: 'valor-estatico', text: "Valor estático", level: 2 as const }, { id: 'erro-util', text: "Erro útil", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Métodos estáticos"}
      description={"O que pertence à família, não à instância."}
      href={"/docs/oop/estaticos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
