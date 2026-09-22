// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/api_rest_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Versionar uma API",
  description: "Na URL ou no cabeçalho, o que obriga a subir a versão, e como aposentar uma com Deprecation e Sunset.",
};

const blocos: Bloco[] = [
  {"p": "Uma API publicada é um contrato com gente que você não conhece. O que **quebra** esse contrato: remover um campo, renomear, mudar o tipo, tornar obrigatório o que era opcional, mudar o significado de um status. O que **não** quebra: acrescentar campo na resposta, acrescentar rota, aceitar um parâmetro opcional novo."},
  {"table": {"head": ["Onde a versão mora", "A favor", "Contra"], "rows": [["na URL: `/v2/pedidos`", "visível, fácil de testar no navegador, cacheável", "a URL do recurso muda"], ["num cabeçalho: `Api-Version: 2`", "a URL é o recurso", "invisível num link; cache precisa de `Vary`"], ["no tipo: `application/vnd.loja.v2+json`", "é o que a negociação faz", "o mais difícil de usar à mão"]]}},
  {"p": "Na dúvida, a URL: é a que dá menos surpresa a quem integra. E a versão velha não some de uma vez — ela avisa antes, com dois cabeçalhos padronizados:"},
  { code: `adopt Arcane.Kiln as Kiln

app := Kiln.app()

action v1(req):
    yield Kiln.json({"nome": "Ana Souza"}, 200, {
        "Deprecation": "@1767225600",                     // RFC 9745: desde quando
        "Sunset": "Wed, 01 Jul 2026 00:00:00 GMT",         // RFC 8594: até quando
        "Link": '</v2/clientes/1>; rel="successor-version"'})

action v2(req):
    yield Kiln.json({"nome": {"primeiro": "Ana", "ultimo": "Souza"}})

Kiln.get(app, "/v1/clientes/:id", v1)
Kiln.get(app, "/v2/clientes/:id", v2)

velha := Kiln.test(app, "GET", "/v1/clientes/1")
assert velha["headers"]["Sunset"].contains("2026")
assert Kiln.test(app, "GET", "/v2/clientes/1")["body"]["nome"]["primeiro"] is "Ana"`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Calcule, não escolha", "texto": "Para uma **biblioteca** em DataForge, a versão sai da superfície: `Abi.proxima_versao(\"1.4.2\", antes, depois)` compara os dois arquivos e diz se é 2.0.0, 1.5.0 ou 1.4.3. Ver [A próxima versão](/docs/abi/versao)."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Versionar uma API"}
      description={"Na URL ou no cabeçalho, o que obriga a subir a versão, e como aposentar uma com Deprecation e Sunset."}
      href={"/docs/api/versionamento"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
