import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A ponte para o Python",
  description: "adopt Python.numpy — usar qualquer biblioteca Python de dentro do DataForge, sem cópia e sem mentira.",
};

const blocos: Bloco[] = [
  {"p": "Uma linguagem que não alcança biblioteca nenhuma é uma ilha. Toda capacidade nova precisa ser reescrita do zero — foi assim que este projeto ganhou um Parquet próprio, um ChaCha20 próprio e 25 algoritmos de aprendizado próprios. Cada um correto, cada um a uma fração do que existe pronto lá fora."},
  {"p": "O DataForge **roda sobre Python** e não alcançava nada dele. Esta é a porta."},

  {"h2": "adopt Python.<módulo>"},
  { code: `adopt Python.numpy as np

a := np.array([1, 2, 3, 4])
out a * 2 + 1          # [3 5 7 9]
out a.sum(), a.mean()  # 10 2.5` },
  {"p": "É `adopt` normal — não há palavra reservada nova. `Python` é um espaço de nomes reservado, resolvido antes da biblioteca padrão e antes dos arquivos vizinhos."},
  { code: `adopt Python.numpy as np              # o módulo inteiro
adopt Python.numpy.linalg as la       # um submódulo
adopt Python.json.{loads, dumps}      # só os nomes que interessam
adopt {sqrt} from Python.math         # a ordem invertida também vale` },

  {"h2": "A ponte não converte"},
  {"p": "Um `ndarray` continua um `ndarray`. É justamente por isso que `a * 2 + 1` faz a conta vetorizada do numpy, em vez de virar um laço sobre um cluster de um milhão de posições."},
  {"p": "Isso funciona porque o interpretador já trata objeto estranho pelo que ele **faz**, e não pelo que ele é — membro, método, índice, `len`, iteração, aritmética, texto e verdade já passavam por protocolo. A ponte não reimplementa nada disso."},
  {"callout": {"tipo": "atencao", "titulo": "O preço da honestidade", "texto": "O vocabulário vaza em dois lugares, e os dois são deliberados. Uma tupla do Python **não** é um `Cluster` — ela indexa e percorre, mas não tem `append`. E `typeof` de um `ndarray` responde `ndarray`, porque é o que ele é. Mentir ali custaria a cópia que a ponte existe para evitar."}},
  {"p": "Número é a exceção: `typeof(a.sum())` responde `Integer`, não `int64`. Um escalar do numpy **faz** conta de inteiro, e `given typeof(x) is \"Integer\"` seria falso para um valor que soma, divide e compara como um. A regra vem do protocolo `numbers` do Python, não de numpy — `Fraction` e `Decimal` entram pela mesma porta."},

  {"h2": "Perguntar antes de depender"},
  {"p": "`Arcane.Ponte` responde sem levantar erro, e é o que permite um programa se adaptar em vez de morrer:"},
  { code: `adopt Arcane.Ponte as Ponte

dados := [4.0, 8.0, 15.0, 16.0]
media := 0.0

given Ponte.tem("numpy"):
    adopt Python.numpy as np
    media := np.array(dados).mean()
otherwise:
    media := dados >> distill a, v: a + v 0 / len(dados)

out media` },
  {"callout": {"tipo": "dica", "texto": "Repare no `media := 0.0` antes do `given`: cada ramo tem o próprio escopo, e o que nasce dentro não vaza para fora. Isso vale para todo `given`, não só aqui."}},

  {"h2": "Explorar de dentro da linguagem"},
  {"p": "Sem isto, descobrir o que um pacote oferece exige sair do DataForge e abrir a documentação dele. No REPL, é a diferença entre experimentar e desistir."},
  { code: `adopt Python.json as json

out Ponte.atributos(json)
# [JSONDecodeError, JSONDecoder, JSONEncoder, codecs, decoder, …]

out Ponte.assinatura(json.dumps)
# dumps(obj, *, skipkeys=False, ensure_ascii=True, …)

out Ponte.doc(json.loads).lines()[0]
# Deserialize \`\`s\`\` (a \`\`str\`\`, \`\`bytes\`\` or \`\`bytearray\`\` instance` },

  {"h2": "Converter quando você quiser"},
  { code: `forma := np.zeros([2, 3]).shape
out typeof(forma)                  # tuple
out typeof(Ponte.cluster(forma))   # Cluster
out Ponte.cluster(forma)           # [2, 3]` },
  {"p": "Serem explícitas é o ponto: a linha diz onde se paga a cópia."},

  {"h2": "A tabela inteira"},
  {"table": {"head": ["", "Faz"], "rows": [
    ["`Ponte.tem(nome)`", "o pacote está instalado? `yes`/`no`, sem levantar erro"],
    ["`Ponte.versao(nome)`", "a versão instalada, ou `void`"],
    ["`Ponte.importar(nome)`", "o módulo como valor — para quando o nome só se sabe rodando"],
    ["`Ponte.onde()`", "o caminho do Python que está por trás"],
    ["`Ponte.empacotado()`", "`yes` se for o executável único, que não tem `pip`"],
    ["`Ponte.atributos(x)`", "os nomes públicos de um módulo ou objeto"],
    ["`Ponte.doc(x)`", "a documentação que o Python carrega no objeto"],
    ["`Ponte.assinatura(x)`", "como se chama, ou `void` se o Python não declara"],
    ["`Ponte.tipo(x)`", "o nome do tipo **do lado do Python** — `ndarray`, `DataFrame`"],
    ["`Ponte.chamavel(x)`", "dá para chamar?"],
    ["`Ponte.cluster(x)`", "qualquer percorrível vira um `Cluster`"],
    ["`Ponte.vault(x)`", "qualquer mapa vira um `Vault`"]]}},

  {"h2": "Quando o pacote não está lá"},
  {"p": "A mensagem responde as três perguntas que você vai ter, nesta ordem: o que faltou, **em qual Python** faltou, e o comando exato para aquele Python."},
  { code: `erro[DF0501]: o pacote Python 'pandas' nao esta instalado.
   ┌─ analise.df:1:1
   │
 1 │ adopt Python.pandas as pd
   │ ^
   │
   = nota: o DataForge roda sobre ~/.dataforge/venv/bin/python3 —
           e e NESSE Python que o pacote precisa estar
   = dica: ~/.dataforge/venv/bin/python3 -m pip install pandas`, lang: 'text' },
  {"p": "O caminho exato importa: o instalador cria uma venv em `~/.dataforge`. Quem roda `pip install pandas` no terminal instala no Python do **sistema**, que é outro, e o `adopt` continua falhando sem que nada explique por quê."},
  {"callout": {"tipo": "atencao", "titulo": "O executável não tem pip", "texto": "Se você instalou o DataForge pelo **executável único**, ele traz um Python próprio e sem `pip` — não consegue instalar pacote nenhum, nunca. A mensagem diz isso com todas as letras e aponta a saída: para usar bibliotecas Python, instale pelo `pip install dataforge-lang`."}},
  {"p": "E o `dataforge check` avisa antes de rodar, porque ele **pode provar** que o pacote não está aqui:"},
  { code: `analise.df:1:1: aviso: o pacote Python 'pandas' nao esta instalado aqui
    sugestão: se ele existir na maquina que vai RODAR o programa,
              este aviso nao se aplica`, lang: 'text' },

  {"h2": "O que a ponte não protege"},
  {"p": "`adopt Python.os` roda o código de inicialização do pacote, exatamente como um `import` faria. **Não há sandbox aqui**, e fingir que há seria pior que não ter."},
  {"p": "Isso não acrescenta uma categoria de risco: a linguagem já tem `Arcane.Process.run` e escrita em disco. O que a ponte faz é tornar a fronteira **visível na linha do `adopt`** — quem lê o código sabe exatamente onde o programa deixou de ser portátil por conta própria."},

  {"h2": "A promessa de zero dependências continua inteira"},
  {"p": "Nada em `dataforge/` importa nada de fora. O que muda é que o **programa de quem escreve** passa a poder escolher as suas."},
  {"p": "É a mesma distinção que separa \"o Python não depende do numpy\" de \"o seu script pode depender\". A palavra `Python` na linha do `adopt` é a declaração explícita de que a fronteira foi cruzada ali."},
];

const headings = [{ id: 'adopt-pythonmodulo', text: "adopt Python.<módulo>", level: 2 as const }, { id: 'a-ponte-nao-converte', text: "A ponte não converte", level: 2 as const }, { id: 'perguntar-antes-de-depender', text: "Perguntar antes de depender", level: 2 as const }, { id: 'explorar-de-dentro-da-linguagem', text: "Explorar de dentro da linguagem", level: 2 as const }, { id: 'converter-quando-voce-quiser', text: "Converter quando você quiser", level: 2 as const }, { id: 'a-tabela-inteira', text: "A tabela inteira", level: 2 as const }, { id: 'quando-o-pacote-nao-esta-la', text: "Quando o pacote não está lá", level: 2 as const }, { id: 'o-que-a-ponte-nao-protege', text: "O que a ponte não protege", level: 2 as const }, { id: 'a-promessa-de-zero-dependencias-continua-inteira', text: "A promessa de zero dependências continua inteira", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"A ponte para o Python"}
      description={"adopt Python.numpy — usar qualquer biblioteca Python de dentro do DataForge, sem cópia e sem mentira."}
      href={"/docs/tecnicas/ponte"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
