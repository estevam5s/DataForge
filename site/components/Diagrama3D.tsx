'use client';

/**
 * Diagramas em três dimensões, com Three.js.
 *
 * Três regras, e elas são o motivo de estes diagramas existirem:
 *
 * 1. **Discreto.** A animação é lenta e de baixa amplitude. Um diagrama
 *    que chama mais atenção que o texto ao lado atrapalha a leitura —
 *    e numa página de documentação o texto é o assunto.
 *
 * 2. **Ele explica.** Cada um mostra uma coisa que prosa explica pior:
 *    um fluxo com etapas, uma árvore onde só parte dos ramos volta, e
 *    a diferença entre vinte idas e uma. Um cubo girando por girar
 *    seria enfeite, e enfeite pesa 600 KB.
 *
 * 3. **`prefers-reduced-motion` desliga o movimento.** Não esconde o
 *    diagrama: ele continua lá, parado, na posição em que se lê melhor.
 *    Quem pediu menos movimento não pediu menos informação.
 *
 * O Three.js é carregado sob demanda (`import()` dentro do efeito), e
 * só quando o diagrama entra na tela. Uma página que tem um diagrama no
 * fim não paga por ele enquanto ninguém rolar até lá.
 */

import { useEffect, useRef, useState } from 'react';

type Tipo = 'pipeline' | 'consulta' | 'lote';

const LEGENDAS: Record<Tipo, { titulo: string; texto: string }> = {
  pipeline: {
    titulo: 'Do texto ao resultado',
    texto: 'Cada etapa entrega a seguinte. O analisador é o único opcional — e é o que fala antes de qualquer coisa rodar.',
  },
  consulta: {
    titulo: 'A consulta escolhe os ramos',
    texto: 'O grafo inteiro existe; a resposta traz só o caminho pedido. Os ramos apagados não são buscados.',
  },
  lote: {
    titulo: 'Vinte idas, ou uma',
    texto: 'À esquerda, um pedido por item. À direita, o lote junta as chaves e vai uma vez.',
  },
};

export function Diagrama3D({ tipo }: { tipo: Tipo }) {
  const caixa = useRef<HTMLDivElement>(null);
  const [visivel, setVisivel] = useState(false);
  const [falhou, setFalhou] = useState(false);

  // Só monta quando entra na tela. Uma página com três diagramas não
  // pode carregar três cenas antes de a primeira linha ser lida.
  useEffect(() => {
    const elemento = caixa.current;
    if (!elemento) return;
    if (typeof IntersectionObserver === 'undefined') {
      setVisivel(true);
      return;
    }
    const observador = new IntersectionObserver(
      (entradas) => {
        if (entradas.some((e) => e.isIntersecting)) {
          setVisivel(true);
          observador.disconnect();
        }
      },
      { rootMargin: '200px' },
    );
    observador.observe(elemento);
    return () => observador.disconnect();
  }, []);

  useEffect(() => {
    if (!visivel || !caixa.current) return;
    let parar = () => {};
    let vivo = true;

    (async () => {
      try {
        const THREE = await import('three');
        if (!vivo || !caixa.current) return;
        parar = montar(THREE, caixa.current, tipo);
      } catch {
        // Sem o Three, a legenda continua dizendo o que o diagrama
        // diria. Um erro de rede não pode deixar um buraco na página.
        setFalhou(true);
      }
    })();

    return () => {
      vivo = false;
      parar();
    };
  }, [visivel, tipo]);

  const legenda = LEGENDAS[tipo];
  return (
    <figure className="my-8 overflow-hidden rounded-2xl border border-line bg-surface/40">
      <div
        ref={caixa}
        className="relative h-[260px] w-full sm:h-[300px]"
        aria-hidden="true"
      />
      <figcaption className="border-t border-line/60 px-4 py-3 text-[13px] leading-[20px] text-muted">
        <strong className="text-strong">{legenda.titulo}.</strong> {legenda.texto}
        {falhou && ' (o diagrama não pôde ser desenhado aqui)'}
      </figcaption>
    </figure>
  );
}

/* ═══════════════════════════════════════════════════════════════
   A cena
   ═══════════════════════════════════════════════════════════════ */

function corDoTema() {
  if (typeof window === 'undefined') return { linha: 0x3a3a42, texto: 0x9a9aa4 };
  const escuro =
    document.documentElement.getAttribute('data-theme') === 'dark' ||
    (document.documentElement.getAttribute('data-theme') !== 'light' &&
      window.matchMedia('(prefers-color-scheme: dark)').matches);
  return escuro
    ? { linha: 0x3a3a42, texto: 0x9a9aa4 }
    : { linha: 0xd4d4dc, texto: 0x6b6b76 };
}

