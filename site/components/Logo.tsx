export function Logo({ size = 34 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 48 48" fill="none" aria-hidden="true">
      <defs>
        <linearGradient id="df-g" x1="8" y1="6" x2="40" y2="42" gradientUnits="userSpaceOnUse">
          <stop stopColor="rgb(var(--accent-soft))" />
          <stop offset="1" stopColor="rgb(var(--accent))" />
        </linearGradient>
      </defs>
      {/* Bigorna estilizada: "forge" — o D é formado pelo vazado */}
      <path
        d="M10 9h16.5c8.2 0 13.5 5.6 13.5 15S34.7 39 26.5 39H10V9Zm7.5 6.6v16.8h8.4c4.4 0 7-3.1 7-8.4s-2.6-8.4-7-8.4h-8.4Z"
        fill="url(#df-g)"
      />
      <path d="M6 20.5h6.5v2.8H6zM6 26h6.5v2.8H6z" fill="rgb(var(--accent))" opacity=".55" />
    </svg>
  );
}
