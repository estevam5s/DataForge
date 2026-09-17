// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/oop_meta.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Injeção de dependência",
  description: "Arcane.Injecao: contêiner com único, transitório e por escopo, fábrica, valor, preguiçoso, dependência opcional e detecção de ciclo.",
};

const blocos: Bloco[] = [
  {"p": "O Princípio da Inversão de Dependência pede que o código de alto nível dependa de **contratos**, e que alguém de fora escolha a implementação. Esse alguém é o contêiner. Ele lê o que já está escrito — o **tipo** dos parâmetros do construtor — e não pede anotação nova."},
  { code: `adopt Arcane.Injecao as DI

contract Repositorio:
    action salvar(item)

contract Relogio:
    action agora()

blueprint RepoMemoria with Repositorio:
    itens := []
    action salvar(item):
        self.itens.append(item)
        yield len(self.itens)

blueprint RelogioFixo with Relogio:
    action agora():
        yield "2026-09-17"

blueprint Cadastro(repo: Repositorio, relogio: Relogio):
    action registrar(nome):
        yield self.repo.salvar($"{nome}@{self.relogio.agora()}")

c := DI.conteiner()
c.unico(Repositorio, RepoMemoria)
c.unico(Relogio, RelogioFixo)

cadastro := c.resolver(Cadastro)
assert cadastro.registrar("ana") is 1
assert cadastro.repo is c.resolver(Repositorio)     // único: a mesma instância`, lang: 'df' },
  {"h2": "Tempo de vida"},
  {"table": {"head": ["Registro", "Quantas instâncias"], "rows": [["`c.unico(Tipo, Impl)`", "uma para o contêiner inteiro"], ["`c.transitorio(Tipo, Impl)`", "uma nova a cada `resolver`"], ["`c.por_escopo(Tipo, Impl)`", "uma por escopo: `e := c.escopo()` … `e.fechar()`"], ["`c.valor(Tipo, obj)`", "o objeto pronto — configuração, conexão, dublê de teste"], ["`c.fabrica(Tipo, acao, escopo)`", "`acao(c)` constrói, quando o construtor não basta"]]}},
  { code: `adopt Arcane.Injecao as DI

blueprint Conexao:
    fechada := no
    action fechar():
        self.fechada := yes

c := DI.conteiner()
c.por_escopo(Conexao)

pedido1 := c.escopo()
a := pedido1.resolver(Conexao)
assert a is pedido1.resolver(Conexao)       // mesma no escopo
pedido1.fechar()
assert a.fechada                             // o escopo fecha o que abriu

pedido2 := c.escopo()
assert pedido2.resolver(Conexao) isnt a      // outro escopo, outra conexão`, lang: 'df' },
  {"h2": "O que o contêiner recusa"},
  { code: `adopt Arcane.Injecao as DI

blueprint Ovo(galinha: Galinha):
    x := 0
blueprint Galinha(ovo: Ovo):
    x := 0

monitor:
    DI.conteiner().resolver(Ovo)
    assert no
handle CircularDependencyError as e:
    assert "Ovo → Galinha → Ovo" in e.message`, lang: 'df' },
  {"list": ["**ciclo**, com a cadeia inteira — `c.preguicoso(Tipo)` quebra, entregando um objeto que só resolve no primeiro uso;", "**parâmetro sem registro** — a menos que tenha padrão, e aí é dependência opcional;", "**único que depende de por-escopo** — o objeto de escopo ficaria preso para sempre dentro do único;", "**por-escopo pedido ao contêiner raiz** — resolvê-lo ali o transformaria num único calado."]},
  {"p": "Injeção por **campo** usa `@Injetar` sobre um campo tipado; por **método**, `c.chamar(acao)` resolve os parâmetros tipados. `c.conferir()` resolve tudo o que foi registrado e devolve a lista de problemas — num teste, isso pega o registro que falta antes da produção."},
];

const headings = [{ id: 'tempo-de-vida', text: "Tempo de vida", level: 2 as const }, { id: 'o-que-o-conteiner-recusa', text: "O que o contêiner recusa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Injeção de dependência"}
      description={"Arcane.Injecao: contêiner com único, transitório e por escopo, fábrica, valor, preguiçoso, dependência opcional e detecção de ciclo."}
      href={"/docs/oop/injecao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
