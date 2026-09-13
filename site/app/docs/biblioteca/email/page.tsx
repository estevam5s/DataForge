// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/plataforma.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Email",
  description: "Montar e enviar e-mail: texto e HTML juntos, anexos, cópia oculta que não vaza e caixa de teste.",
};

const blocos: Bloco[] = [
  {"p": "Todo sistema manda e-mail: a confirmação de cadastro, a redefinição de senha, o relatório de madrugada. Não havia como, e a saída era chamar um serviço de fora por HTTP — o que funciona e cobra por mensagem."},
  {"h2": "Montar"},
  { code: `adopt Arcane.Email as Email

m := Email.mensagem("forja@exemplo.br", "ana@exemplo.br", "Seu pedido")
m.html("<h1>Obrigado</h1><p>Pedido <b>P-1</b> confirmado.</p>")
m.copia_oculta(["auditoria@exemplo.br"])
m.anexar("notas/P-1.pdf")`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Por que um objeto, e não texto", "texto": "Um e-mail com anexo e HTML é MIME multipart, e montá-lo concatenando texto é como montar HTML com `+`: funciona nos casos fáceis e quebra no primeiro acento ou no primeiro anexo binário."}},
  {"h2": "HTML ganha alternativa em texto"},
  {"p": "Sem ela, o cliente de texto puro mostra a marcação crua — e é o que boa parte dos leitores de tela recebe. Quando você não passa uma, ela é derivada do HTML:"},
  { code: `m.html("<h1>Olá</h1><p>tudo bem</p>")
out m.prever()["texto"]                  // "Olá tudo bem"

m.html(corpo_rico, alternativa := "Seu pedido P-1 foi confirmado.")`, lang: 'df' },
  {"h2": "A cópia oculta não vai no cabeçalho"},
  {"p": "Um Bcc escrito no cabeçalho é **visível para todo mundo** — o oposto do que ele significa. Aqui ele entra só na lista de entrega."},
  {"h2": "Prever antes de mandar"},
  { code: `out m.prever()
// {de: …, para: [ana@…, auditoria@…], assunto: …,
//  texto: …, html: …, anexos: [{nome: P-1.pdf, bytes: 84213}], tamanho: 85102}`, lang: 'df' },
  {"callout": {"tipo": "perigo", "titulo": "O erro mais caro daqui", "texto": "Disparar mil e-mails de teste para endereços reais. `prever` mostra o que **seria** enviado, e não envia nada."}},
  {"h2": "Enviar"},
  { code: `r := Email.enviar(m, "smtp.exemplo.br", porta := 587,
    usuario := "forja@exemplo.br", senha := OS.env("SMTP_SENHA"))

out r["entregues"], r["recusados"], r["ok"]`, lang: 'df' },
  {"table": {"head": ["Porta", "O quê"], "rows": [["`587`", "STARTTLS — o padrão"], ["`465`", "TLS direto"], ["`25`", "sem cifra (`seguro := no`)"]]}},
  {"callout": {"tipo": "perigo", "titulo": "TLS é o padrão", "texto": "Uma senha de SMTP trafegando em claro numa rede que você não controla é uma credencial perdida. Quem quiser sem TLS escreve `seguro := no` — e aí a escolha está no código, para alguém ver na revisão."}},
  {"p": "Quando o login é recusado, a mensagem lembra o que costuma ser: **muitos provedores exigem uma senha de aplicativo**, e não a senha da conta."},
  {"h2": "Caixa de teste"},
  {"p": "O mesmo contrato, sem mandar nada — então o código que envia não muda entre o teste e a produção:"},
  { code: `caixa := Email.caixa()
caixa.enviar(m)

assert len(caixa.para("ana@exemplo.br")) is 1
assert caixa.ultimo()["assunto"] is "Seu pedido"`, lang: 'df' },
];

const headings = [{ id: 'montar', text: "Montar", level: 2 as const }, { id: 'html-ganha-alternativa-em-texto', text: "HTML ganha alternativa em texto", level: 2 as const }, { id: 'a-copia-oculta-nao-vai-no-cabecalho', text: "A cópia oculta não vai no cabeçalho", level: 2 as const }, { id: 'prever-antes-de-mandar', text: "Prever antes de mandar", level: 2 as const }, { id: 'enviar', text: "Enviar", level: 2 as const }, { id: 'caixa-de-teste', text: "Caixa de teste", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Email"}
      description={"Montar e enviar e-mail: texto e HTML juntos, anexos, cópia oculta que não vaza e caixa de teste."}
      href={"/docs/biblioteca/email"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
