// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/desktop.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Diálogos",
  description: "Confirmar, abrir arquivo, salvar e escolher pasta — os do sistema na janela, e o roteiro do teste na Sonda.",
};

const blocos: Bloco[] = [
  {"p": "Na janela, cada diálogo é o **nativo** do sistema — o seletor de arquivos do Finder, do Explorer ou do GTK. Na Sonda, é a resposta que o teste deu. E um diálogo que o teste **não** roteirizou é falha: inventar um \"sim\" esconderia exatamente o que quebra em produção."},
  {"table": {"head": ["Chamada", "Devolve", "Cancelado"], "rows": [["`t.confirmar(pergunta)`", "`yes` ou `no`", "`no`"], ["`t.abrir_arquivo(titulo, tipos)`", "o caminho", "`void`"], ["`t.salvar_arquivo(nome_sugerido, tipos)`", "o caminho", "`void`"], ["`t.escolher_pasta(titulo)`", "o caminho", "`void`"]]}},
  { code: `adopt Arcane.Bigorna as B
adopt Arcane.OS as OS

itens := ["a", "b"]
salvo := []
app := B.app("Lista", pasta_de_config := $"{OS.temp_dir()}/df-doc-{randint(100000, 999999)}")

action tela(t):
    t.lista(itens)
    given t.botao("Apagar tudo") and t.confirmar("Apagar os itens?"):
        itens.clear()
    given t.botao("Exportar"):
        caminho := t.salvar_arquivo("itens.txt", ["txt"])
        given caminho isnt void:
            salvo.append(caminho)

app.tela("t", tela)
s := B.testar(app)

// sem roteiro: falha, com a dica do que fazer
monitor:
    s.clicar("Apagar tudo")
    assert no
handle Error as e:
    out e.message

s.responder(no)
s.clicar("Apagar tudo")
assert len(itens) is 2          // "não" não apaga

s.responder("/tmp/itens.txt")
s.clicar("Exportar")
assert salvo is ["/tmp/itens.txt"]

s.responder(void)               // o usuário cancelou
s.clicar("Exportar")
assert len(salvo) is 1
out s.dialogos_pedidos()`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "`t.botao(...) and t.confirmar(...)`", "texto": "O `and` para no primeiro `no`: o diálogo só abre na execução em que o botão foi clicado. Escrito ao contrário, a confirmação abriria em toda reexecução da tela."}},
  {"p": "`s.dialogos_pedidos()` lista o que a tela pediu, na ordem — é como se confere que a pergunta certa foi feita, e não só que a resposta funcionou."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Diálogos"}
      description={"Confirmar, abrir arquivo, salvar e escolher pasta — os do sistema na janela, e o roteiro do teste na Sonda."}
      href={"/docs/desktop/dialogos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