const ACENTO = 0xe5484d;
const APAGADO = 0x5a5a66;

function montar(THREE: typeof import('three'), alvo: HTMLElement, tipo: Tipo) {
  const reduzido =
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const largura = alvo.clientWidth || 600;
  const altura = alvo.clientHeight || 280;

  const cena = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, largura / altura, 0.1, 100);
  camera.position.set(0, 1.6, 9.5);
  camera.lookAt(0, 0, 0);

  let renderizador: import('three').WebGLRenderer;
  try {
    renderizador = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  } catch {
    // Sem WebGL — uma máquina antiga, um navegador com aceleração
    // desligada. A legenda abaixo continua explicando.
    return () => {};
  }
  renderizador.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderizador.setSize(largura, altura);
  renderizador.domElement.style.display = 'block';
  alvo.appendChild(renderizador.domElement);

  cena.add(new THREE.AmbientLight(0xffffff, 0.75));
  const luz = new THREE.DirectionalLight(0xffffff, 0.9);
  luz.position.set(3, 6, 8);
  cena.add(luz);

  const cores = corDoTema();
  const grupo = new THREE.Group();
  cena.add(grupo);

  const animar = construir(THREE, grupo, tipo, cores);

  // Paralaxe de baixa amplitude: a cena se inclina alguns graus com o
  // ponteiro. Sem controle de órbita — um diagrama que a pessoa pode
  // girar até ficar de cabeça para baixo deixa de ser um diagrama.
  let alvoX = 0;
  let alvoY = 0;
  const mover = (e: PointerEvent) => {
    const r = alvo.getBoundingClientRect();
    alvoY = ((e.clientX - r.left) / r.width - 0.5) * 0.5;
    alvoX = ((e.clientY - r.top) / r.height - 0.5) * 0.22;
  };
  const sair = () => {
    alvoX = 0;
    alvoY = 0;
  };
  alvo.addEventListener('pointermove', mover);
  alvo.addEventListener('pointerleave', sair);

  let quadro = 0;
  const inicio = performance.now();
  const laco = () => {
    quadro = requestAnimationFrame(laco);
    const t = (performance.now() - inicio) / 1000;
    if (!reduzido) {
      animar(t);
      grupo.rotation.y += (alvoY - grupo.rotation.y) * 0.05;
      grupo.rotation.x += (alvoX - grupo.rotation.x) * 0.05;
    }
    renderizador.render(cena, camera);
  };
  if (reduzido) {
    animar(0.0001);
    renderizador.render(cena, camera);
  } else {
    laco();
  }

  const redimensionar = () => {
    const l = alvo.clientWidth || largura;
    const a = alvo.clientHeight || altura;
    camera.aspect = l / a;
    camera.updateProjectionMatrix();
    renderizador.setSize(l, a);
  };
  window.addEventListener('resize', redimensionar);

  return () => {
    cancelAnimationFrame(quadro);
    window.removeEventListener('resize', redimensionar);
    alvo.removeEventListener('pointermove', mover);
    alvo.removeEventListener('pointerleave', sair);
    renderizador.dispose();
    cena.traverse((o) => {
      const m = o as import('three').Mesh;
      if (m.geometry) m.geometry.dispose();
      const mat = m.material as import('three').Material | undefined;
      if (mat && 'dispose' in mat) mat.dispose();
    });
    if (renderizador.domElement.parentElement === alvo) {
      alvo.removeChild(renderizador.domElement);
    }
  };
}

type Cores = { linha: number; texto: number };

function construir(
  THREE: typeof import('three'),
  grupo: import('three').Group,
  tipo: Tipo,
  cores: Cores,
): (t: number) => void {
  if (tipo === 'pipeline') return pipeline(THREE, grupo, cores);
  if (tipo === 'consulta') return consulta(THREE, grupo, cores);
  return lote(THREE, grupo, cores);
}

function caixa(
  THREE: typeof import('three'),
  cor: number,
  l = 1.5,
  a = 0.62,
  p = 0.3,
) {
  const geo = new THREE.BoxGeometry(l, a, p);
  const mat = new THREE.MeshStandardMaterial({
    color: cor,
    roughness: 0.62,
    metalness: 0.08,
    transparent: true,
    opacity: 0.95,
  });
  return new THREE.Mesh(geo, mat);
}

