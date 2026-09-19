// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ecossistema.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Onde dois princípios se contradizem",
  description: "Nove tensões reais: a escolha, o motivo, o custo aceito e o arquivo onde a decisão mora. Uma lista de princípios diz o que se quer; a tensão diz o que se escolheu.",
};

const blocos: Bloco[] = [
  {"p": "Um princípio isolado não informa nada. Todo mundo é a favor de segurança, e todo mundo é a favor de velocidade."},
  {"p": "O que informa é **onde dois princípios se contradizem e qual deles venceu** — e essa decisão, nesta linguagem, está sempre num arquivo."},
  { code: `adopt Arcane.Principios as Prin

// A tensao e o conteudo: a lista diz o que se quer, a tensao diz o que
// se escolheu quando nao era possivel querer as duas coisas.
ts := Prin.tensoes()
assert len(ts) bigger_eq 9
cycle t in ts:
    assert len(t["entre"]) is 2
    assert t["escolha"] is not ""
    assert t["custo"] is not ""        // toda escolha tem preco declarado

out $"{len(ts)} tensoes, e cada uma aponta um arquivo"`, lang: 'df' },
  {"h2": "Segurança × verificação: o aviso que não virou erro"},
  {"p": "Duas threads escrevendo na mesma variável perdem atualizações **em silêncio** — medido: 40.425 de 80.000. Numa rota do Kiln é pior, porque a concorrência é invisível: seis pedidos simultâneos numa rota que lê, espera e escreve entregaram **1 de 6**."},
  {"p": "O `check` avisa. Ele não **recusa**."},
  {"callout": {"tipo": "atencao", "titulo": "Por que não é erro", "texto": "Um acumulador protegido por mutex passa pelo mesmo caminho de um sem proteção. Recusá-lo proibiria o uso correto — e a pessoa desligaria a verificação inteira, perdendo também os avisos que valiam. **Custo aceito:** um programa com bug de concorrência passa pelo `check`."}},
  {"p": "E a lista de métodos que disparam o aviso foi **medida, não presumida**: `append` de quatro threads, 5 mil vezes cada, entregou 20.000 de 20.000 — o GIL protege a operação inteira, e avisar sobre ele seria falso alarme em código que funciona."},
  {"h2": "Verificação × falso alarme: o analisador cala"},
  {"p": "A calibragem é **0 erros em 222 arquivos conhecidamente bons**. Quando o analisador não consegue provar, ele fica calado — e a lista de silêncios é explícita."},
  {"table": {"head": ["Cala quando", "Porque"], "rows": [["o outro arquivo não compila", "um falso alarme no caminho mais comum de um projeto modular ensina a desligar a verificação"], ["há ciclo de import", "a leitura não termina, e chutar seria pior"], ["a profundidade (4) acaba", "o custo cresce e a certeza não"], ["o `relay` nomeia algo que só existe em execução", "não há como ler o que ainda não rodou"], ["`v[\"k\"] ?? padrao`", "`??` é exatamente o que a dica daquele erro recomenda — acusar o próprio conserto desligaria a ferramenta"], ["um parâmetro de tipo (`T`) chega com cara de tipo", "sem isso, a trilha ganhava dois alarmes no capítulo que **ensina** generics"]]}},
  {"callout": {"tipo": "perigo", "titulo": "O custo de errar essa escolha foi medido", "texto": "Quando a inferência usou o escopo global em vez do de quem chama, o `check` deu **649 falsos alarmes** num projeto de 252 arquivos — um por uso de parâmetro numa chamada entre módulos. E a suíte passava: os primeiros testes chamavam no nível de topo, onde o escopo global é o certo. Quem pegou foi rodar no projeto grande."}},
  {"h2": "Velocidade × depurabilidade: o depurador desliga o compilador"},
  {"p": "`interp.compilar_corpos = False`. O depurador para em cada linha sombreando `execute`, e o corpo compilado passa por fora."},
  {"p": "Um depurador que enxerga metade das instruções é **pior** que um interpretador mais lento: ele mente sobre onde o programa está."},
  {"callout": {"tipo": "nota", "titulo": "E as duas execuções não são o mesmo caminho", "texto": "Por isso `tests/test_desempenho.py` roda uma amostra dos exercícios com a compilação ligada e desligada e compara a saída **caractere por caractere**. É esse teste que pega um fechamento que divergiu do método que ele espelha."}},
  {"h2": "Velocidade × correção: o escopo do laço"},
  {"p": "Reaproveitar o escopo entre voltas de um laço é a otimização mais rentável do interpretador. E é **a mais perigosa**: errá-la não dá erro, dá resposta errada."},
  { code: `acoes := []
cycle i from 1 to 3:
    acoes.append(lambda => i)          // cada volta tem o SEU 'i'

assert acoes[0]() is 1
assert acoes[1]() is 2
assert acoes[2]() is 3                 // e nao 3, 3, 3
out "cada closure lembra a volta em que nasceu"`, lang: 'df' },
  {"p": "`_corpo_captura_escopo` varre a árvore **inteira**, e não só as instruções — um `lambda` vive dentro de uma expressão. Sem isso, as três closures veriam todas o último valor: o clássico que o Python tem e que aqui não acontece."},
  {"h2": "Extensibilidade × nomes bons"},
  {"p": "`route`, `render`, `server`, `agrupar` e `ordenar` são nomes bons demais para tirar de quem escreve. Por isso palavra nova entra como **contextual**, e não em `KEYWORDS`."},
  { code: `// 'route' e contextual: aqui e um nome comum
route := "/pedidos"
agrupar := yes
assert route is "/pedidos"
assert agrupar is yes
out "as palavras do framework continuam livres"`, lang: 'df' },
  {"table": {"head": ["Família", "Quantas", "Onde valem"], "rows": [["Kiln", "11", "dentro de `server` e de uma rota"], ["OOP / blueprint", "21", "onde um modificador faz sentido"], ["`type`, `opaque`, `where`", "4", "quando a linha confirma a declaração"], ["Crucible", "10", "numa suíte de teste"], ["verbos de quadro", "6", "logo depois de um `>>`"]]}},
  {"callout": {"tipo": "dica", "titulo": "Sete palavras reservadas já foram REMOVIDAS", "texto": "Toda palavra em `KEYWORDS` deixa de poder ser identificador. Antes de acrescentar uma, o repositório cobra `grep -c \"TokenType.NOVA\" dataforge/parser.py` — se der 0, ela só quebra código de usuário sem entregar nada. **Custo aceito:** o parser fica mais complicado, e a gramática do editor precisa de duas travas para não envelhecer."}},
  {"h2": "Runtime modular × zero dependência"},
  {"p": "A biblioteca padrão usa **apenas** a biblioteca padrão do Python. Isso significa código escrito à mão onde havia biblioteca madura:"},
  {"list": ["ChaCha20-Poly1305, pelo RFC 8439", "o `.xlsx`, sem dependência externa", "o WebSocket, pelo RFC 6455 — máscara, ping, pong, continuação e quadro de 64 bits", "os gráficos da Vitrine, em SVG escrito no servidor, com ~4 KB de cliente"]},
  {"p": "O preço está escrito: criptografia e formato de arquivo implementados aqui, com o risco que isso tem. E o ganho também: **um app em rede fechada funciona** — que é onde painel de dados costuma rodar."},
  {"callout": {"tipo": "nota", "titulo": "E há teste cobrando isso", "texto": "Um teste proíbe `http://`, `https://` e `cdn` no CSS e no JS da Vitrine. Uma biblioteca de CDN quebra qualquer app em rede fechada, e a falha aparece no cliente, não no build."}},
  {"h2": "Portabilidade × performance"},
  {"p": "A portabilidade é **herdada** do CPython. É o que dá Linux, macOS, Windows, ARM e ARM64 sem uma linha de código de arquitetura, e o que faz `adopt Python.numpy` existir."},
  {"p": "É também o que põe o teto em ~6,5×. As duas coisas são a mesma decisão vista de dois lados, e não há como ficar só com uma."},
  {"h2": "Controle × segurança: onde a proteção para"},
  {"p": "FFI sem ponteiro não é FFI. `Arcane.C` recusa o nulo e confere o layout da struct contra a ABI — e aritmética de ponteiro é aritmética de ponteiro."},
  {"callout": {"tipo": "perigo", "titulo": "Um segmentation fault não é um erro da linguagem", "texto": "É o processo morrendo. A fronteira está **documentada** em vez de fingida: passado esse ponto, quem escreve é responsável pelo que acontece."}},
  {"h2": "Mensagem útil × identidade do erro"},
  {"p": "O runtime fala português. A tradução acontece **no desenho**, nunca em `error.message`."},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["traduzir ao desenhar", "`e.message` é o que um `handle` compara e o que milhares de testes comparam — traduzir ali mudaria o comportamento de programa já escrito"], ["o que não tem tradução sai em inglês", "ninguém traduz 530 mensagens numa tacada, e um erro é mais útil legível em inglês que ilegível em português"], ["a suíte roda em inglês", "um teste que afirma \"Division by zero\" checa a **estrutura** do relatório; deixar o idioma solto o faria reprovar a cada tradução nova"], ["há um piso de cobertura", "o fallback certo é também o que esconde o buraco: o que falta sai em inglês legível, e ninguém vê"]]}},
  {"p": "O que interessa a um programa é a **identidade** do erro, não o idioma dele. O que interessa a uma pessoa é o contrário — e as duas coisas caibem, desde que em camadas diferentes."},
];

