// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Log seguro e auditoria",
  description: "O log que não pode ser forjado, que não guarda dado pessoal, e a trilha de auditoria que denuncia a linha apagada.",
};

const blocos: Bloco[] = [
  {"p": "O log tem dois inimigos opostos: o que **falta** (o incidente sem rastro) e o que **sobra** (o CPF, a senha, o token gravados em texto). E um terceiro, mais sutil: o log **forjado**, em que um campo com quebra de linha acrescenta um evento que nunca aconteceu."},
  { code: `adopt Arcane.Seguranca as S
adopt Arcane.OS as OS
adopt Arcane.IO as IO

// 1. Forjar: um nome de usuario com '\\n' acrescentaria uma linha inteira.
nome := "ana\\n2026-09-22 INFO login ok usuario=admin"
linha := $"login falhou usuario={S.escapar_log(nome)}"
assert len(linha.lines()) is 1

// 2. Sobrar: o dado pessoal sai mascarado.
evento := "pedido de ana@exemplo.com, cpf 529.982.247-25"
out S.mascarar_pii(evento)
assert "529.982.247-25" not in S.mascarar_pii(evento)

// 3. Apagar: a auditoria e encadeada — cada registro leva o resumo do anterior.
pasta := $"{OS.temp_dir()}/df-aud-{randint(100000, 999999)}"
IO.mkdir(pasta)
a := S.auditoria($"{pasta}/trilha.log")
a.registrar("login", {"usuario": "ana"}, "ana")
a.registrar("exportou", {"linhas": 120}, "ana")
assert a.conferir()["ok"]
IO.remove_tree(pasta)
out "log de uma linha, sem PII, e a trilha integra"`, lang: 'df' },
  {"table": {"head": ["Registre", "Não registre"], "rows": [["quem, o quê, quando, de onde, o resultado", "senha, token, número de cartão, CPF inteiro"], ["a falha de autenticação e de autorização", "o corpo inteiro do pedido"], ["a mudança de permissão e de configuração", "o dado de saúde, o dado de criança"], ["o id da requisição, para cruzar serviços", "a chave de sessão"]]}},
  {"callout": {"tipo": "nota", "titulo": "Encadeada não é imutável", "texto": "Cada registro da `auditoria` carrega o resumo do anterior: apagar ou editar uma linha no meio quebra a corrente, e `conferir()` diz onde. Quem apaga o arquivo **inteiro** não é detectado por ele — por isso a trilha vai também para fora da máquina (um coletor, um bucket com retenção)."}},
  {"p": "Continue em [Detecção](/docs/seguranca/deteccao) e [Incidentes](/docs/seguranca/incidentes)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Log seguro e auditoria"}
      description={"O log que não pode ser forjado, que não guarda dado pessoal, e a trilha de auditoria que denuncia a linha apagada."}
      href={"/docs/seguranca/logs"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
