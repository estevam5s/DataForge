// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/banco.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "ORM",
  description: "Modelos com validação, tipos convertidos e relações que não fazem N+1.",
};

const blocos: Bloco[] = [
  {"p": "Um modelo descreve uma tabela e o que vale nela. O que ele acrescenta ao construtor de consultas:"},
  {"list": ["**validação** antes de ir ao banco, e com **todos** os erros de uma vez", "**tipos convertidos** — o que sai do banco volta como o modelo declara", "**relações** carregadas sem o problema de N+1", "**migrações** a partir da diferença entre o modelo e a tabela"]},
  {"h2": "Declarando"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")

Usuario := Forge.modelo("Usuario", {
    "id":    {"tipo": "Serial"},
    "email": {"tipo": "Texto", "obrigatorio": yes, "unico": yes,
              "validacoes": ["email"]},
    "nome":  {"tipo": "Texto", "obrigatorio": yes,
              "validacoes": [["minimo", 2]]},
    "idade": {"tipo": "Inteiro", "padrao": 0,
              "validacoes": [["minimo", 0], ["maximo", 130]]},
    "ativo": {"tipo": "Booleano", "padrao": yes},
    "perfil": {"tipo": "Json"}
}, {"conexao": db, "marcas_de_tempo": yes})

Forge.migrar_tudo(db)

ana := Usuario.criar({"email": "ana@exemplo.com", "nome": "Ana", "idade": 30})
assert ana["id"] is 1
assert ana["ativo"] is yes`, lang: 'df' },
  {"p": "O nome da tabela sai do plural do modelo: `Usuario` → `usuarios`, `Pedido` → `pedidos`, `Animal` → `animais`. Passe `{\"tabela\": \"...\"}` para um irregular."},
  {"h2": "Os tipos"},
  {"table": {"head": ["Forge", "PostgreSQL", "MySQL", "SQLite"], "rows": [["`Serial`", "SERIAL PRIMARY KEY", "INT AUTO_INCREMENT PK", "INTEGER PK AUTOINCREMENT"], ["`Inteiro`", "INTEGER", "INT", "INTEGER"], ["`Grande`", "BIGINT", "BIGINT", "INTEGER"], ["`Decimal`", "NUMERIC(18,6)", "DECIMAL(18,6)", "NUMERIC"], ["`Real`", "DOUBLE PRECISION", "DOUBLE", "REAL"], ["`Texto`", "TEXT", "VARCHAR(255)", "TEXT"], ["`TextoLongo`", "TEXT", "LONGTEXT", "TEXT"], ["`Booleano`", "BOOLEAN", "TINYINT(1)", "INTEGER"], ["`Data` / `DataHora`", "DATE / TIMESTAMPTZ", "DATE / DATETIME", "TEXT"], ["`Json`", "JSONB", "JSON", "TEXT"], ["`Uuid`", "UUID", "CHAR(36)", "TEXT"], ["`Binario`", "BYTEA", "BLOB", "BLOB"]]}},
  {"callout": {"tipo": "dica", "titulo": "A conversão importa", "texto": "SQLite guarda booleano como 0 e 1. Sem a conversão de volta, `given usuario[\"ativo\"]:` seria sempre verdadeiro — 0 é um inteiro, e a comparação nunca falharia visivelmente. Erros assim vivem meses."}},
  {"h2": "Validação"},
  {"p": "Todos os problemas de uma vez. Um formulário que aponta um erro por vez faz o usuário submeter cinco vezes para descobrir cinco problemas:"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
Usuario := Forge.modelo("Usuario", {
    "id": {"tipo": "Serial"},
    "email": {"tipo": "Texto", "obrigatorio": yes, "validacoes": ["email"]},
    "nome": {"tipo": "Texto", "obrigatorio": yes, "validacoes": [["minimo", 2]]},
    "idade": {"tipo": "Inteiro", "validacoes": [["maximo", 130]]}
}, {"conexao": db})
Forge.migrar_tudo(db)

monitor:
    Usuario.criar({"email": "não-é-email", "nome": "X", "idade": 999})
handle ValidationError as e:
    // e.campos traz um item por problema
    assert len(e.campos) is 3`, lang: 'df' },
  {"table": {"head": ["Regra", "Cobra"], "rows": [["`\"obrigatorio\"`", "não vazio"], ["`\"email\"`", "formato de e-mail"], ["`[\"minimo\", n]`", "número ≥ n, ou texto com n caracteres"], ["`[\"maximo\", n]`", "número ≤ n, ou texto até n caracteres"], ["`[\"formato\", padrao]`", "casa com a expressão regular"], ["`[\"um_de\", [a, b]]`", "está na lista"], ["`\"positivo\"`", "maior que zero"]]}},
  {"h2": "Buscar e escrever"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
U := Forge.modelo("Usuario", {
    "id": {"tipo": "Serial"},
    "nome": {"tipo": "Texto", "obrigatorio": yes},
    "idade": {"tipo": "Inteiro", "padrao": 0}
}, {"conexao": db})
Forge.migrar_tudo(db)

U.criar({"nome": "Ana", "idade": 30})
U.criar({"nome": "Bia", "idade": 25})

assert len(U.todos()) is 2
assert U.buscar(1)["nome"] is "Ana"
assert U.buscar(99) is void
assert U.primeiro(nome := "Bia")["idade"] is 25
assert U.contar() is 2
assert U.existe(nome := "Ana") is yes

U.atualizar(1, {"idade": 31})
assert U.buscar(1)["idade"] is 31

U.criar_ou_atualizar({"nome": "Ana"}, {"idade": 32})
assert U.contar() is 2          // não criou outra

U.remover(2)
assert U.contar() is 1`, lang: 'df' },
  {"p": "`buscar_ou_erro` levanta `RecordNotFoundError` quando não acha — útil numa rota onde a ausência é 404, e desnecessário onde ela é prevista."},
  {"h2": "Marcas de tempo e remoção suave"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
U := Forge.modelo("Usuario", {
    "id": {"tipo": "Serial"},
    "nome": {"tipo": "Texto", "obrigatorio": yes}
}, {"conexao": db, "marcas_de_tempo": yes, "remocao_suave": yes})
Forge.migrar_tudo(db)

u := U.criar({"nome": "Ana"})
assert u["criado_em"] isnt void

U.remover(u["id"])
assert U.contar() is 0                                  // some das buscas
assert len(Forge.consultar(db, "select * from usuarios")) is 1   // mas está lá`, lang: 'df' },
  {"h2": "Ganchos"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
U := Forge.modelo("Usuario", {
    "id": {"tipo": "Serial"},
    "nome": {"tipo": "Texto", "obrigatorio": yes}
}, {"conexao": db})
Forge.migrar_tudo(db)

U.antes_de_salvar(lambda dados => {"nome": dados["nome"].to_upper()})

assert U.criar({"nome": "ana"})["nome"] is "ANA"`, lang: 'df' },
];

const headings = [{ id: 'declarando', text: "Declarando", level: 2 as const }, { id: 'os-tipos', text: "Os tipos", level: 2 as const }, { id: 'validacao', text: "Validação", level: 2 as const }, { id: 'buscar-e-escrever', text: "Buscar e escrever", level: 2 as const }, { id: 'marcas-de-tempo-e-remocao-suave', text: "Marcas de tempo e remoção suave", level: 2 as const }, { id: 'ganchos', text: "Ganchos", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"ORM"}
      description={"Modelos com validação, tipos convertidos e relações que não fazem N+1."}
      href={"/docs/orm"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
