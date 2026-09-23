// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/plataforma_runtime.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Sistema de arquivos",
  description: "Ler, escrever, percorrer e não deixar lixo — Arcane.IO e Arcane.OS na prática.",
};

const blocos: Bloco[] = [
  {"p": "Dois módulos dividem o trabalho: **`Arcane.IO`** mexe em arquivos e pastas; **`Arcane.OS`** responde sobre o ambiente — onde é a casa, qual é o temporário, o que há no `PATH`."},
  {"h2": "Ler e escrever"},
  { code: `adopt Arcane.IO as IO

IO.write("notas.txt", "primeira linha\\n")
IO.append("notas.txt", "segunda linha\\n")

out IO.read("notas.txt").strip().split("\\n")
out IO.exists("notas.txt"), IO.size("notas.txt")
`, lang: 'df' },
  { code: `[primeira linha, segunda linha]
yes 29
`, lang: 'text', title: `saída` },
  {"p": "`IO.write` **sobrescreve**; `IO.append` acrescenta. Não há modo intermediário de propósito: um terceiro verbo com semântica sutil é o tipo de coisa que se erra às três da manhã."},
  {"h2": "Caminhos: monte, não concatene"},
  { code: `IO.join(pasta, "dados", "brutos.csv")    // usa o separador do sistema
IO.basename("/tmp/a/b.txt")              // b.txt
IO.dirname("/tmp/a/b.txt")               // /tmp/a
IO.ext("/tmp/a/b.txt")                   // .txt
IO.abs("./relativo")                     // o caminho absoluto
`, lang: 'df' },
  {"p": "Concatenar com `+` produz um caminho que funciona no seu computador e falha no Windows — e o teste local nunca pega."},
  {"h2": "JSON e CSV, sem cerimônia"},
  { code: `adopt Arcane.IO as IO

IO.write_json("config.json", {"porta": 8000, "debug": yes})
out IO.read_json("config.json")["porta"]          // 8000

// um cluster de VAULTS: a primeira linha vira o cabeçalho
IO.write_csv("dados.csv", [{"nome": "Ana", "idade": 30},
                           {"nome": "Bruno", "idade": 25}])
out IO.read("dados.csv").strip()
`, lang: 'df' },
  { code: `nome,idade
Ana,30
Bruno,25
`, lang: 'text', title: `saída` },
  {"p": "Na leitura, escolha a forma:"},
  { code: `linhas := IO.read_csv("dados.csv")          // cluster de clusters
linhas := IO.read_csv("dados.csv", yes)     // cluster de VAULTS, pelo cabeçalho
`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O vault era destruído em silêncio", "texto": "Até esta versão, `write_csv` passava a lista direto para o escritor — e iterar um vault dá as **chaves**. Gravar dois registros escrevia `nome,idade` duas vezes, e os valores sumiam sem erro nenhum. Perder dado calado é a pior falha possível numa função de gravar arquivo."}},
  {"h2": "Pastas"},
  { code: `adopt Arcane.IO as IO

IO.mkdir("saida")                    // cria, inclusive os pais
out IO.list_dir("saida")             // o que há dentro
IO.copy("a.txt", "saida/a.txt")
IO.copy_tree("modelos", "saida/modelos")
IO.rename("saida/a.txt", "saida/b.txt")
IO.delete("saida/b.txt")             // um arquivo
IO.remove_tree("saida")              // a pasta inteira
`, lang: 'df' },
  {"callout": {"tipo": "perigo", "titulo": "`remove_tree` não pergunta", "texto": "`IO.remove_tree(OS.temp_dir())` destrói o temporário de **todo processo da máquina**. Um exercício deste repositório fez exatamente isso na primeira versão. Sempre uma subpasta própria."}},
  {"h2": "Arquivo ou pasta?"},
  {"p": "`IO.exists` responde *“ha algo aqui?”*, e ha um caso em que isso nao basta: `list_dir` devolve **nomes**, e um deles pode ser uma subpasta. Todo `cycle` sobre uma pasta tinha de adivinhar."},
  { code: `adopt Arcane.IO as IO

arquivos := []
pastas := []
cycle nome in IO.list_dir("."):
    caminho := IO.join(".", nome)
    given IO.is_file(caminho):
        arquivos.append({"nome": nome, "bytes": IO.size(caminho)})
    orif IO.is_dir(caminho):
        pastas.append(nome)

out $"{len(arquivos)} arquivo(s), {len(pastas)} pasta(s)"
`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "`size` de uma pasta nao e o que voce quer", "texto": "`IO.size` devolve o tamanho da **entrada** de diretorio, nao a soma do conteudo. Contar subpasta como arquivo nao levanta erro nenhum: o relatorio so sai com um numero a mais. O modelo `script` do `dataforge new` fazia isso, e foi so por ele que a falta de `is_file` apareceu."}},
  {"h2": "Temporário: sempre uma subpasta sua"},
  { code: `adopt Arcane.IO as IO
adopt Arcane.OS as OS

base := $"{OS.temp_dir()}/meu-programa-{randint(100000, 999999)}"
IO.mkdir(base)

defer:
    IO.remove_tree(base)         // roda na saída da ação, inclusive por erro

IO.write(IO.join(base, "trabalho.txt"), "…")
`, lang: 'df' },
  {"p": "O `defer` é o que garante a limpeza quando a ação sai por erro — que é justamente quando ninguém lembra de limpar."},
  {"h2": "O ambiente, com `Arcane.OS`"},
  {"table": {"head": ["Pergunta", "Resposta"], "rows": [["onde estou?", "`OS.cwd()`"], ["onde está o script?", "`OS.script_dir()`"], ["qual é a casa do usuário?", "`OS.home()`"], ["qual é o temporário?", "`OS.temp_dir()`"], ["qual sistema?", "`OS.is_windows()`, `OS.is_mac()`, `OS.is_linux()`"], ["quantos núcleos?", "`OS.cpu_count()`"], ["a variável de ambiente", "`OS.get_env(nome, padrao)`, `OS.set_env`, `OS.unset_env`"], ["este comando existe?", "`OS.which(\"git\")`"]]}},
  {"p": "`OS.unset_env` existe porque a falta dela aparecia como poluição entre execuções: um exercício imprimia 77 variáveis na primeira rodada e 78 na segunda. Ela devolve `yes`/`no` em vez de levantar — remover é pedir um estado final, e nesse ponto já não importa se estava lá."},
  {"h2": "Arquivo grande: não carregue inteiro"},
  {"p": "`IO.read` traz tudo para a memória. Para um arquivo maior que a RAM, processe por partes — ver [complexidade de espaço](/docs/big-o/espaco)."},
  { code: `// O(n) de espaço: o arquivo inteiro na memória
todas := IO.read("grande.csv").split("\\n")

// O(1) de espaço: uma linha por vez
stream action linhas_de(caminho):
    cycle linha in IO.read(caminho).split("\\n"):
        emit linha

out linhas_de("grande.csv").take(3)
`, lang: 'df' },
  {"h2": "Erros: o que pode falhar, e como"},
  {"table": {"head": ["Situação", "O que acontece"], "rows": [["ler arquivo que não existe", "erro, com o caminho na mensagem"], ["escrever em pasta que não existe", "erro — crie com `IO.mkdir` antes"], ["escrever sem permissão", "erro do sistema, traduzido"], ["`delete` de algo ausente", "erro — confira com `IO.exists`"], ["arquivo fora de UTF-8", "erro de leitura, dizendo qual arquivo"]]}},
  { code: `monitor:
    config := IO.read_json("config.json")
handle Error as e:
    out $"usando o padrao: {e.message}"
    config := {"porta": 8000}
`, lang: 'df' },
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/biblioteca/io", "title": "Arcane.IO", "desc": "a referência completa"}, {"href": "/docs/biblioteca/os", "title": "Arcane.OS", "desc": "o ambiente, o processo e a máquina"}, {"href": "/docs/tecnicas/arquivos", "title": "Receitas com arquivos", "desc": "padrões prontos"}, {"href": "/docs/big-o/dados", "title": "Custo de I/O", "desc": "por que o bloco é a unidade"}]},
];

const headings = [{ id: 'ler-e-escrever', text: "Ler e escrever", level: 2 as const }, { id: 'caminhos-monte-nao-concatene', text: "Caminhos: monte, não concatene", level: 2 as const }, { id: 'json-e-csv-sem-cerimonia', text: "JSON e CSV, sem cerimônia", level: 2 as const }, { id: 'pastas', text: "Pastas", level: 2 as const }, { id: 'arquivo-ou-pasta', text: "Arquivo ou pasta?", level: 2 as const }, { id: 'temporario-sempre-uma-subpasta-sua', text: "Temporário: sempre uma subpasta sua", level: 2 as const }, { id: 'o-ambiente-com-arcaneos', text: "O ambiente, com `Arcane.OS`", level: 2 as const }, { id: 'arquivo-grande-nao-carregue-inteiro', text: "Arquivo grande: não carregue inteiro", level: 2 as const }, { id: 'erros-o-que-pode-falhar-e-como', text: "Erros: o que pode falhar, e como", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Sistema de arquivos"}
      description={"Ler, escrever, percorrer e não deixar lixo — Arcane.IO e Arcane.OS na prática."}
      href={"/docs/arquivos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
