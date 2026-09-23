// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/lavra_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "N+1 e o lote",
  description: "Cem produtos, cem consultas ao banco — e como isso vira duas.",
};

const blocos: Bloco[] = [
  {"p": "O N+1 é o defeito que toda camada de consulta tipada produz por construção: uma busca traz 100 produtos, o campo `categoria` de cada um chama o resolvedor, e são **101** idas ao banco. O código parece certo, e a página leva três segundos."},
  { code: `adopt Arcane.Lavra as Lavra

record Produto:
    id: Integer
    nome: String
    categoria_id: Integer

record Categoria:
    id: Integer
    nome: String

CATEGORIAS := {1: Categoria(1, "bebidas"), 2: Categoria(2, "acessórios")}
PRODUTOS := [Produto(1, "café", 1), Produto(2, "chá", 1), Produto(3, "filtro", 2)]
IDAS := {"n": 0}

action buscar_categorias(chaves):
    // UMA ida, com todas as chaves de uma vez.
    IDAS["n"] := IDAS["n"] + 1
    yield {k: CATEGORIAS[k] cycle k in chaves}

action todos(raiz, args, ctx):
    yield PRODUTOS

action categoria_de(produto, args, ctx):
    // 'pedir' NÃO vai ao banco: ele registra a chave e devolve uma
    // promessa. O Lavra junta as chaves do nível inteiro e chama
    // 'buscar_categorias' UMA vez.
    Lavra.lote(ctx, "categorias", buscar_categorias)
    yield Lavra.pedir(ctx, "categorias", produto.categoria_id)

esq := Lavra.esquema("loja")
Lavra.tipo(esq, Produto)
Lavra.tipo(esq, Categoria)
Lavra.campo(esq, "Produto", "categoria", "Categoria", resolve := categoria_de)
Lavra.busca(esq, "produtos", "[Produto!]!", resolve := todos)
Lavra.conferir(esq)

r := Lavra.executar(esq, """
busca:
    produtos:
        nome
        categoria:
            nome
""")
assert len(r["dados"]["produtos"]) is 3
assert r["dados"]["produtos"][0]["categoria"]["nome"] is "bebidas"

// três produtos, duas categorias distintas — e UMA ida
assert IDAS["n"] is 1
out $"3 produtos, {IDAS['n']} consulta de categoria"`, lang: 'df' },
  {"h2": "Por que isto não é cache"},
  {"table": {"head": ["", "Lote", "Cache"], "rows": [["vive", "uma requisição", "entre requisições"], ["resolve", "N chamadas viram uma", "a segunda chamada não acontece"], ["pode devolver dado velho", "**não**", "sim, e é o ponto dele"], ["precisa de invalidação", "não", "sim — e é a parte difícil"]]}},
  {"p": "Os dois se somam: o lote tira o N+1 de **dentro** da requisição; o cache tira a requisição inteira. Um cache sem lote continua com N+1 na primeira visita, que é a que o usuário novo vê."},
  {"h2": "O campo que custa caro declara o custo"},
  { code: `adopt Arcane.Lavra as Lavra

record Usuario:
    id: Integer

esq := Lavra.esquema("rede")
Lavra.tipo(esq, Usuario)
// 'custo' diz quanto este campo pesa; o limite de complexidade soma
// o custo da consulta ANTES de executar qualquer resolvedor.
Lavra.campo(esq, "Usuario", "amigos", "[Usuario!]!",
    resolve := lambda r, a, c => [], custo := 10)
Lavra.busca(esq, "usuario", "Usuario", resolve := lambda r, a, c => Usuario(1))
Lavra.limites(esq, profundidade := 5, complexidade := 50)
Lavra.conferir(esq)

// Uma consulta funda demais é recusada sem tocar no banco.
r := Lavra.executar(esq, """
busca:
    usuario:
        amigos:
            amigos:
                amigos:
                    amigos:
                        id
""")
assert len(r["erros"]) is 1
out r["erros"][0]["mensagem"]`, lang: 'df' },
  {"p": "Recusar **antes** de executar é o ponto: um limite conferido no meio já pagou metade do custo, e é exatamente essa metade que derruba o banco."},
];

const headings = [{ id: 'por-que-isto-nao-e-cache', text: "Por que isto não é cache", level: 2 as const }, { id: 'o-campo-que-custa-caro-declara-o-custo', text: "O campo que custa caro declara o custo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"N+1 e o lote"}
      description={"Cem produtos, cem consultas ao banco — e como isso vira duas."}
      href={"/docs/lavra/lote"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
