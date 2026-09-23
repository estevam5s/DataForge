// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/lavra_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testar um esquema",
  description: "Sem HTTP, sem servidor — e o teste que pega a quebra de contrato antes do cliente.",
};

const blocos: Bloco[] = [
  {"p": "Um esquema se testa **sem rede**: `Lavra.executar` recebe o texto da consulta e devolve o resultado. O servidor é outra camada, e ela tem os próprios testes."},
  { code: `adopt Arcane.Lavra as Lavra
adopt Arcane.Crucible as Crucible

record Produto:
    id: Integer
    nome: String
    preco: Float

action montar():
    esq := Lavra.esquema("loja")
    Lavra.tipo(esq, Produto)
    Lavra.busca(esq, "produto", "Produto",
        args := {"id": "Integer!"},
        resolve := lambda r, a, c => (
            Produto(1, "café", 32.9) given a["id"] is 1 otherwise void))
    Lavra.conferir(esq)
    yield esq

crucible "o esquema da loja":

    trial "devolve o produto que existe":
        r := Lavra.executar(montar(), "busca:\\n    produto(id: 1):\\n        nome")
        expect r["dados"]["produto"]["nome"] is "café"

    trial "o que nao existe e VOID, e nao erro":
        r := Lavra.executar(montar(), "busca:\\n    produto(id: 99):\\n        nome")
        expect r["dados"]["produto"] is void
        expect len(r["erros"]) is 0

    trial "um campo que nao existe e recusado ANTES de executar":
        r := Lavra.executar(montar(), "busca:\\n    produto(id: 1):\\n        naoExiste")
        expect len(r["erros"]) is 1

    trial "o argumento obrigatorio que falta e recusado":
        r := Lavra.executar(montar(), "busca:\\n    produto:\\n        nome")
        expect len(r["erros"]) is 1

Crucible.run()`, lang: 'df' },
  {"h2": "Validar sem executar"},
  {"p": "`Lavra.validar` responde \"esta consulta é legal neste esquema?\" sem chamar resolvedor nenhum. É o que permite guardar as consultas do aplicativo no repositório e conferir **todas** num teste — a quebra aparece no CI, e não no aplicativo de quem já atualizou."},
  { code: `adopt Arcane.Lavra as Lavra

record Produto:
    id: Integer
    nome: String

esq := Lavra.esquema("loja")
Lavra.tipo(esq, Produto)
Lavra.busca(esq, "produto", "Produto",
    args := {"id": "Integer!"}, resolve := lambda r, a, c => void)
Lavra.conferir(esq)

// as consultas que o aplicativo usa, guardadas no repositório
CONSULTAS := {
    "tela_produto": "busca:\\n    produto(id: 1):\\n        nome",
    "tela_antiga": "busca:\\n    produto(id: 1):\\n        descricao",
}

quebradas := []
cycle nome in sorted(keys(CONSULTAS)):
    erros := Lavra.validar(esq, CONSULTAS[nome])
    given len(erros) > 0:
        quebradas.append(nome)

assert quebradas is ["tela_antiga"]
out $"quebrada(s) pelo esquema atual: {quebradas}"`, lang: 'df' },
  {"h2": "O esquema como texto, num instantâneo"},
  {"p": "`texto_do_esquema` devolve a superfície inteira. Guardá-la num instantâneo faz **qualquer** mudança de contrato aparecer no diff do commit — inclusive a que ninguém pretendia:"},
  { code: `adopt Arcane.Lavra as Lavra

record Produto:
    id: Integer
    nome: String

esq := Lavra.esquema("loja")
Lavra.tipo(esq, Produto)
Lavra.busca(esq, "produtos", "[Produto!]!", resolve := lambda r, a, c => [])
Lavra.conferir(esq)

texto := Lavra.texto_do_esquema(esq)
assert "busca:" in texto and "tipo Produto:" in texto
out texto`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "`conferir` antes de subir", "texto": "Ele acha o campo que aponta para um tipo que não existe, o resolvedor faltando e o ciclo — **antes** da primeira requisição. Sem ele, o erro aparece na consulta de alguém, e o rastro fala do campo, não da declaração."}},
];

const headings = [{ id: 'validar-sem-executar', text: "Validar sem executar", level: 2 as const }, { id: 'o-esquema-como-texto-num-instantaneo', text: "O esquema como texto, num instantâneo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Testar um esquema"}
      description={"Sem HTTP, sem servidor — e o teste que pega a quebra de contrato antes do cliente."}
      href={"/docs/lavra/testar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
