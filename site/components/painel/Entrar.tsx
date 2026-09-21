'use client';

import Link from 'next/link';
import { useEffect, useRef, useState } from 'react';
import { Logo } from '@/components/Logo';
import { Turnstile, type ControleTurnstile } from '@/components/Turnstile';
import { TURNSTILE_LIGADO } from '@/lib/turnstile';
import { useAuth } from '@/lib/supabase/auth';

type Modo = 'entrar' | 'registrar' | 'recuperar';

const TITULOS: Record<Modo, { titulo: string; botao: string }> = {
  entrar: { titulo: 'Entrar no painel', botao: 'Entrar' },
  registrar: { titulo: 'Criar conta', botao: 'Criar conta' },
  recuperar: { titulo: 'Recuperar senha', botao: 'Enviar link' },
};

export function Entrar() {
  const { entrar, registrar, recuperar } = useAuth();
  // '/painel?criar=1' abre direto em "Criar conta". O cabeçalho
  // oferece as duas portas, e levar as duas para o mesmo formulário
  // em modo "entrar" faria a segunda mentir sobre o que faz.
  //
  // Lido de `window` e não de `useSearchParams`: o site é exportado
  // estático, e `useSearchParams` obriga a envolver a página num
  // `<Suspense>` — cerimônia para ler um parâmetro opcional.
  const [modo, setModo] = useState<Modo>(() => {
    if (typeof window === 'undefined') return 'entrar';
    return new URLSearchParams(window.location.search).has('criar')
      ? 'registrar'
      : 'entrar';
  });
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [nome, setNome] = useState('');
  const [erro, setErro] = useState<string | null>(null);
  const [aviso, setAviso] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [captcha, setCaptcha] = useState<string | null>(null);
  const [captchaFalhou, setCaptchaFalhou] = useState(false);
  const widget = useRef<ControleTurnstile>(null);

  // O widget pode RENDERIZAR e nunca terminar: domínio ainda não
  // liberado na chave, desafio interativo que não resolve, extensão
  // de navegador atrapalhando. Nesses casos o `error-callback` não
  // dispara — não há erro, há espera —, e sem um prazo o rótulo do
  // botão fica em "Conclua a verificação" para sempre.
  //
  // Doze segundos: o desafio invisível resolve em menos de dois, e o
  // interativo em poucos segundos depois do clique. Passar disso não
  // é lentidão, é uma espera que não vai terminar.
  useEffect(() => {
    if (!TURNSTILE_LIGADO || captcha || captchaFalhou) return;
    const prazo = setTimeout(() => {
      setCaptchaFalhou(true);
    }, 12000);
    return () => clearTimeout(prazo);
  }, [captcha, captchaFalhou, modo]);

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    setAviso(null);
    setEnviando(true);

    let resultado: string | null = null;
    if (modo === 'entrar') resultado = await entrar(email, senha, captcha);
    else if (modo === 'registrar') resultado = await registrar(email, senha, nome, captcha);
    else resultado = await recuperar(email, captcha);

    // O token é de USO ÚNICO: valeu a tentativa, deu certo ou não.
    // Sem reiniciar aqui, o segundo envio — com a senha certa, depois
    // de um erro de digitação — falharia por 'timeout-or-duplicate',
    // e a pessoa veria uma mensagem sobre captcha onde acabou de
    // corrigir a senha.
    widget.current?.reiniciar();
    setCaptcha(null);
    setCaptchaFalhou(false);

    setEnviando(false);
    if (resultado) {
      setErro(resultado);
      return;
    }
    if (modo === 'registrar') {
      setAviso('Conta criada. Confirme o e-mail para entrar.');
    } else if (modo === 'recuperar') {
      setAviso('Se houver conta com esse e-mail, o link foi enviado.');
    }
  }

  const { titulo, botao } = TITULOS[modo];

  return (
    <div className="flex min-h-screen items-center justify-center px-5 py-12">
      <div className="w-full max-w-[380px]">
        <Link href="/" className="mb-8 flex items-center justify-center gap-2.5">
          <Logo size={30} />
          <span className="text-[19px] font-extrabold tracking-tight">
            DataForge
          </span>
        </Link>

        <div className="surface-card rounded-xl p-6">
          <h1 className="text-[21px] font-bold text-strong">{titulo}</h1>
          <p className="mt-1 text-[13.5px] text-muted">
            {modo === 'recuperar'
              ? 'Enviamos um link para você definir uma senha nova.'
              : 'Guarde projetos, trechos e seu progresso nos exercícios.'}
          </p>

          <form onSubmit={enviar} className="mt-6 space-y-3.5">
            {modo === 'registrar' && (
              <Campo rotulo="Nome" valor={nome} aoMudar={setNome}
                     tipo="text" auto="name" placeholder="Como te chamamos" />
            )}
            <Campo rotulo="E-mail" valor={email} aoMudar={setEmail}
                   tipo="email" auto="email" placeholder="voce@exemplo.com" />
            {modo !== 'recuperar' && (
              <Campo rotulo="Senha" valor={senha} aoMudar={setSenha}
                     tipo="password"
                     auto={modo === 'registrar' ? 'new-password' : 'current-password'}
                     placeholder="ao menos 6 caracteres" />
            )}

            {erro && (
              <p role="alert"
                 className="rounded-lg border border-accent/30 bg-accent/10
                            px-3 py-2 text-[13px] text-accent">
                {erro}
              </p>
            )}
            {aviso && (
              <p role="status"
                 className="rounded-lg border border-line bg-raised px-3 py-2
                            text-[13px] text-body">
                {aviso}
              </p>
            )}

            {/* A verificação fica ACIMA do botão: descobri-la depois de
                clicar em "Entrar" e ver o botão desabilitado é a forma
                mais rápida de alguém achar que o site quebrou. */}
            <Turnstile
              acao={modo}
              controle={widget}
              aoMudarToken={setCaptcha}
              aoFalhar={(motivo) => {
                // FALHA ABERTA, aqui. Se o script não carrega — rede
                // corporativa que bloqueia a Cloudflare, domínio ainda
                // não liberado na chave, extensão de navegador — o
                // botão NÃO pode morrer: quem recusa de verdade é o
                // servidor do Supabase, e um painel que não abre por
                // causa disso é uma porta trancada por acidente, sem
                // ninguém do outro lado para explicar.
                setCaptchaFalhou(true);
                setAviso(`${motivo}. Você pode tentar entrar mesmo assim.`);
              }}
            />

            {/* O BOTÃO NÃO MORRE POR CAUSA DO CAPTCHA — só por já
                estar enviando.

                A versão anterior o desabilitava enquanto não houvesse
                token, e isso contradiz o que este mesmo arquivo diz
                logo acima: quem recusa de verdade é o servidor do
                Supabase. O efeito era uma porta trancada por acidente:
                bastava o widget renderizar e não terminar — domínio
                não liberado, rede corporativa, extensão — para o
                formulário ficar em "Conclua a verificação" para
                sempre, sem erro, sem explicação e sem saída.

                Falhar ABERTO aqui não enfraquece nada: sem token, o
                Supabase recusa e a mensagem é traduzida por
                `traduzirFalhaDeCaptcha`. Um envio recusado com motivo
                é sempre melhor que um botão que não responde. */}
            <button
              type="submit"
              disabled={enviando}
              className="w-full rounded-lg bg-accent px-4 py-2.5 text-[14.5px]
                         font-semibold text-white transition-opacity
                         hover:opacity-90 disabled:opacity-50"
            >
              {enviando
                ? 'Aguarde…'
                : TURNSTILE_LIGADO && !captcha && !captchaFalhou
                  ? `${botao} (verificando…)`
                  : botao}
            </button>
          </form>

          <div className="mt-5 space-y-1.5 text-center text-[13px]">
            {modo === 'entrar' && (
              <>
                <p className="text-muted">
                  Não tem conta?{' '}
                  <button onClick={() => setModo('registrar')}
                          className="link-quiet underline">criar uma</button>
                </p>
                <p className="text-muted">
                  <button onClick={() => setModo('recuperar')}
                          className="link-quiet underline">esqueci a senha</button>
                </p>
              </>
            )}
            {modo !== 'entrar' && (
              <p className="text-muted">
                <button onClick={() => setModo('entrar')}
                        className="link-quiet underline">voltar para entrar</button>
              </p>
            )}
          </div>
        </div>

        <p className="mt-6 text-center text-[12.5px] text-muted">
          <Link href="/docs" className="link-quiet">← voltar à documentação</Link>
        </p>
      </div>
    </div>
  );
}

function Campo({ rotulo, valor, aoMudar, tipo, auto, placeholder }: {
  rotulo: string; valor: string; aoMudar: (v: string) => void;
  tipo: string; auto: string; placeholder: string;
}) {
  const id = `campo-${rotulo.toLowerCase()}`;
  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-[13px] font-medium text-body">
        {rotulo}
      </label>
      <input
        id={id}
        type={tipo}
        required
        autoComplete={auto}
        value={valor}
        onChange={(e) => aoMudar(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-lg border border-line bg-raised px-3 py-2.5
                   text-[14px] text-strong outline-none transition-colors
                   placeholder:text-muted/60 focus:border-accent/50"
      />
    </div>
  );
}
