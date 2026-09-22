// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/testes_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testes de integração",
  description: "O banco de verdade, a rota inteira — e onde termina a unidade.",
};

const blocos: Bloco[] = [
  {"p": "O teste unitário prova que cada peça funciona. O de integração prova que **elas se encaixam**: o SQL que a regra monta é aceito pelo banco, a rota traduz o JSON que o cliente manda. É o teste que pega o erro que só existe entre duas peças."},
  {"h2": "Com o banco de verdade"},
  { code: `adopt Arcane.Crucible
adopt Arcane.Database as DB

action criar_esquema(db):
    DB.execute(db, "CREATE TABLE contas (id INTEGER PRIMARY KEY, dono TEXT UNIQUE, saldo REAL CHECK (saldo >= 0))")

action abrir(db, dono):
    DB.execute(db, "INSERT INTO contas (dono, saldo) VALUES (?, 0)", [dono])

action depositar(db, dono, valor):
    DB.execute(db, "UPDATE contas SET saldo = saldo + ? WHERE dono = ?", [valor, dono])

action saldo(db, dono):
    yield DB.query(db, "SELECT saldo FROM contas WHERE dono = ?", [dono])[0]["saldo"]

crucible "contas no banco":
    trial "deposito aparece no saldo":
        db := DB.memory()
        criar_esquema(db)
        abrir(db, "ana")
        depositar(db, "ana", 50)
        expect saldo(db, "ana") is 50.0

    trial "o banco recusa dono repetido":
        db := DB.memory()
        criar_esquema(db)
        abrir(db, "ana")
        expect(lambda => abrir(db, "ana")).to_raise()

    trial "o CHECK do banco segura o saldo negativo":
        db := DB.memory()
        criar_esquema(db)
        abrir(db, "bia")
        expect(lambda => depositar(db, "bia", -10)).to_raise()

r := Crucible.run()
assert r["falhou"] is 0 and r["passou"] is 3`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Um banco novo por teste", "texto": "`DB.memory()` dentro do trial dá a cada teste um banco limpo, em microssegundos. Um banco compartilhado entre testes faz o resultado depender da ordem — e `Crucible.banco(db)` desfaz a transação no fim do trial quando o banco precisa ser o mesmo."}},
  {"h2": "Com a rota inteira"},
  { code: `adopt Kiln
adopt Arcane.Crucible

server api on 0:
    route POST "/somar":
        given not is_number(body["a"] ?? void) or not is_number(body["b"] ?? void):
            respond 400 json {"erro": "a e b precisam ser numeros"}
        respond json {"resultado": body["a"] + body["b"]}

crucible "rota /somar":
    trial "soma o que chega":
        r := Kiln.test(api, "POST", "/somar", {"a": 2, "b": 3})
        expect r["status"] is 200
        expect r["body"]["resultado"] is 5

    trial "texto no lugar de numero e 400, e nao 500":
        expect Kiln.test(api, "POST", "/somar", {"a": "2", "b": 3})["status"] is 400

r := Crucible.run()
assert r["falhou"] is 0`, lang: 'df' },
  {"h2": "Onde termina a unidade"},
  {"table": {"head": ["Unitário", "Integração", "Ponta a ponta"], "rows": [["a regra, sem banco", "a regra **com** o banco", "o sistema subido"], ["milissegundos", "dezenas de ms", "segundos"], ["centenas", "dezenas", "poucos"], ["diz **qual** peça", "diz **qual encaixe**", "diz que **algo** quebrou"]]}},
  {"p": "Continue em [Ponta a ponta](/docs/testes/ponta-a-ponta) e [A pirâmide](/docs/testes/piramide)."},
];

const headings = [{ id: 'com-o-banco-de-verdade', text: "Com o banco de verdade", level: 2 as const }, { id: 'com-a-rota-inteira', text: "Com a rota inteira", level: 2 as const }, { id: 'onde-termina-a-unidade', text: "Onde termina a unidade", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Testes de integração"}
      description={"O banco de verdade, a rota inteira — e onde termina a unidade."}
      href={"/docs/testes/integracao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
