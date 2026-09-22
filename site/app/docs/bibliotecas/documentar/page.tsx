// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Documentar uma biblioteca",
  description: "dataforge doc, o exemplo que roda — e a única trava que impede a documentação de envelhecer.",
};

const blocos: Bloco[] = [
  {"p": "Documentação apodrece calada: o código muda, o texto fica, e ninguém descobre até alguém seguir a instrução e falhar. A defesa é uma só — **o exemplo tem de rodar**."},
  { code: `// ~/ Converte reais para centavos, sem passar por float.
// ~/
// ~/   Dinheiro.centavos("19,99")   ->   1999
// ~/
// ~/ Levanta FalhaDeFormato quando o texto nao e um valor.
action centavos(texto):
    limpo := texto.replace(".", "").replace(",", "")
    yield int(limpo)

assert centavos("19,99") is 1999
assert centavos("1.234,50") is 123450`, lang: 'df' },
  { code: `dataforge doc src/ --out=doc/API.md     # o Markdown, a partir dos comentarios
dataforge doc src/ --formato=json       # para gerar um site`, lang: 'bash' },
  {"h2": "A trava: extrair e executar"},
  {"p": "É o que este repositório faz com a própria documentação — 67 páginas geradas, e **todo bloco marcado como DataForge é extraído e executado** antes de a página existir. Nenhuma promessa da documentação sobrevive a uma mudança que a contradiga."},
  { code: `# no CI da sua biblioteca
dataforge check .          # o que nem chega a rodar
dataforge test .           # os testes
python3 scripts/rodar_exemplos_da_doc.py   # cada bloco do README`, lang: 'bash' },
  {"callout": {"tipo": "atencao", "titulo": "Um número escrito à mão envelhece sem ninguém ver", "texto": "Uma página desta documentação anunciava *“Funções (28)”* onde havia **44** — e a contagem estava no **título** da seção, que é o que se lê antes da lista. A descrição de um pacote `.deb` dizia *“38 módulos”* quando eram 39. A correção não é conferir de novo: é a contagem sair do próprio módulo, por `inspect`."}},
  {"h2": "O README é a primeira página"},
  {"table": {"head": ["Tem de responder", "Em quantas linhas"], "rows": [["o que esta biblioteca faz", "1"], ["como instalar", "1 comando"], ["o menor exemplo **completo** que funciona", "até 15 linhas"], ["o que ela **não** faz", "3 a 5 linhas"], ["onde está o resto", "1 link"]]}},
  {"callout": {"tipo": "dica", "titulo": "Diga o que ela não faz", "texto": "É a seção que mais economiza tempo de quem lê, e a que quase ninguém escreve. Uma biblioteca de datas que diz logo *“não trata fuso horário”* poupa meia hora a cada pessoa que precisa disso — e evita uma issue por mês."}},
  {"p": "Continue em [dataforge doc](/docs/cli/doc) e [Testes de biblioteca](/docs/bibliotecas/testes)."},
];

const headings = [{ id: 'a-trava-extrair-e-executar', text: "A trava: extrair e executar", level: 2 as const }, { id: 'o-readme-e-a-primeira-pagina', text: "O README é a primeira página", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Documentar uma biblioteca"}
      description={"dataforge doc, o exemplo que roda — e a única trava que impede a documentação de envelhecer."}
      href={"/docs/bibliotecas/documentar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
