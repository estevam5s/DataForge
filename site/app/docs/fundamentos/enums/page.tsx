import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Enums",
  description: "Conjuntos fechados de valores nomeados, com valores associados e integração com match.",
};

const blocos: Bloco[] = [
  {"h2": "Declarar"},
  { code: `enum Status:
    Rascunho
    Publicado
    Arquivado` },
  {"p": "Cada membro carrega três coisas:"},
  { code: `out Status.Publicado.name     # "Publicado" — o identificador
out Status.Publicado.value    # "Publicado" — o valor (padrão: o nome)
out Status.Publicado.index    # 1           — a posição na declaração` },
  {"h2": "O problema que resolve"},
  {"p": "Sem enum, estados viram texto solto:"},
  { code: `pedido := {"status": "publicado"}
given pedido["status"] is "Publicado":     # nunca entra: caixa diferente` },
  {"p": "Um erro de digitação vira um `no` silencioso. Com enum, `Status.Publicad` é erro na hora — e o [`dataforge check`](/docs/cli/check) acha antes mesmo de rodar:"},
  { code: `Enum 'Status' has no member 'Publicad'. Members: Rascunho, Publicado, Arquivado`, lang: 'text' },
  {"h2": "Valores associados"},
  { code: `enum Prioridade:
    Baixa := 1
    Media := 5
    Alta := 10
    Critica := 100

enum Moeda:
    Real := "BRL"
    Dolar := "USD"` },
  {"p": "Sem `:=`, o valor é o próprio nome. Com `:=`, é o que você escrever."},
  {"h3": "A ponte com o mundo externo"},
  {"p": "Dentro do programa você quer `Moeda.Real`. Mas o banco guarda `\"BRL\"`, a API devolve `\"BRL\"`, o CSV tem `\"BRL\"`. O valor é a **ponte**:"},
  { code: `vinda_do_banco := "BRL"
moeda := Moeda.from_value(vinda_do_banco)     # Moeda.Real
moeda := Moeda.from_value(entrada) ?? Moeda.Real   # com padrão` },
  {"p": "`from_value` devolve `void` para um valor desconhecido, em vez de inventar um membro. Combinado com `??`, isso vira um padrão limpo."},
  {"h3": "Valores numéricos como ordem"},
  { code: `tarefas := [
    {"titulo": "revisar", "prio": Prioridade.Baixa},
    {"titulo": "deploy", "prio": Prioridade.Critica}
]

out sorted(tarefas >> morph t: t["prio"].value)     # [1, 100]` },
  {"p": "Isso é mais expressivo que depender de `.index`: o índice reflete a ordem de **declaração**, o valor reflete a ordem de **negócio**. Inserir um membro no meio muda os índices, mas não os pesos."},
  {"h2": "Os utilitários"},
  {"table": {"head": ["Chamada", "Devolve"], "rows": [["`Status.names()`", "`[\"Rascunho\", \"Publicado\", \"Arquivado\"]`"], ["`Status.values()`", "os valores"], ["`Status.members()`", "os membros, para percorrer"], ["`Status.count()`", "`3`"], ["`Status.has(\"X\")`", "`yes` / `no`"], ["`Status.from_name(\"X\")`", "o membro, ou `void`"], ["`Status.from_value(v)`", "o membro com aquele valor, ou `void`"]]}},
  { code: `cycle s in Status.members():
    out $"  {s.index}: {s.name}"` },
  {"h2": "Com match"},
  { code: `action acao(luz):
    match luz:
        point Semaforo.Vermelho:
            yield "frear"
        point Semaforo.Amarelo:
            yield "reduzir"
        point Semaforo.Verde:
            yield "acelerar"
        default:
            yield "estado desconhecido"` },
  {"callout": {"tipo": "atencao", "titulo": "Mantenha o default", "texto": "DataForge 4.0 ainda **não verifica exaustividade** — se amanhã alguém adicionar `Semaforo.Piscante`, nada avisa. O `default` é sua rede. Durante o desenvolvimento, faça-o falhar ruidosamente: `trigger $\"estado nao tratado: {luz}\"`."}},
  {"h2": "Máquina de estados"},
  {"p": "O padrão completo tem três partes: o enum enumera os estados, uma tabela declara as transições legítimas, e as ações só consultam a tabela."},
  { code: `enum Pedido:
    Novo
    Pago
    Enviado
    Entregue

steady TRANSICOES := {
    "Novo": ["Pago"],
    "Pago": ["Enviado"],
    "Enviado": ["Entregue"],
    "Entregue": []
}

action pode_ir(de, para):
    yield para.name in TRANSICOES[de.name]

out pode_ir(Pedido.Novo, Pedido.Pago)        # yes
out pode_ir(Pedido.Novo, Pedido.Entregue)    # no` },
  {"p": "Nenhum estado inválido é representável, e nenhuma transição inválida é possível. `Entregue` com lista vazia é um estado terminal."},
];

const headings = [{ id: 'declarar', text: "Declarar", level: 2 as const }, { id: 'o-problema-que-resolve', text: "O problema que resolve", level: 2 as const }, { id: 'valores-associados', text: "Valores associados", level: 2 as const }, { id: 'os-utilitarios', text: "Os utilitários", level: 2 as const }, { id: 'com-match', text: "Com match", level: 2 as const }, { id: 'maquina-de-estados', text: "Máquina de estados", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Enums"}
      description={"Conjuntos fechados de valores nomeados, com valores associados e integração com match."}
      href={"/docs/fundamentos/enums"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
