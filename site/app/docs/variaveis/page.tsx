import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Variáveis",
  description: "Declaração com :=, constantes com steady, escopo e a variável local com shadow.",
};

const blocos: Bloco[] = [
  {"h2": "Declarar"},
  {"p": "O operador de atribuição é `:=`. Ele cria a variável se ela não existir e atualiza se existir."},
  { code: `nome := "DataForge"
idade := 30
altura := 1.75
ativo := yes
vazio := void

out nome, idade, altura, ativo, vazio` },
  { code: `DataForge 30 1.75 yes void`, lang: 'text', title: `saída` },
  {"callout": {"tipo": "nota", "texto": "`:=` em vez de `=` não é capricho: elimina a confusão clássica entre atribuição e comparação. Em DataForge, `=` sozinho não existe."}},
  {"h2": "Constantes"},
  {"p": "`steady` declara um valor imutável. Reatribuir é erro — detectado inclusive pelo [analisador estático](/docs/tecnicas/analise-estatica), antes de executar."},
  { code: `steady PI := 3.14159
steady LIMITE := 100

out PI, LIMITE

monitor:
    PI := 0
handle e:
    out e.message` },
  { code: `3.14159 100
Cannot reassign steady (constant) 'PI'`, lang: 'text', title: `saída` },
  {"h2": "Escopo"},
  {"p": "Uma ação enxerga as variáveis do escopo onde foi definida. Atribuir a um nome que já existe fora **atualiza** o de fora:"},
  { code: `contador := 0

action incrementar():
    contador := contador + 1     # atualiza o de fora
    yield contador

incrementar()
incrementar()
out contador` },
  { code: `2`, lang: 'text', title: `saída` },
  {"h3": "shadow — uma cópia local"},
  {"p": "Quando você quer um nome local que **não** afeta o de fora, use `shadow`:"},
  { code: `x := 10

action le():
    yield x                  # enxerga o de fora: 10

action sombreia():
    shadow x := 99           # cria uma cópia local
    yield x                  # 99

out le(), sombreia(), x` },
  { code: `10 99 10`, lang: 'text', title: `saída` },
  {"p": "A terceira saída é o ponto: `x` continua valendo 10. `shadow` diz explicitamente \"este nome é meu, aqui dentro\"."},
  {"h2": "Nomes válidos"},
  {"list": ["Começam com letra ou `_`, seguidos de letras, dígitos ou `_`", "São **sensíveis à caixa**: `total` e `Total` são nomes diferentes", "Não podem ser uma das [81 palavras reservadas](/docs/referencia/palavras-reservadas)"]},
  {"callout": {"tipo": "atencao", "titulo": "Cuidado em português", "texto": "As palavras reservadas que mais pegam quem escreve em português: `no`, `in`, `is`, `to`, `from`, `as`, `step`, `point`, `default`. Já `range`, `cluster` e `vault` **são funções**, não reservadas — pode usá-las como nome."}},
  { code: `// nao := 1     # erro: 'no' faz parte de 'nao'? Não — 'nao' é válido.
no := 1         # ERRO: 'no' é palavra reservada (o literal falso)
resposta := no  # certo: usa 'no' como valor` },
  {"h2": "Apagar"},
  {"p": "`delete` remove um nome do escopo:"},
  { code: `temporario := "vai sumir"
out temporario
delete temporario

monitor:
    out temporario
handle e:
    out e.message` },
  { code: `vai sumir
Undefined name: 'temporario'`, lang: 'text', title: `saída` },
];

const headings = [{ id: 'declarar', text: "Declarar", level: 2 as const }, { id: 'constantes', text: "Constantes", level: 2 as const }, { id: 'escopo', text: "Escopo", level: 2 as const }, { id: 'shadow-uma-copia-local', text: "shadow — uma cópia local", level: 3 as const }, { id: 'nomes-validos', text: "Nomes válidos", level: 2 as const }, { id: 'apagar', text: "Apagar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Variáveis"}
      description={"Declaração com :=, constantes com steady, escopo e a variável local com shadow."}
      href={"/docs/variaveis"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
