import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Campos e visibilidade",
  description: "Declarar o que o objeto tem, e decidir quem enxerga.",
};

const blocos: Bloco[] = [
  {"h2": "Campos declarados"},
  { code: `blueprint Contador:
    valor: Integer := 0
    passo: Integer := 1

    action somar():
        self.valor += self.passo
        yield self.valor`, lang: 'df' },
  {"p": "Declarar o campo separa **o que o objeto tem** de **como ele nasce**. Antes do 4.1, para saber a forma de um objeto era preciso ler o `setup` inteiro."},
  {"list": ["Sem padrão, o campo nasce `void` — não é erro, é o valor que diz \"ainda não tem\"", "Campos são herdados; o filho enxerga os do pai sem redeclarar", "A anotação de tipo é verificada pelo analisador estático"]},
  {"callout": {"tipo": "atencao", "titulo": "O padrão é avaliado uma vez", "texto": "Na declaração do blueprint, não a cada `spawn`. Para um valor que precisa ser novo em cada objeto — uma lista, um vault — atribua no `setup`."}},
  {"h2": "Visibilidade"},
  { code: `blueprint Conta:
    private saldo: Float := 0.0      // só dentro de Conta
    protected titular: String := ""  // Conta e seus herdeiros
    numero: String := ""             // público`, lang: 'df' },
  {"p": "Em DataForge, `private` **impede de verdade** — não é convenção. O acesso de fora é recusado, dizendo de onde partiu:"},
  { code: `erro[DF0301]: 'Conta.saldo' is private and was accessed outside any blueprint.
              Only 'Conta' can read it.`, lang: 'text' },
  {"table": {"head": ["", "Quem enxerga"], "rows": [["(nada)", "qualquer código"], ["`protected`", "o blueprint e seus herdeiros"], ["`private`", "só o próprio blueprint"]]}},
  {"p": "O que fica público é a promessa que você mantém. O resto pode mudar sem avisar ninguém — e é essa liberdade que a visibilidade compra."},
  {"h2": "Modificadores combinam"},
  { code: `blueprint Conta:
    private static contador: Integer := 0
    private action registrar_operacao(tipo):
        …`, lang: 'df' },
  {"p": "A ordem não importa: `private static action f()` e `static private action f()` são a mesma coisa."},
  {"h2": "Palavras contextuais"},
  {"p": "`private`, `protected`, `get`, `set`, `operator`, `final` e `abstract` **não são reservadas**. Só têm significado dentro do corpo de um blueprint:"},
  { code: `final := 10                  // uma variável chamada 'final'
action get(chave):           // uma ação chamada 'get'
    yield chave

blueprint Conta:
    private saldo: Float := 0.0    // aqui 'private' é modificador`, lang: 'df' },
  {"p": "Foi deliberado: `get` e `final` são nomes bons demais para tirar de quem escreve. Reservá-los globalmente quebrou três arquivos do próprio repositório na primeira tentativa."},
];

const headings = [{ id: 'campos-declarados', text: "Campos declarados", level: 2 as const }, { id: 'visibilidade', text: "Visibilidade", level: 2 as const }, { id: 'modificadores-combinam', text: "Modificadores combinam", level: 2 as const }, { id: 'palavras-contextuais', text: "Palavras contextuais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Campos e visibilidade"}
      description={"Declarar o que o objeto tem, e decidir quem enxerga."}
      href={"/docs/oop/campos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
