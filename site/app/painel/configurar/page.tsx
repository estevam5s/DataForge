'use client';

import { Cabecalho } from '@/components/painel/Casca';
import { CodeBlock } from '@/components/CodeBlock';
import { configurado, URL_SUPABASE } from '@/lib/supabase/cliente';

export default function Configurar() {
  return (
    <>
      <Cabecalho
        titulo="Ligar o Supabase"
        descricao="Quatro passos. O painel já está pronto do lado do código."
      />

      <div className={`mb-6 rounded-xl border p-4 text-[13.5px] ${
        configurado
          ? 'border-line bg-raised text-body'
          : 'border-accent/30 bg-accent/10 text-accent'}`}>
        {configurado
          ? <>Conectado a <span className="lp-mono">{URL_SUPABASE}</span>.</>
          : 'Ainda não configurado — o painel está em modo demonstração.'}
      </div>

      <ol className="space-y-8">
        <Passo n={1} titulo="Criar o projeto">
          <p className="text-[14px] leading-[23px] text-body">
            Em <a href="https://supabase.com/dashboard" target="_blank"
                  rel="noreferrer noopener" className="link-quiet underline">
            supabase.com/dashboard</a>, crie um projeto. Guarde a senha do banco
            que ele pedir — ela não aparece de novo.
          </p>
        </Passo>

        <Passo n={2} titulo="Aplicar o esquema">
          <p className="mb-3 text-[14px] leading-[23px] text-body">
            No <strong>SQL Editor</strong>, cole o conteúdo de{' '}
            <span className="lp-mono">site/supabase/esquema.sql</span> e execute.
            Ele cria as cinco tabelas, as políticas de RLS e os gatilhos.
          </p>
          <p className="text-[13.5px] text-muted">
            É idempotente: rodar duas vezes não quebra nada.
          </p>
        </Passo>

        <Passo n={3} titulo="Copiar as credenciais">
          <p className="mb-3 text-[14px] leading-[23px] text-body">
            Em <strong>Project Settings → API</strong>, copie a{' '}
            <em>Project URL</em> e a chave <em>anon public</em>. Crie o arquivo{' '}
            <span className="lp-mono">site/.env.local</span>:
          </p>
          <CodeBlock lang="bash" code={
`NEXT_PUBLIC_SUPABASE_URL=https://seu-projeto.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOi...`} />
          <div className="mt-4 rounded-lg border border-line bg-raised p-4">
            <p className="text-[13.5px] leading-[22px] text-body">
              <strong className="text-strong">A chave anon é pública</strong> —
              ela vai no bundle e o navegador a enxerga. É a RLS que protege os
              dados, não o segredo da chave.
            </p>
            <p className="mt-2 text-[13.5px] leading-[22px] text-body">
              A <span className="lp-mono">service_role</span> nunca deve entrar
              aqui: ela ignora RLS e daria acesso a tudo de qualquer navegador.
            </p>
          </div>
        </Passo>

        <Passo n={4} titulo="Configurar a autenticação">
          <p className="mb-3 text-[14px] leading-[23px] text-body">
            Em <strong>Authentication → Providers</strong>, deixe{' '}
            <em>Email</em> ligado. Em <strong>URL Configuration</strong>,
            acrescente o endereço do site em <em>Redirect URLs</em>:
          </p>
          <CodeBlock lang="bash" code={
`https://dataforge-lang.vercel.app/painel/
http://localhost:3000/painel/`} />
        </Passo>

        <Passo n={5} titulo="Publicar">
          <p className="mb-3 text-[14px] leading-[23px] text-body">
            Na Vercel, em <strong>Settings → Environment Variables</strong>,
            repita as duas variáveis. Depois:
          </p>
          <CodeBlock lang="bash" code="vercel deploy --prod" />
        </Passo>
      </ol>

      <div className="surface-card mt-10 rounded-xl p-6">
        <h2 className="font-semibold text-strong">O que o esquema cria</h2>
        <dl className="mt-4 space-y-3 text-[13.5px]">
          {[
            ['perfis', 'nome e bio de cada usuário; criado por gatilho no registro'],
            ['projetos', 'agrupam trechos; podem ser públicos'],
            ['trechos', 'código guardado, ligado a um projeto'],
            ['progresso', 'um registro por exercício concluído'],
            ['anotacoes', 'notas ligadas a uma página da documentação'],
          ].map(([nome, desc]) => (
            <div key={nome} className="flex flex-wrap gap-x-3">
              <dt className="lp-mono w-[92px] shrink-0 text-strong">{nome}</dt>
              <dd className="flex-1 text-muted">{desc}</dd>
            </div>
          ))}
        </dl>
        <p className="mt-4 text-[13px] text-muted">
          Todas com RLS ligada e negada por padrão. Progresso e anotações são
          privados; projetos e trechos seguem a marcação de público.
        </p>
      </div>
    </>
  );
}

function Passo({ n, titulo, children }: {
  n: number; titulo: string; children: React.ReactNode;
}) {
  return (
    <li className="flex gap-4">
      <span className="flex h-7 w-7 shrink-0 items-center justify-center
                       rounded-full bg-accent/12 text-[13px] font-bold text-accent">
        {n}
      </span>
      <div className="min-w-0 flex-1">
        <h2 className="mb-2 font-semibold text-strong">{titulo}</h2>
        {children}
      </div>
    </li>
  );
}
