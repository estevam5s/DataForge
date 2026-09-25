// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/mobile.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Componentes",
  description: "Lista tocável, estado vazio, seção e botão flutuante — e os da Vitrine, que continuam valendo.",
};

const blocos: Bloco[] = [
  {"h2": "Lista"},
  { code: `adopt Arcane.Brasa as Br

contatos := [
    {"id": 1, "nome": "Ana Souza", "cidade": "Recife"},
    {"id": 2, "nome": "Bruno Lima", "cidade": "Curitiba"},
]
app := Br.app("Contatos")

action tela():
    Br.topo("Contatos")
    Br.secao("Favoritos")
    Br.lista(contatos, titulo := "nome", detalhe := "cidade",
             destino := "/contato?id={id}", icone := "usuario")

Br.tela("/", tela)
s := Br.testar(app)
assert s.itens() is [{"titulo": "Ana Souza", "detalhe": "Recife"},
                     {"titulo": "Bruno Lima", "detalhe": "Curitiba"}]`, lang: 'df' },
  {"p": "A **linha inteira** é o alvo, com 56 px de altura — o dedo não acerta um link de 14 px no meio de um texto. `titulo` e `detalhe` são nomes de campo, e o item pode ser vault, record ou instância. O texto é **escapado**: um nome com `<script>` aparece como texto, e não roda."},
  {"h2": "Estado vazio"},
  { code: `adopt Arcane.Brasa as Br

app := Br.app("Pedidos")

action tela():
    Br.topo("Pedidos")
    Br.vazio("Nenhum pedido ainda", "os pedidos novos aparecem aqui")

Br.tela("/", tela)
assert Br.testar(app).tem("Nenhum pedido ainda")`, lang: 'df' },
  {"p": "Uma lista vazia sem explicação parece **travada**. O vazio diz o que é e, na dica, o que fazer."},
  {"h2": "Botão flutuante"},
  { code: `adopt Arcane.Brasa as Br
adopt Arcane.Vitrine as V

notas := []
app := Br.app("Notas")

action lista():
    Br.topo("Notas")
    Br.lista(notas, titulo := "texto")
    Br.botao_flutuante("Nova nota", "/nova")

action nova():
    Br.topo("Nova nota", voltar := yes)
    texto := V.entrada("Texto")
    given V.botao("Salvar"):
        notas.append({"texto": texto})
        V.navegar("/")

Br.tela("/", lista, titulo := "Notas", icone := "lapis", aba := yes)
Br.tela("/nova", nova)

s := Br.testar(app)
s.tocar("Nova nota")
s.digitar("Texto", "comprar pão")
s.clicar("Salvar")
s.ir("/")
assert s.tem("comprar pão")`, lang: 'df' },
  {"p": "Ele fica no canto, **acima** da barra de abas, e respeita a área segura do aparelho (o entalhe e a barra de gestos do iPhone)."},
  {"h2": "Os links são conferidos"},
  {"table": {"head": ["Destino", "Resultado"], "rows": [["`/produto?id=3`", "aceito — um caminho do aplicativo"], ["`tel:`, `sms:`, `mailto:`, `geo:`, `https:`", "aceito — abre o aplicativo do aparelho"], ["`javascript:…`, `//outro.site`, `data:…`", "**recusado** — um dado nunca vira código"]]}},
];

const headings = [{ id: 'lista', text: "Lista", level: 2 as const }, { id: 'estado-vazio', text: "Estado vazio", level: 2 as const }, { id: 'botao-flutuante', text: "Botão flutuante", level: 2 as const }, { id: 'os-links-sao-conferidos', text: "Os links são conferidos", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Componentes"}
      description={"Lista tocável, estado vazio, seção e botão flutuante — e os da Vitrine, que continuam valendo."}
      href={"/docs/mobile/componentes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
