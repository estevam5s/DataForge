// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/reflexo.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Reflexo",
  description: "Reflexão sobre blueprints, contratos e objetos: campos, métodos, modificadores, MRO, herdeiros, anotações, invocação por nome respeitando a visibilidade, criação de tipos em execução e diagrama de classes em Mermaid.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (38)"},
  {"table": {"head": ["Assinatura"], "rows": [["`anotacoes(alvo, membro=None)`"], ["`blueprints()`"], ["`campos(alvo)`"], ["`contratos(alvo)`"], ["`criar_blueprint(nome, definicao=None)`"], ["`cumpre(obj, contrato)`"], ["`definir_metodo(molde, nome, acao)`"], ["`descende(a, b)`"], ["`descendentes(alvo)`"], ["`diagrama(moldes, opcoes=None)`"], ["`documentacao(alvo)`"], ["`e_instancia(valor, molde)`"], ["`escrever(obj, nome, valor)`"], ["`especie(alvo)`"], ["`estaticos(alvo)`"], ["`faltando(obj, contrato)`"], ["`herdeiros(alvo)`"], ["`hierarquia(alvo)`"], ["`inspecionar(obj)`"], ["`instanciar(molde, args=None, nomeados=None)`"], ["`invocar(obj, nome, args=None, nomeados=None)`"], ["`ler(obj, nome)`"], ["`maes(alvo)`"], ["`membros(alvo)`"], ["`meta(alvo)`"], ["`meta_instancia(alvo)`"], ["`metodos(alvo)`"], ["`modificadores(alvo, membro)`"], ["`molde(alvo)`"], ["`mro(alvo)`"], ["`nome(alvo)`"], ["`operadores(alvo)`"], ["`procurar(nome)`"], ["`propriedades(alvo)`"], ["`sugerir(alvo, nome)`"], ["`tem(obj, nome)`"], ["`tipo(valor)`"], ["`traits(alvo)`"]]}},
];

const headings = [{ id: 'funcoes-38', text: "Funções (38)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Reflexo"}
      description={"Reflexão sobre blueprints, contratos e objetos: campos, métodos, modificadores, MRO, herdeiros, anotações, invocação por nome respeitando a visibilidade, criação de tipos em execução e diagrama de classes em Mermaid."}
      href={"/docs/biblioteca/reflexo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
