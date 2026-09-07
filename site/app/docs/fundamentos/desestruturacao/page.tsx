import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Desestruturação",
  description: "Extrair vários valores de uma vez, por posição ou por nome.",
};

const blocos: Bloco[] = [
  {"h2": "Por posição"},
  { code: `a, b := [1, 2]
x, y, z := [10, 20, 30]

out a, b, x + y + z` },
  {"p": "O lado direito é percorrido e cada elemento vai para o nome correspondente."},
  {"h3": "A troca sem temporária"},
  { code: `p := "primeiro"
q := "segundo"
p, q := q, p
out p, q` },
  {"p": "O lado direito é avaliado **inteiro antes** de qualquer atribuição acontecer. Por isso não há variável temporária nem risco de sobrescrever `p` antes de ler."},
  {"h3": "Quantidade errada falha"},
  { code: `m, n := [1, 2, 3]
# Cannot unpack 3 value(s) into 2 name(s)` },
  {"p": "Isso é deliberado. Um `[1, 2, 3]` chegando onde se esperavam dois valores quase sempre significa que a suposição sobre os dados estava errada — e falhar alto é melhor que descartar o `3` em silêncio."},
  {"h2": "Com ...resto"},
  { code: `primeiro, ...outros := [1, 2, 3, 4, 5]
out primeiro, outros            # 1 [2, 3, 4, 5]

inicio, ...meio, fim := [1, 2, 3, 4, 5]
out inicio, meio, fim           # 1 [2, 3, 4] 5

so_um, ...nada := [9]
out nada                        # [] — resto vazio é válido` },
  {"p": "Só é permitido **um** `...resto` por desestruturação — com dois, não haveria como saber onde um termina e o outro começa."},
  {"h2": "Por nome"},
  {"p": "Com chaves, a desestruturação passa a ser por **nome**, e a ordem não importa:"},
  { code: `record Usuario:
    nome: String
    idade: Integer
    cidade: String

u := Usuario("Ana", 30, "Floripa")
{nome, cidade} := u
out $"{nome} mora em {cidade}"

config := {"host": "localhost", "porta": 8080}
{host, porta} := config
out $"{host}:{porta}"` },
  {"table": {"head": ["Forma", "Casa por", "Fonte"], "rows": [["`a, b := …`", "posição", "lista, record"], ["`{a, b} := …`", "nome", "vault, record, instância"]]}},
  {"h3": "Chave ausente falha"},
  { code: `Vault has no key 'inexistente' to destructure. Keys: host, porta, debug`, lang: 'text' },
  {"p": "A mensagem lista as chaves que existem — quase sempre o erro é um nome digitado errado, e ver a lista resolve na hora."},
  {"h3": "Resto nomeado"},
  { code: `{nome, ...resto} := u
out resto        # {idade: 30, cidade: Floripa}` },
  {"p": "Útil para \"pegue esses dois campos e passe o resto adiante\" — um padrão comum ao tratar requisições HTTP."},
  {"h2": "Desempacotar no início da ação"},
  { code: `action apresentar(pessoa):
    {nome, idade} := pessoa
    yield $"{nome}, {idade} anos"` },
  {"p": "Duas vantagens sobre usar `pessoa.nome` no corpo inteiro: a primeira linha **documenta** o que a ação consome, e o resto do corpo fica mais curto."},
  {"h2": "Retornar vários valores"},
  {"p": "DataForge não tem tuplas separadas de listas. Devolver vários valores é devolver uma lista, e quem chama desestrutura:"},
  { code: `action divide_com_resto(a, b):
    yield [a ~/ b, a % b]

quociente, resto := divide_com_resto(17, 5)
out $"17 / 5 = {quociente} resto {resto}"` },
  {"p": "Isso lê melhor que `resultado[0]` e `resultado[1]` espalhados pelo código."},
  {"h2": "Comparando"},
  {"table": {"head": ["DataForge", "JavaScript", "Python"], "rows": [["`a, ...r := lista`", "`const [a, ...r] = lista`", "`a, *r = lista`"], ["`{a, b} := obj`", "`const {a, b} = obj`", "—"]]}},
];

const headings = [{ id: 'por-posicao', text: "Por posição", level: 2 as const }, { id: 'com-resto', text: "Com ...resto", level: 2 as const }, { id: 'por-nome', text: "Por nome", level: 2 as const }, { id: 'desempacotar-no-inicio-da-acao', text: "Desempacotar no início da ação", level: 2 as const }, { id: 'retornar-varios-valores', text: "Retornar vários valores", level: 2 as const }, { id: 'comparando', text: "Comparando", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Desestruturação"}
      description={"Extrair vários valores de uma vez, por posição ou por nome."}
      href={"/docs/fundamentos/desestruturacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
