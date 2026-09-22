// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Organizar um projeto grande",
  description: "O que muda quando o projeto passa de duzentos arquivos — e as quatro decisões que decidem se ele continua navegável.",
};

const blocos: Bloco[] = [
  {"p": "Num arquivo de quarenta linhas, qualquer organização funciona. O que segue é o que passa a importar quando a maioria das chamadas atravessa módulo."},
  {"h2": "Por assunto, e não por tipo"},
  {"table": {"head": ["Por tipo (não)", "Por assunto (sim)"], "rows": [["`modelos/`, `servicos/`, `rotas/`", "`pedidos/`, `clientes/`, `estoque/`"], ["mudar uma regra toca três pastas", "mudar uma regra toca uma pasta"], ["a fronteira do domínio não aparece", "a pasta **é** a fronteira"], ["`modelos/` com quarenta arquivos", "cada pasta cabe na tela"]]}},
  { code: `src/
  pedidos/
    modelo.df        record Pedido, e as regras dele
    repositorio.df   como ele e guardado
    rotas.df         como ele e exposto
    pedidos_test.df
  clientes/
    ...
  compartilhado/
    tipos.df         o que MESMO e de todos`, lang: 'text' },
  {"callout": {"tipo": "atencao", "titulo": "`compartilhado/` é onde o acoplamento se esconde", "texto": "Toda pasta assim começa com três tipos e termina com quarenta — e a partir daí tudo depende de tudo, sem que nenhuma dependência pareça errada individualmente. A regra que segura: um tipo só entra ali quando **três** assuntos diferentes já o usam. Com dois, ele mora no que o criou, e o outro adota de lá."}},
  {"h2": "O ciclo de import é erro, e não estilo"},
  {"p": "Ele estourava só em execução, no primeiro `adopt`, e o `check` passava limpo num projeto que não sobe. Hoje o `check` acusa — e a mensagem mostra a **cadeia inteira**, porque um ciclo de quatro arquivos é impossível de quebrar sem saber por onde ele passa."},
  { code: `dataforge check src/          # acusa o ciclo, com a cadeia
dataforge deps                # o grafo de imports
dataforge deps --ciclos       # so os ciclos`, lang: 'bash' },
  {"h2": "O que medir num projeto grande"},
  {"table": {"head": ["Comando", "O que ele responde"], "rows": [["`dataforge stats`", "as ações e blueprints, o arquivo e a ação mais longos"], ["`dataforge oop`", "acoplamento e coesão; os cheiros com o princípio SOLID"], ["`dataforge deps`", "quem depende de quem, e os ciclos"], ["`dataforge big-o`", "a classe de complexidade de cada ação"], ["`dataforge test --cobertura`", "o que nenhum teste toca — e um arquivo sem teste aparece com **0%**, em vez de sumir"]]}},
  {"callout": {"tipo": "dica", "titulo": "O cache de árvores é o que torna isso rápido", "texto": "Duzentos arquivos importando três vizinhos cada levariam o `check` de 0,7 s a mais de um minuto sem cache. Medido: a fase de parse de 269 arquivos caiu de **258,7 ms para 17,9 ms**, e o `check` de `exercicios/` de 0,918 s para 0,524 s. A chave carrega caminho, `mtime_ns`, tamanho e um resumo do lexer, do parser e da AST — um cache que devolve a árvore errada é pior que nenhum."}},
  {"p": "Continue em [O cache de árvores](/docs/cli/cache) e [Diagnóstico](/docs/modulos/diagnostico)."},
];

const headings = [{ id: 'por-assunto-e-nao-por-tipo', text: "Por assunto, e não por tipo", level: 2 as const }, { id: 'o-ciclo-de-import-e-erro-e-nao-estilo', text: "O ciclo de import é erro, e não estilo", level: 2 as const }, { id: 'o-que-medir-num-projeto-grande', text: "O que medir num projeto grande", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Organizar um projeto grande"}
      description={"O que muda quando o projeto passa de duzentos arquivos — e as quatro decisões que decidem se ele continua navegável."}
      href={"/docs/modulos/organizar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
