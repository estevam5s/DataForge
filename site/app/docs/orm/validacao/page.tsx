// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/banco_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Validação, ganchos e marcas",
  description: "O que o modelo recusa antes de gravar, o que ele preenche sozinho, e a remoção que não apaga.",
};

const blocos: Bloco[] = [
  {"p": "Três coisas que todo sistema escreve à mão em cada lugar — e que, escritas em cada lugar, são esquecidas em um deles."},
  {"h2": "Validar devolve TODOS os problemas"},
  {"p": "Parar no primeiro erro faz o formulário ser corrigido campo a campo, num vaivém: a pessoa conserta o nome, envia, e descobre que o e-mail também estava errado. A lista inteira é o que a tela precisa."},
  { code: `adopt Arcane.Forge as Forge

db := Forge.memoria()
Forge.limpar_modelos()

Usuario := Forge.modelo("Usuario", {"id": "Serial"})
Usuario.campo("nome", "Texto", obrigatorio := yes)
Usuario.campo("email", "Texto", obrigatorio := yes, unico := yes)
Usuario.campo("idade", "Inteiro", padrao := 0)
Forge.ligar(Usuario, db)
Usuario.migrar()

// Faltam os DOIS obrigatorios, e a lista traz os dois.
problemas := Usuario.validar({"idade": 30})
out $"{len(problemas)} problema(s) — e nao so o primeiro:"
cycle p in problemas:
    out $"   {p['campo']}: {p['motivo']}"
assert len(problemas) is 2

assert len(Usuario.validar({"nome": "Ana", "email": "ana@x.com", "idade": 30})) is 0
out "o valido passa"

Forge.fechar(db)`, lang: 'df' },
  {"h2": "Ganchos"},
  { code: `adopt Arcane.Forge as Forge

db := Forge.memoria()
Forge.limpar_modelos()

Conta := Forge.modelo("Conta", {"id": "Serial", "email": "Texto"})
Forge.ligar(Conta, db)
Conta.migrar()

// O e-mail entra sempre em minusculas. Normalizar na aplicacao e o
// que faz o comportamento deixar de depender do motor: o MySQL
// compara sem diferenciar maiusculas, e o Postgres diferencia.
action normalizar(dados):
    dados["email"] := (dados["email"] ?? "").lower()
    yield dados

Conta.antes_de_salvar(normalizar)

c := Conta.criar({"email": "Ana@LOJA.com"})
out $"gravado como: {c['email']}"
assert c["email"] is "ana@loja.com"

Forge.fechar(db)`, lang: 'df' },
  {"h2": "Marcas de tempo e remoção suave"},
  {"table": {"head": ["", "O que faz", "Por que"], "rows": [["`com_marcas_de_tempo()`", "`criado_em` e `atualizado_em`, mantidos sozinhos", "a pergunta *“quando isto mudou?”* aparece em toda investigação, e não dá para responder depois"], ["`com_remocao_suave()`", "`remover` **marca**; as buscas ignoram o marcado", "apagar de verdade é irreversível, e o pedido mais comum depois de um apagar é desfazer"]]}},
  { code: `adopt Arcane.Forge as Forge

db := Forge.memoria()
Forge.limpar_modelos()

Nota := Forge.modelo("Nota", {"id": "Serial", "texto": "Texto"})
Nota.com_marcas_de_tempo()
Nota.com_remocao_suave()
Forge.ligar(Nota, db)
Nota.migrar()

n := Nota.criar({"texto": "primeira"})
out $"criado_em preenchido: {n['criado_em'] isnt void}"

Nota.criar({"texto": "segunda"})
assert Nota.contar() is 2

Nota.remover(n["id"])

// As buscas ignoram o removido — mas ele continua no banco.
assert Nota.contar() is 1
out "removida da vista, e nao do disco"

Forge.fechar(db)`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Remoção suave e LGPD se contradizem", "texto": "O direito à eliminação pede que o dado **saia**, e a remoção suave o mantém. As duas convivem com uma regra escrita: soft delete para o desfazer de curto prazo (dias), e um processo de expurgo que apaga de verdade no fim do prazo — **inclusive nas cópias de segurança**, que é onde quase todo mundo falha. Veja [Operação e conformidade](/docs/seguranca/operacao)."}},
  {"p": "Continue em [Migrações](/docs/orm/migracoes) e [Escopos](/docs/orm/escopos)."},
];

const headings = [{ id: 'validar-devolve-todos-os-problemas', text: "Validar devolve TODOS os problemas", level: 2 as const }, { id: 'ganchos', text: "Ganchos", level: 2 as const }, { id: 'marcas-de-tempo-e-remocao-suave', text: "Marcas de tempo e remoção suave", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Validação, ganchos e marcas"}
      description={"O que o modelo recusa antes de gravar, o que ele preenche sozinho, e a remoção que não apaga."}
      href={"/docs/orm/validacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
