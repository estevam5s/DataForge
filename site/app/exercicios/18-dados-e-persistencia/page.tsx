import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "18 · Dados e persistência",
  description: "6 exercícios: serialização, arquivos, SQLite e HTTP.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 18`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["163", "**Serializacao de dados**", "converta estruturas para JSON, CSV, TOML e de volta."], ["164", "**Arquivos e diretorios**", "leia, escreva e organize arquivos com Arcane.IO."], ["165", "**Banco de dados**", "crie tabelas, insira e consulte com Arcane.Database."], ["166", "**Servidor HTTP**", "monte uma API REST com rotas e JSON."], ["167", "**Cliente HTTP e URLs**", "monte URLs, trate respostas e prepare requisicoes."], ["168", "**Projeto: CRUD com persistencia**", "junte banco, validacao e relatorio num sistema completo."]]}},
  {"h2": "163 · Serializacao de dados"},
  {"p": "Converta estruturas para JSON, CSV, TOML e de volta."},
  { code: `// Exercicio 163 — Serializacao de dados
// Enunciado: converta estruturas para JSON, CSV, TOML e de volta.

adopt Arcane.Serialization as Serde

dados := {
    "app": "DataForge",
    "versao": 4,
    "ativo": yes,
    "tags": ["linguagem", "dados"],
    "autor": {"nome": "Ana", "email": "ana@x.com"}
}

// JSON
texto := Serde.to_json(dados)
out $"json: {texto[0:50]}..."
volta := Serde.from_json(texto)
assert volta["versao"] is 4, "roundtrip json"
assert volta["autor"]["nome"] is "Ana", "aninhado preservado"

// JSON legivel
out ""
out Serde.json_pretty(dados["autor"])

// Leitura tolerante: nunca dispara
out ""
bom := Serde.from_json_safe(texto)
ruim := Serde.from_json_safe("{isso nao e json")
out $"valido: ok={bom.ok}"
out $"invalido: ok={ruim.ok}, erro='{ruim.error[0:30]}...'"
assert bom.ok is yes, "json valido"
assert ruim.ok is no, "json invalido nao dispara"
assert ruim.value is void, "valor padrao"

// Caminho pontuado
out ""
out $"autor.nome: {Serde.json_path(dados, "autor.nome")}"
out $"tags.0:     {Serde.json_path(dados, "tags.0")}"
out $"ausente:    {Serde.json_path(dados, "autor.telefone", "nao informado")}"
assert Serde.json_path(dados, "autor.email") is "ana@x.com", "caminho aninhado"
assert Serde.json_path(dados, "tags.1") is "dados", "indice de lista"

// CSV a partir de registros
registros := [
    {"nome": "Ana", "idade": 30, "setor": "vendas"},
    {"nome": "Bruno", "idade": 25, "setor": "ti"}
]
csv := Serde.records_to_csv(registros)
out ""
out csv
lidos := Serde.csv_to_records(csv)
assert len(lidos) is 2, "dois registros"
assert lidos[0]["nome"] is "Ana", "primeiro registro"

// TOML
config := {"servidor": {"host": "localhost", "porta": 8080}, "debug": yes}
out Serde.to_toml(config)
assert Serde.from_toml(Serde.to_toml(config))["servidor"]["porta"] is 8080, "roundtrip toml"

// Achatar e desachatar
plano := Serde.flatten(dados["autor"])
out $"achatado: {plano}"
assert plano["nome"] is "Ana", "achatado"
assert Serde.unflatten({"a.b.c": 1})["a"]["b"]["c"] is 1, "desachatado"

// JSON Lines: um objeto por linha
linhas := Serde.json_lines(registros)
out ""
out $"json lines tem {len(linhas.lines())} linhas"
assert len(Serde.from_json_lines(linhas)) is 2, "roundtrip jsonl"

// Formatos disponiveis
out ""
out $"formatos: {Serde.formats()}"
`, title: `163_serializacao.df` },
  {"h2": "164 · Arquivos e diretorios"},
  {"p": "Leia, escreva e organize arquivos com Arcane.IO."},
  { code: `// Exercicio 164 — Arquivos e diretorios
// Enunciado: leia, escreva e organize arquivos com Arcane.IO.

adopt Arcane.IO as IO
adopt Arcane.Serialization as Serde

pasta := "_exercicio_164"
IO.mkdir(pasta)
assert IO.exists(pasta) is yes, "pasta criada"

// Escrever e ler texto
alvo := IO.join(pasta, "notas.txt")
IO.write(alvo, "primeira linha\\nsegunda linha\\nterceira linha")

conteudo := IO.read(alvo)
out $"lidas {len(conteudo.lines())} linhas"
assert len(conteudo.lines()) is 3, "tres linhas"
assert conteudo.lines()[0] is "primeira linha", "primeira linha"

// Anexar
IO.append(alvo, "\\nquarta linha")
assert len(IO.read(alvo).lines()) is 4, "quatro apos anexar"

// Tamanho e existencia
out $"tamanho: {IO.size(alvo)} bytes"
assert IO.size(alvo) bigger 0, "arquivo tem conteudo"
assert IO.file_exists(alvo) is yes, "existe"
assert IO.exists(IO.join(pasta, "inexistente.txt")) is no, "nao existe"

// Caminhos
out ""
out $"nome:      {IO.basename(alvo)}"
out $"pasta:     {IO.dirname(alvo)}"
out $"extensao:  {IO.ext(alvo)}"
assert IO.basename(alvo) is "notas.txt", "basename"
assert IO.ext(alvo) is ".txt", "extensao"

// JSON direto em arquivo
config := {"tema": "escuro", "fonte": 14, "plugins": ["a", "b"]}
json_alvo := IO.join(pasta, "config.json")
IO.write_json(json_alvo, config)
lido := IO.read_json(json_alvo)
out ""
out $"config lida: {lido}"
assert lido["fonte"] is 14, "json roundtrip"
assert lido["plugins"] is ["a", "b"], "lista preservada"

// CSV direto em arquivo
csv_alvo := IO.join(pasta, "dados.csv")
IO.write_csv(csv_alvo, [["nome", "nota"], ["Ana", "9.5"], ["Bruno", "7.0"]])
linhas := IO.read_csv(csv_alvo)
out $"csv tem {len(linhas)} linhas"
assert len(linhas) is 3, "cabecalho + dois"
assert linhas[1][0] is "Ana", "primeira linha de dados"

// Listar o diretorio
out ""
arquivos := IO.list_dir(pasta)
out $"na pasta: {sorted(arquivos)}"
assert len(arquivos) is 3, "tres arquivos"

// Copiar e renomear
copia := IO.join(pasta, "notas_copia.txt")
IO.copy(alvo, copia)
assert IO.exists(copia) is yes, "copiado"
assert IO.read(copia) is IO.read(alvo), "conteudo identico"

renomeado := IO.join(pasta, "notas_final.txt")
IO.rename(copia, renomeado)
assert IO.exists(renomeado) is yes, "renomeado"
assert IO.exists(copia) is no, "o antigo sumiu"

// Processar so os .txt
out ""
textos := IO.list_dir(pasta) >> sift nome: nome.endswith(".txt")
out $"arquivos .txt: {len(textos)}"
assert len(textos) is 2, "dois .txt"

// Limpar
cycle nome in IO.list_dir(pasta):
    IO.delete(IO.join(pasta, nome))
IO.delete(pasta)
assert IO.exists(pasta) is no, "pasta removida"
out ""
out "tudo limpo"
`, title: `164_arquivos.df` },
  {"h2": "Os demais"},
  {"p": "Os outros 4 exercícios deste módulo estão em `exercicios/18-dados-e-persistencia/`. Cada um tem um `.md` ao lado com a explicação completa."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '163--serializacao-de-dados', text: "163 · Serializacao de dados", level: 2 as const }, { id: '164--arquivos-e-diretorios', text: "164 · Arquivos e diretorios", level: 2 as const }, { id: 'os-demais', text: "Os demais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"18 · Dados e persistência"}
      description={"6 exercícios: serialização, arquivos, SQLite e HTTP."}
      href={"/exercicios/18-dados-e-persistencia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
