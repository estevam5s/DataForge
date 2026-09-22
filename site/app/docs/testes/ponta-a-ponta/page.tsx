// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/testes_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testes ponta a ponta",
  description: "O programa rodando como o usuário o roda — subprocesso, código de saída e o que só aparece com socket.",
};

const blocos: Bloco[] = [
  {"p": "O teste ponta a ponta executa o programa **como ele é executado**: `dataforge run`, argumentos, saída no terminal, código de saída. Ele é lento e diz pouco sobre onde está o defeito — e pega o que nenhum outro pega: o `main.df` que não liga as peças, a variável de ambiente que falta, o código de saída zero numa falha."},
  {"h2": "A CLI inteira, por subprocesso"},
  { code: `adopt Arcane.Crucible
adopt Arcane.IO as IO
adopt Arcane.OS as OS
adopt Arcane.Process as P

pasta := $"{OS.temp_dir()}/df-e2e-{randint(100000, 999999)}"
IO.mkdir(pasta)
programa := $"{pasta}/somar.df"
IO.write(programa, """adopt Arcane.OS as OS
args := OS.argv()
given len(args) is not 2:
    out "uso: somar A B"
    OS.exit(2)
out int(args[0]) + int(args[1])
""")

crucible "somar, de fora":
    trial "imprime a soma e sai com 0":
        r := P.run(["dataforge", "run", programa, "--", "2", "40"])
        expect r["code"] is 0
        expect r["stdout"].trim() is "42"

    trial "sem argumentos, sai com 2 e diz o uso":
        r := P.run(["dataforge", "run", programa])
        expect r["code"] is 2
        expect "uso" in r["stdout"]

r := Crucible.run()
IO.remove_tree(pasta)
assert r["falhou"] is 0`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Confira o código de saída", "texto": "É o que o CI lê. Uma CLI que imprime *“erro”* e sai com 0 passa em todo pipeline, e o deploy segue com o passo que falhou. O teste ponta a ponta é o único lugar onde isso é conferido."}},
  {"h2": "O que só aparece com socket"},
  {"p": "`Kiln.test` roda a rota **na mesma thread**, sem socket. Três classes de defeito ficam de fora e só aparecem subindo o servidor de verdade:"},
  {"table": {"head": ["Defeito", "Porque o `Kiln.test` não vê"], "rows": [["corrida entre pedidos", "tudo roda numa thread só — ver o aviso `escrita-concorrente`"], ["cookie que o navegador descarta", "`Kiln.test` não devolve cookies"], ["`--host=0.0.0.0` esquecido no contêiner", "não há rede"]]}},
  {"callout": {"tipo": "dica", "titulo": "Poucos, e sobre o caminho feliz", "texto": "Cada teste ponta a ponta custa segundos e quebra por motivos que não são o código (porta ocupada, disco cheio). Tenha um por fluxo que **tem** de funcionar — login, compra, exportação — e deixe as variações para os testes de baixo."}},
  {"p": "Continue em [A pirâmide](/docs/testes/piramide)."},
];

const headings = [{ id: 'a-cli-inteira-por-subprocesso', text: "A CLI inteira, por subprocesso", level: 2 as const }, { id: 'o-que-so-aparece-com-socket', text: "O que só aparece com socket", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Testes ponta a ponta"}
      description={"O programa rodando como o usuário o roda — subprocesso, código de saída e o que só aparece com socket."}
      href={"/docs/testes/ponta-a-ponta"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
