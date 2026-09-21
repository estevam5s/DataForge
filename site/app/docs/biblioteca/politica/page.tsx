// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/politica.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Politica",
  description: "Motor de autorização: RBAC com herança, ABAC por atributo, ACL por objeto, grupos, isolamento por inquilino, negação explícita que vence o papel e delegação com prazo. O padrão é negar, e toda decisão diz qual regra a tomou — um motor que responde só sim/não é impossível de auditar.",
};

const blocos: Bloco[] = [
  {"p": "Autorização escrita como `given usuario[\"papel\"] is \"admin\":` espalha a decisão por cinquenta arquivos. Quando a regra muda — e ela sempre muda — não há onde olhar, e **o que fica para trás não dá erro: fica permitindo**."},
  {"p": "O que este módulo acrescenta não é conveniência. São quatro garantias que um `given` não tem."},
  {"table": {"head": ["Garantia", "Sem ela"], "rows": [
      ["o padrão é **negar**", "uma ação nova nasce permitida para todo mundo"],
      ["**negar vence permitir**", "a exceção “este usuário não” é apagada por um papel"],
      ["ninguém **delega o que não tem**", "a cadeia de delegações cria autoridade do nada"],
      ["a delegação **vence**", "delegar vira conceder, com passos a mais — e ninguém lembra de revogar"]
    ]}},
  { code: `adopt Arcane.Politica as P

pol := P.motor("loja")
pol.papel("leitor", ["pedido:ler"])
pol.papel("editor", ["pedido:escrever"], herda := ["leitor"])
pol.papel("admin", ["pedido:apagar", "usuario:*"], herda := ["editor"])

ana := {"id": "ana", "papel": "admin"}

assert pol.pode(ana, "pedido:ler")["permitido"]

// A decisao explica QUEM decidiu — e nomeia o papel que realmente
// tem a permissao, e nao o que foi consultado.
out pol.pode(ana, "pedido:ler")["motivo"]
// o papel 'leitor' permite 'pedido:ler' (por 'admin')`, title: `RBAC com herança` },
  {"callout": {"tipo": "atencao", "titulo": "A decisão não é um booleano", "texto": "`pode()` devolve `{permitido, motivo, regra, sujeito, ação, recurso}`. Um motor que responde só `yes`/`no` é impossível de auditar e quase impossível de depurar: o incidente pergunta *por que ele conseguiu*, e a resposta é um encolher de ombros. O `motivo` é o que vai para a trilha de auditoria."}},
  {"h2": "As sete camadas, e por que a ordem é contrato"},
  {"p": "`pode()` percorre as camadas nesta ordem e para na primeira que decide. A ordem não é detalhe de implementação: a ACL existe para dizer *“neste objeto, não”*, e se o papel viesse antes ela nunca seria alcançada."},
  {"table": {"head": ["#", "Camada", "O que ela decide"], "rows": [
      ["1", "`tenant`", "um sujeito de outro inquilino não existe para esta política"],
      ["2", "`negacao`", "a negação explícita — vence tudo"],
      ["3", "`acl`", "a lista daquele objeto; **estar nela e não ter a ação é um não**"],
      ["4", "`regra`", "ABAC: a condição olha os valores. `void` é *não opino*"],
      ["5", "`papel`", "RBAC, com herança e curinga explícito"],
      ["6", "`delegacao`", "emprestada, e ainda no prazo"],
      ["7", "`padrao`", "negar"]
    ]}},
  { code: `adopt Arcane.Politica as P

pol := P.motor("docs")
pol.papel("usuario", ["doc:ler"])

// ABAC: a regra decide olhando os valores. 'void' e "nao opino" —
// uma regra que so soubesse dizer nao bloquearia tudo que ela nao
// entende.
pol.regra("somente-dono",
    lambda s, a, r => ((r["dono"] is s["id"]) given r isnt void otherwise void),
    acoes := ["doc:escrever"])

carlos := {"id": "carlos", "papel": "usuario"}

assert pol.pode(carlos, "doc:escrever", {"id": 1, "dono": "carlos"})["permitido"]
assert pol.pode(carlos, "doc:escrever", {"id": 2, "dono": "dani"})["permitido"] is no

// A regra nao opina sobre ler: a decisao cai no papel, e passa.
assert pol.pode(carlos, "doc:ler", {"id": 2, "dono": "dani"})["permitido"]`, title: `ABAC` },
  {"callout": {"tipo": "atencao", "titulo": "Uma regra que falha NEGA", "texto": "Tratar a exceção como *“não opino”* faria um bug virar autorização — o pior defeito possível num motor de política. A regra que levanta é contada no motivo (`a regra 'x' falhou: …`) e a decisão é **não**."}},
  {"h2": "Delegação"},
  { code: `adopt Arcane.Politica as P

pol := P.motor("fin")
pol.papel("gerente", ["pagamento:aprovar"])
pol.papel("analista", ["pagamento:ler"])

chefe := {"id": "chefe", "papel": "gerente"}
sub := {"id": "sub", "papel": "analista"}

pol.delegar(chefe, sub, ["pagamento:aprovar"], prazo := 3600.0)
assert pol.pode(sub, "pagamento:aprovar")["permitido"]

// Ninguem delega o que nao tem: sem essa conferencia, A delega a B
// algo que A nao pode, B delega a C, e C passa a poder.
monitor:
    pol.delegar(sub, chefe, ["pagamento:apagar"])
handle DelegationError as e:
    out "recusado: autoridade nao se cria do nada"`, title: `delegar` },
  {"h2": "O que ele não faz"},
  {"table": {"head": ["Não faz", "Porque"], "rows": [
      ["não busca o sujeito nem o recurso", "um motor que consulta o banco decidiria com dados que quem chama não viu, e o teste dele passaria a precisar de banco"],
      ["**não substitui a autorização na consulta**", "conferir depois de carregar o pedido ainda carrega o pedido de outra pessoa. A defesa que funciona é o `WHERE` que já filtra pelo dono — isto é a segunda camada"],
      ["não é distribuído", "as políticas vivem no processo. O que precisa ser comum é a **fonte** (o banco de papéis), e não o motor"]
    ]}},
  {"p": "Guia com contexto: [Autorização e capacidades](/docs/seguranca/autorizacao)."},
  {"h2": "Funções (6)"},
  {"table": {"head": ["Assinatura"], "rows": [["`camadas()`"], ["`casa(padrao, concreto)`"], ["`de_vault(nome, definicao)`"], ["`identidade(alvo)`"], ["`motor(nome, inquilino='')`"], ["`separacao_de_funcoes(politica, acao, solicitante, aprovador)`"]]}},
];

const headings = [{ id: 'as-sete-camadas-e-por-que-a-ordem-e-contrato', text: "As sete camadas, e por que a ordem é contrato", level: 2 as const }, { id: 'delegacao', text: "Delegação", level: 2 as const }, { id: 'o-que-ele-nao-faz', text: "O que ele não faz", level: 2 as const }, { id: 'funcoes-6', text: "Funções (6)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Politica"}
      description={"Motor de autorização: RBAC com herança, ABAC por atributo, ACL por objeto, grupos, isolamento por inquilino, negação explícita que vence o papel e delegação com prazo. O padrão é negar, e toda decisão diz qual regra a tomou — um motor que responde só sim/não é impossível de auditar."}
      href={"/docs/biblioteca/politica"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
