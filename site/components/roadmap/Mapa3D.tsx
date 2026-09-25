'use client';

/**
 * O mapa em três dimensões da linguagem — Three.js.
 *
 * Três mapas sobre os MESMOS dados, e os dados são gerados:
 * `site/lib/roadmap-gerado.json` sai de `Arcane.Percurso.fases()` e de
 * `Arcane.Ecossistema.componentes()`, que `conferir()` cobra contra o
 * disco nas duas direções. Um mapa da arquitetura escrito à mão
 * envelhece no primeiro módulo novo — e envelhece **calado**, que é o
 * defeito que esta página existe para não ter.
 *
 * ─── Quatro decisões ────────────────────────────────────────
 *
 * 1. **O rótulo é HTML, e não geometria de texto.** `TextGeometry`
 *    pede um carregador de fonte, um arquivo de fonte e um `.json` de
 *    ~300 KB — e o texto sai sem hinting, ilegível abaixo de 14px.
 *    Os rótulos aqui são `<div>` posicionados pela projeção da câmera
 *    a cada quadro: eles ficam nítidos, herdam o tema e o leitor de
 *    tela os lê.
 *
 * 2. **A posição de cada nó é DETERMINÍSTICA.** Nada de `Math.random`:
 *    uma constelação que muda de forma a cada recarregamento não é um
 *    mapa, é um protetor de tela. A posição sai do índice do item e do
 *    grupo dele, então o mesmo componente fica sempre no mesmo lugar.
 *
 * 3. **`prefers-reduced-motion` para a rotação, e não o mapa.** Quem
 *    pediu menos movimento não pediu menos informação: a cena é
 *    desenhada uma vez, na posição em que se lê melhor, e continua
 *    clicável.
 *
 * 4. **Sem WebGL, a lista aparece.** Uma máquina antiga, um navegador
 *    com aceleração desligada, ou um erro ao buscar o Three: a mesma
 *    informação sai como lista navegável pelo teclado. Um mapa que
 *    vira um retângulo vazio some com o conteúdo junto.
 */

import { useEffect, useMemo, useRef, useState } from 'react';

export type Modo = 'percurso' | 'ecossistema' | 'biblioteca';

export type No = {
  id: string;
  rotulo: string;
  grupo: string;
  estado?: string;
  detalhe: string;
  nota?: string;
  porque?: string;
  onde?: string[];
  href?: string;
  peso?: number;
};

type Posicionado = No & { x: number; y: number; z: number };

const CORES = {
  existe: 0x2fa96b,
  equivale: 0xd9992a,
  'nao-existe': 0x8a8a96,
  fase: 0xe5484d,
  modulo: 0x5b7cfa,
} as const;

const CSS_DO_ESTADO: Record<string, string> = {
  existe: 'text-[#2fa96b]',
  equivale: 'text-[#b8811f]',
  'nao-existe': 'text-muted',
};

const ROTULO_DO_ESTADO: Record<string, string> = {
  existe: 'existe',
  equivale: 'equivale',
  'nao-existe': 'não existe',
};

/* ═══════════════════════════════════════════════════════════════
   Onde cada nó fica — determinístico, sempre
   ═══════════════════════════════════════════════════════════════ */

function posicionar(nos: No[], modo: Modo): Posicionado[] {
  if (modo === 'percurso') {
    // Uma fita que desce: as dez fases em ordem, porque a ordem é o
    // assunto. Um anel faria a última encostar na primeira, e elas não
    // se tocam — `execucao` não volta para o `lexer`.
    const n = Math.max(nos.length - 1, 1);
    return nos.map((no, i) => {
      const t = i / n;
      return {
        ...no,
        x: (t - 0.5) * 11,
        y: Math.sin(t * Math.PI) * 1.5 - 0.3,
        z: Math.cos(t * Math.PI * 1.35) * 2.2,
      };
    });
  }

  // Ecossistema e biblioteca: um anel por grupo, empilhados. O grupo
  // é o eixo vertical, e a posição dentro do anel é o índice — assim
  // dá para ler "este grupo está cheio, aquele tem três".
  const grupos: string[] = [];
  for (const no of nos) if (!grupos.includes(no.grupo)) grupos.push(no.grupo);

  const alturaTotal = Math.min(grupos.length * 1.05, 9);
  return nos.map((no) => {
    const g = grupos.indexOf(no.grupo);
    const doGrupo = nos.filter((o) => o.grupo === no.grupo);
    const i = doGrupo.indexOf(no);
    const total = Math.max(doGrupo.length, 1);

    const raio = 2.6 + Math.min(total, 12) * 0.22;
    const angulo = (i / total) * Math.PI * 2 + g * 0.6;
    const y = alturaTotal / 2 - (g / Math.max(grupos.length - 1, 1)) * alturaTotal;

    return {
      ...no,
      x: Math.cos(angulo) * raio,
      y,
      z: Math.sin(angulo) * raio,
    };
  });
}

