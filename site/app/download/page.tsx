import type { Metadata } from 'next';
import Link from 'next/link';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { CodeBlock } from '@/components/CodeBlock';
import dados from '@/lib/dados-gerados.json';

export const metadata: Metadata = {
  title: 'Download do DataForge',
  description:
    'Todas as formas de instalar: instalador gráfico do Windows, executável sem Python, pip, Docker, Arch Linux, Debian e Ubuntu.',
};

const VERSAO = '1.0.0';
const RELEASES = `https://github.com/estevam5s/DataForge/releases/latest/download`;

/** Um caminho de instalação. `pronto` diz se já dá para baixar hoje. */
type Forma = {
  id: string;
  titulo: string;
  para: string;
  comando?: string;
  arquivo?: string;
  tamanho?: string;
  nota?: string;
  pronto: boolean;
  recomendado?: boolean;
};

const FORMAS: { grupo: string; itens: Forma[] }[] = [
  {
    grupo: 'Windows',
    itens: [
      {
        id: 'win-setup',
        titulo: 'Instalador gráfico (.exe)',
        para: 'Quem quer clicar e usar. Não precisa de Python.',
        arquivo: `${RELEASES}/DataForge-${VERSAO}-windows-x64-setup.exe`,
        tamanho: '~13 MB',
        nota: 'Instala na sua pasta de usuário, acrescenta ao PATH e associa os arquivos .df. Não pede senha de administrador.',
        pronto: true,
        recomendado: true,
      },
      {
        id: 'win-ps',
        titulo: 'PowerShell, em um comando',
        para: 'Quem já vive no terminal.',
        comando: 'irm https://dataforge-lang.vercel.app/instalar.ps1 | iex',
        pronto: true,
      },
      {
        id: 'win-zip',
        titulo: 'Executável em .zip',
        para: 'Quem quer descompactar onde escolher, sem instalador.',
        arquivo: `${RELEASES}/dataforge-windows-x64.zip`,
        tamanho: '~12 MB',
        pronto: true,
      },
    ],
  },
  {
    grupo: 'macOS',
    itens: [
      {
        id: 'mac-sh',
        titulo: 'Um comando',
        para: 'Detecta Intel ou Apple Silicon sozinho.',
        comando: 'curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh',
        pronto: true,
        recomendado: true,
      },
      {
        id: 'mac-arm',
        titulo: 'Executável — Apple Silicon',
        para: 'M1, M2, M3, M4. Sem Python na máquina.',
        arquivo: `${RELEASES}/dataforge-macos-arm64.tar.gz`,
        tamanho: '~12 MB',
        pronto: true,
      },
      {
        id: 'mac-x64',
        titulo: 'Executável — Intel',
        para: 'Macs de 2020 ou anteriores.',
        arquivo: `${RELEASES}/dataforge-macos-x64.tar.gz`,
        tamanho: '~12 MB',
        pronto: true,
      },
    ],
  },
  {
    grupo: 'Linux',
    itens: [
      {
        id: 'linux-sh',
        titulo: 'Um comando',
        para: 'Qualquer distribuição, sem tocar no Python do sistema.',
        comando: 'curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh',
        pronto: true,
        recomendado: true,
      },
      {
        id: 'arch',
        titulo: 'Arch Linux e derivadas',
        para: 'Manjaro, EndeavourOS, CachyOS.',
        comando: 'yay -S dataforge   #  ou: paru -S dataforge',
        nota: 'O PKGBUILD está em packaging/arch/ do repositório. Enquanto o pacote não está no AUR, dá para construir dali: makepkg -si.',
        pronto: false,
      },
      {
        id: 'deb',
        titulo: 'Debian e Ubuntu (.deb)',
        para: 'Também Mint, Pop!_OS, Zorin.',
        arquivo: `${RELEASES}/dataforge_${VERSAO}_all.deb`,
        comando: 'sudo dpkg -i dataforge_1.0.0_all.deb',
        tamanho: '~2 KB',
        nota: 'O pacote é fino de propósito: ele chama o pip no postinst, em vez de repetir o que o pip já sabe fazer.',
        pronto: true,
      },
      {
        id: 'linux-bin',
        titulo: 'Executável (.tar.gz)',
        para: 'Qualquer distribuição, sem Python e sem gerenciador.',
        arquivo: `${RELEASES}/dataforge-linux-x64.tar.gz`,
        tamanho: '~12 MB',
        pronto: true,
      },
    ],
  },
  {
    grupo: 'Multiplataforma',
    itens: [
      {
        id: 'pip',
        titulo: 'pip',
        para: 'Quem já tem Python 3.10+ e quer a linguagem no ambiente dele.',
        comando: 'pip install dataforge-lang',
        nota: 'É o único caminho que deixa você usar a ponte para o Python com os seus próprios pacotes instalados.',
        pronto: true,
        recomendado: true,
      },
      {
        id: 'docker',
        titulo: 'Docker',
        para: 'Sem instalar nada na máquina.',
        comando: 'docker run --rm -it estevan5s/dataforge repl',
        nota: 'Imagem multi-estágio, usuário sem privilégio. Para rodar um arquivo seu: docker run --rm -v "$PWD:/app" estevan5s/dataforge run /app/main.df',
        pronto: false,
      },
      {
        id: 'fonte',
        titulo: 'Do código-fonte',
        para: 'Para contribuir, ou para ler o interpretador.',
        comando: 'git clone https://github.com/estevam5s/DataForge\ncd DataForge\npip install -e ".[dev]"',
        pronto: true,
      },
      {
        id: 'tar',
        titulo: 'Tarball do código',
        para: 'Sem git, sem GitHub.',
        arquivo: `/dist/dataforge-${VERSAO}.tar.gz`,
        tamanho: '~1,3 MB',
        nota: 'Com SHA-256 ao lado, em /dist/dataforge-1.0.0.tar.gz.sha256.',
        pronto: true,
      },
    ],
  },
];

