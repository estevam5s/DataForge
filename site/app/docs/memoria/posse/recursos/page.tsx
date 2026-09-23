// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/posse_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O arquivo, o soquete e a conexão",
  description: "O que a posse protege num mundo com coletor — e o que ela não protege.",
};

const blocos: Bloco[] = [
  {"p": "A primeira coisa a dizer, porque ela evita a leitura errada de tudo o mais: **num mundo com coletor, a memória nunca esteve em risco**. O que `Arcane.Posse` protege é o **protocolo** de um recurso — soltar uma vez, não usar depois de soltar, não escrever no meio de uma leitura."},
  {"table": {"head": ["O problema", "Sem posse", "Com posse"], "rows": [["usar depois de fechar", "erro do sistema operacional, três camadas longe", "`PosseMovidaError`, na linha que usou"], ["fechar duas vezes", "erro, ou pior: fecha o descritor de outro", "`soltar` é idempotente"], ["esquecer de fechar", "o arquivo fica aberto até o processo morrer", "o escopo solta, e o `check` avisa"], ["dois donos do mesmo arquivo", "quem fecha primeiro estraga o outro", "há **um** dono, e mover é explícito"]]}},
  { code: `adopt Arcane.Posse as Posse

// O dono carrega o valor E o que fazer ao soltar.
fechados := []
arquivo := Posse.dono({"nome": "dados.csv"},
                      lambda v => fechados.append(v["nome"]),
                      "arquivo")

// Usar é sempre por dentro de uma ação: não há como guardar a
// referência crua e usá-la depois de soltar.
assert arquivo.usar(lambda v => v["nome"]) is "dados.csv"
assert arquivo.vivo() is yes

arquivo.soltar()
assert fechados is ["dados.csv"]
assert arquivo.solto() is yes

// E soltar de novo NÃO é erro.
assert arquivo.soltar() is no`, lang: 'df' },
  {"h2": "Por que `soltar` é idempotente"},
  {"p": "Um `close()` escrito no `defer` **e** no caminho de erro é a forma mais comum de fechar recurso — e se o segundo `soltar` levantasse, a disciplina atrapalharia em vez de ajudar. A regra: soltar é pedir um **estado final**, e nesse ponto já não importa se ele já estava lá."},
  {"h2": "Usar depois de soltar é erro, e o erro diz onde"},
  { code: `adopt Arcane.Posse as Posse

conexao := Posse.dono({"banco": "loja"})
conexao.soltar()

monitor:
    conexao.usar(lambda v => v["banco"])
    assert no
handle Error as e:
    out e.message`, lang: 'df' },
  {"h2": "O de fora solta o que possuía"},
  {"p": "Um dono que guarda outro dono precisa soltá-lo — é a *drop glue*. Sem isso, soltar o de fora deixaria o de dentro aberto, que é exatamente o vazamento que a peça existe para evitar:"},
  { code: `adopt Arcane.Posse as Posse

soltos := []

action abrir(nome):
    yield Posse.dono({"nome": nome}, lambda v => soltos.append(v["nome"]), nome)

// Um 'Escopo' guarda vários, e solta todos na ordem inversa da
// abertura — como a pilha de um bloco.
escopo := Posse.escopo()
escopo.guardar(abrir("conexao"))
escopo.guardar(abrir("transacao"))
escopo.guardar(abrir("arquivo"))
assert escopo.quantos() is 3

escopo.soltar()
assert soltos is ["arquivo", "transacao", "conexao"]
out soltos`, lang: 'df' },
  {"p": "A ordem inversa não é estética: a transação foi aberta **sobre** a conexão, e fechar a conexão primeiro deixaria a transação sem onde confirmar."},
  {"h2": "E o `defer`, que já existia"},
  {"table": {"head": ["", "`defer`", "`Posse`"], "rows": [["quando roda", "na saída da **ação**", "quando o dono é solto, ou o escopo fecha"], ["quem garante", "o interpretador", "quem escreveu"], ["protege de usar depois", "não", "**sim** — e é a diferença que importa"], ["atravessa fronteira", "não", "sim: o dono pode ser movido"], ["custo para quem não usa", "zero", "zero"]]}},
  {"p": "Os dois convivem, e o mais comum é usar `defer` para o caso simples e `Posse` quando o recurso **atravessa** — vai para dentro de uma estrutura, é devolvido por uma ação, ou tem mais de um candidato a dono."},
];

const headings = [{ id: 'por-que-soltar-e-idempotente', text: "Por que `soltar` é idempotente", level: 2 as const }, { id: 'usar-depois-de-soltar-e-erro-e-o-erro-diz-onde', text: "Usar depois de soltar é erro, e o erro diz onde", level: 2 as const }, { id: 'o-de-fora-solta-o-que-possuia', text: "O de fora solta o que possuía", level: 2 as const }, { id: 'e-o-defer-que-ja-existia', text: "E o `defer`, que já existia", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O arquivo, o soquete e a conexão"}
      description={"O que a posse protege num mundo com coletor — e o que ela não protege."}
      href={"/docs/memoria/posse/recursos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