function corDoNo(no: No, modo: Modo): number {
  if (modo === 'percurso') return CORES.fase;
  if (modo === 'biblioteca') return CORES.modulo;
  return CORES[(no.estado as keyof typeof CORES) ?? 'existe'] ?? CORES.existe;
}

/* ═══════════════════════════════════════════════════════════════
   O componente
   ═══════════════════════════════════════════════════════════════ */

export function Mapa3D({
  nos,
  modo,
  altura = 460,
}: {
  nos: No[];
  modo: Modo;
  altura?: number;
}) {
  const caixa = useRef<HTMLDivElement>(null);
  const [semWebGL, setSemWebGL] = useState(false);
  const [selecionado, setSelecionado] = useState<No | null>(null);
  const [rotulos, setRotulos] = useState<
    { id: string; rotulo: string; x: number; y: number; frente: boolean }[]
  >([]);

  const posicionados = useMemo(() => posicionar(nos, modo), [nos, modo]);

  // O nó selecionado é sempre um dos atuais: trocar de mapa com um nó
  // aberto deixaria um painel falando de algo que não está na tela.
  useEffect(() => {
    setSelecionado(null);
  }, [modo]);

  useEffect(() => {
    const elemento = caixa.current;
    if (!elemento) return;

    let vivo = true;
    let desmontar = () => {};

    (async () => {
      let THREE: typeof import('three');
      try {
        THREE = await import('three');
      } catch {
        if (vivo) setSemWebGL(true);
        return;
      }
      if (!vivo || !caixa.current) return;
      const saida = montar(THREE, caixa.current, posicionados, modo, {
        aoClicar: (no) => vivo && setSelecionado(no),
        aoProjetar: (lista) => vivo && setRotulos(lista),
      });
      if (!saida) {
        if (vivo) setSemWebGL(true);
        return;
      }
      desmontar = saida;
    })();

    return () => {
      vivo = false;
      desmontar();
    };
  }, [posicionados, modo]);

  if (semWebGL) {
    return <Lista nos={nos} modo={modo} />;
  }

  return (
    <div className="not-prose">
      <div className="overflow-hidden rounded-2xl border border-line bg-surface/40">
        <div className="relative w-full" style={{ height: altura }}>
          <div ref={caixa} className="absolute inset-0" />

          {/* Os rótulos, projetados a cada quadro. `pointer-events-none`
              para que o clique chegue ao canvas e ao raycaster. */}
          <div className="pointer-events-none absolute inset-0 overflow-hidden">
            {rotulos.map((r) => (
              <span
                key={r.id}
                className="absolute -translate-x-1/2 whitespace-nowrap rounded px-1 text-[10.5px] font-medium leading-[14px] tracking-tight"
                style={{
                  left: r.x,
                  top: r.y,
                  opacity: r.frente ? 0.92 : 0.28,
                  color: 'rgb(var(--strong))',
                  textShadow:
                    '0 1px 3px rgb(var(--base) / .92), 0 0 2px rgb(var(--base))',
                }}
              >
                {r.rotulo}
              </span>
            ))}
          </div>

          <p className="pointer-events-none absolute bottom-2 left-3 text-[11px] text-muted">
            arraste para girar · clique num ponto
          </p>
        </div>

        {/* A legenda de cor só existe onde a cor significa alguma coisa. */}
        {modo === 'ecossistema' && (
          <div className="flex flex-wrap gap-x-5 gap-y-1 border-t border-line/60 px-4 py-2.5 text-[12px] text-muted">
            {(['existe', 'equivale', 'nao-existe'] as const).map((e) => (
              <span key={e} className="inline-flex items-center gap-1.5">
                <span
                  className="inline-block h-2 w-2 rounded-full"
                  style={{ background: `#${CORES[e].toString(16).padStart(6, '0')}` }}
                  aria-hidden="true"
                />
                {ROTULO_DO_ESTADO[e]}
              </span>
            ))}
          </div>
        )}
      </div>

      <Detalhe no={selecionado} modo={modo} />
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   O painel do nó escolhido
   ═══════════════════════════════════════════════════════════════ */

function Detalhe({ no, modo }: { no: No | null; modo: Modo }) {
  if (!no) {
    return (
      <p className="mt-3 text-[13px] leading-[20px] text-muted">
        {modo === 'percurso'
          ? 'As dez fases por que passa um arquivo `.df`. A décima é medida em zero e marcada como não percorrida — executar é o que o programa faz, e um arquivo de verdade abre soquete e escreve em disco.'
          : modo === 'ecossistema'
            ? 'Os 41 componentes que um ecossistema de linguagem costuma ter, com o veredito de cada um conferido contra o disco. Clique num ponto para ver o que ele é, o que existe aqui no lugar dele, e por quê.'
            : 'Os 89 módulos da biblioteca, agrupados. Clique num ponto para abrir a referência dele.'}
      </p>
    );
  }

  return (
    <div className="mt-3 rounded-2xl border border-line bg-raised/40 p-4 sm:p-5">
      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <h3 className="text-[15px] font-semibold text-strong">{no.rotulo}</h3>
        {no.estado && (
          <span className={`text-[12px] font-medium ${CSS_DO_ESTADO[no.estado] ?? 'text-muted'}`}>
            {ROTULO_DO_ESTADO[no.estado] ?? no.estado}
          </span>
        )}
        <span className="text-[12px] text-muted">{no.grupo}</span>
      </div>

      <p className="mt-2 text-[13.5px] leading-[21px] text-body">{no.detalhe}</p>

      {no.nota && (
        <p className="mt-2 text-[13.5px] leading-[21px] text-body">
          <strong className="text-strong">Aqui:</strong> {no.nota}
        </p>
      )}

      {no.porque && (
        <p className="mt-2 text-[13.5px] leading-[21px] text-muted">
          <strong className="text-strong">Por quê:</strong> {no.porque}
        </p>
      )}

      {no.onde && no.onde.length > 0 && (
        <p className="mt-3 flex flex-wrap gap-1.5">
          {no.onde.map((caminho) => (
            <code
              key={caminho}
              className="rounded border border-line bg-surface px-1.5 py-0.5 text-[11.5px] text-muted"
            >
              {caminho}
            </code>
          ))}
        </p>
      )}

      {no.href && (
        <a
          href={no.href}
          className="mt-3 inline-block text-[13px] font-medium text-accent hover:underline"
        >
          Abrir a referência →
        </a>
      )}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Sem WebGL — a mesma informação, como lista
   ═══════════════════════════════════════════════════════════════ */

function Lista({ nos, modo }: { nos: No[]; modo: Modo }) {
  const grupos: string[] = [];
  for (const no of nos) if (!grupos.includes(no.grupo)) grupos.push(no.grupo);

  return (
    <div className="not-prose rounded-2xl border border-line bg-surface/40 p-4 sm:p-5">
      <p className="mb-4 text-[13px] text-muted">
        O mapa em três dimensões não pôde ser desenhado aqui. A mesma informação,
        em lista:
      </p>
      {grupos.map((g) => (
        <div key={g} className="mb-4 last:mb-0">
          <h4 className="mb-1.5 text-[13px] font-semibold text-strong">{g}</h4>
          <ul className="space-y-1">
            {nos
              .filter((n) => n.grupo === g)
              .map((n) => (
                <li key={n.id} className="text-[13px] leading-[20px] text-body">
                  <span className="font-medium text-strong">{n.rotulo}</span>
                  {n.estado && (
                    <span className={`ml-2 text-[11.5px] ${CSS_DO_ESTADO[n.estado] ?? ''}`}>
                      {ROTULO_DO_ESTADO[n.estado] ?? n.estado}
                    </span>
                  )}
                  {' — '}
                  {n.detalhe}
                  {n.href && (
                    <a href={n.href} className="ml-1.5 text-accent hover:underline">
                      ver
                    </a>
                  )}
                </li>
              ))}
          </ul>
        </div>
      ))}
      <p className="sr-only">{modo}</p>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   A cena
   ═══════════════════════════════════════════════════════════════ */

function temaEscuro() {
  if (typeof window === 'undefined') return true;
  const attr = document.documentElement.getAttribute('data-theme');
  if (attr === 'dark') return true;
  if (attr === 'light') return false;
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

function montar(
  THREE: typeof import('three'),
  alvo: HTMLElement,
  nos: Posicionado[],
  modo: Modo,
  ganchos: {
    aoClicar: (no: No) => void;
    aoProjetar: (
      lista: { id: string; rotulo: string; x: number; y: number; frente: boolean }[],
    ) => void;
  },
): (() => void) | null {
  const reduzido =
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const largura = alvo.clientWidth || 800;
  const altura = alvo.clientHeight || 460;
  const escuro = temaEscuro();

  const cena = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, largura / altura, 0.1, 200);
  camera.position.set(0, modo === 'percurso' ? 2.2 : 3.4, modo === 'percurso' ? 12 : 13.5);
  camera.lookAt(0, 0, 0);

  let renderizador: import('three').WebGLRenderer;
  try {
    renderizador = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  } catch {
    return null;
  }
  renderizador.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderizador.setSize(largura, altura);
  renderizador.domElement.style.display = 'block';
  renderizador.domElement.style.cursor = 'grab';
  alvo.appendChild(renderizador.domElement);

  cena.add(new THREE.AmbientLight(0xffffff, 0.85));
  const luz = new THREE.DirectionalLight(0xffffff, 0.85);
  luz.position.set(4, 8, 10);
  cena.add(luz);

  const grupo = new THREE.Group();
  cena.add(grupo);

  // Tudo que for criado entra aqui, e o desmonte percorre a lista. Sem
  // isso, trocar de mapa três vezes deixa três cenas de geometria viva
  // na GPU — o vazamento clássico de quem usa Three em React.
  const descartaveis: { dispose: () => void }[] = [];

  const esfera = new THREE.SphereGeometry(1, 20, 16);
  descartaveis.push(esfera);

  const malhas: import('three').Mesh[] = [];
  const porMalha = new Map<import('three').Mesh, Posicionado>();

  for (const no of nos) {
    const cor = corDoNo(no, modo);
    const vazio = no.estado === 'nao-existe';
    const material = new THREE.MeshStandardMaterial({
      color: cor,
      roughness: 0.45,
      metalness: 0.05,
      transparent: vazio,
      opacity: vazio ? 0.35 : 1,
      wireframe: vazio,
    });
    descartaveis.push(material);

    const malha = new THREE.Mesh(esfera, material);
    const raio = 0.12 + Math.min(no.peso ?? 0, 120) / 900;
    malha.scale.setScalar(modo === 'percurso' ? 0.26 : raio);
    malha.position.set(no.x, no.y, no.z);
    grupo.add(malha);
    malhas.push(malha);
    porMalha.set(malha, no);
  }

  // As arestas. No percurso elas são o assunto — cada fase entrega a
  // seguinte —, e nos outros mapas elas ligam cada nó ao centro do
  // anel dele, o que desenha o grupo sem precisar escrever o nome.
  const corDaLinha = escuro ? 0x3a3a42 : 0xd0d0d8;
  const materialDaLinha = new THREE.LineBasicMaterial({
    color: corDaLinha,
    transparent: true,
    opacity: 0.65,
  });
  descartaveis.push(materialDaLinha);

  if (modo === 'percurso') {
    const pontos = nos.map((n) => new THREE.Vector3(n.x, n.y, n.z));
    const curva = new THREE.CatmullRomCurve3(pontos);
    const geo = new THREE.BufferGeometry().setFromPoints(curva.getPoints(160));
    descartaveis.push(geo);
    grupo.add(new THREE.Line(geo, materialDaLinha));
  } else {
    const segmentos: number[] = [];
    const centros = new Map<string, { y: number }>();
    for (const no of nos) if (!centros.has(no.grupo)) centros.set(no.grupo, { y: no.y });
    for (const no of nos) {
      const c = centros.get(no.grupo)!;
      segmentos.push(0, c.y, 0, no.x, no.y, no.z);
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(segmentos, 3));
    descartaveis.push(geo);
    grupo.add(new THREE.LineSegments(geo, materialDaLinha));
  }

  /* ── Girar com o ponteiro ───────────────────────────────── */

  let giroY = 0;
  let giroX = modo === 'percurso' ? 0 : -0.18;
  let arrastando = false;
  let ultimoX = 0;
  let ultimoY = 0;
  let moveu = 0;

  const tela = renderizador.domElement;

  const comecar = (e: PointerEvent) => {
    arrastando = true;
    moveu = 0;
    ultimoX = e.clientX;
    ultimoY = e.clientY;
    tela.style.cursor = 'grabbing';
    tela.setPointerCapture(e.pointerId);
  };

  const mover = (e: PointerEvent) => {
    if (!arrastando) return;
    const dx = e.clientX - ultimoX;
    const dy = e.clientY - ultimoY;
    moveu += Math.abs(dx) + Math.abs(dy);
    giroY += dx * 0.006;
    giroX = Math.max(-0.9, Math.min(0.9, giroX + dy * 0.004));
    ultimoX = e.clientX;
    ultimoY = e.clientY;
  };

  const raio = new THREE.Raycaster();
  const ponteiro = new THREE.Vector2();

  const terminar = (e: PointerEvent) => {
    const eraArrasto = moveu > 6;
    arrastando = false;
    tela.style.cursor = 'grab';
    try {
      tela.releasePointerCapture(e.pointerId);
    } catch {
      /* o ponteiro já pode ter sido solto pelo navegador */
    }
    // Um arrasto que termina em cima de um nó NÃO é um clique nele:
    // girar o mapa abriria um painel a cada volta.
    if (eraArrasto) return;

    const r = tela.getBoundingClientRect();
    ponteiro.x = ((e.clientX - r.left) / r.width) * 2 - 1;
    ponteiro.y = -((e.clientY - r.top) / r.height) * 2 + 1;
    raio.setFromCamera(ponteiro, camera);
    const atingidos = raio.intersectObjects(malhas, false);
    if (atingidos.length > 0) {
      const no = porMalha.get(atingidos[0].object as import('three').Mesh);
      if (no) ganchos.aoClicar(no);
    }
  };

  tela.addEventListener('pointerdown', comecar);
  tela.addEventListener('pointermove', mover);
  tela.addEventListener('pointerup', terminar);
  tela.addEventListener('pointercancel', () => {
    arrastando = false;
    tela.style.cursor = 'grab';
  });

  /* ── Redimensionar ──────────────────────────────────────── */

  const aoRedimensionar = () => {
    const l = alvo.clientWidth || largura;
    const a = alvo.clientHeight || altura;
    camera.aspect = l / a;
    camera.updateProjectionMatrix();
    renderizador.setSize(l, a);
  };
  const observador =
    typeof ResizeObserver !== 'undefined' ? new ResizeObserver(aoRedimensionar) : null;
  observador?.observe(alvo);

  /* ── O laço ─────────────────────────────────────────────── */

  const projetado = new THREE.Vector3();

  // Projetar 76 rótulos a 60 quadros por segundo reescreveria o DOM
  // 4560 vezes por segundo. Doze por segundo é o suficiente para o
  // texto acompanhar a rotação sem que ninguém veja atraso.
  let ultimaProjecao = 0;

  const projetar = () => {
    const l = tela.clientWidth;
    const a = tela.clientHeight;
    const lista = nos.map((no, i) => {
      const malha = malhas[i];
      projetado.copy(malha.position);
      grupo.localToWorld(projetado);
      const distancia = projetado.distanceTo(camera.position);
      projetado.project(camera);
      return {
        id: no.id,
        rotulo: no.rotulo,
        x: (projetado.x * 0.5 + 0.5) * l,
        y: (-projetado.y * 0.5 + 0.5) * a - 16,
        frente: distancia < camera.position.length() + 0.4,
      };
    });
    ganchos.aoProjetar(lista);
  };

  let quadro = 0;
  const inicio = performance.now();

  const laco = () => {
    quadro = requestAnimationFrame(laco);
    const agora = performance.now();

    if (!reduzido && !arrastando) {
      giroY += 0.0016;
    }
    grupo.rotation.y = giroY;
    grupo.rotation.x = giroX;

    if (modo === 'percurso' && !reduzido) {
      // Uma pulsação que percorre a fita: ela mostra que as fases têm
      // ORDEM, que é a única coisa que o desenho precisa afirmar.
      const t = ((agora - inicio) / 2600) % 1;
      malhas.forEach((m, i) => {
        const meu = i / Math.max(malhas.length - 1, 1);
        const perto = Math.max(0, 1 - Math.abs(t - meu) * 7);
        m.scale.setScalar(0.26 + perto * 0.13);
      });
    }

    renderizador.render(cena, camera);

    if (agora - ultimaProjecao > 80) {
      ultimaProjecao = agora;
      projetar();
    }
  };

  if (reduzido) {
    grupo.rotation.y = giroY;
    grupo.rotation.x = giroX;
    renderizador.render(cena, camera);
    projetar();
  } else {
    laco();
  }

  return () => {
    cancelAnimationFrame(quadro);
    observador?.disconnect();
    tela.removeEventListener('pointerdown', comecar);
    tela.removeEventListener('pointermove', mover);
    tela.removeEventListener('pointerup', terminar);
    for (const d of descartaveis) d.dispose();
    renderizador.dispose();
    if (tela.parentNode === alvo) alvo.removeChild(tela);
  };
}
