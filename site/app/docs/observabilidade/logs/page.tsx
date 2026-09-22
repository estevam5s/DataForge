// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/observabilidade_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Logs estruturados",
  description: "Uma linha de JSON por evento, com os campos para filtrar — e o que nunca vai para o log.",
};

const blocos: Bloco[] = [
  {"p": "`\"pedido 7 criado por ana em 3,2 s\"` é legível para uma pessoa e inútil para uma busca: achar todos os pedidos lentos exige uma expressão regular por formato de frase. Em JSON, cada informação é um **campo**, e a busca é uma consulta."},
  { code: `adopt Arcane.Logging as Log

log := Log.logger("pedidos")
log.as_json()
log.info("pedido criado", {"pedido": 7, "usuario": "ana", "duracao_s": 3.2})`, lang: 'df' },
  { code: `{"time": "2026-09-22T10:55:14", "level": "INFO", "logger": "pedidos",
 "message": "pedido criado", "pedido": 7, "usuario": "ana", "duracao_s": 3.2}`, lang: 'text' },
  {"table": {"head": ["Nível", "Quando"], "rows": [["`debug`", "detalhe para quem está depurando — desligado em produção"], ["`info`", "o que aconteceu e alguém pode querer contar depois"], ["`warn`", "algo inesperado que o programa contornou"], ["`error`", "falhou, e alguém vai precisar olhar"], ["`fatal`", "o processo não tem como seguir"]]}},
  {"callout": {"tipo": "perigo", "titulo": "O que nunca entra no log", "texto": "Senha, token, número de cartão, CPF inteiro, o corpo inteiro de um pedido. O log é lido por mais gente que o banco, fica guardado por mais tempo, e vaza por lugares que ninguém protege. `Seguranca.escapar_log` fecha a injeção de linha; `Privacidade.pseudonimizar` troca o identificador por um que não se desfaz sem chave."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Logs estruturados"}
      description={"Uma linha de JSON por evento, com os campos para filtrar — e o que nunca vai para o log."}
      href={"/docs/observabilidade/logs"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
