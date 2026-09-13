// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "12 · Records e enums",
  description: "6 exercícios: imutabilidade, 'with' e enums com valor.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 12`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[127](#127-records)", "**Records**", "declare um record, construa instancias e comprove a igualdade estrutural."], ["[128](#128-imutabilidade-e-with)", "**Imutabilidade e with**", "comprove que um record nao muda, e crie copias alteradas com with."], ["[129](#129-records-com-metodos)", "**Records com metodos**", "adicione comportamento a um record sem abrir mao da imutabilidade."], ["[130](#130-enums)", "**Enums**", "declare um conjunto fechado de valores e use seus membros com seguranca."], ["[131](#131-enums-com-valores)", "**Enums com valores**", "associe dados a cada membro e converta de ida e volta."], ["[132](#132-enums-com-match)", "**Enums com match**", "use pattern matching para tratar cada membro e garantir cobertura."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "127 · Records"},
  {"p": "**Enunciado.** declare um record, construa instancias e comprove a igualdade estrutural."},
  { code: `record Usuario:
    nome: String
    idade: Integer
    email: String := "sem@email"

// Construcao posicional e nomeada
a := Usuario("Ana", 30)
b := Usuario(nome := "Bruno", idade := 25, email := "b@x.com")

out a
out b
out a.nome, a.idade, a.email

// Igualdade e estrutural: mesmos campos, mesmo valor
out Usuario("Ana", 30) is Usuario("Ana", 30)
out Usuario("Ana", 30) is Usuario("Ana", 31)

assert a.email is "sem@email", "campo com valor padrao"
assert Usuario("Ana", 30) is Usuario("Ana", 30), "igualdade estrutural"
assert Usuario("Ana", 30) isnt Usuario("Ana", 31), "campos diferentes"
assert typeof(a) is "Usuario", "typeof devolve o nome do record"

// Campo obrigatorio ausente
faltou := no
monitor:
    Usuario("Carla")
handle e:
    faltou := yes
    out "erro:", e.message
assert faltou is yes, "idade e obrigatoria"

// Tipo errado no campo
tipo_errado := no
monitor:
    Usuario(42, 30)
handle e:
    tipo_errado := yes
    out "erro:", e.message
assert tipo_errado is yes, "nome precisa ser String"`, lang: 'df', title: `exercicios/12-records-e-enums/127_record_basico.df` },
  {"h3": "Conceitos"},
  {"p": "Um **record** é um agregado de dados nomeados e tipados. Comparando com o que você já conhece:"},
  {"table": {"head": ["Linguagem", "Equivalente"], "rows": [["Python", "`@dataclass(frozen=True)`"], ["TypeScript", "`interface` / `type`"], ["Java", "`record`"], ["Go", "`struct`"], ["Rust", "`struct`"]]}},
  {"p": "**Declaração**"},
  { code: `record Usuario:
    nome: String
    idade: Integer
    email: String := "sem@email"`, lang: 'df' },
  {"p": "Cada campo **exige** um tipo. Um `:=` depois do tipo dá um valor padrão, o que torna o campo opcional na construção."},
  {"p": "**Construção**"},
  {"p": "Duas formas, ambas verificadas:"},
  { code: `Usuario("Ana", 30)                              // posicional
Usuario(nome := "Ana", idade := 30)             // nomeada`, lang: 'df' },
  {"p": "A forma nomeada é preferível quando há mais de três campos: `Usuario(\"Ana\", 30, \"a@x.com\", yes, 2)` é ilegível."},
  {"h3": "Igualdade estrutural"},
  {"p": "Esta é a diferença central em relação a um `blueprint`:"},
  { code: `Usuario("Ana", 30) is Usuario("Ana", 30)    // yes`, lang: 'df' },
  {"p": "Duas instâncias com os mesmos valores **são iguais**, mesmo sendo objetos distintos. Blueprints comparam por identidade; records, por conteúdo."},
  {"p": "Isso é o que torna records úteis como chaves, como valores em conjuntos e em comparações de teste."},
  {"h3": "Quando usar record e quando usar blueprint"},
  {"table": {"head": ["Use `record`", "Use `blueprint`"], "rows": [["dados sem comportamento próprio", "objetos com estado que muda"], ["igualdade por valor", "identidade importa"], ["imutável", "precisa mutar campos"], ["sem herança", "herança, traits, polimorfismo"]]}},
  {"h3": "Saída esperada"},
  { code: `Usuario(nome: Ana, idade: 30, email: sem@email)
Usuario(nome: Bruno, idade: 25, email: b@x.com)
Ana 30 sem@email
yes
no
erro: Record 'Usuario' is missing field 'idade'
erro: field 'nome' of record 'Usuario' declared as String but got Integer`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Adicione `ativo: Boolean := yes` e veja que o código existente continua válido.", "Rode `dataforge check`: ele aponta `Usuario(\"Carla\")` **antes** de executar."]},
  {"h2": "128 · Imutabilidade e with"},
  {"p": "**Enunciado.** comprove que um record nao muda, e crie copias alteradas com with."},
  { code: `record Conta:
    titular: String
    saldo: Number

original := Conta("Ana", 1000)

// Tentar mudar um campo e erro
bloqueou := no
monitor:
    original.saldo := 2000
handle e:
    bloqueou := yes
    out e.message

assert bloqueou is yes, "record e imutavel"
assert original.saldo is 1000, "o valor original nao mudou"

// 'with' produz uma copia com os campos trocados
depositado := original with {"saldo": original.saldo + 500}
out original
out depositado

assert original.saldo is 1000, "o original continua intacto"
assert depositado.saldo is 1500, "a copia tem o novo valor"
assert depositado.titular is "Ana", "os demais campos vieram junto"

// Encadear transformacoes lendo de cima para baixo
action depositar(conta, valor):
    yield conta with {"saldo": conta.saldo + valor}

action sacar(conta, valor):
    guard valor smaller_eq conta.saldo, "saldo insuficiente"
    yield conta with {"saldo": conta.saldo - valor}

final := sacar(depositar(depositar(original, 200), 300), 100)
out final
assert final.saldo is 1400, "1000 +200 +300 -100"
assert original.saldo is 1000, "nada disso tocou no original"

// Campo inexistente no with
erro := no
monitor:
    original with {"limite": 5000}
handle e:
    erro := yes
    out e.message
assert erro is yes, "with recusa campo que nao existe"`, lang: 'df', title: `exercicios/12-records-e-enums/128_record_imutavel.df` },
  {"h3": "Conceitos"},
  {"p": "Um record é **imutável**. Isso não é uma restrição arbitrária: é o que permite a igualdade estrutural funcionar de forma confiável e o que elimina uma classe inteira de bugs — o valor que você guardou não muda debaixo dos seus pés."},
  { code: `original.saldo := 2000
// erro: Record 'Conta' is immutable: cannot assign to 'saldo'.`, lang: 'df' },
  {"h3": "O operador `with`"},
  {"p": "Para \"mudar\" um record você deriva um novo:"},
  { code: `depositado := original with {"saldo": original.saldo + 500}`, lang: 'df' },
  {"p": "Leia como: *\"o mesmo que `original`, mas com `saldo` valendo outra coisa\"*."},
  {"table": {"head": ["Linguagem", "Equivalente"], "rows": [["Python", "`dataclasses.replace(obj, saldo=…)`"], ["JavaScript", "`{...obj, saldo: …}`"], ["Rust", "`Conta { saldo: …, ..original }`"], ["Elixir", "`%{original \\", "saldo: …}`"]]}},
  {"p": "O `with` também **valida os nomes**: pedir um campo que não existe é erro, não silêncio. Compare com o spread de JavaScript, onde `{...obj, sldo: 1}` cria alegremente um campo novo com o nome digitado errado."},
  {"h3": "Transformações encadeadas"},
  {"p": "Como cada operação devolve um record novo, elas compõem naturalmente:"},
  { code: `final := sacar(depositar(depositar(original, 200), 300), 100)`, lang: 'df' },
  {"p": "Nenhuma das chamadas tocou em `original`. Se algo der errado no meio, você ainda tem o estado anterior intacto — que é exatamente o que se quer numa transação."},
  {"h3": "Um detalhe de leitura"},
  {"p": "Chamadas aninhadas se leem de dentro para fora, o que cansa. Com pipelines fica mais direto:"},
  { code: `final := [original]
    >> morph c: depositar(c, 200)
    >> morph c: depositar(c, 300)`, lang: 'df' },
  {"h3": "Saída esperada"},
  { code: `Record 'Conta' is immutable: cannot assign to 'saldo'. Build a changed copy with "registro with {'saldo': valor}".
Conta(titular: Ana, saldo: 1000)
Conta(titular: Ana, saldo: 1500)
Conta(titular: Ana, saldo: 1400)
Record 'Conta' has no field(s): limite`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Faça `sacar` retirar mais do que o saldo e veja o `guard` agir.", "Guarde cada estado intermediário numa lista para ter o histórico completo."]},
  {"h2": "129 · Records com metodos"},
  {"p": "**Enunciado.** adicione comportamento a um record sem abrir mao da imutabilidade."},
  { code: `record Retangulo:
    largura: Number
    altura: Number

    action area():
        yield self.largura * self.altura

    action perimetro():
        yield 2 * (self.largura + self.altura)

    action e_quadrado():
        yield self.largura is self.altura

    action escalar(fator):
        yield Retangulo(self.largura * fator, self.altura * fator)

    action toString():
        yield $"{self.largura}x{self.altura}"

r := Retangulo(3, 4)
out r
out $"area: {r.area()}  perimetro: {r.perimetro()}"
out $"quadrado? {r.e_quadrado()}"

dobro := r.escalar(2)
out $"dobrado: {dobro} com area {dobro.area()}"

assert r.area() is 12, "area"
assert r.perimetro() is 14, "perimetro"
assert r.e_quadrado() is no, "3x4 nao e quadrado"
assert Retangulo(5, 5).e_quadrado() is yes, "5x5 e quadrado"
assert dobro.area() is 48, "area dobrada em cada lado quadruplica"
assert str(r) is "3x4", "toString"
assert r.largura is 3, "escalar nao alterou o original"

// Metodos convivem com pattern matching
action classificar(fig):
    match fig:
        point Retangulo(l, a) when l is a:
            yield "quadrado"
        point Retangulo:
            yield "retangulo"
        default:
            yield "outra forma"

out classificar(Retangulo(2, 2)), classificar(r), classificar(42)
assert classificar(Retangulo(2, 2)) is "quadrado", "pattern com guarda"`, lang: 'df', title: `exercicios/12-records-e-enums/129_record_com_metodos.df` },
  {"h3": "Conceitos"},
  {"p": "Um record pode ter métodos. A regra é simples e não tem exceção: **um método pode ler `self`, nunca escrever**."},
  { code: `record Retangulo:
    largura: Number
    altura: Number

    action area():
        yield self.largura * self.altura`, lang: 'df' },
  {"h3": "Métodos que \"modificam\""},
  {"p": "Quando um método precisaria mudar o estado, ele devolve um record novo:"},
  { code: `action escalar(fator):
    yield Retangulo(self.largura * fator, self.altura * fator)`, lang: 'df' },
  {"p": "Chamar `r.escalar(2)` não altera `r` — devolve outro retângulo. Esse é o mesmo padrão de `\"abc\".upper()` em qualquer linguagem: a string original continua lá."},
  {"h3": "`toString`"},
  {"p": "O método `toString` é especial: o runtime o chama em `out` e em `str()`."},
  { code: `action toString():
    yield $"{self.largura}x{self.altura}"`, lang: 'df' },
  {"p": "Sem ele, `out r` mostraria `Retangulo(largura: 3, altura: 4)`. Com ele, `3x4`."},
  {"h3": "Records em pattern matching"},
  {"p": "Records se desmontam em padrões, e é aí que o desenho todo se paga:"},
  { code: `match fig:
    point Retangulo(l, a) when l is a:
        yield "quadrado"
    point Retangulo:
        yield "retangulo"`, lang: 'df' },
  {"p": "`point Retangulo(l, a)` faz três coisas de uma vez: verifica o tipo, extrai os campos por posição e liga cada um a um nome. O `when` acrescenta uma condição."},
  {"h3": "Saída esperada"},
  { code: `3x4
area: 12  perimetro: 14
quadrado? no
dobrado: 6x8 com area 48
quadrado retangulo outra forma`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Adicione `action diagonal()` usando `sqrt`.", "Faça `escalar` recusar fator zero ou negativo com `guard`.", "Acrescente `point Retangulo(l, a) when l bigger a: yield \"deitado\"` e veja onde"]},
  {"p": "colocá-lo para que seja alcançado."},
  {"h2": "130 · Enums"},
  {"p": "**Enunciado.** declare um conjunto fechado de valores e use seus membros com seguranca."},
  { code: `enum Status:
    Rascunho
    Publicado
    Arquivado

out Status.Rascunho
out Status.Publicado.name, Status.Publicado.value, Status.Publicado.index

// Membros comparam por identidade dentro do enum
out Status.Rascunho is Status.Rascunho
out Status.Rascunho is Status.Publicado

assert Status.Rascunho is Status.Rascunho, "mesmo membro"
assert Status.Rascunho isnt Status.Publicado, "membros diferentes"
assert Status.Publicado.index is 1, "indice segue a ordem de declaracao"
assert typeof(Status.Rascunho) is "Status", "typeof devolve o enum"

// Utilitarios do enum
out Status.names()
out Status.count()
out Status.has("Publicado"), Status.has("Removido")

assert Status.names() is ["Rascunho", "Publicado", "Arquivado"], "nomes na ordem"
assert Status.count() is 3, "tres membros"
assert Status.has("Publicado") is yes, "membro existe"
assert Status.has("Removido") is no, "membro inexistente"

// Membro inexistente e erro, nao void
erro := no
monitor:
    out Status.Removido
handle e:
    erro := yes
    out e.message
assert erro is yes, "acessar membro inexistente dispara"

// Percorrer todos
cycle s in Status.members():
    out $"  {s.index}: {s.name}"`, lang: 'df', title: `exercicios/12-records-e-enums/130_enum_basico.df` },
  {"h3": "Conceitos"},
  {"p": "Um **enum** define um conjunto fechado. Comparando:"},
  {"table": {"head": ["Linguagem", "Equivalente"], "rows": [["Python", "`class Status(Enum)`"], ["TypeScript", "`enum Status { … }`"], ["Rust", "`enum Status { … }` (sem payload, por ora)"], ["Java", "`enum Status { … }`"]]}},
  { code: `enum Status:
    Rascunho
    Publicado
    Arquivado`, lang: 'df' },
  {"h3": "O problema que ele resolve"},
  {"p": "Sem enum, estados viram texto solto:"},
  { code: `pedido := {"status": "publicado"}
given pedido["status"] is "Publicado":     // nunca entra: caixa diferente`, lang: 'df' },
  {"p": "Um erro de digitação vira um `no` silencioso. Com enum, `Status.Publicad` é erro na hora — e o `dataforge check` acha antes mesmo de rodar."},
  {"h3": "Cada membro carrega três coisas"},
  { code: `Status.Publicado.name     // "Publicado"  — o identificador
Status.Publicado.value    // "Publicado"  — o valor (padrão = nome)
Status.Publicado.index    // 1            — a posição na declaração`, lang: 'df' },
  {"p": "O `.index` segue a ordem em que você escreveu, o que o torna útil para ordenar: `Rascunho` vem antes de `Publicado`, que vem antes de `Arquivado`."},
  {"h3": "Utilitários"},
  {"table": {"head": ["Chamada", "Devolve"], "rows": [["`Status.names()`", "`[\"Rascunho\", \"Publicado\", \"Arquivado\"]`"], ["`Status.values()`", "os valores"], ["`Status.members()`", "os membros, para percorrer"], ["`Status.count()`", "`3`"], ["`Status.has(\"X\")`", "`yes` / `no`"], ["`Status.from_name(\"X\")`", "o membro, ou `void`"], ["`Status.from_value(v)`", "o membro com aquele valor, ou `void`"]]}},
  {"h3": "Saída esperada"},
  { code: `Status.Rascunho
Publicado Publicado 1
yes
no
[Rascunho, Publicado, Arquivado]
3
yes no
Enum 'Status' has no member 'Removido'. Members: Rascunho, Publicado, Arquivado
  0: Rascunho
  1: Publicado
  2: Arquivado`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Ordene uma lista de status por `.index`.", "Escreva `action proximo(s)` que avança para o próximo membro."]},
  {"h2": "131 · Enums com valores"},
  {"p": "**Enunciado.** associe dados a cada membro e converta de ida e volta."},
  { code: `enum Prioridade:
    Baixa := 1
    Media := 5
    Alta := 10
    Critica := 100

enum Moeda:
    Real := "BRL"
    Dolar := "USD"
    Euro := "EUR"

out Prioridade.Alta.value
out Moeda.Real.value

assert Prioridade.Alta.value is 10, "valor numerico"
assert Moeda.Dolar.value is "USD", "valor textual"

// Converter de valor para membro — util ao ler dados externos
vinda_do_banco := "EUR"
moeda := Moeda.from_value(vinda_do_banco)
out $"{vinda_do_banco} -> {moeda.name}"
assert moeda is Moeda.Euro, "from_value encontra o membro"
assert Moeda.from_value("JPY") is void, "valor desconhecido devolve void"

// Usar os valores para ordenar
tarefas := [
    {"titulo": "revisar", "prio": Prioridade.Baixa},
    {"titulo": "deploy", "prio": Prioridade.Critica},
    {"titulo": "reuniao", "prio": Prioridade.Media}
]

por_urgencia := sorted(tarefas >> morph t: t["prio"].value)
out por_urgencia
assert por_urgencia is [1, 5, 100], "valores ordenados"

// Somar os valores
peso_total := Prioridade.values() >> distill acc, v: acc + v 0
out $"soma dos pesos: {peso_total}"
assert peso_total is 116, "1 + 5 + 10 + 100"

// Escolher com base no valor
action nivel(p):
    given p.value bigger_eq 100:
        yield "largar tudo"
    orif p.value bigger_eq 10:
        yield "hoje ainda"
    otherwise:
        yield "quando der"

out nivel(Prioridade.Critica), nivel(Prioridade.Alta), nivel(Prioridade.Baixa)
assert nivel(Prioridade.Critica) is "largar tudo", "critica"`, lang: 'df', title: `exercicios/12-records-e-enums/131_enum_com_valores.df` },
  {"h3": "Conceitos"},
  {"p": "Um membro pode carregar um valor:"},
  { code: `enum Prioridade:
    Baixa := 1
    Media := 5
    Alta := 10
    Critica := 100`, lang: 'df' },
  {"p": "Sem `:=`, o valor é o próprio nome. Com `:=`, é o que você escrever — número, texto, qualquer coisa."},
  {"h3": "Por que isso importa: a fronteira do sistema"},
  {"p": "Dentro do seu programa você quer `Moeda.Real`. Mas o banco de dados guarda `\"BRL\"`, a API devolve `\"BRL\"`, o CSV tem `\"BRL\"`. O valor é a **ponte** entre os dois mundos:"},
  { code: `vinda_do_banco := "EUR"
moeda := Moeda.from_value(vinda_do_banco)     // Moeda.Euro`, lang: 'df' },
  {"p": "E `from_value` devolve `void` para um valor desconhecido, em vez de inventar um membro. Combinado com `??`, isso vira um padrão limpo:"},
  { code: `moeda := Moeda.from_value(entrada) ?? Moeda.Real`, lang: 'df' },
  {"h3": "Valores numéricos como ordem"},
  {"p": "Quando o valor é um número, ele carrega significado de ordenação:"},
  { code: `sorted(tarefas >> morph t: t["prio"].value)     // [1, 5, 100]`, lang: 'df' },
  {"p": "Isso é mais expressivo do que depender de `.index`: o `.index` reflete a ordem de declaração, o `.value` reflete a ordem de *negócio*. Se amanhã você inserir `Urgente := 50` no meio da lista, os índices mudam mas os pesos não."},
  {"h3": "Comparando com outras linguagens"},
  {"p": "Em TypeScript, `enum Prioridade { Baixa = 1 }` gera um mapeamento bidirecional implícito e `Prioridade[1]` funciona. Em DataForge a conversão é explícita (`from_value`), o que evita a ambiguidade de um enum cujos valores colidem com seus índices."},
  {"h3": "Saída esperada"},
  { code: `10
BRL
EUR -> Euro
[1, 5, 100]
soma dos pesos: 116
largar tudo hoje ainda quando der`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Acrescente `Urgente := 50` e confirme que a ordenação por `.value` continua certa.", "Escreva `action de_texto(t)` usando `from_value(t) ?? Prioridade.Media`."]},
  {"h2": "132 · Enums com match"},
  {"p": "**Enunciado.** use pattern matching para tratar cada membro e garantir cobertura."},
  { code: `enum Semaforo:
    Vermelho := "pare"
    Amarelo := "atencao"
    Verde := "siga"

action acao(luz):
    match luz:
        point Semaforo.Vermelho:
            yield "frear"
        point Semaforo.Amarelo:
            yield "reduzir"
        point Semaforo.Verde:
            yield "acelerar"
        default:
            yield "estado desconhecido"

cycle luz in Semaforo.members():
    out $"{luz.name} ({luz.value}) -> {acao(luz)}"

assert acao(Semaforo.Vermelho) is "frear", "vermelho"
assert acao(Semaforo.Verde) is "acelerar", "verde"
assert acao("qualquer coisa") is "estado desconhecido", "default protege"

// Maquina de estados com enum
enum Pedido:
    Novo
    Pago
    Enviado
    Entregue

steady TRANSICOES := {
    "Novo":["Pago"],
    "Pago":["Enviado"],
    "Enviado":["Entregue"],
    "Entregue":[]
}

action pode_ir(de, para):
    yield para.name in TRANSICOES[de.name]

action avancar(atual):
    permitidos := TRANSICOES[atual.name]
    given len(permitidos) is 0:
        yield void
    yield Pedido.from_name(permitidos[0])

estado := Pedido.Novo
caminho := [estado.name]
persist estado isnt void:
    proximo := avancar(estado)
    given proximo is void:
        halt
    caminho.append(proximo.name)
    estado := proximo

out caminho
assert caminho is ["Novo", "Pago", "Enviado", "Entregue"], "ciclo completo"
assert pode_ir(Pedido.Novo, Pedido.Pago) is yes, "transicao valida"
assert pode_ir(Pedido.Novo, Pedido.Entregue) is no, "transicao invalida"`, lang: 'df', title: `exercicios/12-records-e-enums/132_enum_e_match.df` },
  {"h3": "Conceitos"},
  {"p": "Enum e `match` foram feitos um para o outro:"},
  { code: `match luz:
    point Semaforo.Vermelho:
        yield "frear"
    point Semaforo.Amarelo:
        yield "reduzir"
    point Semaforo.Verde:
        yield "acelerar"
    default:
        yield "estado desconhecido"`, lang: 'df' },
  {"p": "`point Semaforo.Vermelho` é um **padrão de valor**: casa por igualdade com aquele membro específico."},
  {"h3": "Por que manter o `default`"},
  {"p": "DataForge 4.0 ainda não verifica exaustividade (avisar quando um membro ficou de fora está no roadmap). Enquanto isso, o `default` é sua rede: se amanhã alguém adicionar `Semaforo.Piscante`, o programa não silencia — cai num ramo que você controla."},
  {"p": "Um truque útil: faça o `default` **falhar ruidosamente** durante o desenvolvimento."},
  { code: `default:
    trigger $"estado nao tratado: {luz}"`, lang: 'df' },
  {"p": "Assim o membro novo aparece na primeira execução, não na primeira reclamação."},
  {"h3": "Máquina de estados"},
  {"p": "O padrão completo tem três partes:"},
  { code: `enum Pedido:
    Novo
    Pago
    Enviado
    Entregue

steady TRANSICOES := {
    "Novo": ["Pago"],
    "Pago": ["Enviado"],
    "Enviado": ["Entregue"],
    "Entregue": []
}`, lang: 'df' },
  {"p": "1. O **enum** enumera os estados possíveis. 2. A **tabela** declara quais saltos são legítimos. 3. As **ações** só consultam a tabela."},
  {"p": "Nenhum estado inválido é representável, e nenhuma transição inválida é possível. `Entregue` com lista vazia é um estado terminal — o laço para sozinho."},
  {"h3": "`from_name` fecha o ciclo"},
  {"p": "A tabela guarda texto (`\"Pago\"`), mas o programa trabalha com membros. `Pedido.from_name(texto)` converte de volta, devolvendo `void` se o nome não existir."},
  {"h3": "Saída esperada"},
  { code: `Vermelho (pare) -> frear
Amarelo (atencao) -> reduzir
Verde (siga) -> acelerar
[Novo, Pago, Enviado, Entregue]`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Acrescente `Cancelado` e permita `Novo -> Cancelado`.", "Faça `avancar` devolver todos os próximos possíveis em vez do primeiro.", "Troque o `default` por `trigger` e adicione um membro sem tratá-lo."]},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/12-records-e-enums/127_record_basico.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '127-records', text: "127 · Records", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'igualdade-estrutural', text: "Igualdade estrutural", level: 3 as const }, { id: 'quando-usar-record-e-quando-usar-blueprint', text: "Quando usar record e quando usar blueprint", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '128-imutabilidade-e-with', text: "128 · Imutabilidade e with", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-operador-with', text: "O operador `with`", level: 3 as const }, { id: 'transformacoes-encadeadas', text: "Transformações encadeadas", level: 3 as const }, { id: 'um-detalhe-de-leitura', text: "Um detalhe de leitura", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '129-records-com-metodos', text: "129 · Records com metodos", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'metodos-que-modificam', text: "Métodos que \"modificam\"", level: 3 as const }, { id: 'tostring', text: "`toString`", level: 3 as const }, { id: 'records-em-pattern-matching', text: "Records em pattern matching", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '130-enums', text: "130 · Enums", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'o-problema-que-ele-resolve', text: "O problema que ele resolve", level: 3 as const }, { id: 'cada-membro-carrega-tres-coisas', text: "Cada membro carrega três coisas", level: 3 as const }, { id: 'utilitarios', text: "Utilitários", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '131-enums-com-valores', text: "131 · Enums com valores", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'por-que-isso-importa-a-fronteira-do-sistema', text: "Por que isso importa: a fronteira do sistema", level: 3 as const }, { id: 'valores-numericos-como-ordem', text: "Valores numéricos como ordem", level: 3 as const }, { id: 'comparando-com-outras-linguagens', text: "Comparando com outras linguagens", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '132-enums-com-match', text: "132 · Enums com match", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'por-que-manter-o-default', text: "Por que manter o `default`", level: 3 as const }, { id: 'maquina-de-estados', text: "Máquina de estados", level: 3 as const }, { id: 'fromname-fecha-o-ciclo', text: "`from_name` fecha o ciclo", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"12 · Records e enums"}
      description={"6 exercícios: imutabilidade, 'with' e enums com valor."}
      href={"/docs/exercicios/12-records-e-enums"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
