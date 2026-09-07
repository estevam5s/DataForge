import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Ações",
  description: "Funções em DataForge: parâmetros, tipos, aridade, closures, lambdas, decoradores e defer.",
};

const blocos: Bloco[] = [
  {"h2": "Declarar"},
  { code: `action somar(a, b):
    yield a + b

out somar(2, 3)     # 5` },
  {"p": "`yield` devolve o valor **e encerra a ação**. Sem `yield`, a ação devolve `void`."},
  {"callout": {"tipo": "atencao", "texto": "`yield` aqui é **retorno**, não geração. Para produzir uma sequência existe `stream action` com `emit` — veja [Generators](/fundamentos/generators)."}},
  {"h2": "Parâmetros"},
  {"h3": "Valores padrão"},
  { code: `action criar(nome, papel := "leitor", ativo := yes):
    yield {"nome": nome, "papel": papel, "ativo": ativo}

out criar("Ana")                  # papel = "leitor"
out criar("Bruno", "admin")` },
  {"h3": "Argumentos nomeados"},
  { code: `action retangulo(largura := 1, altura := 1):
    yield largura * altura

out retangulo(altura := 5, largura := 3)     # 15 — fora de ordem` },
  {"h3": "Tipos"},
  { code: `action media(nums: Cluster) -> Float:
    yield sum(nums) / len(nums)

out media([1, 2, 3])     # 2.0` },
  {"p": "Parâmetros e retorno são verificados. A mensagem de erro nomeia exatamente o parâmetro:"},
  { code: `parameter 'nums' of action 'media' declared as Cluster but got String`, lang: 'text' },
  {"h2": "Aridade verificada"},
  {"p": "Chamar com argumentos a mais ou a menos dispara erro — e o [analisador estático](/tecnicas/analise-estatica) acha isso antes de executar:"},
  { code: `action f(a, b):
    yield a + b

# f(1)          -> action 'f' is missing argument(s): b
# f(1, 2, 3)    -> action 'f' takes 2 argument(s) but 3 were given` },
  {"h2": "Recursão"},
  { code: `action fatorial(n):
    given n smaller_eq 1:
        yield 1
    yield n * fatorial(n - 1)

out fatorial(6)     # 720` },
  {"p": "Recursão infinita vira `StackOverflowError_` após 1000 quadros, com o nome da ação culpada na mensagem. Recursões legítimas de até ~900 níveis funcionam."},
  {"h2": "Ações de alta ordem e closures"},
  { code: `action fabrica_somador(n):
    action somador(x):
        yield x + n          # 'n' vem do escopo de fora — isso é a closure
    yield somador

soma10 := fabrica_somador(10)
out soma10(5)                  # 15
out fabrica_somador(3)(4)      # 7 — chamada encadeada` },
  {"h2": "Lambdas"},
  {"p": "Três grafias, todas equivalentes:"},
  { code: `dobro := lambda x: x * 2
soma := lambda a, b => a + b
fixo := lambda: 42

out [1, 2, 3].map(lambda n: n * n)              # [1, 4, 9]
out [1, 2, 3, 4].filter(lambda n: n % 2 is 0)   # [2, 4]` },
  {"h2": "Decoradores"},
  {"p": "`mark @nome` envolve uma ação com outra, sem alterar seu corpo:"},
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
  {"h2": "defer"},
  {"p": "Agenda um bloco para rodar quando a ação terminar — **em qualquer caminho de saída**, inclusive por erro:"},
  { code: `action com_recurso():
    abrir()
    defer:
        fechar()          # roda aconteça o que acontecer
    processar()
    yield "pronto"` },
  {"p": "Vários `defer` rodam em ordem inversa (LIFO), que é a ordem correta para desmontar recursos dependentes. Detalhes em [Tratamento de erros](/erros)."},
];

const headings = [{ id: 'declarar', text: "Declarar", level: 2 as const }, { id: 'parametros', text: "Parâmetros", level: 2 as const }, { id: 'aridade-verificada', text: "Aridade verificada", level: 2 as const }, { id: 'recursao', text: "Recursão", level: 2 as const }, { id: 'acoes-de-alta-ordem-e-closures', text: "Ações de alta ordem e closures", level: 2 as const }, { id: 'lambdas', text: "Lambdas", level: 2 as const }, { id: 'decoradores', text: "Decoradores", level: 2 as const }, { id: 'defer', text: "defer", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Ações"}
      description={"Funções em DataForge: parâmetros, tipos, aridade, closures, lambdas, decoradores e defer."}
      href={"/acoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
