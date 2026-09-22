// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/gramatica_doc.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Gramática — Declarações",
  description: "9 produções: ação, record, enum, blueprint, trait, type. Cada exemplo é aceito pelo parser.",
};

const blocos: Bloco[] = [
  {"p": "Declarações dão nome a algo que dura: uma ação, um tipo, um molde de objeto. Duas de topo com o mesmo nome no mesmo arquivo viram aviso — a primeira não tem como ser alcançada."},
  {"table": {"head": ["Produção", "Nós que ela produz"], "rows": [["`action`", "`ActionDeclaration`, `YieldStatement`"], ["`stream`", "`EmitStatement`"], ["`record`", "`RecordDeclaration`"], ["`enum`", "`EnumDeclaration`"], ["`blueprint`", "`BlueprintDeclaration`"], ["`trait`", "`TraitDeclaration`"], ["`type`", "`TypeDeclaration`"], ["`shadow_static`", "`ShadowDeclaration`, `StaticDeclaration`"], ["`root`", "`BlueprintDeclaration`"]]}},
  {"h2": "action"},
  { code: `acao          = [ "async" | "stream" ] "action" nome [ genericos ]
                "(" [ parametros ] ")" [ "->" tipo ] ":" bloco ;
parametro     = nome [ ":" tipo ] [ ":=" expressao ] ;`, lang: 'text' },
  { code: `action somar(a: Integer, b := 1) -> Integer:
    yield a + b`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "`yield` devolve e **encerra**; para uma sequência, `stream action` + `emit`."}},
  {"h2": "stream"},
  { code: `produzir      = "emit" expressao ;`, lang: 'text' },
  { code: `stream action nat():
    n := 0
    persist yes:
        emit n
        n += 1`, lang: 'df' },
  {"h2": "record"},
  { code: `record        = "record" nome [ genericos ] ":" NEWLINE INDENT
                { campo | acao } DEDENT ;
campo         = nome ":" tipo [ ":=" expressao ] NEWLINE ;`, lang: 'text' },
  { code: `record Ponto:
    x: Integer
    y: Integer`, lang: 'df' },
  {"h2": "enum"},
  { code: `enum          = "enum" nome ":" NEWLINE INDENT { membro | acao } DEDENT ;
membro        = nome [ ":=" expressao ] NEWLINE ;`, lang: 'text' },
  { code: `enum Cor:
    Verde
    Azul := "a"`, lang: 'df' },
  {"h2": "blueprint"},
  { code: `blueprint     = { modificador } "blueprint" nome [ genericos ] [ "(" campos ")" ]
                [ "extends" nome ] [ "with" nome { "," nome } ] ":" bloco ;`, lang: 'text' },
  { code: `blueprint Forma:
    action area():
        yield 0

blueprint Quadrado(lado) extends Forma:
    action area():
        yield self.lado ** 2`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "`self` sempre: `x` sem `self.` lê a variável de fora."}},
  {"h2": "trait"},
  { code: `trait         = "trait" nome ":" NEWLINE INDENT { assinatura | acao } DEDENT ;`, lang: 'text' },
  { code: `trait Mede:
    action medir()`, lang: 'df' },
  {"h2": "type"},
  { code: `tipo_nomeado  = [ "opaque" ] "type" nome [ genericos ] ":=" tipo
                [ "where" expressao ] ;`, lang: 'text' },
  { code: `type Id := Integer
type Positivo := Integer where valor bigger 0
opaque type Cpf := String where len(valor) is 11`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "`type`, `opaque` e `where` são contextuais: `type := 3` continua valendo."}},
  {"h2": "shadow_static"},
  { code: `sombra        = "shadow" nome ":=" expressao ;
estatico      = "static" nome ":=" expressao ;`, lang: 'text' },
  { code: `x := 1
action f():
    shadow x := 99
    yield x
blueprint Config:
    static padrao := "claro"`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "Dentro de uma ação, `:=` escreve o nome de fora quando ele existe; `shadow` declara uma cópia local de propósito."}},
  {"h2": "root"},
  { code: `mae           = "root" "." nome "(" [ argumentos ] ")" ;`, lang: 'text' },
  { code: `blueprint Base:
    action nome():
        yield "base"

blueprint Filha extends Base:
    action nome():
        yield root.nome() + "+filha"`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O que engana", "texto": "`root` segue a MRO a partir de quem **declarou** o método — com três níveis de herança, o pai da instância entraria em laço."}},
  {"p": "Estas produções saem de `dataforge/gramatica.py`. No terminal: `dataforge gramatica declaracoes`. Volte para [a gramática](/docs/referencia/gramatica)."},
];

const headings = [{ id: 'action', text: "action", level: 2 as const }, { id: 'stream', text: "stream", level: 2 as const }, { id: 'record', text: "record", level: 2 as const }, { id: 'enum', text: "enum", level: 2 as const }, { id: 'blueprint', text: "blueprint", level: 2 as const }, { id: 'trait', text: "trait", level: 2 as const }, { id: 'type', text: "type", level: 2 as const }, { id: 'shadowstatic', text: "shadow_static", level: 2 as const }, { id: 'root', text: "root", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Gramática — Declarações"}
      description={"9 produções: ação, record, enum, blueprint, trait, type. Cada exemplo é aceito pelo parser."}
      href={"/docs/referencia/gramatica/declaracoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
