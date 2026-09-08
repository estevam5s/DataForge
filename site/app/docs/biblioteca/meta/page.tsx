import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Meta",
  description: "Ler os decoradores em tempo de execução.",
};

const blocos: Bloco[] = [
  {"p": "`Arcane.Meta` lê os metadados que os [decoradores](/docs/fundamentos/decoradores-avancados) deixaram. É a metade que torna um decorador útil: `@Rota(\"/itens\")` grava o caminho, e `Meta.ler` o devolve."},
  { code: `adopt Arcane.Meta as Meta

@Rota("GET", "/itens")
action listar():
    yield itens

Meta.tem(listar, "Rota")        // yes
Meta.arg(listar, "Rota", 0)     // GET` },
  {"h2": "Leitura"},
  {"table": {"head": ["Função", "Devolve"], "rows": [["`Meta.tem(alvo, nome)`", "o alvo foi decorado com `@nome`?"], ["`Meta.nomes(alvo)`", "os nomes dos decoradores, na ordem em que aparecem"], ["`Meta.todos(alvo)`", "todos os metadados: `[{nome, args, kwargs}]`"], ["`Meta.ler(alvo, nome)`", "o primeiro `@nome`, ou `void`"], ["`Meta.todos_de(alvo, nome)`", "todas as ocorrências de `@nome` (decorador repetível)"], ["`Meta.arg(alvo, nome, i, padrao)`", "um argumento posicional, com padrão"], ["`Meta.opcao(alvo, nome, chave, padrao)`", "um argumento nomeado, com padrão"]]}},
  {"p": "Todas devolvem o padrão (ou `void`) quando o decorador não existe — nunca levantam. Perguntar por um decorador ausente é o caso normal, não erro."},
  {"h2": "Varredura"},
  { code: `// os métodos de um controlador anotados com @Rota
cycle r in Meta.metodos_com(UsuariosController, "Rota"):
    out r["nome"], r["meta"]["args"]

// de uma lista de blueprints, os @Injetavel
servicos := Meta.filtrar([Repo, Cache, Config], "Injetavel")` },
  {"table": {"head": ["Função", "Devolve"], "rows": [["`Meta.metodos_com(blueprint, nome)`", "`[{nome, metodo, meta}]` — os métodos anotados"], ["`Meta.filtrar(valores, nome)`", "de uma lista ou vault, os que têm `@nome`"], ["`Meta.descrever(alvo)`", "tipo, nome, decoradores, métodos e campos"]]}},
  {"p": "`metodos_com` é o que um roteador usa para descobrir rotas a partir de uma classe; `filtrar` é o que um contêiner usa para achar o que registrar."},
  {"h2": "Escrita"},
  { code: `// anotar algo que já existe, sem a sintaxe de decorador
Meta.marcar(minha_acao, "Cache", 60)
out Meta.arg(minha_acao, "Cache", 0)    // 60

Meta.limpar(minha_acao)                 // remove tudo — útil em teste` },
  {"p": "`marcar` serve para anotar um valor vindo de outro módulo, e para escrever decoradores que anotam além do que receberam."},
  {"h2": "O que sobrevive ao embrulho"},
  { code: `@logar          // embrulha
@Rota("/x")     // só anota
action f(n):
    yield n

Meta.tem(f, "Rota")     // yes — o embrulho herdou a anotação` },
  {"p": "Quando um decorador embrulha o alvo, o embrulho **herda** os metadados de quem embrulhou. Sem isso, `@logar @Rota(...)` perderia a anotação assim que o primeiro decorador devolvesse um embrulho — e a ordem dos decoradores viraria uma armadilha."},
  {"h2": "Onde ver funcionando"},
  {"table": {"head": ["Onde", "O quê"], "rows": [["[Decoradores](/docs/fundamentos/decoradores-avancados)", "um roteador e um contêiner de injeção completos"], ["[Playground](/painel/playground)", "o exemplo \"Decoradores\", rodando no navegador"], ["`tests/test_decoradores.py`", "20 testes"]]}},
];

const headings = [{ id: 'leitura', text: "Leitura", level: 2 as const }, { id: 'varredura', text: "Varredura", level: 2 as const }, { id: 'escrita', text: "Escrita", level: 2 as const }, { id: 'o-que-sobrevive-ao-embrulho', text: "O que sobrevive ao embrulho", level: 2 as const }, { id: 'onde-ver-funcionando', text: "Onde ver funcionando", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Meta"}
      description={"Ler os decoradores em tempo de execução."}
      href={"/docs/biblioteca/meta"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
