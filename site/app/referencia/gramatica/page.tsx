import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Gramática (EBNF)",
  description: "A gramática formal da linguagem, em notação EBNF.",
};

const blocos: Bloco[] = [
  {"p": "Esta é a gramática que o [parser](/referencia/arquitetura) implementa, extraída da referência oficial do repositório."},
  {"h2": "Notação"},
  {"table": {"head": ["Símbolo", "Significa"], "rows": [["`{ x }`", "zero ou mais repetições de `x`"], ["`[ x ]`", "`x` é opcional"], ["`x | y`", "`x` ou `y`"], ["`\"literal\"`", "texto exato"], ["`INDENT` / `DEDENT`", "tokens que o lexer emite ao mudar o nível de indentação"]]}},
  {"h2": "A gramática"},
  { code: `programa       = { instrução } ;

instrução      = decl_var | decl_destr | decl_steady | decl_shadow | decl_static
               | decl_ação | decl_blueprint | decl_trait
               | decl_record | decl_enum
               | adopt | relay
               | condicional | seleção_match | laço
               | bloco_erro | concorrência
               | out | emit | yield | halt | skip | trigger | assert
               | delete | wait | inspect | expressão ;

decl_var       = identificador [ ":" tipo ] ":=" expressão
               | alvo ( "+=" | "-=" | "*=" | "/=" | "%=" ) expressão ;
decl_destr     = alvos_pos ":=" expressão { "," expressão }
               | "{" alvos_nom "}" ":=" expressão ;
alvos_pos      = alvo_destr { "," alvo_destr } ;
alvos_nom      = alvo_destr { "," alvo_destr } ;
alvo_destr     = [ "..." ] identificador ;

decl_record    = "record" identificador ":" NEWLINE INDENT
                 { campo_record | decl_ação } DEDENT ;
campo_record   = identificador ":" tipo [ ":=" expressão ] NEWLINE ;
decl_enum      = "enum" identificador ":" NEWLINE INDENT
                 { membro_enum | decl_ação } DEDENT ;
membro_enum    = identificador [ ":=" expressão ] NEWLINE ;
decl_steady    = "steady" identificador ":=" expressão ;
decl_shadow    = "shadow" identificador ":=" expressão ;
decl_static    = "static" identificador ":=" expressão ;

decl_ação      = { "mark" "@" identificador [ "(" args ")" ] }
                 [ "async" | "stream" ] "action" identificador
                 "(" [ params ] ")" [ "->" tipo ] ":" bloco ;
params         = param { "," param } ;
param          = identificador [ ":" tipo ] [ ":=" expressão ] ;

decl_blueprint = "blueprint" identificador [ "(" nomes ")" ]
                 [ "extends" nomes ] [ "with" nomes ] ":" bloco ;
decl_trait     = "trait" identificador ":" bloco ;

adopt          = "adopt" caminho [ "as" identificador ]
               | "adopt" caminho "." seleção
               | "adopt" seleção "from" caminho ;
seleção        = "{" sel_item { "," sel_item } "}" ;
sel_item       = identificador [ "as" identificador ] ;
relay          = "relay" nomes ;
emit           = "emit" expressão { "," expressão } ;

condicional    = "given" expressão ":" bloco
                 { "orif" expressão ":" bloco }
                 [ "otherwise" ":" bloco ] ;
seleção_match  = "match" expressão ":" NEWLINE INDENT
                 { "point" padrão [ "when" expressão ] ":" bloco }
                 [ "default" ":" bloco ] DEDENT ;

padrão         = padrão_alt [ "as" identificador ] ;
padrão_alt     = padrão_base { "or" padrão_base } ;
padrão_base    = literal
               | "_"
               | identificador                          (* minúscula: captura *)
               | Identificador                          (* Maiúscula: tipo *)
               | Identificador "(" [ sub_padrões ] ")"  (* record por posição/nome *)
               | Identificador { "." nome }             (* valor nomeado *)
               | "[" [ padrão_seq ] "]"
               | "{" [ padrão_mapa ] "}" ;
sub_padrões    = ( padrão | identificador ":=" padrão )
                 { "," ( padrão | identificador ":=" padrão ) } ;
padrão_seq     = ( padrão | "..." [ identificador ] )
                 { "," ( padrão | "..." [ identificador ] ) } ;
padrão_mapa    = ( primário ":" padrão | "..." [ identificador ] )
                 { "," ( primário ":" padrão | "..." [ identificador ] ) } ;

laço           = "cycle" identificador "from" expressão "to" expressão
                     [ "step" expressão ] ":" bloco
               | "cycle" identificador "in" expressão ":" bloco
               | "persist" expressão ":" bloco
               | "perform" ":" bloco "persist" expressão ;

bloco_erro     = "monitor" ":" bloco
                 [ "handle" [ identificador "as" ] identificador ":" bloco ]
                 [ "ensure" ":" bloco ]
               | "retry" expressão ":" bloco
                 [ ( "handle" | "recover" ) [ identificador ] ":" bloco ]
               | "guard" expressão ( [ "," expressão ] | "otherwise" ":" bloco )
               | "validate" expressão ( [ "," expressão ] | "otherwise" ":" bloco )
               | "propagate" [ expressão ]
               | "defer" ":" bloco ;

concorrência   = "thread" ":" bloco
               | "parallel" ":" bloco
               | "channel" identificador
               | "observe" identificador "in" expressão ":" bloco
               | "pulse" expressão [ "," expressão ] ;

expressão      = pipeline ;
pipeline       = ternário { ">>" op_pipeline } ;
ternário       = coalescência [ "given" coalescência "otherwise" ternário ] ;
coalescência   = ou { "??" ou } ;
op_pipeline    = "sift"    ( identificador ":" ou | identificador )
               | "morph"   ( identificador ":" ou | identificador )
               | "distill" ( identificador [ "," ] identificador ":" ou [ ou ]
                           | identificador ou ) ;
ou             = e { "or" e } ;
e              = negação { "and" negação } ;
negação        = [ "not" ] comparação ;
comparação     = adição ( [ "not" ] "in" adição
                        | { op_comp adição } ) ;
adição         = multiplicação { ( "+" | "-" ) multiplicação } ;
multiplicação  = unário { ( "*" | "/" | "%" | "~/" | "//" ) unário } ;
unário         = ( "+" | "-" | "not" ) unário | potência ;
potência       = posfixo [ "**" unário ] ;
posfixo        = primário { "." nome | "?." nome
                          | "[" índice "]" | "(" args ")"
                          | "with" dicionário } ;
índice         = expressão | [expressão] ":" [expressão] [ ":" [expressão] ] ;

primário       = literal | interpolada | identificador | "(" expressão ")"
               | lista | dicionário | lambda
               | compreensão_lista | compreensão_vault
               | "self" | "root"
               | ( "spawn" | "forge" ) posfixo
               | "typeof" unário
               | "cast" unário "as" identificador
               | "await" expressão
               | "stream" ou
               | "in" [ texto ]
               | "frame" primário
               | "train" posfixo "using" expressão
               | "predict" posfixo "using" expressão ;

lambda         = "lambda" [ params_lambda ] ( ":" | "=>" ) ou ;
interpolada    = "$" '"' { texto | "{" expressão "}" } '"' ;
lista          = "[" [ elemento { "," elemento } ] "]" ;
elemento       = expressão | "..." expressão ;
dicionário     = "{" [ par_ou_spread { "," par_ou_spread } ] "}" ;
par_ou_spread  = expressão ":" expressão | "..." expressão ;

compreensão_lista = "[" expressão cláusulas "]" ;
compreensão_vault = "{" expressão ":" expressão cláusulas "}" ;
cláusulas      = cláusula { cláusula } ;
cláusula       = "cycle" identificador { "," identificador }
                 "in" expressão [ "given" expressão ] ;

args           = ( expressão | "..." expressão
                 | identificador ":=" expressão )
                 { "," ( expressão | "..." expressão
                       | identificador ":=" expressão ) } ;

bloco          = NEWLINE INDENT { instrução } DEDENT ;`, lang: 'text', title: `EBNF` },
  {"h2": "Indentação"},
  {"p": "O lexer emite `INDENT` e `DEDENT` ao entrar e sair de um bloco, como Python. Isso é o que permite blocos sem chaves. Duas regras adicionais:"},
  {"list": ["Dentro de `(`, `[`, `{` a indentação é ignorada — expressões podem quebrar linha livremente.", "Uma linha começando com `.` ou `>>` **continua** a linha anterior, permitindo encadear métodos e pipelines em várias linhas."]},
  {"callout": {"tipo": "atencao", "texto": "Tabs são erro (`SyncError`). A convenção são 4 espaços por nível."}},
];

const headings = [{ id: 'notacao', text: "Notação", level: 2 as const }, { id: 'a-gramatica', text: "A gramática", level: 2 as const }, { id: 'indentacao', text: "Indentação", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Gramática (EBNF)"}
      description={"A gramática formal da linguagem, em notação EBNF."}
      href={"/referencia/gramatica"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