const headings = [{ id: 'seguranca-verificacao-o-aviso-que-nao-virou-erro', text: "Segurança × verificação: o aviso que não virou erro", level: 2 as const }, { id: 'verificacao-falso-alarme-o-analisador-cala', text: "Verificação × falso alarme: o analisador cala", level: 2 as const }, { id: 'velocidade-depurabilidade-o-depurador-desliga-o-compilador', text: "Velocidade × depurabilidade: o depurador desliga o compilador", level: 2 as const }, { id: 'velocidade-correcao-o-escopo-do-laco', text: "Velocidade × correção: o escopo do laço", level: 2 as const }, { id: 'extensibilidade-nomes-bons', text: "Extensibilidade × nomes bons", level: 2 as const }, { id: 'runtime-modular-zero-dependencia', text: "Runtime modular × zero dependência", level: 2 as const }, { id: 'portabilidade-performance', text: "Portabilidade × performance", level: 2 as const }, { id: 'controle-seguranca-onde-a-protecao-para', text: "Controle × segurança: onde a proteção para", level: 2 as const }, { id: 'mensagem-util-identidade-do-erro', text: "Mensagem útil × identidade do erro", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Onde dois princípios se contradizem"}
      description={"Nove tensões reais: a escolha, o motivo, o custo aceito e o arquivo onde a decisão mora. Uma lista de princípios diz o que se quer; a tensão diz o que se escolheu."}
      href={"/docs/ecossistema/tensoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
