/**
 * Marca do DataForge — uma bigorna.
 *
 * "Forge" é o que a linguagem faz: recebe dado bruto e o molda. A bigorna
 * é a superfície onde isso acontece, e tem uma silhueta que sobrevive a
 * 16px — o teste que separa um logo de um desenho.
 *
 * O caminho é único e sólido, sem traço nem gradiente: assim a marca
 * funciona em qualquer fundo, em uma cor só, e não some quando reduzida.
 */

/** O caminho da bigorna, num viewBox 64×64. Fonte única para todos os usos. */
export const CAMINHO_MARCA =
  'M8 14h48a2 2 0 011.6 3.2L50 25a3 3 0 01-2.4 1.2H41v9.4a4 4 0 001 2.6' +
  'l6.5 7.6A3 3 0 0146.2 51H17.8a3 3 0 01-2.3-5l6.5-7.7a4 4 0 001-2.6V26.2' +
  'h-6.6a3 3 0 01-2.4-1.2L6.4 17.2A2 2 0 018 14z';

export function Logo({
  size = 34,
  className = '',
  cor,
}: {
  size?: number;
  className?: string;
  /** Sobrepõe a cor; por padrão segue o acento do tema. */
  cor?: string;
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      className={className}
      role="img"
      aria-label="DataForge"
    >
      <path d={CAMINHO_MARCA} fill={cor ?? 'rgb(var(--accent))'} />
    </svg>
  );
}

/** A marca com o nome ao lado — para cabeçalho e rodapé. */
export function LogoCompleto({
  size = 30,
  className = '',
}: {
  size?: number;
  className?: string;
}) {
  return (
    <span className={`inline-flex items-center gap-2.5 ${className}`}>
      <Logo size={size} />
      <span
        className="font-extrabold tracking-tight"
        style={{ fontSize: size * 0.58 }}
      >
        DataForge
      </span>
    </span>
  );
}
