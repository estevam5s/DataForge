// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ffi_c.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "FFI: o mapa",
  description: "Item por item da parte 6 da referência Deep Tech — C/C++, ponteiros crus, callbacks e bibliotecas dinâmicas — cruzado com o que o DataForge tem.",
};

const blocos: Bloco[] = [
  {"p": "A sexta parte de uma referência Deep Tech cobre interoperabilidade com C/C++, ponteiros crus, callbacks e bibliotecas dinâmicas. Quase tudo isso existe aqui — porque FFI é sobre **protocolo de chamada**, e isso não depende de a linguagem ser compilada."},
  {"h2": "26 · Interoperabilidade C/C++"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["FFI, C function calls", "`C.carregar(…)` e `lib.funcao(nome, [tipos], retorno)`", "[Chamar C](/docs/ffi/c)"], ["C structs, unions", "`C.estrutura`, `C.uniao` — com tamanho, alinhamento e deslocamentos", "[Chamar C](/docs/ffi/c)"], ["C enums", "`C.enumeracao({…})`: inteiro com nome, que é o que atravessa", "[Chamar C](/docs/ffi/c)"], ["data layout, ABI compatibility", "vem do `ctypes`, que segue a ABI da plataforma", "[Chamar C](/docs/ffi/c)"], ["calling conventions", "a padrão (`cdecl`) é a que o `ctypes` usa; `stdcall` do Windows **não** está exposto", "—"], ["C++ interoperability, name mangling", "**só via `extern \"C\"`**: o nome decorado do C++ não é estável entre compiladores, e resolvê-lo seria adivinhar", "[Chamar C](/docs/ffi/c)"], ["headers, bindings automáticos", "**não existem**: não há leitor de `.h`. A assinatura é declarada à mão — e declarar é o que impede o erro silencioso", "—"]]}},
  {"h2": "27 · Ponteiros crus"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["`*mut T` / `*const T`", "`C.ponteiro(alvo, tipo)` — um só, sem distinção de mutabilidade", "[Ponteiros](/docs/ffi/ponteiros)"], ["pointer arithmetic", "`p.deslocar(n)` (itens) e `p.deslocar_bytes(n)`", "[Ponteiros](/docs/ffi/ponteiros)"], ["dereference", "`p.ler()` e `p.escrever(v)`, no tipo declarado", "[Ponteiros](/docs/ffi/ponteiros)"], ["raw memory, manual allocation/deallocation", "`C.alocar`, `C.liberar`, `C.copiar`, `C.de_bytes`, `C.para_bytes`", "[Ponteiros](/docs/ffi/ponteiros)"], ["memory alignment", "`C.alinhamento_de(tipo)` e `Molde.alinhamento()`", "[Chamar C](/docs/ffi/c)"], ["`unsafe` blocks", "**não existem**: não há bloco a marcar. O módulo inteiro é a fronteira insegura, e a documentação diz isso em vez de espalhar uma palavra", "—"]]}},
  {"h2": "28 · Callbacks cross-language"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["funções como callbacks", "`C.retorno_de_chamada(acao, [tipos], retorno)`", "[Callbacks](/docs/ffi/callbacks)"], ["closures", "a ação leva o fechamento; o C não sabe, e não precisa saber", "[Callbacks](/docs/ffi/callbacks)"], ["function pointers", "`cb.endereco()`, e o próprio `cb` passa como `ponteiro`", "[Callbacks](/docs/ffi/callbacks)"], ["context pointers", "declare um `ponteiro` a mais na assinatura", "[Callbacks](/docs/ffi/callbacks)"], ["callback lifecycle", "explícito: `vivo()` / `soltar()` — um callback coletado derruba o processo", "[Callbacks](/docs/ffi/callbacks)"], ["static trampolines", "o `ctypes` monta; não há o que escrever", "—"]]}},
  {"h2": "29 · Bibliotecas dinâmicas"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["`dlopen`, runtime loading", "`C.carregar(nome_ou_caminho)`", "[Chamar C](/docs/ffi/c)"], ["`dlsym`, symbol resolution", "`lib.tem(nome)` e `lib.funcao(nome, …)`, com erro que nomeia o símbolo", "[Chamar C](/docs/ffi/c)"], [".so, .dylib, .dll", "os três, pelo mesmo `carregar`; a busca usa o mecanismo do sistema", "[Chamar C](/docs/ffi/c)"], ["símbolos do próprio processo", "`C.do_processo()` — o `dlopen(NULL)`", "[Chamar C](/docs/ffi/c)"], ["static linking", "**não se aplica**: não há binário a ligar — o DataForge é interpretado", "—"], ["plugin architectures", "duas formas: `.so` carregado com `C.carregar`, e [plugin do `check`](/docs/metaprogramacao/plugins) escrito em DataForge", "[Plugins](/docs/metaprogramacao/plugins)"]]}},
  {"h2": "O resumo honesto"},
  {"p": "Esta é a parte com a **maior cobertura** de todas até aqui: das quatro seções, três estão quase inteiras, e a quarta (C/C++) só deixa de fora o que depende de ler cabeçalho ou de decodificar nome de C++ — duas coisas que, feitas por adivinhação, produziriam exatamente o tipo de erro que FFI já tem demais."},
  {"callout": {"tipo": "atencao", "titulo": "A regra que vale para o módulo inteiro", "texto": "Nada aqui é seguro, e o módulo não finge. Ponteiro cru, aritmética de endereço e `liberar` são ferramentas de quem sabe o que está fazendo. O que dá para conferir sem custo — ponteiro nulo, tipo desconhecido, símbolo ausente, aridade errada — é conferido; o resto é responsabilidade de quem chama. Para não depender de disciplina, junte com [`Arcane.Posse`](/docs/memoria/posse): o bloco sai no fim do escopo, inclusive quando o corpo falha."}},
];

const headings = [{ id: '26-interoperabilidade-cc', text: "26 · Interoperabilidade C/C++", level: 2 as const }, { id: '27-ponteiros-crus', text: "27 · Ponteiros crus", level: 2 as const }, { id: '28-callbacks-cross-language', text: "28 · Callbacks cross-language", level: 2 as const }, { id: '29-bibliotecas-dinamicas', text: "29 · Bibliotecas dinâmicas", level: 2 as const }, { id: 'o-resumo-honesto', text: "O resumo honesto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"FFI: o mapa"}
      description={"Item por item da parte 6 da referência Deep Tech — C/C++, ponteiros crus, callbacks e bibliotecas dinâmicas — cruzado com o que o DataForge tem."}
      href={"/docs/ffi/mapa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
