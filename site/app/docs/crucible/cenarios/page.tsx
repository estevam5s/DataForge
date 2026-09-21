// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/crucible_doc.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Cenários: concorrência, tempo e rede",
  description: "Provar que o mutex segura, que o cache vence amanhã, e o que o cliente faz com um 503.",
};

const blocos: Bloco[] = [
  {"p": "Os matchers respondem *\"o valor é o esperado?\"*. Estas quatro ferramentas respondem uma pergunta anterior: **em que mundo o código está rodando?** Elas montam o cenário — e não comparam nada."},
  {"h2": "Concorrência: a corrida que o `check` só avisa"},
  {"p": "A linguagem **não sincroniza sozinha**, e isso está documentado: duas threads escrevendo no mesmo nome perdem atualizações, em silêncio. O `check` avisa sobre o padrão (`escrita-concorrente`) — mas avisar não é provar, e um teste que roda a ação uma vez por thread não detecta nada, porque a janela é estreita."},
  { code: `action test_o_contador_perde_sem_mutex():
    contador := spawn Contador()
    r := Crucible.corrida(lambda => contador.somar(),
                          threads := 4, voltas := 5000,
                          leitor := lambda => contador.valor())
    expect(r.perdeu()).to_be_true()
    out $"perdeu {r.perdidas()} de {r.esperado}"

action test_com_mutex_nao_perde():
    contador := spawn ContadorProtegido()
    r := Crucible.corrida(lambda => contador.somar(),
                          threads := 4, voltas := 5000,
                          leitor := lambda => contador.valor())
    expect(r.perdeu()).to_be_false()`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "A barreira é o ponto", "texto": "As threads largam **juntas**. Sem isso, a primeira costuma terminar antes de a última começar — e o teste passa justamente no código que tem a corrida."}},
  {"table": {"head": ["", "O que diz"], "rows": [["`r.perdeu()`", "`yes` quando o total não bate"], ["`r.perdidas()`", "quantas atualizações sumiram"], ["`r.erros`", "o que estourou **dentro** da thread — sem isto, morreria calado"], ["`r.para_vault()`", "tudo, para um relatório"]]}},
  {"h2": "Determinismo: o mesmo dado dá o mesmo resultado?"},
  { code: `r := Crucible.determinismo(lambda => montar_relatorio(vendas), vezes := 5)
expect(r["estavel"]).to_be_true()`, lang: 'df' },
  {"p": "É a propriedade que um relatório precisa ter e que quase nada tem: um `id()` na chave de um cache, uma ordem de vault, um `random` sem semente — os três passam no teste que roda **uma** vez."},
  {"p": "A comparação é por **foto estrutural**, e não por referência: duas listas iguais são objetos diferentes, e comparar referência diria \"instável\" para código perfeitamente determinístico."},
  {"h2": "O relógio que anda"},
  {"p": "`freeze_time` congela; o relógio **anda**. A diferença importa para testar o que depende de *intervalo* — um cache com validade, um recuo, um prazo — porque congelado eles nunca vencem, e com o relógio de verdade o teste precisa dormir."},
  { code: `action test_o_cache_vence_em_trinta_minutos():
    Crucible.com_relogio(lambda r => conferir_validade(r),
                         "2026-09-20 10:00:00")

action conferir_validade(r):
    cache.guardar("cotacao", 5.42)
    r.avancar(minutos := 29)
    expect(cache.obter("cotacao")).to_be(5.42)
    r.avancar(minutos := 2)
    expect(cache.obter("cotacao")).to_be_void()`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Use `com_relogio`, e não `ligar` à mão", "texto": "Ele desliga o relógio **mesmo quando o trial estoura**. Um relógio ligado que escapa faz todos os trials seguintes verem o tempo parado — e a suíte passa a falhar em lugares que não têm nada a ver."}},
  {"h2": "Um HTTP que você controla"},
  {"p": "Um dublê substitui o cliente e prova que o código chamou um método. O **servidor falso** sobe um socket de verdade e prova que o código fala HTTP direito — cabeçalho, corpo, status — e o que ele faz com um 503. São perguntas diferentes, e a segunda é a que quebra em produção."},
  { code: `action test_o_cliente_repete_duas_vezes_e_desiste():
    s := Crucible.servidor_falso()
    s.falhar("/precos", 503, vezes := 2)
    s.responder("/precos", {"dolar": 5.42})

    resposta := meu_cliente.buscar(s.url("/precos"))

    expect(resposta["dolar"]).to_be(5.42)
    expect(s.quantos("/precos")).to_be(3)
    s.parar()`, lang: 'df' },
  {"p": "O `vezes` é o que torna testável o *\"falha duas vezes e na terceira funciona\"* — o comportamento que um cliente com recuo promete e quase nunca tem teste."},
  {"table": {"head": ["Programar", "Perguntar"], "rows": [["`s.responder(rota, corpo, status)`", "`s.pedidos(rota)` — tudo o que chegou"], ["`s.falhar(rota, status, vezes)`", "`s.ultimo(rota)` — o último, com corpo e cabeçalhos"], ["`s.demorar(segundos)`", "`s.quantos(rota)`"], ["`s.url(caminho)`", "`s.limpar()` · `s.parar()`"]]}},
  {"p": "Uma rota que ninguém programou responde **404**, e não um corpo vazio: um 200 sem conteúdo faria o teste falhar num ponto distante, dizendo que o dado veio errado."},
];

const headings = [{ id: 'concorrencia-a-corrida-que-o-check-so-avisa', text: "Concorrência: a corrida que o `check` só avisa", level: 2 as const }, { id: 'determinismo-o-mesmo-dado-da-o-mesmo-resultado', text: "Determinismo: o mesmo dado dá o mesmo resultado?", level: 2 as const }, { id: 'o-relogio-que-anda', text: "O relógio que anda", level: 2 as const }, { id: 'um-http-que-voce-controla', text: "Um HTTP que você controla", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Cenários: concorrência, tempo e rede"}
      description={"Provar que o mutex segura, que o cache vence amanhã, e o que o cliente faz com um 503."}
      href={"/docs/crucible/cenarios"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