function fio(
  THREE: typeof import('three'),
  de: import('three').Vector3,
  para: import('three').Vector3,
  cor: number,
) {
  const geo = new THREE.BufferGeometry().setFromPoints([de, para]);
  const mat = new THREE.LineBasicMaterial({
    color: cor,
    transparent: true,
    opacity: 0.55,
  });
  return new THREE.Line(geo, mat);
}

/** As cinco etapas, e o dado passando por elas. */
function pipeline(
  THREE: typeof import('three'),
  grupo: import('three').Group,
  cores: Cores,
) {
  const etapas = 5;
  const passo = 1.95;
  const inicio = -((etapas - 1) * passo) / 2;
  const blocos: import('three').Mesh[] = [];

  for (let i = 0; i < etapas; i++) {
    const b = caixa(THREE, i === 3 ? ACENTO : APAGADO, 1.45, 0.58, 0.34);
    b.position.set(inicio + i * passo, 0, 0);
    grupo.add(b);
    blocos.push(b);
    if (i > 0) {
      grupo.add(
        fio(
          THREE,
          new THREE.Vector3(inicio + (i - 1) * passo + 0.73, 0, 0),
          new THREE.Vector3(inicio + i * passo - 0.73, 0, 0),
          cores.linha,
        ),
      );
    }
  }

  const bolinha = new THREE.Mesh(
    new THREE.SphereGeometry(0.15, 24, 16),
    new THREE.MeshStandardMaterial({ color: ACENTO, roughness: 0.35 }),
  );
  grupo.add(bolinha);

  return (t: number) => {
    const avanco = (t * 0.34) % 1;
    const x = inicio - 0.9 + avanco * ((etapas - 1) * passo + 1.8);
    bolinha.position.set(x, 0.52 + Math.sin(avanco * Math.PI) * 0.22, 0.32);
    blocos.forEach((b, i) => {
      const centro = inicio + i * passo;
      const perto = Math.max(0, 1 - Math.abs(x - centro) / 1.1);
      b.position.y = perto * 0.1;
      (b.material as import('three').MeshStandardMaterial).emissive.setHex(
        perto > 0.3 ? 0x2a1416 : 0x000000,
      );
    });
  };
}

/** A árvore do grafo: só o caminho pedido volta aceso. */
function consulta(
  THREE: typeof import('three'),
  grupo: import('three').Group,
  cores: Cores,
) {
  type No = { mesh: import('three').Mesh; pedido: boolean; ordem: number };
  const nos: No[] = [];

  const raiz = caixa(THREE, ACENTO, 1.5, 0.56, 0.32);
  raiz.position.set(0, 2.05, 0);
  grupo.add(raiz);
  nos.push({ mesh: raiz, pedido: true, ordem: 0 });

  // Nível 1: três campos, dois pedidos.
  const nivel1 = [-2.5, 0, 2.5];
  const pedidos1 = [true, true, false];
  nivel1.forEach((x, i) => {
    const b = caixa(THREE, pedidos1[i] ? ACENTO : APAGADO, 1.25, 0.5, 0.28);
    b.position.set(x, 0.35, 0);
    grupo.add(b);
    grupo.add(
      fio(
        THREE,
        new THREE.Vector3(0, 1.77, 0),
        new THREE.Vector3(x, 0.6, 0),
        pedidos1[i] ? ACENTO : cores.linha,
      ),
    );
    nos.push({ mesh: b, pedido: pedidos1[i], ordem: 1 });
  });

  // Nível 2: pendurados no segundo campo, um pedido.
  const nivel2 = [-1.3, 1.3];
  const pedidos2 = [true, false];
  nivel2.forEach((x, i) => {
    const b = caixa(THREE, pedidos2[i] ? ACENTO : APAGADO, 1.05, 0.44, 0.26);
    b.position.set(x, -1.35, 0);
    grupo.add(b);
    grupo.add(
      fio(
        THREE,
        new THREE.Vector3(0, 0.1, 0),
        new THREE.Vector3(x, -1.12, 0),
        pedidos2[i] ? ACENTO : cores.linha,
      ),
    );
    nos.push({ mesh: b, pedido: pedidos2[i], ordem: 2 });
  });

  return (t: number) => {
    nos.forEach((no) => {
      const mat = no.mesh.material as import('three').MeshStandardMaterial;
      if (!no.pedido) {
        mat.opacity = 0.2;
        return;
      }
      // A onda desce a árvore: raiz, campos, netos — na ordem em que
      // o executor resolve.
      const fase = (t * 0.5 - no.ordem * 0.22) % 1.6;
      const brilho = fase > 0 && fase < 0.5 ? Math.sin(fase * Math.PI * 2) : 0;
      mat.opacity = 0.92;
      mat.emissive.setHex(brilho > 0.15 ? 0x3a1a1d : 0x120a0b);
      no.mesh.scale.setScalar(1 + Math.max(0, brilho) * 0.06);
    });
  };
}

