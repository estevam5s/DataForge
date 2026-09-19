// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_quadro.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Quadro — a tabela de dados",
  description: "Colunas nomeadas e linhas como vault: filtrar, agrupar, resumir, juntar, pivotar, limpar e descrever.",
};

const blocos: Bloco[] = [
  {"p": "`Quadro` é a tabela da linguagem. Ele existe porque a forma natural de dado aqui — um cluster de vaults — responde bem a \"percorra\" e mal a \"agrupe por cidade e some o valor\"."},
  { code: `adopt Arcane.Quadro as Q

vendas := Q.de_vaults([
    {"produto": "cafe",   "regiao": "sul",   "valor": 120.0, "qtd": 4},
    {"produto": "cafe",   "regiao": "norte", "valor": 90.0,  "qtd": 3},
    {"produto": "cha",    "regiao": "sul",   "valor": 60.0,  "qtd": 2},
    {"produto": "cha",    "regiao": "norte", "valor": void,  "qtd": 1},
    {"produto": "acucar", "regiao": "sul",   "valor": 30.0,  "qtd": 5}
])

out typeof(vendas)          // Quadro
out vendas.forma()          // [5, 4]
out vendas.texto()
`, lang: 'df' },
  { code: `produto  regiao  valor  qtd
-------  ------  -----  ---
cafe     sul     120    4
cafe     norte   90     3
cha      sul     60     2
cha      norte   void   1
acucar   sul     30     5
[5 linha(s) × 4 coluna(s)]
`, lang: 'text', title: `saída` },
  {"h2": "As cinco decisões"},
  {"table": {"head": ["Decisão", "Porque"], "rows": [["**A linha é um vault**", "é a forma que o resto da linguagem já usa: `IO.read_csv(c, yes)` devolve vaults, `Database.query` devolve vaults, e o `>>` já sabe percorrê-los"], ["**Por dentro é colunar**", "`descrever`, `normalizar` e `correlacao` viram uma passada por coluna em vez de uma por célula"], ["**Todo verbo devolve um quadro NOVO**", "como `record` e `with`: o original nunca muda, e o pipeline fica reexecutável"], ["**A ausência tem um nome só**", "`void`, texto vazio e NaN são três jeitos de dizer a mesma coisa; tratá-los como coisas diferentes é de onde vem metade do bug de limpeza"], ["**Coluna que não existe é ERRO**", "com sugestão. Devolver uma coluna vazia calada é o jeito mais rápido de um relatório sair errado sem ninguém notar"]]}},
  { code: `out vendas.pegar("prodto")
`, lang: 'df' },
  { code: `erro: a coluna 'prodto' não existe neste quadro
  = nota: as colunas são: produto, regiao, valor, qtd
  = dica: você quis dizer 'produto'?
`, lang: 'text' },
  {"h2": "Nascer"},
  {"table": {"head": ["Forma", "De onde vem o dado"], "rows": [["`Q.de_vaults(linhas)`", "um cluster de vaults — o que `read_csv` e `query` devolvem"], ["`Q.de_colunas(vault)`", "um vault de clusters — a forma colunar"], ["`Q.de_csv(caminho)`", "um arquivo; a primeira linha é o cabeçalho"], ["`Q.de_json(caminho)`", "cluster de vaults ou vault de clusters"], ["`Q.vazio(colunas)`", "um quadro sem linhas, com as colunas declaradas"]]}},
  {"callout": {"tipo": "dica", "titulo": "O CSV traz tudo como texto", "texto": "Somar uma coluna de texto é o primeiro engano de quem chega. `Q.de_csv` infere o tipo por padrão — e só converte a coluna **inteira**: uma coluna com `[\"1\", \"2\", \"n/a\"]` fica como está, porque converter metade produziria uma coluna de dois tipos."}},
  {"h2": "Olhar antes de calcular"},
  {"p": "`perfil()` é o primeiro comando a rodar num conjunto que você não conhece:"},
  { code: `out vendas.perfil().texto()
`, lang: 'df' },
  { code: `coluna   tipo     linhas  ausentes  ausentes_pct  distintos  minimo  maximo  exemplo
-------  -------  ------  --------  ------------  ---------  ------  ------  -------
produto  String   5       0         0             3          void    void    cafe
regiao   String   5       0         0             2          void    void    sul
valor    Float    5       1         20            4          30      120     120
qtd      Integer  5       0         0             5          1       5       4
`, lang: 'text', title: `saída` },
  {"p": "E `descrever()` dá contagem, média, desvio, mínimo, quartis e máximo das colunas numéricas — **com a contagem de ausentes ao lado da média**, porque uma média sobre dados com buraco não avisa que tinha buraco."},
  {"h2": "Os verbos, por família"},
  {"table": {"head": ["Família", "Verbos"], "rows": [["**olhar**", "`colunas`, `forma`, `altura`, `largura`, `coluna`, `linha`, `topo`, `fim`, `fatiar`, `amostra`, `texto`"], ["**escolher**", "`pegar`, `sem`, `renomear`, `onde`, `ordenar`, `distintas`, `duplicadas`"], ["**mudar**", "`com`, `mapear`, `converter`, `inferir_tipos`"], ["**ausência**", "`nulos`, `sem_nulos`, `preencher`"], ["**agrupar**", "`agrupar`, `resumir`, `contar_valores`, `tabela_cruzada`, `pivotar`, `despivotar`"], ["**juntar**", "`juntar` (dentro, esquerda, direita, fora), `empilhar`"], ["**escala**", "`normalizar`, `padronizar`, `codificar`, `discretizar`"], ["**estatística**", "`descrever`, `correlacao`, `perfil`, `fora_da_curva`"], ["**sair**", "`para_vaults`, `para_colunas`, `para_csv`, `para_json`"]]}},
  {"h2": "Agrupar e resumir"},
  { code: `r := vendas.agrupar("produto").resumir({"valor": "soma", "qtd": "media"})
out r.texto()
`, lang: 'df' },
  { code: `produto  valor_soma  qtd_media
-------  ----------  ---------
cafe     210         3.5
cha      60          1.5
acucar   30          5
`, lang: 'text', title: `saída` },
  {"p": "As agregações são: `soma`, `media`, `mediana`, `minimo`, `maximo`, `contagem`, `contagem_valida`, `distintos`, `desvio`, `variancia`, `primeiro`, `ultimo`, `juntar` e `lista`."},
  {"callout": {"tipo": "atencao", "titulo": "A tabela é fechada de propósito", "texto": "O nome da agregação vem como **texto**, e um nome desconhecido é recusado com a lista do que existe. Aceitar qualquer ação abriria a porta para um nome vindo de fora — de um `?agregar=` de uma tela, por exemplo."}},
  {"p": "**`contagem` e `contagem_valida` respondem perguntas diferentes**: quantas linhas há, e quantas têm valor. Num conjunto com ausência, confundir as duas troca a média."},
  {"h2": "Juntar"},
  {"p": "Os quatro `JOIN` do SQL, com os nomes da linguagem:"},
  { code: `regioes := Q.de_vaults([{"regiao": "sul", "gerente": "Ana"}])

out vendas.juntar(regioes, "regiao").altura()               // 3  — dentro
out vendas.juntar(regioes, "regiao", "esquerda").altura()   // 5
out vendas.juntar(regioes, "regiao", "fora").altura()       // 5
`, lang: 'df' },
  {"h2": "Limpar"},
  { code: `limpo := vendas
    .preencher({"valor": "media"})     // ou um valor, "mediana", "anterior", "seguinte"
    .sem_duplicadas()
    .converter({"qtd": "Integer"})

out limpo.nulos()
`, lang: 'df' },
  {"p": "`converter` devolve `void` no que não converte, em vez de levantar: parar na primeira célula ruim de um CSV de um milhão de linhas não ajuda ninguém. Quantas não converteram aparece em `perfil()`, e é ali que a decisão se toma."},
  {"h2": "O quadro fala o protocolo da linguagem"},
  {"p": "Nada no `cycle`, no `len` ou no `>>` sabe o que é um quadro. Eles funcionam porque iterar um quadro dá **linhas como vault** — é o mesmo protocolo que faz a ponte para o Python funcionar sem conversão."},
  { code: `cycle linha in vendas:
    out linha["produto"]

out len(vendas)                    // 5 linhas
out vendas["valor"]                // a coluna
out vendas[0]                      // a linha, como vault
out vendas[0:2].altura()           // uma fatia, como quadro
`, lang: 'df' },
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/dados/verbos", "title": "Os verbos do pipeline", "desc": "a sintaxe: `>> onde valor bigger 50 >> agrupar produto`"}, {"href": "/docs/dados", "title": "Análise de dados", "desc": "o caminho de um conjunto até a resposta"}, {"href": "/docs/dados/mapa", "title": "O mapa do ecossistema", "desc": "o que é nativo, o que é ponte, e o que está fora"}, {"href": "/docs/biblioteca", "title": "A biblioteca", "desc": "os 64 módulos, e onde cada um entra"}]},
];

const headings = [{ id: 'as-cinco-decisoes', text: "As cinco decisões", level: 2 as const }, { id: 'nascer', text: "Nascer", level: 2 as const }, { id: 'olhar-antes-de-calcular', text: "Olhar antes de calcular", level: 2 as const }, { id: 'os-verbos-por-familia', text: "Os verbos, por família", level: 2 as const }, { id: 'agrupar-e-resumir', text: "Agrupar e resumir", level: 2 as const }, { id: 'juntar', text: "Juntar", level: 2 as const }, { id: 'limpar', text: "Limpar", level: 2 as const }, { id: 'o-quadro-fala-o-protocolo-da-linguagem', text: "O quadro fala o protocolo da linguagem", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Quadro — a tabela de dados"}
      description={"Colunas nomeadas e linhas como vault: filtrar, agrupar, resumir, juntar, pivotar, limpar e descrever."}
      href={"/docs/dados/quadro"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
