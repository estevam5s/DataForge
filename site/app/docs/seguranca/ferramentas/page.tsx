// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_informacao.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "As ferramentas",
  description: "Detecção de segredos, linter de segurança, análise estática, verificações em execução e trilha de auditoria — o que cada uma pega, e o que ela não pega.",
};

const blocos: Bloco[] = [
  {"p": "Uma ferramenta de segurança vale pelo que ela **pega** e pelo que ela **não acusa por engano**. A segunda metade decide se ela continua ligada: um alarme falso no caminho comum ensina a ignorar a saída, e uma ferramenta ignorada não protege nada."},
  {"h2": "`dataforge seguranca`"},
  {"p": "Duas varreduras sobre cada arquivo: **segredos por formato** e **dez regras sintáticas**. Ela lê `.df`, `.env`, `.json`, `.toml`, `.yml`, `.sh`, `.ts` e `.md` — um segredo vaza do arquivo de configuração muito mais do que do código."},
  { code: `// $ dataforge seguranca .
//
// ALTO  src/config.df:12:14  [segredo-no-codigo]
//         Stripe escrito no arquivo (sk_l************).
//         dica: Leia de 'OS.env' e ROTACIONE a chave que ja esteve aqui.
//
// MEDIO src/relatorio.df:88:5  [md5-ou-sha1]
//         MD5 e SHA-1 estao quebrados para assinatura.
//         dica: Use 'sha256'. Para senha, 'hash_password'.
//
// 2 achado(s) em 143 arquivo(s) — 1 de gravidade alta

// --strict        reprova a esteira de CI
// --json          vira entrada de outra ferramenta
// --so=alto       esconde os medios`, lang: 'df' },
  {"table": {"head": ["Regra", "Gravidade", "O que ela acusa"], "rows": [["`segredo-no-codigo`", "alto", "chave de API, token ou bloco de chave privada no arquivo"], ["`sql-concatenado`", "alto", "SQL montado com interpolação ou concatenação"], ["`shell-com-texto`", "alto", "linha de shell montada com interpolação"], ["`senha-sem-derivacao`", "alto", "senha guardada com resumo simples"], ["`verificacao-desligada`", "alto", "`verificar := no` no caminho de produção"], ["`md5-ou-sha1`", "médio", "MD5 e SHA-1 para assinatura"], ["`html-sem-escape`", "médio", "HTML montado com interpolação"], ["`aleatorio-fraco`", "médio", "`randint` para token, senha ou chave"], ["`comparacao-de-segredo`", "médio", "comparar segredo com `is` vaza tempo"], ["`caminho-de-fora`", "médio", "caminho montado com valor que veio de fora"]]}},
  {"callout": {"tipo": "atencao", "titulo": "O que a varredura CALA, e por quê", "texto": "Sem três silêncios ela apontava **19 vezes** neste repositório, e as 19 eram falso alarme — inclusive os exercícios que *ensinam* a não escrever token no arquivo. Ela cala sobre: **(1)** valor que se anuncia como exemplo (`\"123456:AAHexemplo\"`); **(2)** **JWT com papel `anon`** — a chave `anon` do Supabase vai no pacote do navegador de propósito, e só o conteúdo a separa da `service_role`, então o papel é lido de dentro do próprio token; **(3)** credencial de `localhost` e dos domínios reservados da RFC 2606."}},
  { code: `adopt Arcane.Seguranca as Seg

// A mesma varredura, chamada de dentro de um programa — e util num
// gancho de pre-commit ou antes de gravar um log.
fonte := "chave := \\"ghp_abcdefghijklmnopqrstuvwxyz0123456789\\""

achados := Seg.procurar_segredos(fonte)
assert len(achados) is 1
out $"{achados[0]['tipo']} na linha {achados[0]['linha']}: {achados[0]['trecho']}"

// O trecho ja vem MASCARADO: um relatorio de vazamento que imprime
// o segredo inteiro e mais um lugar onde ele esta.
assert "abcdefghijkl" not in achados[0]["trecho"]

// E 'redigir' devolve o texto com os segredos trocados no lugar,
// para gravar um corpo de pedido no log sem que o log vire o
// proximo vazamento.
assert "abcdefghijkl" not in Seg.redigir(fonte)`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "O escape, quando o achado é deliberado", "texto": "`// df: permitir segredo-no-codigo` na linha, ou na de cima, silencia **aquela** regra ali — e vale em qualquer arquivo, não só num `.df`. A regra tem de ser **nomeada**: um `permitir` solto esconderia o próximo achado, que ninguém pediu para esconder. Um analisador sem escape obriga a escolher entre conviver com o alarme e desligar tudo, e a segunda é o que acontece."}},
  {"h2": "Análise estática"},
  {"table": {"head": ["Comando", "O que ele pega que importa para segurança"], "rows": [["`dataforge check`", "nome, aridade e tipo — **inclusive entre arquivos**; campo inexistente com sugestão"], ["`dataforge check --strict`", "avisos viram erros; é o que vai na esteira"], ["`dataforge lint`", "variável escrita e nunca lida, ramo redundante"], ["`dataforge seguranca`", "as duas varreduras acima"], ["`dataforge oop`", "acoplamento e coesão — complexidade é onde a falha se esconde"], ["`dataforge deps`", "o grafo de imports, e o ciclo"]]}},
  {"callout": {"tipo": "atencao", "titulo": "O aviso que é o único bug caro que nem o check nem o lint mencionavam", "texto": "`escrita-concorrente`: o `check` avisa quando um `thread`, `parallel` **ou `route`** escreve num nome que vem de fora. **A rota é o caso que mais importa** — o Kiln usa `ThreadingHTTPServer`, cada pedido roda numa thread, e ali a concorrência é *invisível* para quem escreve. Medido: seis pedidos simultâneos numa rota que lê, espera e escreve entregaram **1 de 6**."}},
  {"h2": "Verificações em execução"},
  {"p": "O que a análise estática não consegue provar continua sendo conferido quando o programa roda — e o erro tem nome, linha e dica."},
  {"table": {"head": ["Confere", "O erro"], "rows": [["tipo declarado, em toda fronteira", "`TypeError`"], ["índice fora do alcance", "`IndexError`"], ["chave que não existe", "`KeyError`"], ["membro de `void`", "`NullReferenceError`"], ["refinamento de um `type … where`", "o erro nomeia o tipo, não a base"], ["invariante de um agregado", "`InvariantError`, e o comando é desfeito"], ["limite de bloco e ponteiro nulo", "`BufferOverflowError`, `NullPointerError`"], ["entrada hostil recusada", "`UnsafeInputError`"]]}},
  {"h2": "Trilha de auditoria"},
  {"p": "Responsabilização exige um registro que não possa ser alterado sem deixar marca. A trilha encadeia o resumo do registro anterior em cada registro."},
  { code: `adopt Arcane.Seguranca as Seg
adopt Arcane.OS as OS
adopt Arcane.IO as IO

caminho := $"{OS.temp_dir()}/df-auditoria-{randint(100000, 999999)}.log"
livro := Seg.auditoria(caminho)

livro.registrar("login", {"ip": "203.0.113.7"}, quem := "ana")
livro.registrar("apagou_pedido", {"pedido": 42}, quem := "ana")
livro.registrar("exportou_relatorio", {"linhas": 1200}, quem := "bruno")

r := livro.conferir()
assert r["ok"]
out $"{r['registros']} registros, cadeia fecha"

// Os dados passam por 'redigir' ANTES de serem gravados: uma trilha
// de auditoria e exatamente o tipo de arquivo que acaba anexado a
// um chamado.
livro.registrar("deploy", {"token": "ghp_abcdefghijklmnopqrstuvwxyz01"})
cycle linha in livro.ler():
    assert "abcdefghijkl" not in str(linha)

out "o segredo nao entra nem na propria auditoria"

IO.delete(caminho)`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "A cadeia dá evidência, e não impedimento", "texto": "Nada num arquivo local impede alguém com acesso de editá-lo. O que a cadeia dá é que **alterar ou apagar uma linha faz a próxima deixar de fechar**, e `conferir()` diz em qual. Para que a evidência valha, a trilha tem de ser copiada para **fora da máquina que a escreve** — e isso está aqui, na documentação, porque o código não tem como garantir."}},
  {"h2": "A esteira completa"},
  { code: `// .github/workflows/ci.yml — as cinco que reprovam de verdade
//
//   dataforge check . --strict
//   dataforge lint .
//   dataforge seguranca . --strict
//   dataforge test tests/ --cobertura --minimo=80
//   dataforge devops doctor
//
// E o gancho local, que pega antes de o segredo sair da maquina:
//
//   # .git/hooks/pre-commit
//   #!/bin/sh
//   dataforge seguranca . --strict || exit 1`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "O gancho local não substitui a esteira", "texto": "Um gancho de pré-commit pode ser pulado com `--no-verify`, e é pulado. Ele existe para dar a resposta **rápida** a quem está escrevendo; quem **reprova** é o CI, que não tem como ser pulado. Os dois rodam o mesmo comando de propósito: se divergirem, o local passa a aprovar o que o remoto recusa, e a confiança no primeiro acaba."}},
];

const headings = [{ id: 'dataforge-seguranca', text: "`dataforge seguranca`", level: 2 as const }, { id: 'analise-estatica', text: "Análise estática", level: 2 as const }, { id: 'verificacoes-em-execucao', text: "Verificações em execução", level: 2 as const }, { id: 'trilha-de-auditoria', text: "Trilha de auditoria", level: 2 as const }, { id: 'a-esteira-completa', text: "A esteira completa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"As ferramentas"}
      description={"Detecção de segredos, linter de segurança, análise estática, verificações em execução e trilha de auditoria — o que cada uma pega, e o que ela não pega."}
      href={"/docs/seguranca/ferramentas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
