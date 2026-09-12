import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Número exato",
  description: "Arcane.Decimal — para quando 0,1 + 0,2 precisa dar 0,3: dinheiro, imposto, e todo número que alguém confere na mão.",
};

const blocos: Bloco[] = [
  { code: `out 0.1 + 0.2        # 0.30000000000000004`, lang: 'df' },
  {"p": "`Float` é IEEE 754 de 64 bits, e ele **não representa 0,1**. Representa o binário mais próximo, e a diferença aparece na soma."},
  {"p": "Isso não é defeito do DataForge — é assim em toda linguagem com ponto flutuante binário, e é o **certo** para física, estatística e gráficos, onde a precisão relativa importa mais que o dígito decimal exato."},
  {"callout": {"tipo": "atencao", "texto": "É errado para dinheiro, para imposto e para qualquer número que uma pessoa vai conferir na mão. Um centavo que some numa linha some de novo num milhão de linhas."}},

  {"h2": "A resposta"},
  { code: `adopt Arcane.Decimal as Dec

a := Dec.de("0.1")
b := Dec.de("0.2")
out a + b            # 0.3`, lang: 'df' },
  {"p": "`Decimal` guarda o número em base **dez**, do jeito que foi escrito. A aritmética é a da própria linguagem — `+`, `-`, `*`, `/`, `bigger`, `is` funcionam — porque o interpretador trata valor por protocolo, e não por tipo."},
  { code: `preco := Dec.de("19.99")
out preco * 3                 # 59.97
out typeof(preco)             # Decimal
out max([Dec.de("3.10"), Dec.de("1.05")])   # 3.10`, lang: 'df' },

  {"h2": "Arredondar é meio-para-cima"},
  { code: `out Dec.arredondar(Dec.de("2.5"))    # 3
out round(2.5)                       # 2.0`, lang: 'df' },
  {"p": "O `round` embutido faz arredondamento **bancário**: 0,5 vira 0 e 2,5 vira 2. É o certo para estatística, porque não enviesa uma série longa."},
  {"p": "Para dinheiro é errado: 2,5 centavos precisam virar 3, **sempre**, ou o cliente reclama do extrato. É a mesma decisão que o pacote `moeda` já tinha tomado."},
  {"p": "Os outros modos continuam à mão: `MEIO_PAR`, `MEIO_PARA_BAIXO`, `CIMA`, `BAIXO`, `TRUNCA`, `LONGE_DO_ZERO`."},

  {"h2": "Repartir sem perder centavo"},
  { code: `partes := Dec.repartir(Dec.de("10.00"), 3)
out partes                   # [3.34, 3.33, 3.33]
out Dec.soma(partes)         # 10.00`, lang: 'df' },
  {"p": "Três vezes 3,33 são 9,99, e o décimo real sumiu. Dividir dinheiro em partes iguais quase nunca dá partes iguais — o resto é distribuído um centavo por parte, que é como uma conta é rateada de verdade."},

  {"h2": "Misturar exato com aproximado é recusado"},
  { code: `erro[DF0301]: '+' entre um Decimal e um Float e recusado.
   = nota: a esquerda e exata e a direita e aproximada; o resultado
           seria aproximado, e a garantia se perderia sem aviso
   = dica: converta o lado que falta:
       Decimal.de(x) + exato       para seguir exato
       Decimal.float(exato) + x    para aceitar o float`, lang: 'text' },
  {"p": "Somar um número exato com um aproximado devolve um aproximado. A recusa é deliberada: sem ela, a garantia que se veio buscar desapareceria em silêncio, e o erro só apareceria três somas depois."},
  {"p": "Com **inteiro** funciona sem conversão — inteiro é exato, então não há nada a perder."},

  {"h2": "`Dec.de(0.1)` devolve `0.1`"},
  {"p": "E não `0.1000000000000000055511151231257827…`, que é o binário cru. A conversão passa pelo texto do número: é o que a pessoa escreveu e o que ela quer dizer. Converter o binário seria tecnicamente mais fiel e praticamente inútil — ninguém digita `0.1` querendo o binário mais próximo dele."},
  {"callout": {"tipo": "dica", "texto": "Ainda assim, prefira `Dec.de(\"0.1\")` com aspas quando o número vier escrito no código. Aí não há float nenhum no caminho, e não há o que discutir."}},

  {"h2": "A tabela inteira"},
  {"table": {"head": ["", "Faz"], "rows": [
    ["`Dec.de(x)`", "texto, inteiro ou float viram exato — aceita vírgula"],
    ["`Dec.de_centavos(1999)`", "`19.99` — a ponte com quem guarda dinheiro em inteiro"],
    ["`Dec.zero()`", "o zero exato"],
    ["`Dec.texto(d, casas)`", "como texto, arredondando se `casas` vier"],
    ["`Dec.float(d)` / `Dec.inteiro(d)`", "de volta — **a exatidão acaba aqui**"],
    ["`Dec.centavos(d)`", "`19.99` vira `1999`"],
    ["`Dec.arredondar(d, casas, modo)`", "meio-para-cima por padrão"],
    ["`Dec.soma(xs)` / `Dec.media(xs)`", "sobre um cluster, exato"],
    ["`Dec.repartir(d, partes, casas)`", "divide sem perder centavo"],
    ["`Dec.abs(d)` / `Dec.sinal(d)`", "valor absoluto e −1/0/1"],
    ["`Dec.casas(d)` / `Dec.e_decimal(x)` / `Dec.modos()`", "perguntar"]]}},

  {"h2": "Quando não usar"},
  {"p": "Para física, estatística, geometria e gráficos, use `Float`. Decimal é mais lento, e a exatidão decimal não é a garantia que esses domínios precisam — ali o que importa é precisão relativa, e o ponto flutuante binário é a ferramenta certa."},
  {"p": "Para dinheiro guardado em banco de dados, considere também o pacote [`moeda`](/docs/pacotes/moeda), que trabalha em centavos inteiros e traz a formatação em BRL."},
];

const headings = [{ id: 'a-resposta', text: "A resposta", level: 2 as const }, { id: 'arredondar-e-meio-para-cima', text: "Arredondar é meio-para-cima", level: 2 as const }, { id: 'repartir-sem-perder-centavo', text: "Repartir sem perder centavo", level: 2 as const }, { id: 'misturar-exato-com-aproximado-e-recusado', text: "Misturar exato com aproximado é recusado", level: 2 as const }, { id: 'decde01-devolve-01', text: "`Dec.de(0.1)` devolve `0.1`", level: 2 as const }, { id: 'a-tabela-inteira', text: "A tabela inteira", level: 2 as const }, { id: 'quando-nao-usar', text: "Quando não usar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Número exato"}
      description={"Arcane.Decimal — para quando 0,1 + 0,2 precisa dar 0,3: dinheiro, imposto, e todo número que alguém confere na mão."}
      href={"/docs/tecnicas/decimal"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
