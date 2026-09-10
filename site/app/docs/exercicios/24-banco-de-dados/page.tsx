import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "24 · Banco de dados",
  description: "8 exercícios: Forge: conexão, consultas, transações e ORM.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 24`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["201", "**Conectar e consultar**", "abra um banco, crie uma tabela e leia de volta."], ["202", "**Construtor de consultas**", "monte consultas encadeando chamadas, sem escrever SQL."], ["203", "**Injecao de SQL, e por que ela nao acontece aqui**", "tente derrubar uma tabela por um campo de busca."], ["204", "**Transacoes**", "transfira saldo entre contas, e garanta que nao suma dinheiro."], ["205", "**Modelos e validacao**", "declare um modelo, e deixe que ele recuse dado invalido."], ["206", "**Relacoes, e o problema do N+1**", "carregue os pedidos de cem usuarios em duas consultas."], ["207", "**Migracoes**", "evolua o esquema sem perder o que ja esta gravado."], ["208", "**Pool de conexoes**", "reaproveite conexoes, e garanta que elas voltem."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/24-banco-de-dados/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/24-banco-de-dados/201_conectar.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"24 · Banco de dados"}
      description={"8 exercícios: Forge: conexão, consultas, transações e ORM."}
      href={"/docs/exercicios/24-banco-de-dados"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
