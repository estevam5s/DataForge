import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Generators",
  description: "stream action e emit: sequências produzidas sob demanda, inclusive infinitas.",
};

const blocos: Bloco[] = [
  {"h2": "A forma"},
  { code: `stream action contar(ate):
    cycle i from 1 to ate:
        emit i

s := contar(5)
out typeof(s)              # Stream
out s.to_cluster()         # [1, 2, 3, 4, 5]
out contar(1000).take(3)   # [1, 2, 3]` },
  {"table": {"head": ["Palavra", "Efeito"], "rows": [["`stream action`", "a chamada devolve um `Stream`, não um valor"], ["`emit`", "produz um item e **continua** de onde parou"]]}},
  {"h2": "emit e yield são coisas diferentes"},
  { code: `action f():
    yield 1        # devolve 1 e ENCERRA a ação

stream action g():
    emit 1         # produz 1 e CONTINUA
    emit 2` },
  {"p": "Em Python as duas ideias dividem a mesma palavra (`yield`), o que é uma fonte conhecida de confusão — uma função vira geradora só por conter um `yield`, sem nada no cabeçalho anunciando isso."},
  {"p": "DataForge separa: `stream action` no cabeçalho diz o que a ação **é**, `emit` diz o que ela **faz**. Dentro de um `stream action`, `yield` ainda serve para encerrar a produção antes do fim."},
  {"h2": "Sequências infinitas"},
  {"p": "Um `persist yes:` dentro de um `stream action` não trava o programa:"},
  { code: `stream action naturais():
    n := 0
    persist yes:
        emit n
        n += 1

out naturais().take(6)     # [0, 1, 2, 3, 4, 5]` },
  {"h3": "Por que funciona"},
  {"p": "O corpo **não roda na chamada**. `naturais()` devolve um `Stream` sem executar nada. A execução acontece sob demanda: cada `emit` roda quando alguém pede o próximo item, e **pausa** logo depois."},
  {"p": "`take(6)` pede seis itens, recebe seis, e para de pedir. O laço infinito simplesmente nunca chega à sétima volta."},
  {"h3": "Fibonacci"},
  { code: `stream action fibonacci():
    a := 0
    b := 1
    persist yes:
        emit a
        a, b := b, a + b

out fibonacci().take(10)   # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]` },
  {"p": "Essa definição é completa e não menciona limite algum. Quem chama decide. Repare no `a, b := b, a + b` — a [desestruturação](/docs/fundamentos/desestruturacao) faz a troca simultânea sem variável temporária."},
  {"h2": "Consumir"},
  {"table": {"head": ["Chamada", "Devolve"], "rows": [["`s.to_cluster()`", "tudo, como lista"], ["`s.take(n)`", "os `n` primeiros"], ["`s.next()`", "o próximo item, ou `void`"], ["`s.count()`", "quantos itens ao todo"], ["`s.first()`", "o primeiro, ou `void`"], ["`s.map(f)` `s.filter(f)`", "lista transformada ou filtrada"], ["`s.reset()`", "reinicia o `next()`"], ["`cycle v in s:`", "percorre item a item"]]}},
  {"callout": {"tipo": "perigo", "texto": "`to_cluster()` num generator **realmente** infinito trava o programa. Use `take(n)` ou garanta um `halt` dentro dele."}},
  {"h2": "Parar por dentro"},
  { code: `stream action ate_passar(limite):
    n := 1
    persist yes:
        given n bigger limite:
            halt
        emit n
        n *= 3

out ate_passar(100).to_cluster()     # [1, 3, 9, 27, 81]` },
  {"p": "Agora `to_cluster()` é seguro: a sequência termina sozinha."},
  {"h2": "Encadear"},
  {"p": "Aqui está o padrão que dá poder à ideia — um generator que consome outro:"},
  { code: `stream action so_pares(fonte):
    cycle v in fonte:
        given v % 2 is 0:
            emit v

stream action dobrar(fonte):
    cycle v in fonte:
        emit v * 2

cadeia := dobrar(so_pares(naturais()))
out cadeia.take(5)     # [4, 8, 12, 16, 20]` },
  {"p": "`naturais()` é infinito. `so_pares` filtra, `dobrar` transforma — e **nada roda** até o `take(5)`. Cada item atravessa a cadeia inteira sob demanda; a memória usada não depende do tamanho da fonte."},
  {"p": "É o mesmo desenho dos pipes do Unix: `yes | grep … | sed …` não trava porque cada estágio consome o anterior aos poucos."},
  {"h2": "Processamento incremental"},
  {"p": "O ganho fica óbvio quando a fonte é grande:"},
  { code: `stream action linhas_do_log():
    cycle l in IO.read("app.log").lines():
        emit l

stream action interpretar(fonte):
    cycle linha in fonte:
        partes := linha.split(" ")
        emit {"data": partes[0], "nivel": partes[1]}

stream action apenas(fonte, nivel):
    cycle registro in fonte:
        given registro["nivel"] is nivel:
            emit registro

primeiro_erro := apenas(interpretar(linhas_do_log()), "ERROR").first()` },
  {"p": "Isso lê até o primeiro erro e **para**. Se ele estiver na linha 3, as outras 999.997 nunca são tocadas."},
  {"h2": "emit fora de um generator"},
  {"p": "Fora do corpo de um `stream action`, `emit` é um alias histórico de `out` — ele imprime. Isso mantém compatível o código escrito antes do 4.0."},
];

const headings = [{ id: 'a-forma', text: "A forma", level: 2 as const }, { id: 'emit-e-yield-sao-coisas-diferentes', text: "emit e yield são coisas diferentes", level: 2 as const }, { id: 'sequencias-infinitas', text: "Sequências infinitas", level: 2 as const }, { id: 'por-que-funciona', text: "Por que funciona", level: 3 as const }, { id: 'fibonacci', text: "Fibonacci", level: 3 as const }, { id: 'consumir', text: "Consumir", level: 2 as const }, { id: 'parar-por-dentro', text: "Parar por dentro", level: 2 as const }, { id: 'encadear', text: "Encadear", level: 2 as const }, { id: 'processamento-incremental', text: "Processamento incremental", level: 2 as const }, { id: 'emit-fora-de-um-generator', text: "emit fora de um generator", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Generators"}
      description={"stream action e emit: sequências produzidas sob demanda, inclusive infinitas."}
      href={"/docs/fundamentos/generators"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
