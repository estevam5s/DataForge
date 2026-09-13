// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "03 · Coleções",
  description: "14 exercícios: cluster e vault, fatias, spread e compreensões.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 03`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[025](#025-clusters-listas)", "**Clusters (listas)**", "crie, acesse e altere elementos de um cluster."], ["[026](#026-fatiamento)", "**Fatiamento**", "extraia trechos de um cluster com [inicio:fim:passo]."], ["[027](#027-metodos-de-cluster)", "**Metodos de cluster**", "use append, insert, remove, pop, sort e reverse."], ["[028](#028-agregacoes-numericas)", "**Agregacoes numericas**", "calcule soma, minimo, maximo e media de um cluster."], ["[029](#029-unique-flatten-e-chunk)", "**unique, flatten e chunk**", "limpe e reorganize dados aninhados."], ["[030](#030-ordenacao)", "**Ordenacao**", "ordene numeros e textos, e ordene ao contrario."], ["[031](#031-vaults-dicionarios)", "**Vaults (dicionarios)**", "crie, leia, atualize e remova chaves de um vault."], ["[032](#032-percorrendo-vaults)", "**Percorrendo vaults**", "use keys, values e items para somar um estoque."], ["[033](#033-operacoes-avancadas-de-vault)", "**Operacoes avancadas de vault**", "use merge, pick, omit, invert e map_values."], ["[034](#034-matrizes)", "**Matrizes**", "monte uma matriz identidade 3x3 e calcule o traco."], ["[035](#035-pilha-e-fila)", "**Pilha e fila**", "implemente LIFO e FIFO usando cluster."], ["[036](#036-busca-linear-e-binaria)", "**Busca linear e binaria**", "implemente as duas buscas e compare o resultado."], ["[037](#037-bubble-sort)", "**Bubble sort**", "ordene um cluster sem usar sorted()."], ["[038](#038-contagem-de-frequencias)", "**Contagem de frequencias**", "conte quantas vezes cada item aparece."]]}},
  {"h2": "025 · Clusters (listas)"},
  {"p": "**Enunciado.** crie, acesse e altere elementos de um cluster."},
  { code: `nums := [10, 20, 30, 40, 50]
out "primeiro:", nums[0], "ultimo:", nums[-1], "tamanho:", len(nums)

nums[1] := 99
out nums

assert nums[0] is 10, "indice 0"
assert nums[-1] is 50, "indice negativo"
assert nums[1] is 99, "atribuicao por indice"
assert len(nums) is 5, "tamanho"`, lang: 'df', title: `exercicios/03-colecoes/025_clusters.df` },
  {"h2": "026 · Fatiamento"},
  {"p": "**Enunciado.** extraia trechos de um cluster com [inicio:fim:passo]."},
  { code: `letras := ["a", "b", "c", "d", "e", "f"]

out letras[1:4], letras[:3], letras[3:], letras[::2], letras[-2:]

assert letras[1:4] is ["b", "c", "d"], "intervalo"
assert letras[:3] is ["a", "b", "c"], "do inicio"
assert letras[3:] is ["d", "e", "f"], "ate o fim"
assert letras[::2] is ["a", "c", "e"], "passo 2"
assert letras[-2:] is ["e", "f"], "dois ultimos"
assert letras[::-1] is ["f", "e", "d", "c", "b", "a"], "invertido"`, lang: 'df', title: `exercicios/03-colecoes/026_fatiamento.df` },
  {"h2": "027 · Metodos de cluster"},
  {"p": "**Enunciado.** use append, insert, remove, pop, sort e reverse."},
  { code: `pilha := [3, 1, 2]
pilha.append(4)
assert pilha is [3, 1, 2, 4], "append"

pilha.insert(0, 0)
assert pilha is [0, 3, 1, 2, 4], "insert"

pilha.remove(3)
assert pilha is [0, 1, 2, 4], "remove"

ultimo := pilha.pop()
assert ultimo is 4, "pop devolve o ultimo"
assert pilha is [0, 1, 2], "pop remove"

pilha.append(9)
pilha.reverse()
assert pilha is [9, 2, 1, 0], "reverse"

pilha.sort()
assert pilha is [0, 1, 2, 9], "sort"

out "cluster final:", pilha`, lang: 'df', title: `exercicios/03-colecoes/027_metodos_de_cluster.df` },
  {"h2": "028 · Agregacoes numericas"},
  {"p": "**Enunciado.** calcule soma, minimo, maximo e media de um cluster."},
  { code: `vendas := [120, 340, 90, 500, 210]

out "soma  ", sum(vendas)
out "minimo", min(vendas)
out "maximo", max(vendas)
out "media ", mean(vendas)
out "desvio", round(stdev(vendas), 4)

assert sum(vendas) is 1260, "soma"
assert min(vendas) is 90, "minimo"
assert max(vendas) is 500, "maximo"
assert mean(vendas) is 252.0, "media"
assert median(vendas) is 210, "mediana"`, lang: 'df', title: `exercicios/03-colecoes/028_agregacoes.df` },
  {"h2": "029 · unique, flatten e chunk"},
  {"p": "**Enunciado.** limpe e reorganize dados aninhados."},
  { code: `bruto := [[1, 2], [2, 3], [3, [4, 4]]]
plano := flatten(bruto)
distintos := unique(plano)
blocos := distintos.chunk(2)

out "plano:    ", plano
out "distintos:", distintos
out "blocos:   ", blocos

assert plano is [1, 2, 2, 3, 3, 4, 4], "flatten profundo"
assert distintos is [1, 2, 3, 4], "unique preserva a ordem"
assert blocos is [[1, 2], [3, 4]], "chunk de 2"`, lang: 'df', title: `exercicios/03-colecoes/029_unique_flatten.df` },
  {"h2": "030 · Ordenacao"},
  {"p": "**Enunciado.** ordene numeros e textos, e ordene ao contrario."},
  { code: `nums := [5, 3, 9, 1]
palavras := ["uva", "abacaxi", "maca"]

assert sorted(nums) is [1, 3, 5, 9], "numeros"
assert sorted(palavras) is ["abacaxi", "maca", "uva"], "alfabetica"
assert reversed(sorted(nums)) is [9, 5, 3, 1], "decrescente"

out sorted(nums), sorted(palavras), reversed(sorted(nums))`, lang: 'df', title: `exercicios/03-colecoes/030_ordenacao.df` },
  {"h2": "031 · Vaults (dicionarios)"},
  {"p": "**Enunciado.** crie, leia, atualize e remova chaves de um vault."},
  { code: `pessoa := {"nome": "Ana", "idade": 30}

out pessoa["nome"], pessoa.idade
pessoa["cidade"] := "Floripa"
pessoa["idade"] := 31

assert pessoa["cidade"] is "Floripa", "nova chave"
assert pessoa["idade"] is 31, "atualizacao"
assert pessoa.has("nome") is yes, "has"
assert pessoa.has("email") is no, "chave ausente"
assert pessoa.get("email", "sem email") is "sem email", "get com padrao"

pessoa.delete("cidade")
assert pessoa.has("cidade") is no, "delete"
out pessoa`, lang: 'df', title: `exercicios/03-colecoes/031_vaults.df` },
  {"h2": "032 · Percorrendo vaults"},
  {"p": "**Enunciado.** use keys, values e items para somar um estoque."},
  { code: `estoque := {"parafuso": 120, "porca": 80, "arruela": 200}

total := 0
cycle par in estoque.items():
    out par[0].pad_end(10), par[1]
    total += par[1]

assert len(estoque.keys()) is 3, "3 chaves"
assert sum(estoque.values()) is 400, "soma dos valores"
assert total is 400, "soma via items"
out "total:", total`, lang: 'df', title: `exercicios/03-colecoes/032_vault_iteracao.df` },
  {"h2": "033 · Operacoes avancadas de vault"},
  {"p": "**Enunciado.** use merge, pick, omit, invert e map_values."},
  { code: `base := {"a": 1, "b": 2, "c": 3}

assert base.merge({"d": 4}) is {"a": 1, "b": 2, "c": 3, "d": 4}, "merge"
assert base.pick("a", "c") is {"a": 1, "c": 3}, "pick"
assert base.omit("b") is {"a": 1, "c": 3}, "omit"
assert base.invert() is {1: "a", 2: "b", 3: "c"}, "invert"
assert base.map_values(lambda v: v * 10) is {"a": 10, "b": 20, "c": 30}, "map_values"

out base.merge({"d": 4})
out base.map_values(lambda v: v * 10)`, lang: 'df', title: `exercicios/03-colecoes/033_vault_avancado.df` },
  {"h2": "034 · Matrizes"},
  {"p": "**Enunciado.** monte uma matriz identidade 3x3 e calcule o traco."},
  { code: `n := 3
matriz := []
cycle i from 0 to n - 1:
    linha := []
    cycle j from 0 to n - 1:
        given i is j:
            linha.append(1)
        otherwise:
            linha.append(0)
    matriz.append(linha)

traco := 0
cycle i from 0 to n - 1:
    traco += matriz[i][i]

cycle linha in matriz:
    out linha

assert matriz is [[1, 0, 0], [0, 1, 0], [0, 0, 1]], "identidade"
assert traco is 3, "traco da identidade 3x3"`, lang: 'df', title: `exercicios/03-colecoes/034_matrizes.df` },
  {"h2": "035 · Pilha e fila"},
  {"p": "**Enunciado.** implemente LIFO e FIFO usando cluster."},
  { code: `pilha := []
pilha.append("a")
pilha.append("b")
pilha.append("c")
topo := pilha.pop()
assert topo is "c", "pilha LIFO"
assert pilha is ["a", "b"], "pilha apos pop"

fila := []
fila.append("x")
fila.append("y")
fila.append("z")
primeiro := fila.pop(0)
assert primeiro is "x", "fila FIFO"
assert fila is ["y", "z"], "fila apos remover o primeiro"

out "pilha:", pilha, "| fila:", fila`, lang: 'df', title: `exercicios/03-colecoes/035_pilha_fila.df` },
  {"h2": "036 · Busca linear e binaria"},
  {"p": "**Enunciado.** implemente as duas buscas e compare o resultado."},
  { code: `action busca_linear(lista, alvo):
    cycle i from 0 to len(lista) - 1:
        given lista[i] is alvo:
            yield i
    yield -1

action busca_binaria(lista, alvo):
    esq := 0
    dir := len(lista) - 1
    persist esq smaller_eq dir:
        meio := (esq + dir) ~/ 2
        given lista[meio] is alvo:
            yield meio
        orif lista[meio] smaller alvo:
            esq := meio + 1
        otherwise:
            dir := meio - 1
    yield -1

ordenada := [1, 3, 5, 7, 9, 11]
cycle alvo in [1, 7, 11, 4]:
    out alvo, "-> linear", busca_linear(ordenada, alvo), "| binaria", busca_binaria(ordenada, alvo)

assert busca_linear(ordenada, 7) is 3, "linear"
assert busca_binaria(ordenada, 7) is 3, "binaria"
assert busca_binaria(ordenada, 4) is -1, "ausente"`, lang: 'df', title: `exercicios/03-colecoes/036_busca.df` },
  {"h2": "037 · Bubble sort"},
  {"p": "**Enunciado.** ordene um cluster sem usar sorted()."},
  { code: `action bubble(lista):
    copia := lista.copy()
    n := len(copia)
    cycle i from 0 to n - 2:
        cycle j from 0 to n - 2 - i:
            given copia[j] bigger copia[j + 1]:
                tmp := copia[j]
                copia[j] := copia[j + 1]
                copia[j + 1] := tmp
    yield copia

entrada := [5, 2, 9, 1, 7]
saida := bubble(entrada)
out "entrada:", entrada
out "saida:  ", saida

assert saida is [1, 2, 5, 7, 9], "ordenado"
assert entrada is [5, 2, 9, 1, 7], "a entrada nao foi alterada"`, lang: 'df', title: `exercicios/03-colecoes/037_ordenacao_manual.df` },
  {"h2": "038 · Contagem de frequencias"},
  {"p": "**Enunciado.** conte quantas vezes cada item aparece."},
  { code: `votos := ["ana", "bruno", "ana", "carla", "ana", "bruno"]
contagem := votos.frequencies()

out contagem

vencedor := ""
maximo := 0
cycle par in contagem.items():
    given par[1] bigger maximo:
        maximo := par[1]
        vencedor := par[0]

out "vencedor:", vencedor, "com", maximo, "votos"
assert contagem["ana"] is 3, "ana"
assert contagem["bruno"] is 2, "bruno"
assert vencedor is "ana", "vencedor"`, lang: 'df', title: `exercicios/03-colecoes/038_frequencias.df` },
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/03-colecoes/025_clusters.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '025-clusters-listas', text: "025 · Clusters (listas)", level: 2 as const }, { id: '026-fatiamento', text: "026 · Fatiamento", level: 2 as const }, { id: '027-metodos-de-cluster', text: "027 · Metodos de cluster", level: 2 as const }, { id: '028-agregacoes-numericas', text: "028 · Agregacoes numericas", level: 2 as const }, { id: '029-unique-flatten-e-chunk', text: "029 · unique, flatten e chunk", level: 2 as const }, { id: '030-ordenacao', text: "030 · Ordenacao", level: 2 as const }, { id: '031-vaults-dicionarios', text: "031 · Vaults (dicionarios)", level: 2 as const }, { id: '032-percorrendo-vaults', text: "032 · Percorrendo vaults", level: 2 as const }, { id: '033-operacoes-avancadas-de-vault', text: "033 · Operacoes avancadas de vault", level: 2 as const }, { id: '034-matrizes', text: "034 · Matrizes", level: 2 as const }, { id: '035-pilha-e-fila', text: "035 · Pilha e fila", level: 2 as const }, { id: '036-busca-linear-e-binaria', text: "036 · Busca linear e binaria", level: 2 as const }, { id: '037-bubble-sort', text: "037 · Bubble sort", level: 2 as const }, { id: '038-contagem-de-frequencias', text: "038 · Contagem de frequencias", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"03 · Coleções"}
      description={"14 exercícios: cluster e vault, fatias, spread e compreensões."}
      href={"/docs/exercicios/03-colecoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
