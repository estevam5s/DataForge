// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/banco.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Migrações",
  description: "Com histórico no banco, não num arquivo — e nunca apagando dado sozinho.",
};

const blocos: Bloco[] = [
  {"h2": "A forma simples: a diferença"},
  {"p": "O modelo descreve como a tabela deveria ser. `diferenca()` compara com como ela **é**:"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
U := Forge.modelo("Usuario", {
    "id": {"tipo": "Serial"},
    "nome": {"tipo": "Texto", "obrigatorio": yes}
}, {"conexao": db})
Forge.migrar_tudo(db)

// agora o modelo cresce
U2 := Forge.modelo("Usuario", {
    "id": {"tipo": "Serial"},
    "nome": {"tipo": "Texto", "obrigatorio": yes},
    "telefone": {"tipo": "Texto"}
}, {"conexao": db})

d := U2.diferenca()
assert d["colunas_faltando"] is ["telefone"]

U2.aplicar_diferenca()
assert U2.diferenca()["colunas_faltando"] is []`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "`aplicar_diferenca` nunca apaga", "texto": "Ele cria o que falta e **relata** o que sobra, sem remover. Perda de dado não se automatiza: uma coluna que sumiu do modelo pode ter sido um engano de digitação, e a diferença entre um `ALTER TABLE DROP` e uma restauração de backup é grande."}},
  {"p": "Comparar o modelo com a tabela de verdade é melhor que confiar num histórico de arquivos, que diverge assim que alguém mexe no banco à mão."},
  {"h2": "A forma completa: passos numerados"},
  {"p": "Para o que a diferença não cobre — renomear uma coluna, migrar dados, criar um índice composto:"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
m := Forge.migracoes(db)

m.passo("001_cria_usuarios",
    lambda c => c.executar(
        "create table usuarios (id integer primary key, nome text)"),
    lambda c => c.executar("drop table usuarios"))

m.passo("002_acrescenta_email",
    lambda c => c.executar("alter table usuarios add column email text"),
    lambda c => c.executar("alter table usuarios drop column email"))

assert m.subir() is ["001_cria_usuarios", "002_acrescenta_email"]
assert m.pendentes() is []
assert m.subir() is []              // rodar de novo não repete`, lang: 'df' },
  {"h2": "O histórico mora no banco"},
  {"p": "Numa tabela `_forge_migracoes`. Guardá-lo ali, e não num arquivo, é o que faz duas máquinas concordarem sobre o estado: **um arquivo versionado diz o que deveria ter rodado; a tabela diz o que rodou.**"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
m := Forge.migracoes(db)
m.passo("001", lambda c => c.executar("create table a (id integer)"),
        lambda c => c.executar("drop table a"))
m.subir()

e := m.estado()
assert e["aplicadas"] is 1
assert e["pendentes"] is 0
assert e["passos"][0]["reversivel"] is yes`, lang: 'df' },
  {"h2": "Falha para tudo"},
  {"p": "Continuar depois de uma migração que falhou deixa o banco num estado que nenhuma migração previu:"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
m := Forge.migracoes(db)
m.passo("001", lambda c => c.executar("create table a (id integer)"))
m.passo("002", lambda c => c.executar("isto não é sql"))
m.passo("003", lambda c => c.executar("create table c (id integer)"))

monitor:
    m.subir()
handle MigrationError as e:
    assert "002" in e.message

// a 003 não rodou
assert not ("c" in Forge.tabelas(db))`, lang: 'df' },
  {"h2": "Desfazer"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
m := Forge.migracoes(db)
m.passo("001", lambda c => c.executar("create table a (id integer)"),
        lambda c => c.executar("drop table a"))
m.subir()

assert m.descer(1) is ["001"]
assert not ("a" in Forge.tabelas(db))`, lang: 'df' },
  {"p": "Só desce o que declarou como desfazer. Uma migração sem caminho de volta avisa em vez de tentar adivinhar."},
  {"callout": {"tipo": "dica", "titulo": "Escreva o `descer` mesmo que não use", "texto": "O momento em que você precisa dele é o pior momento possível para escrevê-lo. Escrever no mesmo dia da subida custa dois minutos."}},
];

const headings = [{ id: 'a-forma-simples-a-diferenca', text: "A forma simples: a diferença", level: 2 as const }, { id: 'a-forma-completa-passos-numerados', text: "A forma completa: passos numerados", level: 2 as const }, { id: 'o-historico-mora-no-banco', text: "O histórico mora no banco", level: 2 as const }, { id: 'falha-para-tudo', text: "Falha para tudo", level: 2 as const }, { id: 'desfazer', text: "Desfazer", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Migrações"}
      description={"Com histórico no banco, não num arquivo — e nunca apagando dado sozinho."}
      href={"/docs/orm/migracoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
