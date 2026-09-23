// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_engenharia.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Contratos de dados",
  description: "O acordo entre quem produz e quem consome — escrito, versionado e cobrado.",
};

const blocos: Bloco[] = [
  {"p": "Um contrato de dados é a mesma ideia do `Arcane.Abi` aplicada a uma tabela: **o que este conjunto promete**, e o que conta como quebra. Sem ele, quem produz não sabe o que pode mudar, e quem consome descobre no incidente."},
  { code: `adopt Arcane.Qualidade as Qual

// O contrato é DADO: dá para versioná-lo, difundi-lo e testá-lo.
CONTRATO := {
    "esquema": {
        "id": {"tipo": "inteiro", "nulavel": no},
        "cliente": {"tipo": "texto", "nulavel": no},
        "valor": {"tipo": "numero", "nulavel": no},
    },
    // As regras são um vault POR CAMPO — a mesma forma do 'perfil'.
    "regras": {
        "valor": {"minimo": 0},
        "id": {"unico": yes},
    },
    "frescor_dias": 1,
}

lote := [{"id": 1, "cliente": "Ana", "valor": 10.0},
         {"id": 2, "cliente": "Bia", "valor": 20.0}]

// 1. o esquema
assert Qual.exigir_esquema(lote, CONTRATO["esquema"])["ok"] is yes

// 2. as regras
r := Qual.conferir(lote, CONTRATO["regras"])
assert r["ok"] is yes
assert r["taxa_boa"] is 1.0
out Qual.relatorio(r)`, lang: 'df' },
  {"h2": "O que um contrato precisa dizer"},
  {"table": {"head": ["Parte", "Pergunta que ela responde"], "rows": [["esquema", "quais campos, de que tipo, e quais podem faltar"], ["chave", "o que identifica uma linha — e se ela é única"], ["regras de valor", "faixa, formato, lista fechada"], ["frescor", "quão velho o dado pode estar"], ["volume esperado", "quantas linhas por dia são normais"], ["quem responde", "a pessoa ou o time — sem isso, o contrato não tem dono"]]}},
  {"h2": "Volume também é contrato"},
  {"p": "Um lote que chega com 3 linhas onde chegam 30 mil **não quebra nenhuma regra de esquema**: cada linha está perfeita. E é uma das falhas mais comuns — a origem filtrou errado, e o relatório do dia sai com um centésimo do faturamento."},
  { code: `adopt Arcane.Qualidade as Qual

action conferir_volume(lote, esperado, tolerancia):
    quantas := len(lote)
    piso := esperado * (1 - tolerancia)
    teto := esperado * (1 + tolerancia)
    given quantas < piso or quantas > teto:
        trigger $"o lote tem {quantas} linha(s), e o esperado é ~{esperado} (±{round(tolerancia * 100)}%)"
    yield quantas

assert conferir_volume([1, 2, 3, 4, 5], 5, 0.5) is 5

monitor:
    conferir_volume([1], 100, 0.2)
    assert no
handle Error as e:
    out e.message`, lang: 'df' },
  {"h2": "E frescor"},
  { code: `adopt Arcane.Qualidade as Qual
adopt Arcane.Time as T

agora := T.now()
lote := [{"id": 1, "quando": agora}]

// 'atualidade' conta quantas linhas são mais velhas que o limite.
velhas := Qual.atualidade(lote, "quando", 1)
out velhas
assert velhas["velhas"] is 0
assert velhas["proporcao"] is 0.0`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Um contrato sem dono não é contrato", "texto": "Ele precisa nomear quem responde quando quebra. Um arquivo de regras que ninguém mantém vira ruído no CI em três meses — e a reação é desligar a verificação, que é pior que nunca tê-la escrito."}},
];

const headings = [{ id: 'o-que-um-contrato-precisa-dizer', text: "O que um contrato precisa dizer", level: 2 as const }, { id: 'volume-tambem-e-contrato', text: "Volume também é contrato", level: 2 as const }, { id: 'e-frescor', text: "E frescor", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Contratos de dados"}
      description={"O acordo entre quem produz e quem consome — escrito, versionado e cobrado."}
      href={"/docs/dados/contratos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
