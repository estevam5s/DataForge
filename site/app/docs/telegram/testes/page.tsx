// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/telegram.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testar um bot sem rede",
  description: "A sonda injeta updates e devolve o que o bot teria enviado — sem token, sem celular.",
};

const blocos: Bloco[] = [
  {"p": "Um bot que só pode ser testado conversando com ele no celular **não tem teste**: não roda no CI, não repete, e não diz o que quebrou."},
  { code: `adopt Arcane.Telegram as Tg
adopt Arcane.Test as T

action test_o_start_cumprimenta_pelo_nome():
    t := Tg.testar(meu_bot())
    t.comando("start")
    T.assert_true("Ana" in t.ultima())

action test_o_botao_edita_a_mensagem():
    t := Tg.testar(meu_bot())
    t.clicar("ajuda")
    T.assert_eq(t.quantas("answerCallbackQuery"), 1)`, lang: 'df' },
  {"h2": "O que a sonda faz"},
  {"table": {"head": ["Agir", "Perguntar"], "rows": [["`t.mandar(texto)`", "`t.ultima()` — a última mensagem enviada"], ["`t.comando(nome, ...)`", "`t.respostas()` — todas elas"], ["`t.clicar(dados)`", "`t.disse(trecho)` — se alguma contém o trecho"], ["`t.enviar_foto()` · `t.enviar_documento()`", "`t.ultimo_teclado()`"], ["`t.consultar(texto)`", "`t.chamadas(metodo)` · `t.quantas(metodo)`"], ["`t.entrar()`", "`t.estado(chave)` · `t.falhou()` · `t.falhas()`"]]}},
  {"p": "O dublê aceita **qualquer** método que ele não conheça, anotando a chamada em vez de estourar um erro: um dublê que precisa acompanhar cada método novo do cliente envelhece no primeiro recurso acrescentado."},
  {"h2": "Testar uma conversa inteira"},
  { code: `action test_o_cadastro_valida_o_email():
    t := Tg.testar(meu_bot())
    t.comando("cadastro")
    t.mandar("Ana")
    t.mandar("sem arroba")
    T.assert_true("invalido" in t.ultima())
    t.mandar("ana@exemplo.br")
    T.assert_true(t.disse("Pronto"))
    T.assert_eq(t.estado("__conversa__"), void)`, lang: 'df' },
];

const headings = [{ id: 'o-que-a-sonda-faz', text: "O que a sonda faz", level: 2 as const }, { id: 'testar-uma-conversa-inteira', text: "Testar uma conversa inteira", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Testar um bot sem rede"}
      description={"A sonda injeta updates e devolve o que o bot teria enviado — sem token, sem celular."}
      href={"/docs/telegram/testes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
