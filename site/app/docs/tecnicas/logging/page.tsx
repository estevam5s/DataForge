import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Logging",
  description: "Registro estruturado com níveis, campos, arquivo e formato JSON.",
};

const blocos: Bloco[] = [
  {"h2": "Por que não usar out"},
  {"p": "`out` serve para falar com quem está olhando o terminal agora. Log serve para responder perguntas depois: *o que aconteceu às 3h da manhã?*"},
  {"p": "A diferença prática está em três coisas que `out` não tem: **nível**, **campos estruturados** e **destino configurável**."},
  {"h2": "Os seis níveis"},
  { code: `adopt Arcane.Logging as Log

registro := Log.logger("pedidos", "DEBUG")

registro.debug("iniciando o processamento")
registro.info("pedido recebido", {"id": 1042, "cliente": "Ana"})
registro.warn("estoque baixo", {"produto": "P02", "restam": 3})
registro.error("pagamento recusado", {"id": 1042, "codigo": 402})` },
  {"table": {"head": ["Nível", "Quando"], "rows": [["`TRACE`", "detalhe fino, normalmente desligado"], ["`DEBUG`", "o que ajuda a investigar"], ["`INFO`", "eventos normais que valem registrar"], ["`WARN`", "algo estranho, mas o programa segue"], ["`ERROR`", "uma operação falhou"], ["`FATAL`", "o programa não continua"]]}},
  {"p": "O nível do logger é um **piso**: com `WARN`, tudo abaixo é descartado sem custo. Uma linha muda a verbosidade do sistema inteiro."},
  {"h2": "Campos estruturados"},
  { code: `registro.info("pedido recebido", {"id": 1042, "cliente": "Ana"})` },
  { code: `23:59:01 INFO  [pedidos] pedido recebido id=1042 cliente=Ana`, lang: 'text', title: `saída` },
  {"p": "Compare com `out $\"pedido {id} do cliente {nome}\"`. A diferença aparece na hora de procurar: com campos, `grep 'id=1042'` acha tudo daquele pedido. Com texto interpolado, a estrutura se perdeu na formatação."},
  {"h2": "Contexto fixo"},
  { code: `servico := Log.logger("api", "INFO")
servico.with_context({"servico": "checkout", "versao": "1.2"})
servico.info("requisicao recebida", {"rota": "/pagar"})` },
  {"p": "Esses campos passam a aparecer em **toda** linha daquele logger. Você escreve uma vez o que é constante."},
  {"h2": "JSON para máquina"},
  { code: `maquina := Log.logger("api", "INFO")
maquina.as_json(yes)
maquina.info("evento", {"usuario": 7, "acao": "login"})` },
  { code: `{"time": "...", "level": "INFO", "logger": "api", "message": "evento", "usuario": 7, "acao": "login"}`, lang: 'json', title: `saída` },
  {"p": "Uma linha de configuração troca o público-alvo do log de humano para máquina — o formato que Elasticsearch, Loki e CloudWatch esperam."},
  {"h2": "Arquivo"},
  { code: `arquivo := Log.logger("disco", "INFO")
arquivo.to_file("app.log", yes)     # yes = anexar
arquivo.info("linha gravada")
arquivo.close()` },
  {"p": "O `close` garante que o buffer foi para o disco. Em programa que roda continuamente, combine com `defer`."},
  {"h2": "Guardar em memória"},
  { code: `auditoria := Log.logger("auditoria", "INFO")
auditoria.keep(yes)
...
erros := auditoria.records() >> sift r: r["level"] is "ERROR"` },
  {"p": "Útil em teste: você verifica **que o log certo foi emitido**, sem ler stdout."},
  {"h2": "Registrar e repassar"},
  { code: `action camada_media():
    monitor:
        camada_baixa()
    handle e:
        registro.error("falha na camada baixa", {"motivo": e.message})
        propagate e.message` },
  {"p": "A camada do meio anota o que sabe e repassa. O anti-padrão oposto é engolir: `handle e: registro.error(\"falhou\")` faz o chamador achar que deu certo."},
];

const headings = [{ id: 'por-que-nao-usar-out', text: "Por que não usar out", level: 2 as const }, { id: 'os-seis-niveis', text: "Os seis níveis", level: 2 as const }, { id: 'campos-estruturados', text: "Campos estruturados", level: 2 as const }, { id: 'contexto-fixo', text: "Contexto fixo", level: 2 as const }, { id: 'json-para-maquina', text: "JSON para máquina", level: 2 as const }, { id: 'arquivo', text: "Arquivo", level: 2 as const }, { id: 'guardar-em-memoria', text: "Guardar em memória", level: 2 as const }, { id: 'registrar-e-repassar', text: "Registrar e repassar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Logging"}
      description={"Registro estruturado com níveis, campos, arquivo e formato JSON."}
      href={"/docs/tecnicas/logging"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
