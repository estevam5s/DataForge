// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/oop_meta.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Metaclasses",
  description: "meta blueprint e using: interceptar a criação de classes, a construção de objetos e o acesso a membros, com ganchos de nome fixo.",
};

const blocos: Bloco[] = [
  {"p": "Uma metaclasse é o blueprint que governa como **outros blueprints** nascem e se comportam. Em DataForge ela é um `meta blueprint`, aplicado com `using`, e fala com a linguagem por **ganchos de nome fixo** — um `on_…` desconhecido é recusado com sugestão, porque um gancho com nome errado nunca rodaria e nada avisaria."},
  {"table": {"head": ["Gancho", "Quando", "Devolver algo"], "rows": [["`on_forge(molde)`", "o blueprint acabou de ser montado", "substitui o blueprint"], ["`on_extend(mae, filha)`", "um blueprint governado ganhou filha", "—"], ["`on_spawn(molde, args)`", "antes de construir", "entrega esse objeto no lugar"], ["`on_ready(obj)`", "o objeto nasceu, invariantes conferidas", "—"], ["`on_read(obj, nome, valor)`", "toda leitura de membro", "troca o valor lido"], ["`on_missing(obj, nome)`", "leitura de membro que não existe", "é o valor lido"], ["`on_write(obj, nome, valor)`", "toda escrita de campo", "troca o valor gravado"], ["`on_call(obj, nome, args)`", "chamada de método vinda de fora", "—"], ["`on_serialize(obj, vault)`", "`Objetos.para_vault`", "substitui o vault"], ["`on_deserialize(molde, vault)`", "`Objetos.de_vault`", "substitui o vault"]]}},
  {"h2": "Registro automático de classes"},
  { code: `adopt Arcane.Reflexo as R

meta blueprint Registro:
    tabelas := {}
    action on_forge(molde):
        self.tabelas[R.nome(molde)] := R.nome(molde).lower() + "s"

blueprint Entidade using Registro:
    id := 0

blueprint Usuario extends Entidade:
    nome := ""

blueprint Pedido extends Entidade:
    total := 0

reg := R.meta_instancia(Pedido)
assert reg.tabelas["Usuario"] is "usuarios"
assert len(reg.tabelas) is 3`, lang: 'df' },
  {"p": "A metaclasse é **herdada**: `Usuario` não escreve `using`, e é governado. Ela tem uma instância só, compartilhada por tudo que governa — é o `self` dos ganchos e onde ela guarda estado."},
  {"h2": "Validar a classe na declaração"},
  { code: `adopt Arcane.Reflexo as R

meta blueprint ComId:
    action on_forge(molde):
        nomes := [c["nome"] cycle c in R.campos(molde)]
        given not ("id" in nomes):
            trigger $"{R.nome(molde)} precisa de um campo 'id'"

blueprint Cliente using ComId:
    id := 0

monitor:
    blueprint Rascunho using ComId:
        texto := ""
    assert no
handle Error as e:
    assert "precisa de um campo" in e.message`, lang: 'df' },
  {"h2": "Instanciação controlada e auditoria"},
  { code: `meta blueprint Auditado:
    escritas := []
    unicos := {}
    action on_write(obj, nome, valor):
        self.escritas.append(nome)
    action on_spawn(molde, args):
        yield void            // void: constrói normalmente

blueprint Config using Auditado:
    porta := 80
    action trocar(p):
        self.porta := p

c := spawn Config()
c.trocar(8080)
c.porta := 9090
assert c.porta is 9090`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Um gancho não dispara outro", "texto": "Dentro de `on_read`, ler um campo do objeto não chama `on_read` de novo — seria recursão sem fim. E duas metaclasses só convivem na mesma linhagem se uma descender da outra: a filha não pode escolher qual regra da mãe ignorar (`MetaclassError`)."}},
];

const headings = [{ id: 'registro-automatico-de-classes', text: "Registro automático de classes", level: 2 as const }, { id: 'validar-a-classe-na-declaracao', text: "Validar a classe na declaração", level: 2 as const }, { id: 'instanciacao-controlada-e-auditoria', text: "Instanciação controlada e auditoria", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Metaclasses"}
      description={"meta blueprint e using: interceptar a criação de classes, a construção de objetos e o acesso a membros, com ganchos de nome fixo."}
      href={"/docs/oop/metaclasses"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
