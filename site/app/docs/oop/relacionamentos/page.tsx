import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Relacionamentos entre objetos",
  description: "Associação, agregação, composição, dependência — e por que a diferença importa.",
};

const blocos: Bloco[] = [
  {"p": "Objetos se conhecem de jeitos diferentes, e o jeito decide quem cria quem, quem morre com quem, e o que quebra ao mudar."},
  {"h2": "As quatro formas"},
  {"table": {"head": ["", "Força", "Ciclo de vida", "Exemplo"], "rows": [["**dependência**", "a mais fraca", "independentes", "um método recebe um `Relatorio` como parâmetro"], ["**associação**", "fraca", "independentes", "`Pedido` conhece o `Cliente`"], ["**agregação**", "média", "independentes", "`Time` tem `Jogador`; o jogador sobrevive ao time"], ["**composição**", "forte", "morrem juntos", "`Pedido` tem `ItemDePedido`; sem pedido, o item não existe"]]}},
  {"h2": "Dependência"},
  {"p": "A mais fraca: o objeto usa outro, mas não o guarda."},
  { code: `blueprint Impressora:
    // 'documento' entra, é usado, e vai embora
    action imprimir(documento):
        yield $"imprimindo: {documento.titulo}"

record Documento:
    titulo: String

p := spawn Impressora()
assert p.imprimir(Documento("Contrato")) is "imprimindo: Contrato"`, lang: 'df' },
  {"h2": "Associação"},
  {"p": "O objeto **guarda** uma referência ao outro, mas os dois existem por conta própria:"},
  { code: `blueprint Cliente:
    action setup(nome):
        self.nome := nome

blueprint Pedido:
    action setup(cliente, total):
        self.cliente := cliente
        self.total := total

    get resumo():
        yield $"{self.cliente.nome}: {self.total}"

ana := spawn Cliente("Ana")
p1 := spawn Pedido(ana, 100)
p2 := spawn Pedido(ana, 250)

// um cliente, dois pedidos — e o cliente existia antes deles
assert p1.resumo is "Ana: 100"
assert p2.cliente is p1.cliente`, lang: 'df' },
  {"h2": "Agregação"},
  {"p": "\"Tem um\", mas a parte sobrevive ao todo:"},
  { code: `blueprint Jogador:
    action setup(nome):
        self.nome := nome

blueprint Time:
    action setup(nome):
        self.nome := nome
        self.jogadores := []

    action contratar(jogador):
        self.jogadores.append(jogador)
        yield len(self.jogadores)

    action liberar(jogador):
        self.jogadores.remove(jogador)
        yield len(self.jogadores)

j := spawn Jogador("Pelé")
t := spawn Time("Santos")
t.contratar(j)
t.liberar(j)

// o time acabou com ele; o jogador continua existindo
assert j.nome is "Pelé"`, lang: 'df' },
  {"h2": "Composição"},
  {"p": "\"É feito de\": a parte **nasce e morre** com o todo, e não é compartilhada:"},
  { code: `record ItemDePedido:
    produto: String
    quantidade: Integer
    preco: Float

    action subtotal():
        yield self.quantidade * self.preco

blueprint Pedido:
    action setup():
        self.itens := []

    // o pedido CRIA seus itens — eles não vêm de fora
    action adicionar(produto, quantidade, preco):
        self.itens.append(ItemDePedido(produto, quantidade, preco))
        yield len(self.itens)

    get total():
        soma := 0.0
        cycle i in self.itens:
            soma += i.subtotal()
        yield soma

p := spawn Pedido()
p.adicionar("Teclado", 2, 250.0)
p.adicionar("Mouse", 1, 90.0)
assert p.total is 590.0`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Como distinguir", "texto": "Pergunte: **se o todo for destruído, a parte ainda faz sentido?** Um jogador sem time faz. Um item de pedido sem pedido não faz. O primeiro é agregação, o segundo é composição."}},
  {"h2": "Cardinalidade"},
  {"p": "Quantos de cada lado. É o que vira chave estrangeira no banco:"},
  {"table": {"head": ["Notação", "Significa", "No [ORM](/docs/orm/relacoes)"], "rows": [["1 → 1", "um para um", "`tem_um`"], ["1 → N", "um para muitos", "`tem_muitos`"], ["N → 1", "muitos para um", "`pertence_a`"], ["N → N", "muitos para muitos", "`muitos_para_muitos`, com tabela ponte"]]}},
  { code: `// Cliente 1 ─── N Pedido ─── N Produto
adopt Forge

db := Forge.conectar(":memory:")

Cliente := Forge.modelo("Cliente", {
    "id": {"tipo": "Serial"},
    "nome": {"tipo": "Texto", "obrigatorio": yes}
}, {"conexao": db})

Pedido := Forge.modelo("Pedido", {
    "id": {"tipo": "Serial"},
    "cliente_id": {"tipo": "Inteiro", "indice": yes},
    "total": {"tipo": "Real", "padrao": 0}
}, {"conexao": db})

Cliente.tem_muitos("pedidos", "Pedido")
Pedido.pertence_a("cliente", "Cliente")
Forge.migrar_tudo(db)

ana := Cliente.criar({"nome": "Ana"})
Pedido.criar({"cliente_id": ana["id"], "total": 100.0})

com_pedidos := Cliente.com(Cliente.todos(), "pedidos")
assert len(com_pedidos[0]["pedidos"]) is 1`, lang: 'df' },
  {"h2": "Navegabilidade"},
  {"p": "Uma associação pode ser **unidirecional** (o pedido conhece o cliente, mas o cliente não lista pedidos) ou **bidirecional** (os dois se conhecem)."},
  {"p": "Bidirecional é mais conveniente e mais caro: os dois lados precisam ficar consistentes, e há sempre o risco de um ciclo na serialização."},
  {"callout": {"tipo": "atencao", "titulo": "Comece unidirecional", "texto": "Só acrescente o outro lado quando alguém precisar dele. Uma referência que ninguém usa é código para manter sem retorno — e um ciclo esperando para estourar no `para_json`."}},
];

const headings = [{ id: 'as-quatro-formas', text: "As quatro formas", level: 2 as const }, { id: 'dependencia', text: "Dependência", level: 2 as const }, { id: 'associacao', text: "Associação", level: 2 as const }, { id: 'agregacao', text: "Agregação", level: 2 as const }, { id: 'composicao', text: "Composição", level: 2 as const }, { id: 'cardinalidade', text: "Cardinalidade", level: 2 as const }, { id: 'navegabilidade', text: "Navegabilidade", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Relacionamentos entre objetos"}
      description={"Associação, agregação, composição, dependência — e por que a diferença importa."}
      href={"/docs/oop/relacionamentos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
