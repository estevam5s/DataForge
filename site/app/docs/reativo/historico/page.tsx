// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/reativo_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Desfazer e refazer",
  description: "Um histórico que acompanha o sinal sem que quem escreve saiba — e o lote que vira um passo só.",
};

const blocos: Bloco[] = [
  {"p": "Desfazer costuma ser escrito como uma pilha de comandos inversos, e cada comando novo precisa lembrar de empilhar o seu. `R.historico` inverte isso: ele **observa** o sinal e anota cada valor anterior. Quem escreve no sinal não sabe que existe desfazer — e por isso não tem como esquecer dele."},
  { code: `adopt Arcane.Reativo as R

texto := R.sinal("")
h := R.historico(texto)

texto.escrever("O")
texto.escrever("Ol")
texto.escrever("Olá")

h.desfazer()
assert texto.ler() is "Ol"
h.desfazer()
assert texto.ler() is "O"
h.refazer()
assert texto.ler() is "Ol"
assert h.passos() is {"desfazer": 2, "refazer": 1}

texto.escrever("Oi")                 // escrever algo novo...
assert not h.pode_refazer()          // ...apaga o que dava para refazer`, lang: 'df' },
  {"h2": "Um lote é um passo"},
  {"p": "Colar um parágrafo escreve várias vezes; desfazer a colagem deveria voltar **tudo**. Dentro de `R.lote`, as escritas viram uma notificação só — e o histórico anota um passo só:"},
  { code: `adopt Arcane.Reativo as R

doc := R.sinal("")
h := R.historico(doc)

action colar():
    doc.escrever("Primeira linha")
    doc.escrever("Primeira linha\\nSegunda linha")

R.lote(colar)
assert h.passos()["desfazer"] is 1
h.desfazer()
assert doc.ler() is ""`, lang: 'df' },
  {"list": ["**Limite**: `R.historico(sinal, 100)` guarda até 100 passos e descarta o mais velho — sem teto, editar por horas vira memória.", "**Só de sinal**: um derivado não se escreve, e \"desfazer\" nele seria desfazer nas fontes — recusado na criação.", "**`h.parar()`** desliga o histórico quando a tela fecha."]},
];

const headings = [{ id: 'um-lote-e-um-passo', text: "Um lote é um passo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Desfazer e refazer"}
      description={"Um histórico que acompanha o sinal sem que quem escreve saiba — e o lote que vira um passo só."}
      href={"/docs/reativo/historico"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
