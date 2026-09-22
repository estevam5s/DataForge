// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/cli_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "dataforge new e info",
  description: "Os modelos de projeto — e por que todo projeto criado passa nos próprios testes.",
};

const blocos: Bloco[] = [
  {"p": "`dataforge new` cria um projeto a partir de um modelo. A promessa de todos é a mesma: o projeto criado **roda e passa nos próprios testes** antes de você mexer em qualquer coisa. Um esqueleto com `TODO` é apagado na primeira hora; um projeto que funciona é o ponto de partida."},
  { code: `dataforge new                    # escolhe na tela
dataforge new --list             # so os modelos
dataforge new api loja           # direto
cd loja && dataforge test tests/ # verde, antes de qualquer mudanca
dataforge info                   # o manifesto: nome, versao, entrada, dependencias`, lang: 'bash' },
  {"table": {"head": ["Modelo", "O que ele traz", "O tipo de projeto"], "rows": [["`cli`", "argumentos, tabela colorida, `--help`", "[CLI de anotações](/docs/projetos/cli-notas)"], ["`api`", "rotas, JSON, 404/405 e testes sem socket", "[API REST](/docs/projetos/api-rest)"], ["`web`", "páginas HTML, estáticos, escape automático", "[Site estático](/docs/projetos/site-estatico)"], ["`data`", "banco, estatística, exportação para Excel", "[ETL](/docs/projetos/etl)"], ["`lib`", "`relay`, testes e pronto para publicar", "[Biblioteca](/docs/projetos/biblioteca)"], ["`oop`", "blueprints, traits, propriedades, operadores", "[Estoque](/docs/projetos/estoque)"], ["`script`", "arquivos, JSON, datas, processos", "[Agendador](/docs/projetos/agendador)"], ["`painel`", "métricas, gráficos, filtros e testes", "[Painel](/docs/projetos/painel)"], ["`bot`", "comandos, botões, conversa e testes sem rede", "[Bot](/docs/projetos/bot-atendimento)"], ["`test`", "como se testa: asserts, erros, cobertura", "[TDD](/docs/testes/tdd)"]]}},
  {"h2": "A estrutura é sempre a mesma"},
  { code: `loja/
  forge.toml     nome, versao, entrada, dependencias, scripts
  README.md
  .gitignore     forge_modules/, .env, *.db
  src/           o codigo
  tests/         os testes — dataforge test tests/`, lang: 'text' },
  {"p": "Quem aprendeu um projeto sabe se achar em qualquer outro. E o `forge.toml` já fixa a versão da linguagem (`dataforge = \">=1.1\"`), que `dataforge run` **cobra** — ver [Versões](/docs/cli/versoes)."},
  {"p": "Continue em [Os vinte e dois tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'a-estrutura-e-sempre-a-mesma', text: "A estrutura é sempre a mesma", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"dataforge new e info"}
      description={"Os modelos de projeto — e por que todo projeto criado passa nos próprios testes."}
      href={"/docs/cli/new"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
