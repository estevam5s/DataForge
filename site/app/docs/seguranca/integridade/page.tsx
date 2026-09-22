// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Integridade",
  description: "SRI para o script de CDN, o manifesto de uma pasta, e o manifesto assinado que denuncia a troca conjunta.",
};

const blocos: Bloco[] = [
  {"p": "Integridade é o \"I\" da tríade, e o menos implementado: quase todo sistema cifra, poucos conferem. `Arcane.Integridade` responde três perguntas: o script da CDN é o que eu aprovei? a pasta de produção mudou desde o deploy? e quem trocou um arquivo trocou também o manifesto?"},
  {"h2": "SRI — o script de terceiro"},
  { code: `adopt Arcane.Integridade as I

js := "alert('Hello, world.');"
valor := I.sri(js)
out $"<script src=\\"https://cdn.exemplo.com/a.js\\" integrity=\\"{valor}\\" crossorigin=\\"anonymous\\"></script>"

// O exemplo da MDN — o mesmo valor que o navegador calcula.
assert valor is "sha384-H8BRh8j48O9oYatfu5AZzq6A9RINhZO5H16dQZngK7T62em8MUt1FLm52t+eX6xO"
assert not I.conferir_sri(js + " ", valor)`, lang: 'df' },
  {"h2": "O manifesto de uma pasta"},
  { code: `adopt Arcane.Integridade as I
adopt Arcane.IO as IO
adopt Arcane.OS as OS

app := $"{OS.temp_dir()}/df-int-{randint(100000, 999999)}"
IO.mkdir(app)
IO.write($"{app}/main.df", "out 1")
IO.write($"{app}/config.toml", "porta = 8080")

chave := "mora-fora-desta-maquina-000"
assinado := I.assinar_manifesto(I.manifesto(app), chave)

// ... depois do deploy, alguem mexe:
IO.write($"{app}/main.df", "out 2")
IO.write($"{app}/porta-dos-fundos.df", "out 3")

r := I.conferir_manifesto(app, assinado["arquivos"])
out r
assert r["alterados"] is ["main.df"] and r["acrescentados"] is ["porta-dos-fundos.df"]

// E quem troca o arquivo e o manifesto JUNTOS e pego pela assinatura.
forjado := assinado with {}
forjado["arquivos"] := I.manifesto(app)
assert not I.verificar_manifesto(forjado, chave)
IO.remove_tree(app)`, lang: 'df' },
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["caminho relativo e com `/`", "o manifesto do Windows não confere no Linux"], ["link simbólico não é seguido", "o manifesto descreve arquivos de fora da pasta"], ["a assinatura usa uma chave que mora **fora**", "quem troca o arquivo troca o manifesto junto, e ele continua batendo"], ["comparação em tempo constante", "a assinatura é descoberta pelo tempo de resposta"]]}},
  {"p": "Continue em [Cadeia de suprimentos](/docs/seguranca/cadeia) e [Arcane.Integridade](/docs/biblioteca/integridade)."},
];

const headings = [{ id: 'sri-o-script-de-terceiro', text: "SRI — o script de terceiro", level: 2 as const }, { id: 'o-manifesto-de-uma-pasta', text: "O manifesto de uma pasta", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Integridade"}
      description={"SRI para o script de CDN, o manifesto de uma pasta, e o manifesto assinado que denuncia a troca conjunta."}
      href={"/docs/seguranca/integridade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
