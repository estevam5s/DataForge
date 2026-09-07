import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Modelagem",
  description: "Record ou blueprint, herança ou composição — as escolhas que importam.",
};

const blocos: Bloco[] = [
  {"p": "A sintaxe é a parte fácil. O que custa é escolher entre as formas — e o custo aparece meses depois, quando mudar a escolha significa reescrever quem usa."},
  {"h2": "Record ou blueprint"},
  {"p": "**Dois desses, com os mesmos valores, são a mesma coisa?**"},
  {"table": {"head": ["", "`record`", "`blueprint`"], "rows": [["Igualdade", "estrutural", "identidade"], ["Mutação", "imutável; `with` copia", "estado evolui"], ["Exemplo", "ponto, dinheiro, data, cor", "conta, sessão, conexão, carrinho"]]}},
  { code: `record Ponto:
    x: Integer
    y: Integer

    action distancia_ate(outro):
        yield sqrt((self.x - outro.x) ** 2 + (self.y - outro.y) ** 2)

// dois pontos com as mesmas coordenadas SAO o mesmo ponto
a := Ponto(1, 2)
b := Ponto(1, 2)
assert a is b, "records com os mesmos valores sao iguais"
assert a.distancia_ate(Ponto(4, 6)) is 5.0, "e tem comportamento"

// e nao mudam: 'with' cria outro
movido := a with {"x": 10}
assert a.x is 1, "o original nao mudou"
assert movido.x is 10, "a copia tem o valor novo"

monitor:
    a.x := 99
    assert no, "deveria ter recusado"
handle e:
    out "record e imutavel"`, lang: 'df' },
  {"p": "Usar blueprint para valor força a implementar `operator ==` à mão e a lembrar de copiar antes de passar adiante. Usar record para entidade obriga a recriar o objeto a cada mudança, e duas contas iguais viram uma."},
  {"h2": "Herança ou composição"},
  { code: `blueprint Carro:
    modelo: String := ""

    action setup(modelo, motor):
        self.modelo := modelo
        self.motor := motor        // o carro TEM um motor

    action dar_partida():
        yield $"{self.modelo}: {self.motor.ligar()}"

    action ficha():
        yield $"{self.modelo} — {round(self.motor.potencia(), 1)} kW"`, lang: 'df' },
  {"p": "Composição permite **trocar a peça**: `carro.motor := spawn MotorCombustao(100)` é o mesmo carro com outro motor. Com herança, seria outro tipo."},
  {"p": "O custo é uma indireção — `self.motor.ligar()` em vez de `self.ligar()`. Para uma relação que realmente é \"é um\", herança é mais direta."},
  {"h2": "Polimorfismo"},
  {"p": "O ganho não é evitar `given`. É que o código que percorre a lista **não muda quando chega um tipo novo**:"},
  { code: `formatos := [spawn ComoJson(dados), spawn ComoCsv(dados), spawn ComoTexto(dados)]

// este laco nao sabe quantos formatos existem, nem quais
cycle f in formatos:
    out $"--- .{f.extensao()} ---"
    out f.exportar()`, lang: 'df' },
  {"p": "Compare com a alternativa: um `given/orif` que cresce toda vez que chega um formato. Acrescentar tipo vira adição, não edição — e é essa propriedade que faz o código envelhecer bem."},
  {"h2": "Quando não vale"},
  {"list": ["Polimorfismo com dois casos que nunca vão crescer é cerimônia — um `given` resolve e se lê melhor", "Se cada implementação precisa de um parâmetro diferente, a interface comum não existe de verdade", "Tornar tudo privado e criar `get`/`set` para cada campo devolve o problema ao ponto de partida: exponha comportamento, não estado"]},
  {"h2": "Praticar"},
  {"p": "Os dez exercícios do [módulo 21](/docs/exercicios) percorrem essas decisões, e os [projetos](/docs/projetos) mostram as escolhas em programas completos."},
];

const headings = [{ id: 'record-ou-blueprint', text: "Record ou blueprint", level: 2 as const }, { id: 'heranca-ou-composicao', text: "Herança ou composição", level: 2 as const }, { id: 'polimorfismo', text: "Polimorfismo", level: 2 as const }, { id: 'quando-nao-vale', text: "Quando não vale", level: 2 as const }, { id: 'praticar', text: "Praticar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Modelagem"}
      description={"Record ou blueprint, herança ou composição — as escolhas que importam."}
      href={"/docs/oop/modelagem"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