function Etiqueta({ children, tom }: { children: string; tom: 'ok' | 'espera' }) {
  const cor =
    tom === 'ok'
      ? 'border-[color:var(--accent)]/40 text-accent'
      : 'border-[color:var(--border)] text-muted';
  return (
    <span className={`rounded-full border px-2 py-[2px] text-[11px] font-semibold ${cor}`}>
      {children}
    </span>
  );
}

function Cartao({ forma }: { forma: Forma }) {
  return (
    <div className="rounded-xl border border-[color:var(--border)] bg-[color:var(--surface)] p-5">
      <div className="flex flex-wrap items-center gap-2">
        <h3 className="text-[15px] font-bold text-strong">{forma.titulo}</h3>
        {forma.recomendado && <Etiqueta tom="ok">recomendado</Etiqueta>}
        {!forma.pronto && <Etiqueta tom="espera">na próxima versão</Etiqueta>}
        {forma.tamanho && (
          <span className="ml-auto text-[12px] text-muted">{forma.tamanho}</span>
        )}
      </div>

      <p className="mt-1 text-[13px] leading-[20px] text-muted">{forma.para}</p>

      {forma.comando && (
        <div className="mt-3">
          <CodeBlock code={forma.comando} lang="bash" />
        </div>
      )}

      {forma.arquivo && forma.pronto && (
        <a
          href={forma.arquivo}
          className="mt-3 inline-flex items-center gap-2 rounded-lg border border-[color:var(--accent)]/40 px-3 py-[6px] text-[13px] font-semibold text-accent transition hover:bg-[color:var(--accent)]/10"
        >
          Baixar
          <span aria-hidden>↓</span>
        </a>
      )}

      {forma.nota && (
        <p className="mt-3 text-[12px] leading-[19px] text-muted">{forma.nota}</p>
      )}
    </div>
  );
}

