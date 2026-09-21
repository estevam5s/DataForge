// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/estruturas.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Ponteiros",
  description: "Aritmética por elemento, cast, distância — e as duas formas de um ponteiro não valer nada.",
};

const blocos: Bloco[] = [
  {"h2": "Andar por elemento, e não por byte"},
  { code: `p := Est.ponteiro(numeros, "u32")

out p.ler()
out p.mais(1).ler()          // o PRÓXIMO u32
out p.mais(1).endereco()     // 4 — e não 1
out p.cluster(4)             // os quatro a partir daqui`, lang: 'df' },
  {"p": "`p + 1` num `u32*` do C anda quatro bytes. Andar um byte é um índice, não um ponteiro — e é a conta que quem escreve C faz o tempo todo. `p.distancia(q)` responde na mesma unidade, e é recusada entre tipos diferentes: a conta é em elementos, e dois tipos têm tamanhos diferentes."},
  {"h2": "O cast"},
  { code: `p.como("u8").mais(3).ler()   // os mesmos bytes, outro tipo`, lang: 'df' },
  {"h2": "As duas formas de não valer nada"},
  {"table": {"head": ["", "O que é"], "rows": [["`Est.nulo()`", "o endereço existe e vale **zero**; lê-lo seria a falha de segmentação clássica"], ["bloco liberado", "o endereço continua na mão de alguém, e o bloco declarou o fim"]]}},
  { code: `p := Est.nulo()
out p.e_nulo()      // yes
p.ler()             // NullPointerError

morto := Est.bloco(8)
q := Est.ponteiro(morto, "u32")
morto.liberar()
q.ler()             // DanglingPointerError`, lang: 'df' },
  {"p": "`NullPointerError` é diferente de `NullReferenceError`, que fala de um `void` da linguagem. Aqui o endereço existe."},
  {"h2": "O ponteiro segura o bloco — e isso é uma decisão"},
  {"callout": {"tipo": "nota", "titulo": "A referência fraca era uma armadilha", "texto": "A primeira versão guardava uma referência fraca, para imitar o C. O efeito: `Est.ponteiro(Est.bloco(8), \"u32\")` nascia pendurado, porque o bloco temporário morria assim que a chamada voltava. Um ponteiro cuja validade depende de a expressão ter sido guardada numa variável aparece e some conforme a contagem de referências — que é a pior classe de defeito. Num mundo com coletor a memória nunca esteve em risco; o que se protege é o **protocolo**, e ele tem um ponto só: `liberar()`."}},
  {"h2": "União"},
  { code: `Valor := Est.uniao("Valor", [
    ["inteiro", "u32"],
    ["flutuante", "f32"]
], ordem := "rede")

Valor.escrever(caixa, {"flutuante": 1.0})
out Valor.ler(caixa)["inteiro"]     // 1065353216 — o IEEE 754 de 1.0`, lang: 'df' },
  {"p": "Todos os campos no mesmo deslocamento zero, e o tamanho é o do maior. Escrever um e ler outro devolve a reinterpretação dos bytes — que é o ponto de uma união, e também o que a torna perigosa quando o tipo escrito não é registrado em algum lugar."},
  {"h2": "O exemplo completo"},
  {"p": "`examples/estrutura_binaria.df` monta um arquivo com cabeçalho e três registros, percorre com janelas, escreve por ponteiro e demonstra as cinco recusas — com `assert` em cada afirmação."},
];

const headings = [{ id: 'andar-por-elemento-e-nao-por-byte', text: "Andar por elemento, e não por byte", level: 2 as const }, { id: 'o-cast', text: "O cast", level: 2 as const }, { id: 'as-duas-formas-de-nao-valer-nada', text: "As duas formas de não valer nada", level: 2 as const }, { id: 'o-ponteiro-segura-o-bloco-e-isso-e-uma-decisao', text: "O ponteiro segura o bloco — e isso é uma decisão", level: 2 as const }, { id: 'uniao', text: "União", level: 2 as const }, { id: 'o-exemplo-completo', text: "O exemplo completo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Ponteiros"}
      description={"Aritmética por elemento, cast, distância — e as duas formas de um ponteiro não valer nada."}
      href={"/docs/estruturas/ponteiros"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