/** Vinte setas para o banco, ou uma. */
function lote(
  THREE: typeof import('three'),
  grupo: import('three').Group,
  cores: Cores,
) {
  const esquerda = new THREE.Group();
  const direita = new THREE.Group();
  esquerda.position.x = -3.1;
  direita.position.x = 3.1;
  grupo.add(esquerda, direita);

  const bancoEsq = caixa(THREE, APAGADO, 2.1, 0.5, 0.5);
  bancoEsq.position.set(0, -1.9, 0);
  esquerda.add(bancoEsq);
  const bancoDir = caixa(THREE, APAGADO, 2.1, 0.5, 0.5);
  bancoDir.position.set(0, -1.9, 0);
  direita.add(bancoDir);

  const itensEsq: import('three').Mesh[] = [];
  const itensDir: import('three').Mesh[] = [];
  const quantos = 8;
  for (let i = 0; i < quantos; i++) {
    const x = -1.55 + (i / (quantos - 1)) * 3.1;
    const a = caixa(THREE, APAGADO, 0.3, 0.3, 0.3);
    a.position.set(x, 1.55, 0);
    esquerda.add(a);
    itensEsq.push(a);
    esquerda.add(
      fio(
        THREE,
        new THREE.Vector3(x, 1.4, 0),
        new THREE.Vector3(0, -1.65, 0),
        cores.linha,
      ),
    );

    const b = caixa(THREE, APAGADO, 0.3, 0.3, 0.3);
    b.position.set(x, 1.55, 0);
    direita.add(b);
    direita.add(
      fio(
        THREE,
        new THREE.Vector3(x, 1.4, 0),
        new THREE.Vector3(0, 0.35, 0),
        cores.linha,
      ),
    );
  }

  // O lote: uma caixa no meio, e UM fio até o banco.
  const feixe = caixa(THREE, ACENTO, 1.5, 0.42, 0.42);
  feixe.position.set(0, 0.08, 0);
  direita.add(feixe);
  direita.add(
    fio(
      THREE,
      new THREE.Vector3(0, -0.13, 0),
      new THREE.Vector3(0, -1.65, 0),
      ACENTO,
    ),
  );

  const bolinhas: import('three').Mesh[] = [];
  for (let i = 0; i < quantos; i++) {
    const p = new THREE.Mesh(
      new THREE.SphereGeometry(0.088, 16, 12),
      new THREE.MeshStandardMaterial({ color: APAGADO, roughness: 0.4 }),
    );
    esquerda.add(p);
    bolinhas.push(p);
    itensDir.push(p);
  }
  const unica = new THREE.Mesh(
    new THREE.SphereGeometry(0.13, 20, 14),
    new THREE.MeshStandardMaterial({ color: ACENTO, roughness: 0.35 }),
  );
  direita.add(unica);

  return (t: number) => {
    const ciclo = (t * 0.26) % 1;
    bolinhas.forEach((p, i) => {
      const x = -1.55 + (i / (quantos - 1)) * 3.1;
      // Cada uma sai num instante diferente: são idas separadas.
      const meu = (ciclo + i * 0.11) % 1;
      p.position.set(x + (0 - x) * meu, 1.4 + (-1.65 - 1.4) * meu, 0.16);
      (p.material as import('three').MeshStandardMaterial).opacity = 1;
    });
    // A do lote só desce depois de a fila encher.
    const desce = Math.max(0, (ciclo - 0.55) / 0.45);
    unica.position.set(0, 0.35 + (-1.65 - 0.35) * desce, 0.16);
    unica.visible = ciclo > 0.55;
    (feixe.material as import('three').MeshStandardMaterial).emissive.setHex(
      ciclo < 0.55 ? 0x2a1416 : 0x000000,
    );
    itensEsq.forEach((m, i) => {
      const mat = m.material as import('three').MeshStandardMaterial;
      mat.emissive.setHex(((ciclo + i * 0.11) % 1) < 0.12 ? 0x202028 : 0x000000);
    });
    itensDir.forEach(() => undefined);
  };
}
