import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Escopo",
  description: "Como os nomes são resolvidos, e o que shadow faz.",
};

const blocos: Bloco[] = [
  {"h2": "A cadeia de escopos"},
  {"p": "Cada bloco cria um escopo filho. Ao procurar um nome, o interpretador sobe a cadeia até encontrá-lo — ou dispara `NameError_`."},
  { code: `global := "topo"

action externa():
    da_acao := "acao"

    action interna():
        do_bloco := "interna"
        out global, da_acao, do_bloco     # enxerga os três

    interna()

externa()` },
  {"h2": "Atribuir atualiza onde existe"},
  { code: `contador := 0

action incrementar():
    contador := contador + 1     # atualiza o de FORA
    yield contador

incrementar()
incrementar()
out contador                     # 2` },
  {"p": "`:=` procura o nome na cadeia. Se encontra, atualiza ali. Se não encontra, cria no escopo atual."},
  {"h2": "shadow — uma cópia local"},
  { code: `x := 10

action sombreia():
    shadow x := 99     # cria uma cópia local, não toca no de fora
    yield x

out sombreia(), x      # 99 10` },
  {"p": "`shadow` diz explicitamente \"este nome é meu, aqui dentro\". Sem ele, a atribuição afetaria o `x` externo."},
  {"h2": "Escopos de bloco"},
  {"p": "Laços, condicionais e blocos `monitor` criam escopos próprios. A variável do `cycle` existe só ali dentro:"},
  { code: `cycle i from 1 to 3:
    dentro := i * 2

# out i        # erro — 'i' não existe aqui fora` },
  {"p": "O mesmo vale para a variável de uma [compreensão](/fundamentos/compreensoes)."},
  {"h2": "Closures"},
  {"p": "Uma ação aninhada **captura** o escopo onde foi criada, e o mantém vivo mesmo depois que a ação externa terminou:"},
  { code: `action fabrica(n):
    action somador(x):
        yield x + n     # 'n' continua acessível
    yield somador

soma5 := fabrica(5)
out soma5(10)           # 15 — 'n' ainda vale 5` },
  {"p": "Detalhes em [Closures e lambdas](/fundamentos/closures)."},
  {"h2": "self e this"},
  {"p": "Dentro de um método, `self` (ou `this`, sinônimo) é a instância atual:"},
  { code: `blueprint Conta(saldo):
    action depositar(valor):
        self.saldo := self.saldo + valor
        yield self.saldo` },
  {"callout": {"tipo": "atencao", "texto": "Escrever `saldo` em vez de `self.saldo` lê a variável do **escopo externo**, não o campo. É o erro mais comum ao escrever métodos."}},
  {"h2": "Constantes"},
  {"p": "`steady` marca o nome como imutável naquele escopo. Reatribuir dispara erro, mesmo de dentro de uma ação aninhada."},
  {"h2": "Módulos"},
  {"p": "Cada arquivo importado tem seu próprio escopo de topo, e só exporta o que o `relay` permitir. Veja [Módulos](/fundamentos/modulos)."},
];

const headings = [{ id: 'a-cadeia-de-escopos', text: "A cadeia de escopos", level: 2 as const }, { id: 'atribuir-atualiza-onde-existe', text: "Atribuir atualiza onde existe", level: 2 as const }, { id: 'shadow--uma-copia-local', text: "shadow — uma cópia local", level: 2 as const }, { id: 'escopos-de-bloco', text: "Escopos de bloco", level: 2 as const }, { id: 'closures', text: "Closures", level: 2 as const }, { id: 'self-e-this', text: "self e this", level: 2 as const }, { id: 'constantes', text: "Constantes", level: 2 as const }, { id: 'modulos', text: "Módulos", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Escopo"}
      description={"Como os nomes são resolvidos, e o que shadow faz."}
      href={"/fundamentos/escopo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
