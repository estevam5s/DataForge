import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Spread e rest",
  description: "O operador ... expandindo coleções e coletando o que sobra.",
};

const blocos: Bloco[] = [
  {"h2": "Dois trabalhos opostos"},
  {"p": "`...` faz coisas diferentes conforme o lado em que aparece:"},
  {"table": {"head": ["Posição", "Significa", "Exemplo"], "rows": [["esquerda do `:=`", "**coleta**", "`a, ...resto := lista`"], ["dentro de `[…]`", "**expande**", "`[...a, ...b]`"], ["dentro de `{…}`", "**expande**", "`{...padrao, ...usuario}`"], ["numa chamada", "**expande** argumentos", "`f(...args)`"]]}},
  {"h2": "Expandir listas"},
  { code: `a := [1, 2]
b := [3, 4]

out [...a, ...b, 5]           # [1, 2, 3, 4, 5]
out [0, ...a]                 # [0, 1, 2]
out [...antes, novo, ...depois]   # inserir no meio` },
  {"h2": "Expandir vaults"},
  {"p": "Esta é a aplicação mais comum, e resolve num gesto o que normalmente seriam cinco linhas:"},
  { code: `padrao := {"tema": "claro", "fonte": 14}
usuario := {"tema": "escuro"}

final := {...padrao, ...usuario}
out final                     # {tema: escuro, fonte: 14}` },
  {"p": "**O último vence.** As preferências do usuário sobrescrevem o padrão; o que ele não definiu vem do padrão."},
  {"h2": "Expandir argumentos"},
  { code: `action somar(a, b, c):
    yield a + b + c

args := [1, 2, 3]
out somar(...args)            # 6` },
  {"h2": "Cópia rasa"},
  { code: `original := [1, 2, 3]
copia := [...original]
copia.append(4)

out original, copia           # [1, 2, 3] [1, 2, 3, 4]` },
  {"p": "Cria uma lista **nova**. É \"rasa\" porque objetos *dentro* da lista continuam compartilhados — para uma cópia profunda existe `deep_copy`."},
  {"h2": "Coletar com ...resto"},
  { code: `primeiro, ...outros := [1, 2, 3, 4]
{nome, ...campos} := usuario` },
  {"p": "Detalhes em [Desestruturação](/fundamentos/desestruturacao)."},
  {"h2": "Em pattern matching"},
  { code: `match lista:
    point [primeiro, ...resto]:
        yield $"comeca com {primeiro}, mais {len(resto)}"
    point ["dizer", ...palavras]:
        yield $"dizendo: {palavras.join(" ")}"` },
  {"h2": "O que pode ser expandido"},
  {"list": ["`Cluster` — os elementos", "`String` — os caracteres", "`Vault` — as chaves (em lista) ou os pares (em vault)", "`Stream` — materializa e expande", "Um `record` ou instância, dentro de `{…}` — os campos"]},
  {"p": "Espalhar um número ou `void` dispara erro com a mensagem explicando o que se espera."},
  {"h2": "Comparando"},
  {"table": {"head": ["DataForge", "JavaScript", "Python"], "rows": [["`[...a, ...b]`", "`[...a, ...b]`", "`[*a, *b]`"], ["`{...a, ...b}`", "`{...a, ...b}`", "`{**a, **b}`"], ["`f(...args)`", "`f(...args)`", "`f(*args)`"]]}},
];

const headings = [{ id: 'dois-trabalhos-opostos', text: "Dois trabalhos opostos", level: 2 as const }, { id: 'expandir-listas', text: "Expandir listas", level: 2 as const }, { id: 'expandir-vaults', text: "Expandir vaults", level: 2 as const }, { id: 'expandir-argumentos', text: "Expandir argumentos", level: 2 as const }, { id: 'copia-rasa', text: "Cópia rasa", level: 2 as const }, { id: 'coletar-com-resto', text: "Coletar com ...resto", level: 2 as const }, { id: 'em-pattern-matching', text: "Em pattern matching", level: 2 as const }, { id: 'o-que-pode-ser-expandido', text: "O que pode ser expandido", level: 2 as const }, { id: 'comparando', text: "Comparando", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Spread e rest"}
      description={"O operador ... expandindo coleções e coletando o que sobra."}
      href={"/fundamentos/spread"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
