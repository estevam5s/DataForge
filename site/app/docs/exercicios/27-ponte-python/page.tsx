// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "27 · Ponte para o Python",
  description: "1 exercícios: adopt Python.*: numpy, pandas e o que vem junto.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 27`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[219](#219-a-ponte-para-o-python)", "**A ponte para o Python**", "use uma biblioteca Python de dentro do DataForge, e faca"]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "219 · A ponte para o Python"},
  {"p": "**Enunciado.** use uma biblioteca Python de dentro do DataForge, e faca"},
  { code: `// o programa continuar funcionando quando ela nao estiver instalada.

adopt Arcane.Ponte as Ponte

// ── 1. Perguntar antes de depender ──
//
// 'tem' responde sem levantar erro. E o que separa um programa que se
// adapta de um que morre na primeira linha numa maquina diferente.

out $"o Python por tras: {Ponte.onde().split("/").last()}"
out $"math instalado?   {Ponte.tem("math")}"
out $"xyz123 instalado? {Ponte.tem("xyz123_nao_existe")}"

assert Ponte.tem("math") is yes, "a biblioteca padrao do Python sempre esta la"
assert Ponte.tem("xyz123_nao_existe") is no, "e o que nao existe, nao"

// ── 2. Trazer um modulo ──
//
// E 'adopt' normal. Nao ha palavra reservada nova: 'Python' e um
// espaco de nomes reservado, resolvido antes da biblioteca padrao.

adopt Python.math as pm
adopt Python.json as json

out ""
out $"pm.gcd(12, 18) = {pm.gcd(12, 18)}"
assert pm.gcd(12, 18) is 6, "maximo divisor comum"

// So os nomes que interessam, se preferir
adopt Python.math.{floor, isqrt}
assert floor(3.9) is 3, "floor"
assert isqrt(17) is 4, "raiz inteira"

// ── 3. Os valores atravessam sem copia ──
//
// Um Cluster E uma lista do Python, e um Vault E um dicionario. Nao ha
// conversao na ida — por isso passar uma colecao grande nao custa nada.

v := {"nome": "Ana", "notas":[9, 8, 10]}
texto := json.dumps(v)
de_volta := json.loads(texto)

out ""
out texto
assert typeof(de_volta) is "Vault", "voltou como Vault"
assert de_volta["notas"][2] is 10, "as notas sobreviveram a ida e volta"

// ── 4. Uma acao do DataForge vira funcao do Python ──

adopt Python.functools as ft

action somar(a, b):
    yield a + b

total := ft.reduce(somar, [1, 2, 3, 4, 5], 0)
out ""
out $"reduce com uma acao daqui: {total}"
assert total is 15, "o Python chamou a acao do DataForge"

// ── 5. O programa se adapta ──
//
// Repare no 'media := 0.0' ANTES do 'given': cada ramo tem o proprio
// escopo, e o que nasce dentro nao vaza para fora.

dados := [4.0, 8.0, 15.0, 16.0]
media := 0.0

given Ponte.tem("statistics"):
    adopt Python.statistics as st
    media := st.mean(dados)
otherwise:
    media := (dados >> distill a, v: a + v 0) / len(dados)

out ""
out $"media: {media}"
assert media is 10.75, "os dois caminhos dao o mesmo numero"

// ── 6. Explorar de dentro da linguagem ──
//
// Sem isto, descobrir o que um pacote oferece exige sair do DataForge
// e abrir a documentacao dele.

out ""
out $"json tem 'dumps'? {"dumps" in Ponte.atributos(json)}"
out $"assinatura: {Ponte.assinatura(pm.gcd) ?? "o Python nao declara"}"
out $"doc: {Ponte.doc(pm.isqrt).lines()[0]}"

assert "loads" in Ponte.atributos(json), "atributos lista o que existe"

// ── 7. A ponte NAO converte, e e isso que a faz valer ──
//
// Uma tupla do Python indexa e percorre, mas nao tem 'append'. Dizer
// que ela e um Cluster seria mentira; 'Ponte.cluster' converte quando
// voce QUER — e a linha diz onde se paga a copia.

par := pm.frexp(8.0)
out ""
out $"typeof da tupla:  {typeof(par)}"
out $"typeof convertido: {typeof(Ponte.cluster(par))}"
assert typeof(Ponte.cluster(par)) is "Cluster", "a conversao e explicita"

// ── 8. O erro do outro lado chega capturavel ──

monitor:
    json.loads("{isso nao e json}")
handle e:
    out ""
    out $"erro do Python, capturado aqui: {e.type}"

out ""
out "ok"`, lang: 'df', title: `exercicios/27-ponte-python/219_ponte_python.df` },
  {"h3": "Conceitos"},
  { code: `adopt Python.numpy as np              // o módulo inteiro
adopt Python.numpy.linalg as la       // um submódulo
adopt Python.json.{loads, dumps}      // só os nomes que interessam
adopt {sqrt} from Python.math         // a ordem invertida também vale`, lang: 'df' },
  {"p": "Não há palavra reservada nova. `Python` é um **espaço de nomes reservado**, resolvido antes da biblioteca padrão e antes dos arquivos vizinhos — um `Python.df` no disco não sequestra o import."},
  {"h3": "Para que serve"},
  {"p": "Uma linguagem que não alcança biblioteca nenhuma é uma ilha: toda capacidade nova precisa ser reescrita do zero. O DataForge **roda sobre Python** e não alcançava nada dele. Esta é a porta."},
  {"h3": "A ponte não converte"},
  {"p": "Um `ndarray` continua um `ndarray`:"},
  { code: `adopt Python.numpy as np

a := np.array([1, 2, 3, 4])
out a * 2 + 1        // [3 5 7 9] — conta vetorizada do numpy`, lang: 'df' },
  {"p": "Se a ponte copiasse, `a * 2` viraria um laço sobre um cluster de um milhão de posições, e a razão de usar numpy desapareceria."},
  {"p": "Isso funciona porque o interpretador trata objeto estranho pelo que ele **faz**, não pelo que ele é — membro, método, índice, `len`, iteração, aritmética, texto e verdade já passavam por protocolo."},
  {"p": "O preço é que o vocabulário vaza em dois lugares, e os dois são deliberados:"},
  {"table": {"head": ["", "`typeof` responde", "Por quê"], "rows": [["tupla do Python", "`tuple`", "ela indexa e percorre, mas não tem `append`"], ["`ndarray`", "`ndarray`", "é o que ele é"], ["`np.int64`", "**`Integer`**", "ele *faz* conta de inteiro"]]}},
  {"p": "O último é a exceção que prova a regra: `given typeof(x) is \"Integer\"` seria falso para um valor que soma, divide e compara como um. A regra vem do protocolo `numbers` do Python — não há nada de numpy dentro do interpretador, e `Fraction` e `Decimal` entram pela mesma porta."},
  {"h3": "Perguntar antes de depender"},
  { code: `adopt Arcane.Ponte as Ponte

dados := [4.0, 8.0, 15.0, 16.0]
media := 0.0

given Ponte.tem("statistics"):
    adopt Python.statistics as st
    media := st.mean(dados)
otherwise:
    media := (dados >> distill a, v: a + v 0) / len(dados)`, lang: 'df' },
  {"p": "O `media := 0.0` antes do `given` não é enfeite: cada ramo tem o próprio escopo, e o que nasce dentro não vaza para fora."},
  {"h3": "Explorar de dentro da linguagem"},
  {"table": {"head": ["", "Faz"], "rows": [["`Ponte.atributos(x)`", "os nomes públicos de um módulo ou objeto"], ["`Ponte.doc(x)`", "a documentação que o Python carrega no objeto"], ["`Ponte.assinatura(x)`", "como se chama, ou `void` se o Python não declara"], ["`Ponte.tipo(x)`", "o nome do tipo **do lado de lá**"], ["`Ponte.cluster(x)` / `Ponte.vault(x)`", "converte, explicitamente"], ["`Ponte.tem(nome)` / `Ponte.versao(nome)`", "sem levantar erro"], ["`Ponte.onde()` / `Ponte.empacotado()`", "qual Python está por trás"]]}},
  {"p": "`Ponte.assinatura` devolve `void` para função escrita em C que não declara os argumentos. Inventar `(…)` faria você achar que a função não tem nenhum."},
  {"h3": "Quando o pacote não está lá"},
  {"p": "A mensagem responde as três perguntas que você vai ter, nesta ordem: o que faltou, **em qual Python** faltou, e o comando exato para aquele Python."},
  {"p": "O caminho importa: o instalador cria uma venv em `~/.dataforge`. Quem roda `pip install pandas` no terminal instala no Python do **sistema**, que é outro, e o `adopt` continua falhando sem que nada explique."},
  {"p": "E o `dataforge check` avisa antes de rodar, porque ele consegue **provar** que o pacote não está aqui."},
  {"p": "> **O executável único não tem `pip`.** Ele traz um Python próprio e > nunca vai instalar pacote nenhum. A mensagem diz isso com todas as > letras, em vez de sugerir um comando que não funcionaria."},
  {"h3": "O que a ponte não protege"},
  {"p": "`adopt Python.os` roda o código de inicialização do pacote, exatamente como um `import` faria. **Não há sandbox**, e fingir que há seria pior que não ter."},
  {"p": "Isso não acrescenta uma categoria de risco — a linguagem já tem `Arcane.Process.run` e escrita em disco. O que a ponte faz é tornar a fronteira **visível na linha do `adopt`**."},
  {"h3": "A promessa de zero dependências continua inteira"},
  {"p": "Nada em `dataforge/` importa nada de fora. O que muda é que o **programa de quem escreve** passa a poder escolher as suas — a mesma distinção entre \"o Python não depende do numpy\" e \"o seu script pode depender\"."},
  {"h3": "Saída esperada"},
  { code: `o Python por tras: python3
math instalado?   yes
xyz123 instalado? no

pm.gcd(12, 18) = 6

{"nome": "Ana", "notas": [9, 8, 10]}

reduce com uma acao daqui: 15

media: 10.75

json tem 'dumps'? yes
assinatura: gcd(*integers)
doc: Return the integer part of the square root of the input.

typeof da tupla:  tuple
typeof convertido: Cluster

erro do Python, capturado aqui: ValueError

ok`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["`Ponte.atributos` num pacote que você use, e chame algo de lá.", "Instale o `requests` e escreva um `adopt Python.requests` que busque"]},
  {"p": "uma página — compare com o `Arcane.Http` da linguagem."},
  {"list": ["Rode `dataforge check` num arquivo que importe um pacote ausente.", "Escreva uma ação que só usa numpy quando ele existe, e caia num laço"]},
  {"p": "quando não existe. Rode os dois caminhos."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/27-ponte-python/219_ponte_python.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '219-a-ponte-para-o-python', text: "219 · A ponte para o Python", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'para-que-serve', text: "Para que serve", level: 3 as const }, { id: 'a-ponte-nao-converte', text: "A ponte não converte", level: 3 as const }, { id: 'perguntar-antes-de-depender', text: "Perguntar antes de depender", level: 3 as const }, { id: 'explorar-de-dentro-da-linguagem', text: "Explorar de dentro da linguagem", level: 3 as const }, { id: 'quando-o-pacote-nao-esta-la', text: "Quando o pacote não está lá", level: 3 as const }, { id: 'o-que-a-ponte-nao-protege', text: "O que a ponte não protege", level: 3 as const }, { id: 'a-promessa-de-zero-dependencias-continua-inteira', text: "A promessa de zero dependências continua inteira", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"27 · Ponte para o Python"}
      description={"1 exercícios: adopt Python.*: numpy, pandas e o que vem junto."}
      href={"/docs/exercicios/27-ponte-python"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
