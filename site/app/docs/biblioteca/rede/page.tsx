// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/plataforma.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Rede",
  description: "TCP, UDP, DNS e TLS — o que está abaixo do HTTP.",
};

const blocos: Bloco[] = [
  {"p": "O [Kiln](/docs/kiln) fala HTTP e a [Malha](/docs/tecnicas/microservicos) fala com outro serviço. **Abaixo disso não havia nada**: um protocolo próprio, um agente que manda uma linha por UDP, ou descobrir para onde um nome aponta pediam sair da linguagem."},
  {"p": "E o TLS estava na lista do que **não existe**, na própria documentação. Ele existe agora, dos dois lados."},
  {"h2": "TCP"},
  { code: `adopt Arcane.Rede as Rede

action atender(conexao):
    pedido := conexao.receber_linha()
    conexao.enviar_linha(pedido.upper())

Rede.servir(atender, host := "0.0.0.0", porta := 9000)`, lang: 'df' },
  { code: `cliente := Rede.conectar("127.0.0.1", 9000)
cliente.enviar_linha("forja")
out cliente.receber_linha()        // FORJA
cliente.fechar()`, lang: 'df' },
  {"h3": "O TCP não tem fronteira de mensagem"},
  {"p": "Ele entrega um **fluxo de bytes**, e não mensagens. O formato mais comum para resolver isso é tamanho + corpo:"},
  { code: `adopt Arcane.Bytes as Bytes

action mandar(conexao, texto):
    dados := Bytes.de_texto(texto)
    conexao.enviar(Bytes.empacotar(">u32", len(dados)))
    conexao.enviar(dados)

action receber(conexao):
    quanto := Bytes.desempacotar(">u32", conexao.receber_exato(4))[0]
    yield Bytes.para_texto(conexao.receber_exato(quanto))`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "`receber_exato`, e não `receber`", "texto": "O `recv` devolve **menos** do que se pediu com frequência num pedaço que atravessa pacotes. Tratar o retorno curto como a mensagem inteira corrompe a próxima — e o sintoma é uma conexão que funciona e de repente para."}},
  {"h3": "Ler"},
  {"table": {"head": ["Chamada", "Faz"], "rows": [["`receber(n, prazo)`", "o que chegou, até `n` bytes"], ["`receber_exato(n, prazo)`", "insiste até completar `n`"], ["`receber_linha(prazo, limite)`", "até a quebra, **com teto**"], ["`receber_tudo(prazo, limite)`", "até o outro lado fechar"], ["`enviar(dados)` · `enviar_linha(t)`", "manda tudo, sem devolver pela metade"]]}},
  {"callout": {"tipo": "perigo", "titulo": "O prazo tem padrão, e o limite também", "texto": "Uma leitura sem prazo é a forma mais comum de um serviço travar para sempre: o outro lado caiu sem fechar o socket, e o `recv` fica esperando um byte que nunca vem. E uma linha sem teto deixa um cliente que nunca manda `\\n` encher a memória do servidor — um ataque de uma linha."}},
  {"h2": "UDP"},
  {"p": "Manda e esquece: sem conexão, sem ordem, sem garantia. É o **certo** para métrica, descoberta e log — onde perder um pacote custa menos que a espera de confirmar cada um."},
  { code: `coletor := Rede.udp(porta := 8125, escutar := yes)
chegou := coletor.receber()
out chegou["host"], chegou["dados"]

agente := Rede.udp()
agente.enviar("pedidos=42", "127.0.0.1", 8125)`, lang: 'df' },
  {"h2": "DNS"},
  { code: `out Rede.resolver("dataforge-lang.vercel.app")
// [{ip: 76.76.21.21, versao: 4}, …]

out Rede.nome_de("8.8.8.8")      // dns.google
out Rede.meu_ip()                // o IP com que esta máquina sai`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "`meu_ip` não é `gethostbyname`", "texto": "Numa máquina com `/etc/hosts` comum, resolver o próprio nome devolve `127.0.0.1` e não serve para nada. Abrir um socket UDP para fora (sem mandar nada) faz o sistema escolher a interface de verdade."}},
  {"h2": "Portas"},
  { code: `porta := Rede.porta_livre()                          // livre agora
given Rede.porta_aberta("db", 5432):
    out "o banco está de pé"

Rede.esperar_porta("api", 8080, prazo := 30.0)       // espera subir`, lang: 'df' },
  {"p": "`esperar_porta` substitui o *\"sobe o serviço e dorme dois segundos torcendo para dar tempo\"* de todo script de integração. Quando ela desiste, diz o que costuma ser:"},
  { code: `erro: api:8080 não abriu em 30s.
  O serviço não subiu, subiu em outra porta, ou subiu em
  127.0.0.1 quando deveria ser 0.0.0.0.`, lang: 'text' },
  {"callout": {"tipo": "atencao", "titulo": "`porta_aberta` abre uma conexão de verdade", "texto": "Não há como perguntar sem bater na porta. Um servidor que conta conexões vai ver esta também — e um que lê uma linha logo de cara vai receber o fim da conexão."}},
  {"h2": "TLS"},
  { code: `// cliente
seguro := Rede.conectar("api.exemplo.br", 443, tls := yes)

// servidor
Rede.servir(atender, porta := 443,
    tls := {"certificado": "cert.pem", "chave": "chave.pem"})`, lang: 'df' },
  {"h3": "O certificado que vence sem avisar"},
  {"p": "Um certificado vencido derruba o site inteiro, e o aviso chega pelo cliente reclamando. Isto é o que um monitor pergunta:"},
  { code: `ficha := Rede.certificado_de("dataforge-lang.vercel.app")
out ficha["emissor"], ficha["valido_ate"], ficha["nomes"]

given Rede.dias_ate_vencer("api.exemplo.br") smaller 14:
    alertar("o certificado vence em menos de duas semanas")`, lang: 'df' },
];

const headings = [{ id: 'tcp', text: "TCP", level: 2 as const }, { id: 'o-tcp-nao-tem-fronteira-de-mensagem', text: "O TCP não tem fronteira de mensagem", level: 3 as const }, { id: 'ler', text: "Ler", level: 3 as const }, { id: 'udp', text: "UDP", level: 2 as const }, { id: 'dns', text: "DNS", level: 2 as const }, { id: 'portas', text: "Portas", level: 2 as const }, { id: 'tls', text: "TLS", level: 2 as const }, { id: 'o-certificado-que-vence-sem-avisar', text: "O certificado que vence sem avisar", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Rede"}
      description={"TCP, UDP, DNS e TLS — o que está abaixo do HTTP."}
      href={"/docs/biblioteca/rede"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