export default function Pagina() {
  const totalExercicios = Object.values(dados.exercicios).reduce(
    (soma, lista) => soma + lista.length,
    0,
  );

  return (
    <div className="page-glow min-h-screen">
      <Header />

      <main id="conteudo" className="mx-auto max-w-[860px] px-4 py-10 sm:py-14">
        <p className="nav-label mb-2 text-accent">Download</p>
        <h1 className="text-[32px] font-extrabold leading-[1.15] tracking-tight text-strong sm:text-[38px]">
          DataForge {VERSAO}
        </h1>
        <p className="mt-3 max-w-[640px] text-[16px] leading-[26px] text-muted">
          Todas as formas de instalar, em um lugar. Se você só quer experimentar,
          o{' '}
          <Link href="/instalar" className="text-accent underline-offset-2 hover:underline">
            assistente de instalação
          </Link>{' '}
          detecta o seu sistema e monta o comando.
        </p>

        <div className="mt-6 rounded-xl border border-[color:var(--border)] bg-[color:var(--surface)] p-4">
          <p className="text-[13px] leading-[21px] text-muted">
            <strong className="text-strong">Qual escolher.</strong> Se você{' '}
            <strong className="text-strong">usa</strong> a linguagem e não mexe em
            Python, pegue o executável ou o instalador — eles trazem o Python
            dentro. Se você <strong className="text-strong">já programa em Python</strong> e
            quer usar os seus pacotes pela{' '}
            <Link href="/docs/tecnicas/ponte" className="text-accent underline-offset-2 hover:underline">
              ponte
            </Link>
            , use o <code className="text-accent">pip</code>: é o único caminho em
            que o <code className="text-accent">adopt Python.numpy</code> enxerga o
            que você já tem instalado.
          </p>
        </div>

        {FORMAS.map((secao) => (
          <section key={secao.grupo} className="mt-10">
            <h2 className="text-[20px] font-bold tracking-tight text-strong">
              {secao.grupo}
            </h2>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              {secao.itens.map((forma) => (
                <Cartao key={forma.id} forma={forma} />
              ))}
            </div>
          </section>
        ))}

        <section className="mt-12 rounded-xl border border-[color:var(--border)] bg-[color:var(--surface)] p-5">
          <h2 className="text-[16px] font-bold text-strong">Conferir o que você baixou</h2>
          <p className="mt-2 text-[13px] leading-[21px] text-muted">
            Cada release traz um <code className="text-accent">SHA256SUMS.txt</code> com a
            soma de todos os arquivos. Vale conferir — um download pela metade
            existe, tem o nome certo, e não funciona.
          </p>
          <div className="mt-3">
            <CodeBlock
              code={`# Linux e macOS\nsha256sum -c SHA256SUMS.txt\n\n# Windows (PowerShell)\nGet-FileHash dataforge-windows-x64.zip -Algorithm SHA256`}
              lang="bash"
            />
          </div>
        </section>

        <section className="mt-8">
          <h2 className="text-[20px] font-bold tracking-tight text-strong">
            Depois de instalar
          </h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <Link
              href="/docs/primeiros-passos"
              className="rounded-xl border border-[color:var(--border)] bg-[color:var(--surface)] p-4 transition hover:border-[color:var(--accent)]/40"
            >
              <p className="text-[14px] font-bold text-strong">Primeiros passos</p>
              <p className="mt-1 text-[12px] leading-[19px] text-muted">
                Do <code>dataforge repl</code> ao primeiro programa.
              </p>
            </Link>
            <Link
              href="/docs/exercicios"
              className="rounded-xl border border-[color:var(--border)] bg-[color:var(--surface)] p-4 transition hover:border-[color:var(--accent)]/40"
            >
              <p className="text-[14px] font-bold text-strong">
                {totalExercicios} exercícios
              </p>
              <p className="mt-1 text-[12px] leading-[19px] text-muted">
                Cada um com <code>assert</code>, todos verificados.
              </p>
            </Link>
            <Link
              href="/docs/tecnicas/editor"
              className="rounded-xl border border-[color:var(--border)] bg-[color:var(--surface)] p-4 transition hover:border-[color:var(--accent)]/40"
            >
              <p className="text-[14px] font-bold text-strong">O editor</p>
              <p className="mt-1 text-[12px] leading-[19px] text-muted">
                <code>dataforge editor</code> instala a extensão do VS Code.
              </p>
            </Link>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
