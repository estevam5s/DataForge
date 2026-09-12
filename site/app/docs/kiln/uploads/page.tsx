// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/kiln_extra.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Receber arquivos",
  description: "multipart/form-data, e as três recusas que separam um upload de uma porta aberta.",
};

const blocos: Bloco[] = [
  {"p": "O corpo de um pedido é interpretado pelo `Content-Type`. Com `multipart/form-data`, os campos comuns vão para `req[\"body\"]` e os arquivos para `req[\"files\"]`."},
  { code: `adopt Kiln

server importador on 8080:
    route POST "/importar":
        arquivo := Kiln.upload(req, "planilha")
        given arquivo is void:
            respond 400 json {"erro": "nenhum arquivo em 'planilha'"}

        linhas := arquivo["texto"].lines() >> sift l: l.trim() is not ""
        gravado := Kiln.salvar_upload(arquivo, "envios",
                                      tipos := [".csv", ".xlsx"],
                                      limite := 5242880)
        respond json {
            "titulo": req["body"]["titulo"] ?? "",
            "linhas": len(linhas),
            "em": gravado["caminho"]
        }`, lang: 'df' },
  {"h2": "O que chega"},
  {"table": {"head": ["Chamada", "Devolve"], "rows": [["`Kiln.upload(req, campo)`", "o vault de um arquivo, ou `void`"], ["`Kiln.uploads(req)`", "todos, por nome de campo"], ["`req[\"body\"]`", "os campos comuns, como num formulário qualquer"], ["`req[\"files\"]`", "o mesmo que `Kiln.uploads(req)`"]]}},
  { code: `{
    "nome":     "vendas.csv",        // já sem o caminho do cliente
    "tipo":     "text/csv",
    "tamanho":  1284,
    "conteudo": <bytes>,
    "texto":    "id,valor\\n1,10\\n…"
}`, lang: 'text' },
  {"p": "Campos e arquivos ficam **separados** de propósito: quem escreve lê `body[\"titulo\"]` sem saber se o formulário tinha arquivo, e um `cycle` sobre `body` não topa com bytes onde espera texto."},
  {"callout": {"tipo": "nota", "titulo": "Campo repetido vira cluster", "texto": "`tags=a&tags=b` chega como `[\"a\", \"b\"]`, e não como `\"b\"`. É assim que um `<select multiple>` e uma lista de caixas de marcar chegam — o último valor sozinho perderia os outros."}},
  {"p": "O caminho que o cliente manda é descartado: o IE mandava `C:\\Users\\ana\\foto.jpg`, e um navegador hostil manda o que quiser. Fica só `foto.jpg`."},
  {"h2": "Gravar"},
  { code: `gravado := Kiln.salvar_upload(arquivo, "envios",
                              tipos := [".csv", ".xlsx"],
                              limite := 5242880)
// {"caminho": "envios/a3f91c2e4b08.csv",
//  "nome": "a3f91c2e4b08.csv",
//  "nome_original": "vendas.csv",
//  "tamanho": 1284}`, lang: 'df' },
  {"table": {"head": ["Recusa", "Por quê"], "rows": [["nome com `/`, `\\` ou `..`", "`../../.ssh/authorized_keys` escreve **fora** da pasta de destino"], ["acima do `limite`", "um upload de 4 GB enche o disco"], ["extensão fora de `tipos`", "`.php` numa pasta servida como estática é execução remota"]]}},
  {"p": "E o nome final **nunca** é o que o cliente mandou: leva um prefixo aleatório. Dois usuários enviando `foto.jpg` não podem sobrescrever um ao outro, e um nome escolhido por quem envia é um nome que ele pode adivinhar depois. `nome_original` volta no resultado, para guardar no banco e mostrar ao usuário."},
  {"callout": {"tipo": "atencao", "titulo": "Recusar, e não sanear", "texto": "`basename(\"../../x\")` devolve `x`, e a travessia fica neutralizada. Mas um cliente que manda `../../.ssh/authorized_keys` está quebrado ou é hostil, e aceitar como `authorized_keys` **esconde isso de quem lê o log**."}},
  {"h2": "Dois limites, e eles são diferentes"},
  { code: `Kiln.config(app, "limite_corpo", 20971520)     // 20 MB — o do PEDIDO
Kiln.salvar_upload(arquivo, pasta, limite := 5242880)  // 5 MB — o do ARQUIVO`, lang: 'df' },
  {"p": "O limite do pedido é verificado **antes** de o corpo ser lido na memória: um POST maior é recusado com 413 sem chegar à rota. Sem ele, um POST de 2 GB derruba o processo sem exploit nenhum. O padrão é 10 MB."},
  {"p": "O do arquivo é por arquivo, depois de o corpo estar lido. Aumentar um sem o outro não funciona."},
  {"h2": "Vários arquivos"},
  { code: `route POST "/galeria":
    arquivos := Kiln.uploads(req)
    salvos := []
    cycle nome, arquivo in arquivos:
        salvos.append(Kiln.salvar_upload(arquivo, "fotos",
                                         tipos := [".jpg", ".png", ".webp"]))
    respond json {"salvos": len(salvos)}`, lang: 'df' },
  {"h2": "Testar sem navegador"},
  {"p": "`Kiln.test` aceita o corpo cru — basta montar o `multipart`, que é o que o [exercício 223](/docs/exercicios/30-tempo-real) faz:"},
  { code: `corpo := "--X\\r\\n" +
         "Content-Disposition: form-data; name=\\"titulo\\"\\r\\n\\r\\n" +
         "Vendas\\r\\n" +
         "--X\\r\\n" +
         "Content-Disposition: form-data; name=\\"planilha\\"; " +
         "filename=\\"v.csv\\"\\r\\nContent-Type: text/csv\\r\\n\\r\\n" +
         "id,valor\\n1,10\\n\\r\\n" +
         "--X--\\r\\n"

r := Kiln.test(app, "POST", "/importar", corpo,
               {"content-type": "multipart/form-data; boundary=X"})
assert r["status"] is 200`, lang: 'df' },
  {"h2": "Onde continuar"},
  {"cards": [{"href": "/docs/kiln/tempo-real", "title": "Tempo real", "meta": "SSE e WebSocket", "desc": "O servidor empurrando, e as duas vias."}, {"href": "/docs/kiln/middleware", "title": "Middleware", "desc": "CORS, limite de taxa, CSRF e cabeçalhos."}, {"href": "/docs/exercicios/30-tempo-real", "title": "O exercício", "desc": "Upload testado ponta a ponta, sem navegador."}]},
];

const headings = [{ id: 'o-que-chega', text: "O que chega", level: 2 as const }, { id: 'gravar', text: "Gravar", level: 2 as const }, { id: 'dois-limites-e-eles-sao-diferentes', text: "Dois limites, e eles são diferentes", level: 2 as const }, { id: 'varios-arquivos', text: "Vários arquivos", level: 2 as const }, { id: 'testar-sem-navegador', text: "Testar sem navegador", level: 2 as const }, { id: 'onde-continuar', text: "Onde continuar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Receber arquivos"}
      description={"multipart/form-data, e as três recusas que separam um upload de uma porta aberta."}
      href={"/docs/kiln/uploads"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
