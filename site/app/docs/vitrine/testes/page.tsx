// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/vitrine.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testar sem navegador",
  description: "A sonda clica, digita e pergunta; e o pedido HTTP roda sem socket.",
};

const blocos: Bloco[] = [
  {"p": "O framework foi desenhado para isto: a árvore de componentes é um **dado**, e conferir um dado é o que um teste sabe fazer."},
  { code: `adopt Arcane.Vitrine as V
adopt Crucible

action painel():
    V.titulo("Painel")
    given V.botao("Somar"):
        V.estado.somar("total")
    V.metrica("Total", V.estado.obter("total", 0))

crucible "o painel":
    trial "o botão soma":
        t := V.testar(painel)
        t.clicar("Somar")
        assert t.metrica("Total") is "1"

    trial "e não soma sozinho":
        t := V.testar(painel)
        t.rodar()
        assert t.metrica("Total") is "0"`, lang: 'df' },
  {"h2": "Agir"},
  {"table": {"head": ["Chamada", "Faz"], "rows": [["`t.clicar(rótulo)`", "clica no botão e roda a página de novo"], ["`t.digitar(rótulo, valor)`", "preenche um campo"], ["`t.marcar(rótulo, yes)`", "liga uma caixa ou interruptor"], ["`t.selecionar(rótulo, valor)`", "escolhe numa lista"], ["`t.abrir_aba(rótulo)`", "troca de aba"], ["`t.enviar(formulário)`", "aperta o botão de envio"], ["`t.enviar_arquivo(rótulo, nome, conteúdo)`", "simula um upload"], ["`t.ir_para(caminho)`", "vai para outra página"], ["`t.rodar()`", "roda de novo, sem interação"]]}},
  {"h2": "Perguntar"},
  {"table": {"head": ["Chamada", "Devolve"], "rows": [["`t.texto()`", "a página como texto corrido — para `assert \"erro\" in …`"], ["`t.achar(tipo)`", "todos os nós de um tipo"], ["`t.primeiro(tipo)`", "o primeiro"], ["`t.quantos(tipo)`", "quantos existem"], ["`t.existe(tipo, rótulo)`", "`yes`/`no`"], ["`t.metrica(rótulo)`", "o valor de uma métrica"], ["`t.valor(rótulo)`", "o valor de um campo"], ["`t.alertas(nível)`", "as mensagens de sucesso, erro, aviso"], ["`t.estado(chave)`", "o estado da sessão"], ["`t.falhou()` · `t.falhas()`", "se algo disparou, e o quê"], ["`t.html()` · `t.arvore()`", "a página como HTML, ou como vault"]]}},
  {"p": "Quando um rótulo não existe, a mensagem lista os que existem na página — o erro mais comum ao escrever um teste é errar o texto do botão."},
  {"h2": "HTTP de verdade, sem socket"},
  {"p": "A sonda pula o HTTP. Para testar status, cabeçalho e redirecionamento, `V.pedir`:"},
  { code: `r := V.pedir(app, "GET", "/")
assert r["status"] is 200
assert r["headers"]["X-Content-Type-Options"] is "nosniff"

r2 := V.pedir(app, "GET", "/produto/42")
assert "Produto 42" in r2["body"]`, lang: 'df' },
  {"p": "É o `Kiln.test` por baixo: executa a rota inteira, com middleware, sem abrir porta nenhuma."},
  {"callout": {"tipo": "atencao", "titulo": "O que só aparece com um servidor de verdade", "texto": "`V.pedir` roda tudo numa thread e para antes do cabeçalho `Set-Cookie`. Bug de concorrência e bug de cookie só aparecem com `V.servir(0)` e um cliente HTTP real — foi assim que se descobriu um cookie malformado que fazia cada pedido abrir uma sessão nova, com o sintoma de um contador que nunca passava de 1."}},
];

const headings = [{ id: 'agir', text: "Agir", level: 2 as const }, { id: 'perguntar', text: "Perguntar", level: 2 as const }, { id: 'http-de-verdade-sem-socket', text: "HTTP de verdade, sem socket", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Testar sem navegador"}
      description={"A sonda clica, digita e pergunta; e o pedido HTTP roda sem socket."}
      href={"/docs/vitrine/testes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
