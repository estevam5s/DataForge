import type { Metadata } from 'next';
import Link from 'next/link';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { Assistente } from '@/components/instalar/Assistente';

export const metadata: Metadata = {
  title: 'Instalar o DataForge',
  description:
    'Um comando, e a linguagem fica pronta. macOS, Linux e Windows — o assistente detecta o seu sistema.',
};

export default function Pagina() {
  return (
    <div className="page-glow min-h-screen">
      <Header />

      <main id="conteudo" className="mx-auto max-w-[720px] px-4 py-10 sm:py-14">
        <p className="nav-label mb-2 text-accent">Instalação</p>
        <h1 className="text-[32px] font-extrabold leading-[1.15] tracking-tight text-strong sm:text-[38px]">
          Instalar o DataForge
        </h1>
        <p className="mt-3 text-[16px] leading-[26px] text-muted">
          Um comando, e a linguagem fica pronta. O instalador cria um ambiente
          próprio em uma pasta sua — não mexe no Python do sistema, e não pede
          senha de administrador.
        </p>

        <div className="mt-8">
          <Assistente />
        </div>

        <section className="mt-12">
          <h2 className="text-[20px] font-bold tracking-tight text-strong">
            Prefere ir direto?
          </h2>
          <p className="mt-1.5 text-[14px] leading-[22px] text-muted">
            O assistente monta o comando com as suas escolhas. Se as opções
            padrão servem, é uma linha:
          </p>

          <div className="mt-4 space-y-3">
            <Bloco
              titulo="macOS e Linux"
              comando="curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh"
            />
            <Bloco
              titulo="Windows (PowerShell)"
              comando="irm https://dataforge-lang.vercel.app/instalar.ps1 | iex"
            />
            <Bloco
              titulo="Com pip, num ambiente virtual seu"
              comando="pip install dataforge-lang"
            />
          </div>

          <div className="mt-5 rounded-xl border border-line bg-surface/50 p-4">
            <p className="text-[13.5px] font-semibold text-strong">
              Ler antes de executar
            </p>
            <p className="mt-1 text-[13px] leading-[21px] text-muted">
              Canalizar um script da internet direto para o <code>sh</code> pede
              confiança na origem — e desconfiar é razoável. Para conferir
              primeiro:
            </p>
            <pre className="mt-2.5 overflow-x-auto rounded-lg border border-line bg-base p-3 font-mono text-[12px] leading-[19px] text-strong">
{`curl -fsSL https://dataforge-lang.vercel.app/instalar.sh -o instalar.sh
less instalar.sh        # leia
sh instalar.sh`}
            </pre>
          </div>
        </section>

        <section className="mt-12">
          <h2 className="text-[20px] font-bold tracking-tight text-strong">
            Depois de instalar
          </h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <Card
              href="/docs/primeiros-passos"
              titulo="Primeiros passos"
              desc="a linguagem em vinte minutos, escrevendo"
            />
            <Card
              href="/docs/editor"
              titulo="Configurar o editor"
              desc="dataforge editor instala a extensão sozinho"
            />
            <Card
              href="/docs/exercicios"
              titulo="200 exercícios"
              desc="cada um roda e verifica o próprio resultado"
            />
            <Card
              href="/docs/instalacao"
              titulo="Guia completo"
              desc="requisitos, ambiente virtual e solução de problemas"
            />
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}

function Bloco({ titulo, comando }: { titulo: string; comando: string }) {
  return (
    <div className="rounded-xl border border-line bg-surface/50">
      <p className="border-b border-line/60 px-3.5 py-2 text-[12.5px] font-semibold text-muted">
        {titulo}
      </p>
      <pre className="overflow-x-auto px-3.5 py-3 font-mono text-[12.5px] text-strong">
        {comando}
      </pre>
    </div>
  );
}

function Card({
  href,
  titulo,
  desc,
}: {
  href: string;
  titulo: string;
  desc: string;
}) {
  return (
    <Link
      href={href}
      className="group rounded-xl border border-line bg-surface/50 p-4 transition-colors hover:border-accent/45 hover:bg-raised"
    >
      <p className="text-[14px] font-semibold text-strong transition-colors group-hover:text-accent">
        {titulo}
      </p>
      <p className="mt-1 text-[13px] leading-[20px] text-muted">{desc}</p>
    </Link>
  );
}
