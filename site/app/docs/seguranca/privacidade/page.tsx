// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "LGPD na prática",
  description: "Finalidade, necessidade, consentimento, retenção e os direitos do titular — como operações sobre dado, com Arcane.Privacidade.",
};

const blocos: Bloco[] = [
  {"p": "A LGPD fala em princípios — finalidade, adequação, necessidade, transparência, segurança (art. 6º). No código eles viram perguntas concretas: **para que** este dado é usado, **quais campos** a finalidade precisa, **até quando** ele pode ficar, e **onde** ele mora quando o titular pede para ver ou apagar. `Arcane.Privacidade` torna cada resposta registrável."},
  {"callout": {"tipo": "atencao", "titulo": "Não é parecer jurídico", "texto": "Este módulo não decide a base legal de um tratamento nem substitui o encarregado (DPO). Ele torna as decisões **registráveis e conferíveis** — que é o que se pede num incidente ou numa fiscalização."}},
  {"h2": "Consentimento por finalidade"},
  { code: `adopt Arcane.Privacidade as P

c := P.consentimentos()
c.conceder("ana", "nota-fiscal", "1", 100)
c.conceder("ana", "marketing", "1", 100)
c.revogar("ana", "marketing", 500)

// Uma finalidade nao autoriza outra.
assert c.pode("ana", "nota-fiscal", "", 600)
assert not c.pode("ana", "pesquisa", "", 600)

// A revogacao vale dali em diante — e o passado continua respondivel.
assert c.pode("ana", "marketing", "", 300)
assert not c.pode("ana", "marketing", "", 600)
assert len(c.historico("ana")) is 3
out c.finalidades("ana")`, lang: 'df' },
  {"h2": "Necessidade e retenção"},
  { code: `adopt Arcane.Privacidade as P

clientes := [
    {"id": 1, "nome": "Ana", "cpf": "529.982.247-25", "cidade": "Recife", "criado": "2019-01-10"},
    {"id": 2, "nome": "Bia", "cpf": "111.444.777-35", "cidade": "Natal", "criado": "2026-08-01"}
]

// O relatorio de vendas por cidade nao precisa de nome nem de CPF.
relatorio := P.minimizar(clientes, ["id", "cidade"])
assert "cpf" not in relatorio[0]

// Cinco anos de retencao: o que passou do prazo, e o que nao diz quando nasceu.
agora := 1790000000
vencidos := P.vencidos(clientes, "criado", 5 * 365, agora)
assert len(vencidos) is 1 and vencidos[0]["id"] is 1
out $"{len(vencidos)} registro(s) a eliminar"`, lang: 'df' },
  {"h2": "Acesso e eliminação — em todo lugar"},
  { code: `adopt Arcane.Privacidade as P

banco := {"ana": {"email": "ana@exemplo.com"}}
newsletter := ["ana@exemplo.com"]

t := P.titulares()
t.registrar("banco", lambda tit: banco[tit] ?? void, lambda tit: pop(banco, tit))
t.registrar("newsletter",
    lambda tit: [e cycle e in newsletter given e.startswith(tit)],
    lambda tit: newsletter.remove("ana@exemplo.com"))

copia := t.exportar("ana")
assert copia["completo"] and copia["dados"]["banco"]["email"] is "ana@exemplo.com"

r := t.esquecer("ana")
assert r["completo"] and r["apagados"] is ["banco", "newsletter"]
assert "ana" not in banco and len(newsletter) is 0
out "acesso e eliminacao em todo lugar registrado"`, lang: 'df' },
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["consentimento **por finalidade**, com versão do termo", "o aceite da nota fiscal vira autorização de marketing"], ["a revogação acrescenta, não apaga", "não se prova que havia consentimento no dia do envio"], ["minimizar por lista de **permitidos**", "o campo novo (o CPF de ontem) sai no relatório sem ninguém decidir"], ["o registro **sem data** é vencido", "o que não diz quando nasceu fica para sempre"], ["o pedido do titular relata **falhas**", "o dado apagado em nove de onze lugares, e a resposta *“feito”*"]]}},
  {"p": "Continue em [Anonimização](/docs/seguranca/anonimizacao) e [Arcane.Privacidade](/docs/biblioteca/privacidade)."},
];

const headings = [{ id: 'consentimento-por-finalidade', text: "Consentimento por finalidade", level: 2 as const }, { id: 'necessidade-e-retencao', text: "Necessidade e retenção", level: 2 as const }, { id: 'acesso-e-eliminacao-em-todo-lugar', text: "Acesso e eliminação — em todo lugar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"LGPD na prática"}
      description={"Finalidade, necessidade, consentimento, retenção e os direitos do titular — como operações sobre dado, com Arcane.Privacidade."}
      href={"/docs/seguranca/privacidade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
