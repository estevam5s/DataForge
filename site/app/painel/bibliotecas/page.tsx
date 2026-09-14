'use client';

import { useEffect, useState } from 'react';
import { Cabecalho, Vazio } from '@/components/painel/Casca';
import { CodeBlock } from '@/components/CodeBlock';
import { useAuth } from '@/lib/supabase/auth';
import {
  bibliotecasPublicas, enviarBiblioteca, minhasBibliotecas,
  type Biblioteca,
} from '@/lib/supabase/comunidade';

const ESTADO: Record<Biblioteca['estado'], { rotulo: string; classe: string }> = {
  pendente: { rotulo: 'Em revisão', classe: 'border-line text-muted' },
  aprovada: { rotulo: 'No registro', classe: 'border-accent/50 text-accent' },
  recusada: { rotulo: 'Recusada', classe: 'border-line text-body' },
};

/** O nome é a chave pública do pacote: ele vira `dataforge add <nome>`. */
const NOME_VALIDO = /^[a-z][a-z0-9_-]{1,38}[a-z0-9]$/;
const SEMVER = /^[0-9]+\.[0-9]+\.[0-9]+([-+][0-9A-Za-z.-]+)?$/;
const SHA256 = /^[0-9a-f]{64}$/;

export default function PaginaBibliotecas() {
  const { usuario, carregando } = useAuth();

  const [nome, setNome] = useState('');
  const [versao, setVersao] = useState('1.0.0');
  const [descricao, setDescricao] = useState('');
  const [tarball, setTarball] = useState('');
  const [sha, setSha] = useState('');
  const [licenca, setLicenca] = useState('MIT');
  const [repositorio, setRepositorio] = useState('');
  const [documentacao, setDocumentacao] = useState('');
  const [palavras, setPalavras] = useState('');

  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [ok, setOk] = useState(false);
  const [minhas, setMinhas] = useState<Biblioteca[]>([]);
  const [publicas, setPublicas] = useState<Biblioteca[]>([]);

  useEffect(() => {
    bibliotecasPublicas().then((r) => setPublicas(r.dados));
  }, []);
  useEffect(() => {
    if (usuario) minhasBibliotecas(usuario.id).then((r) => setMinhas(r.dados));
  }, [usuario]);

  const recarregar = () => {
    if (usuario) minhasBibliotecas(usuario.id).then((r) => setMinhas(r.dados));
    bibliotecasPublicas().then((r) => setPublicas(r.dados));
  };

  // Conferido aqui E no banco. Aqui, para a mensagem aparecer enquanto
  // se digita; lá, porque quem manda o POST escolhe se executa isto.
  const nomeRuim = nome.length > 0 && !NOME_VALIDO.test(nome);
  const versaoRuim = versao.length > 0 && !SEMVER.test(versao);
  const shaRuim = sha.length > 0 && !SHA256.test(sha.toLowerCase());

  const completo =
    NOME_VALIDO.test(nome) && SEMVER.test(versao)
    && descricao.trim().length >= 10 && tarball.startsWith('https://')
    && SHA256.test(sha.toLowerCase());

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    setEnviando(true);
    const falha = await enviarBiblioteca({
      nome: nome.trim().toLowerCase(),
      versao: versao.trim(),
      descricao: descricao.trim(),
      tarball: tarball.trim(),
      sha256: sha.trim().toLowerCase(),
      licenca: licenca.trim() || 'MIT',
      repositorio: repositorio.trim(),
      documentacao: documentacao.trim(),
      palavras: palavras.split(',').map((p) => p.trim()).filter(Boolean),
    });
    setEnviando(false);
    if (falha) { setErro(falha); return; }
    setOk(true);
    recarregar();
  }

  if (carregando) {
    return <div className="h-40 animate-pulse rounded-xl border border-line bg-raised/25" />;
  }

  if (!usuario) {
    return (
      <>
        <Cabecalho titulo="Publicar uma biblioteca" />
        <Vazio
          titulo="Entre para publicar"
          texto="O pacote fica ligado à sua conta: o nome é de quem o publicou primeiro, e só essa pessoa manda versão nova dele."
        />
      </>
    );
  }

  return (
    <>
      <Cabecalho
        titulo="Publicar uma biblioteca"
        descricao="Mande um pacote seu para o registro. Depois de aprovado, qualquer pessoa o instala com dataforge add."
      />

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_330px]">
        <div className="space-y-8">
          {/* ── como empacotar ── */}
          <section className="rounded-xl border border-line px-5 py-4">
            <h2 className="text-[14px] font-semibold text-strong">
              Antes de enviar: empacote e publique o tarball
            </h2>
            <p className="mt-1.5 text-[13.5px] text-muted">
              O registro guarda o <em>endereço</em> do pacote e o hash dele — não
              o arquivo. Hospede o <code>.tar.gz</code> onde quiser (release do
              GitHub serve), e cole aqui o link e o sha256 que o{' '}
              <code>pack</code> imprime.
            </p>
            <div className="mt-3">
              <CodeBlock
                lang="bash"
                code={`cd minha-lib
dataforge pack                    # gera o .tar.gz e imprime o sha256
shasum -a 256 minha-lib-1.0.0.tar.gz`}
              />
            </div>
            <p className="mt-2.5 text-[12.5px] text-muted">
              O hash não é burocracia: é ele que faz o <code>dataforge add</code>{' '}
              recusar um tarball trocado no caminho.
            </p>
          </section>

          {/* ── o formulário ── */}
          <form onSubmit={enviar} className="space-y-5">
            <div className="grid gap-5 sm:grid-cols-2">
              <Campo
                id="nome" rotulo="Nome do pacote" valor={nome} mudou={setNome}
                obrigatorio placeholder="validador" fonte
                erro={nomeRuim ? 'Minúsculas, dígitos, hífen e _ — começando por letra.' : ''}
                ajuda={`Vira: dataforge add ${nome || 'nome'}`}
              />
              <Campo
                id="versao" rotulo="Versão" valor={versao} mudou={setVersao}
                obrigatorio placeholder="1.0.0" fonte
                erro={versaoRuim ? 'Semver: 1.0.0, 2.1.3, 1.0.0-beta.1.' : ''}
                ajuda="O resolvedor compara estes três números."
              />
            </div>

            <Campo
              id="descricao" rotulo="O que ela faz" valor={descricao}
              mudou={setDescricao} obrigatorio area
              placeholder="Uma frase. Aparece na busca e no dataforge search."
              ajuda={descricao.trim().length > 0 && descricao.trim().length < 10
                ? 'Pelo menos dez caracteres.'
                : 'Entre 10 e 300 caracteres.'}
            />

            <Campo
              id="tarball" rotulo="Endereço do .tar.gz" valor={tarball}
              mudou={setTarball} obrigatorio fonte
              placeholder="https://github.com/voce/minha-lib/releases/download/v1.0.0/minha-lib-1.0.0.tar.gz"
              erro={tarball.length > 0 && !tarball.startsWith('https://')
                ? 'Só https. Um link http num instalador é um ataque de rede esperando acontecer.'
                : ''}
            />

            <Campo
              id="sha" rotulo="sha256 do arquivo" valor={sha} mudou={setSha}
              obrigatorio fonte placeholder="64 caracteres hexadecimais"
              erro={shaRuim ? 'São 64 caracteres de 0-9 e a-f.' : ''}
            />

            <div className="grid gap-5 sm:grid-cols-2">
              <Campo id="licenca" rotulo="Licença" valor={licenca} mudou={setLicenca}
                     placeholder="MIT" />
              <Campo id="palavras" rotulo="Palavras-chave" valor={palavras}
                     mudou={setPalavras} placeholder="cpf, validação, formulário"
                     ajuda="Separadas por vírgula. É por elas que o search acha." />
            </div>

            <div className="grid gap-5 sm:grid-cols-2">
              <Campo id="repo" rotulo="Repositório" valor={repositorio}
                     mudou={setRepositorio} fonte placeholder="https://github.com/voce/minha-lib" />
              <Campo id="doc" rotulo="Documentação" valor={documentacao}
                     mudou={setDocumentacao} fonte placeholder="https://…" />
            </div>

            {erro && (
              <p role="alert" className="rounded-lg border border-accent/40 bg-accent/8
                                         px-4 py-2.5 text-[13.5px] text-body">
                {erro}
              </p>
            )}

            {ok && !erro && (
              <p role="status" className="rounded-lg border border-line bg-raised/40
                                          px-4 py-2.5 text-[13.5px] text-body">
                Enviada para revisão. Um pacote entra no registro depois que alguém
                o revisa — o <code>dataforge add</code> baixa e executa o que está
                lá, e aprovar sozinho tornaria isso um canal de distribuição de código.
              </p>
            )}

            <button
              type="submit"
              disabled={enviando || !completo}
              className="rounded-lg bg-accent px-5 py-2.5 text-[14px] font-semibold
                         text-white transition-opacity disabled:opacity-40"
            >
              {enviando ? 'Enviando…' : 'Enviar para revisão'}
            </button>
          </form>
        </div>

        {/* ── as minhas, e o registro ── */}
        <aside className="space-y-8">
          <section>
            <h2 className="mb-3 text-[13px] font-semibold uppercase tracking-wide text-muted">
              As suas
            </h2>
            {minhas.length === 0 ? (
              <p className="rounded-xl border border-dashed border-line px-4 py-8
                            text-center text-[13.5px] text-muted">
                Nenhuma ainda.
              </p>
            ) : (
              <ul className="space-y-2.5">
                {minhas.map((b) => (
                  <li key={b.id} className="rounded-xl border border-line px-4 py-3">
                    <div className="flex items-baseline justify-between gap-2">
                      <code className="text-[13.5px] font-semibold text-strong">
                        {b.nome}
                      </code>
                      <span className={`shrink-0 rounded border px-1.5 py-0.5
                                        text-[11px] ${ESTADO[b.estado].classe}`}>
                        {ESTADO[b.estado].rotulo}
                      </span>
                    </div>
                    <p className="mt-1 text-[12.5px] text-muted">
                      {b.versao} · {b.downloads} download{b.downloads === 1 ? '' : 's'}
                    </p>
                    {b.estado === 'recusada' && b.motivo && (
                      <p className="mt-2 border-l-2 border-line pl-2.5 text-[12.5px] text-body">
                        {b.motivo}
                      </p>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section>
            <h2 className="mb-3 text-[13px] font-semibold uppercase tracking-wide text-muted">
              No registro
            </h2>
            {publicas.length === 0 ? (
              <p className="rounded-xl border border-dashed border-line px-4 py-8
                            text-center text-[13.5px] text-muted">
                O registro da comunidade ainda está vazio. A primeira pode ser a sua.
              </p>
            ) : (
              <ul className="space-y-2">
                {publicas.slice(0, 12).map((b) => (
                  <li key={b.id} className="rounded-lg border border-line px-3.5 py-2.5">
                    <code className="text-[13px] font-semibold text-strong">{b.nome}</code>
                    <span className="ml-2 text-[12px] text-muted">{b.versao}</span>
                    <p className="mt-0.5 line-clamp-2 text-[12.5px] text-muted">
                      {b.descricao}
                    </p>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </aside>
      </div>
    </>
  );
}

function Campo({
  id, rotulo, valor, mudou, placeholder, ajuda, erro,
  obrigatorio, area, fonte,
}: {
  id: string; rotulo: string; valor: string; mudou: (v: string) => void;
  placeholder?: string; ajuda?: string; erro?: string;
  obrigatorio?: boolean; area?: boolean; fonte?: boolean;
}) {
  const base = `w-full rounded-lg border bg-transparent px-3 py-2 text-[14px]
                text-strong outline-none placeholder:text-muted
                ${fonte ? 'font-mono text-[13px]' : ''}
                ${erro ? 'border-accent/60' : 'border-line focus:border-accent/60'}`;
  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-[13px] font-semibold text-strong">
        {rotulo}
        {!obrigatorio && <span className="ml-1 font-normal text-muted">(opcional)</span>}
      </label>
      {area ? (
        <textarea
          id={id} value={valor} onChange={(e) => mudou(e.target.value)}
          required={obrigatorio} rows={3} maxLength={300}
          placeholder={placeholder} className={`${base} resize-y`}
          aria-describedby={`${id}-ajuda`}
        />
      ) : (
        <input
          id={id} value={valor} onChange={(e) => mudou(e.target.value)}
          required={obrigatorio} placeholder={placeholder} className={base}
          aria-describedby={`${id}-ajuda`}
          aria-invalid={erro ? true : undefined}
        />
      )}
      {(erro || ajuda) && (
        <p
          id={`${id}-ajuda`}
          role={erro ? 'alert' : undefined}
          className={`mt-1.5 text-[12.5px] ${erro ? 'text-accent' : 'text-muted'}`}
        >
          {erro || ajuda}
        </p>
      )}
    </div>
  );
}
