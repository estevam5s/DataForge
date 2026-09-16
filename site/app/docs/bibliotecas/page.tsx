// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Escrever uma biblioteca",
  description: "Do primeiro arquivo ao pacote publicado — estrutura, contrato, versão, testes e registro.",
};

const blocos: Bloco[] = [
  {"p": "Uma biblioteca é um projeto com uma diferença que muda tudo: **outra pessoa vai depender dela**. O que num programa é detalhe interno — o nome de uma ação, a ordem de um parâmetro, o formato de um retorno — vira promessa."},
  {"p": "Esta seção é o caminho inteiro, na ordem em que ele acontece."},
  {"cards": [{"href": "/docs/bibliotecas/estrutura", "title": "1. Estrutura", "desc": "o esqueleto, o forge.toml e onde cada coisa mora"}, {"href": "/docs/bibliotecas/contrato", "title": "2. O contrato", "desc": "o que o relay promete, e o que quebra quem depende de você"}, {"href": "/docs/bibliotecas/testes", "title": "3. Testes de biblioteca", "desc": "testar pelo nome público, e não pelo caminho interno"}, {"href": "/docs/bibliotecas/versao", "title": "4. Versão", "desc": "semver, o que cada número significa, e como o resolvedor lê"}, {"href": "/docs/bibliotecas/publicar", "title": "5. Publicar", "desc": "empacotar, o registro estático, e o que vai dentro do tarball"}, {"href": "/docs/bibliotecas/manutencao", "title": "6. Manter", "desc": "depreciar sem quebrar, e o que fazer numa mudança incompatível"}]},
  {"h2": "Em trinta segundos"},
  { code: `dataforge init minha-lib && cd minha-lib

# escreva src/main.df, com 'relay' no fim
dataforge check .
dataforge test tests/

dataforge pack                      # gera dist/minha-lib-1.0.0.tar.gz
dataforge publish --registry=../registro
`, lang: 'bash' },
  {"h2": "As quatro bibliotecas deste repositório"},
  {"p": "Elas existem como referência de quem for escrever a sua — e como prova de que o gerenciador funciona ponta a ponta:"},
  {"table": {"head": ["Pacote", "O que faz"], "rows": [["[`validador`](/docs/pacotes/validador)", "CPF, CNPJ, e-mail, CEP e esquema de formulário"], ["[`tabela`](/docs/pacotes/tabela)", "saída tabular para terminal"], ["[`datas`](/docs/pacotes/datas)", "datas em pt-BR, com feriados"], ["[`cofre`](/docs/pacotes/cofre)", "configuração em camadas"]]}},
  {"p": "As quatro somam 46 testes, e o código de cada uma é curto o bastante para ser lido inteiro."},
  {"h2": "O que distingue uma biblioteca de um programa"},
  {"table": {"head": ["", "Programa", "Biblioteca"], "rows": [["quem decide a entrada", "você", "**quem usa**"], ["renomear uma ação", "um `grep` e pronto", "**quebra** todo mundo"], ["erro sem tratamento", "aparece para você", "aparece na aplicação de outra pessoa"], ["efeito no topo do arquivo", "aceitável", "**inaceitável** — roda no `adopt` de quem importa"], ["dependência nova", "sua escolha", "vira dependência de todos os seus usuários"], ["o teste", "prova que funciona", "**é** a documentação do contrato"]]}},
  {"callout": {"tipo": "atencao", "titulo": "A regra que resume as seis linhas", "texto": "Numa biblioteca, o mais caro não é escrever — é **mudar de ideia depois**. Tudo nesta seção existe para adiar o menos possível a hora de decidir o que é público."}},
];

const headings = [{ id: 'em-trinta-segundos', text: "Em trinta segundos", level: 2 as const }, { id: 'as-quatro-bibliotecas-deste-repositorio', text: "As quatro bibliotecas deste repositório", level: 2 as const }, { id: 'o-que-distingue-uma-biblioteca-de-um-programa', text: "O que distingue uma biblioteca de um programa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Escrever uma biblioteca"}
      description={"Do primeiro arquivo ao pacote publicado — estrutura, contrato, versão, testes e registro."}
      href={"/docs/bibliotecas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
