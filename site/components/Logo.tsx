/**
 * Marca do DataForge — a pantera.
 *
 * O caminho vem de `lib/marca.ts`, vetorizado de `logo.png` por
 * `tools/vetorizar_logo.py`. Não edite o caminho aqui: rode o gerador.
 *
 * É um caminho só, com fill-rule evenodd — os vãos (olho, boca, garras)
 * são subcaminhos no sentido inverso. Sem traço e sem gradiente, para a
 * marca funcionar em qualquer fundo, numa cor só, e não sumir aos 16px.
 */

import { CAMINHO_MARCA, VIEWBOX_MARCA } from '@/lib/marca';

export { CAMINHO_MARCA };

export function Logo({
  size = 40,
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
      viewBox={VIEWBOX_MARCA}
      className={className}
      role="img"
      aria-label="DataForge"
    >
      <path
        d={CAMINHO_MARCA}
        fillRule="evenodd"
        fill={cor ?? 'rgb(var(--accent))'}
      />
    </svg>
  );
}

/**
 * A marca com o nome ao lado.
 *
 * O cabeçalho usa só a `Logo` — uma marca reconhecível não precisa
 * repetir o próprio nome ao lado dela. Isto fica para onde o contexto
 * não deixa claro de quem é o site: rodapé, e-mail, README.
 */
export function LogoCompleto({
  size = 32,
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
        style={{ fontSize: size * 0.55 }}
      >
        DataForge
      </span>
    </span>
  );
}
