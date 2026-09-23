// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_engenharia.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Deriva de esquema",
  description: "Alguém a montante acrescentou uma coluna, renomeou outra e passou a mandar o id como texto.",
};

const blocos: Bloco[] = [
  {"p": "É a falha que mais derruba pipeline em produção, e ela não chega como erro: o programa continua rodando, e o número sai errado. `Qualidade.esquema_de` lê o esquema **do dado** — ele não é declarado, e é isso que permite comparar o lote de hoje com o de ontem sem ninguém ter escrito o contrato antes."},
  { code: `adopt Arcane.Qualidade as Qual

ontem := [{"id": 1, "nome": "Ana", "valor": 10.5},
          {"id": 2, "nome": "Bia", "valor": 20.0}]

esquema := Qual.esquema_de(ontem)
assert esquema["id"]["tipo"] is "inteiro"
assert esquema["nome"]["nulavel"] is no
out esquema`, lang: 'df' },
  {"h2": "Os três baldes"},
  {"p": "São os do `Arcane.Abi`, pela mesma razão: há mudança que quebra, mudança que não quebra, e mudança sobre a qual **não dá para saber**."},
  {"table": {"head": ["Balde", "O que é"], "rows": [["`quebra`", "campo que sumiu, tipo que mudou, campo que passou a vir vazio"], ["`compativel`", "campo novo — quem não o lê não vê diferença"], ["`desconhecido`", "o campo existe dos dois lados e um deles nunca viu valor"]]}},
  { code: `adopt Arcane.Qualidade as Qual

ontem := [{"id": 1, "nome": "Ana", "valor": 10.5},
          {"id": 2, "nome": "Bia", "valor": 20.0}]
hoje := [{"id": "3", "nome": "Cau", "valor": 30.0, "canal": "web"},
         {"id": "4", "nome": void,  "valor": 1.0,  "canal": "app"}]

d := Qual.deriva(Qual.esquema_de(ontem), Qual.esquema_de(hoje))
out d["resumo"]
cycle q in d["quebra"]:
    out $"  QUEBRA  {q['campo']}: {q['o_que']} ({q['antes']} → {q['agora']})"
cycle c in d["compativel"]:
    out $"  ok      {c['campo']}: {c['o_que']}"

assert d["ok"] is no
assert len(d["compativel"]) is 1`, lang: 'df' },
  {"h2": "Presença e vazios são contas diferentes"},
  {"p": "Um campo que vem **sempre**, com metade em branco, tem presença 1,0 e vazios 0,5 — e é o segundo número que quebra quem lê. Confundir os dois foi o primeiro defeito desta peça:"},
  { code: `adopt Arcane.Qualidade as Qual

e := Qual.esquema_de([{"a": "x"}, {"a": void}])
assert e["a"]["presenca"] is 1.0      // a chave veio nas duas linhas
assert e["a"]["vazios"] is 0.5        // e metade estava vazia
assert e["a"]["nulavel"] is yes`, lang: 'df' },
  {"h2": "Na entrada do pipeline"},
  { code: `adopt Arcane.Qualidade as Qual

CONTRATO := {
    "id": {"tipo": "inteiro", "nulavel": no},
    "nome": {"tipo": "texto", "nulavel": no},
    "valor": {"tipo": "numero", "nulavel": no},
}

bom := [{"id": 1, "nome": "Ana", "valor": 10.0}]
relato := Qual.exigir_esquema(bom, CONTRATO)
assert relato["ok"] is yes

// E o lote que mudou de tipo é RECUSADO, com o que mudou na mensagem.
ruim := [{"id": "1", "nome": "Ana", "valor": 10.0}]
monitor:
    Qual.exigir_esquema(ruim, CONTRATO)
    assert no
handle Error as e:
    out e.message`, lang: 'df' },
  {"p": "Falhar aqui custa **uma execução**; deixar passar custa um relatório errado que ninguém desconfia. É a mesma conta do `Forge.esperar`, que recusa uma senha errada na hora em vez de insistir por quarenta segundos."},
  {"h2": "O terceiro balde, e por que ele existe"},
  { code: `adopt Arcane.Qualidade as Qual

// 'b' veio só como vazio ontem, e como texto hoje. Acusar reprovaria
// o correto; calar deixaria passar o que quebra. Ele vai para o
// balde que diz "não dá para saber".
antes := Qual.esquema_de([{"a": 1, "b": void}])
depois := Qual.esquema_de([{"a": 2, "b": "texto"}])

d := Qual.deriva(antes, depois)
assert d["quebra"] is []
assert d["desconhecido"][0]["campo"] is "b"
out d["desconhecido"][0]`, lang: 'df' },
];

const headings = [{ id: 'os-tres-baldes', text: "Os três baldes", level: 2 as const }, { id: 'presenca-e-vazios-sao-contas-diferentes', text: "Presença e vazios são contas diferentes", level: 2 as const }, { id: 'na-entrada-do-pipeline', text: "Na entrada do pipeline", level: 2 as const }, { id: 'o-terceiro-balde-e-por-que-ele-existe', text: "O terceiro balde, e por que ele existe", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Deriva de esquema"}
      description={"Alguém a montante acrescentou uma coluna, renomeou outra e passou a mandar o id como texto."}
      href={"/docs/dados/deriva"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
