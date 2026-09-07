/**
 * Terminal estático. As saídas vêm de execuções reais das ferramentas
 * do DataForge — nada aqui é ilustrativo.
 */
export type Linha = { t: string; c?: 'cmd' | 'erro' | 'aviso' | 'ok' | 'dim' | 'info' };

const cor: Record<string, string> = {
  cmd: 'text-white',
  erro: 'text-[#ff5c72]',
  aviso: 'text-[#e3b341]',
  ok: 'text-[#4ec9a4]',
  info: 'text-[#6cb6ff]',
  dim: 'text-white/40',
};

export function Terminal({ linhas, titulo }: { linhas: Linha[]; titulo: string }) {
  return (
    <div className="lp-card overflow-hidden rounded-[18px]">
      <div className="flex items-center gap-2 border-b border-[var(--lp-line)] px-4 py-3">
        <span className="h-[11px] w-[11px] rounded-full bg-[#ff5f57]" />
        <span className="h-[11px] w-[11px] rounded-full bg-[#febc2e]" />
        <span className="h-[11px] w-[11px] rounded-full bg-[#28c840]" />
        <span className="lp-mono ml-3 text-[11px] tracking-[1px] text-white/40">{titulo}</span>
      </div>
      <div className="overflow-x-auto px-4 py-4 sm:px-6 sm:py-5">
        <pre className="lp-mono text-[12px] leading-[21px] sm:text-[13px] sm:leading-[23px]">
          {linhas.map((l, i) => (
            <div key={i} className={cor[l.c ?? 'dim'] ?? 'text-white/70'}>
              {l.c === 'cmd' ? <span className="text-[var(--lp-warm)]">$ </span> : null}
              {l.t || ' '}
            </div>
          ))}
        </pre>
      </div>
    </div>
  );
}
