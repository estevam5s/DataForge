// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/oop_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "SOLID",
  description: "Os cinco princípios, cada um com o problema que resolve — em DataForge.",
};

const blocos: Bloco[] = [
  {"p": "SOLID não é lei; são cinco observações sobre o que costuma dar errado. Cada uma abaixo vem com o código ruim e o bom, para a diferença ficar concreta."},
  {"h2": "S — Responsabilidade única"},
  {"p": "*Uma classe deve ter um só motivo para mudar.*"},
  { code: `// Ruim: muda se a regra de imposto mudar, se o formato do
// relatório mudar, OU se o banco mudar. Três motivos.
blueprint FolhaRuim:
    action setup(salario):
        self.salario := salario

    action calcular_imposto():
        yield self.salario * 0.275

    action formatar_relatorio():
        yield $"Salário: {self.salario}"

    action salvar():
        yield "gravado"

assert (spawn FolhaRuim(1000)).calcular_imposto() is 275.0`, lang: 'df' },
  { code: `// Bom: cada peça muda por um motivo só
record Folha:
    salario: Float

blueprint CalculadoraDeImposto:
    action calcular(folha):
        yield folha.salario * 0.275

blueprint RelatorioDeFolha:
    action formatar(folha):
        yield $"Salário: {folha.salario}"

f := Folha(1000.0)
assert (spawn CalculadoraDeImposto()).calcular(f) is 275.0
assert (spawn RelatorioDeFolha()).formatar(f) is "Salário: 1000.0"`, lang: 'df' },
  {"h2": "O — Aberto/fechado"},
  {"p": "*Aberto para extensão, fechado para modificação.* Acrescentar comportamento não deveria exigir editar o que já funciona."},
  { code: `// Ruim: cada meio de pagamento novo mexe aqui
action cobrar_ruim(tipo, valor):
    match tipo:
        point "pix":
            yield valor
        point "cartao":
            yield valor * 1.05
        default:
            trigger "meio desconhecido"

assert cobrar_ruim("pix", 100) is 100`, lang: 'df' },
  { code: `// Bom: um meio novo é um blueprint novo
trait MeioDePagamento:
    action cobrar(valor)

blueprint Pix with MeioDePagamento:
    action cobrar(valor):
        yield valor

blueprint Cartao with MeioDePagamento:
    action cobrar(valor):
        yield valor * 1.05

blueprint Boleto with MeioDePagamento:
    action cobrar(valor):
        yield valor + 3.50

action cobrar(meio, valor):
    yield meio.cobrar(valor)

assert cobrar(spawn Pix(), 100) is 100
assert cobrar(spawn Boleto(), 100) is 103.5`, lang: 'df' },
  {"h2": "L — Substituição de Liskov"},
  {"p": "*Onde cabe a mãe, tem de caber a filha.* Uma subclasse não pode quebrar o que a mãe prometeu."},
  { code: `// Ruim: Quadrado herda de Retangulo e quebra a promessa
blueprint Retangulo:
    action setup(largura, altura):
        self.largura := largura
        self.altura := altura

    action area():
        yield self.largura * self.altura

blueprint QuadradoRuim extends Retangulo:
    action setup(lado):
        root.setup(lado, lado)

    // quem tem um Retangulo espera mudar um lado só
    action mudar_largura(v):
        self.largura := v
        self.altura := v        // surpresa

r := spawn QuadradoRuim(5)
r.mudar_largura(3)
assert r.area() is 9          // quem esperava 15 se enganou`, lang: 'df' },
  { code: `// Bom: os dois implementam o contrato, sem herdar um do outro
trait Forma:
    action area()

blueprint Retangulo(largura, altura) with Forma:
    action area():
        yield self.largura * self.altura

blueprint Quadrado(lado) with Forma:
    action area():
        yield self.lado ** 2

assert (spawn Retangulo(3, 5)).area() is 15
assert (spawn Quadrado(4)).area() is 16`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O clássico quadrado/retângulo", "texto": "Matematicamente todo quadrado é um retângulo. Em código, a herança quebra porque `Retangulo` promete que largura e altura mudam separadamente — e o quadrado não pode cumprir. **Ser um** na matemática não é **ser um** no código."}},
  {"h2": "I — Segregação de interface"},
  {"p": "*Ninguém deve depender de método que não usa.* Traits pequenos e específicos, não um grande."},
  { code: `// Ruim: uma impressora simples é obrigada a saber escanear
trait MaquinaRuim:
    action imprimir(doc)
    action escanear(doc)
    action enviar_fax(doc)

blueprint SimplesRuim with MaquinaRuim:
    action imprimir(doc):
        yield "imprimiu"
    action escanear(doc):
        trigger "não sei escanear"        // implementa para nada
    action enviar_fax(doc):
        trigger "não sei mandar fax"

assert (spawn SimplesRuim()).imprimir("x") is "imprimiu"`, lang: 'df' },
  { code: `// Bom: traits separados, cada objeto implementa o que faz
trait Impressora:
    action imprimir(doc)

trait Scanner:
    action escanear(doc)

blueprint Simples with Impressora:
    action imprimir(doc):
        yield "imprimiu"

blueprint Multifuncional with Impressora, Scanner:
    action imprimir(doc):
        yield "imprimiu"
    action escanear(doc):
        yield "escaneou"

assert (spawn Simples()).imprimir("x") is "imprimiu"
assert (spawn Multifuncional()).escanear("x") is "escaneou"`, lang: 'df' },
  {"h2": "D — Inversão de dependência"},
  {"p": "*Dependa de abstração, não de implementação.* O código de negócio não deveria saber que o banco é PostgreSQL."},
  { code: `// Ruim: a regra de negócio conhece o detalhe do armazenamento
blueprint ServicoRuim:
    action setup():
        self.linhas := []

    action cadastrar(nome):
        self.linhas.append($"INSERT INTO usuarios VALUES ('{nome}')")
        yield len(self.linhas)

assert (spawn ServicoRuim()).cadastrar("Ana") is 1`, lang: 'df' },
  { code: `// Bom: a regra depende de um contrato; o detalhe entra por fora
trait RepositorioDeUsuarios:
    action salvar(nome)
    action contar()

blueprint RepositorioEmMemoria with RepositorioDeUsuarios:
    action setup():
        self.itens := []
    action salvar(nome):
        self.itens.append(nome)
        yield nome
    action contar():
        yield len(self.itens)

blueprint ServicoDeCadastro:
    action setup(repositorio):
        self.repositorio := repositorio

    action cadastrar(nome):
        given len(nome) smaller 2:
            trigger "nome curto demais"
        yield self.repositorio.salvar(nome)

// o teste usa memória; a produção usaria o Forge — mesma classe
s := spawn ServicoDeCadastro(spawn RepositorioEmMemoria())
s.cadastrar("Ana")
assert s.repositorio.contar() is 1`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "É o que torna teste barato", "texto": "Um serviço que recebe o repositório por parâmetro se testa sem banco nenhum. Um que constrói o próprio exige subir PostgreSQL para testar uma regra de validação de nome."}},
  {"h2": "Acoplamento e coesão"},
  {"p": "Os cinco princípios servem a duas ideias mais gerais:"},
  {"table": {"head": ["", "Você quer", "Sinal de problema"], "rows": [["**acoplamento**", "baixo — poucas peças se conhecem", "mudar A obriga a mudar B, C e D"], ["**coesão**", "alta — o que está junto pertence junto", "uma classe chamada `Utils` ou `Manager`"]]}},
  {"p": "Ver [modelagem](/docs/oop/modelagem)."},
];

const headings = [{ id: 's-responsabilidade-unica', text: "S — Responsabilidade única", level: 2 as const }, { id: 'o-abertofechado', text: "O — Aberto/fechado", level: 2 as const }, { id: 'l-substituicao-de-liskov', text: "L — Substituição de Liskov", level: 2 as const }, { id: 'i-segregacao-de-interface', text: "I — Segregação de interface", level: 2 as const }, { id: 'd-inversao-de-dependencia', text: "D — Inversão de dependência", level: 2 as const }, { id: 'acoplamento-e-coesao', text: "Acoplamento e coesão", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"SOLID"}
      description={"Os cinco princípios, cada um com o problema que resolve — em DataForge."}
      href={"/docs/oop/solid"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
