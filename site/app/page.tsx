import type { Metadata } from 'next';
import { NavSite } from '@/components/landing/NavSite';
import { Heroi } from '@/components/landing/Heroi';
import { Pilares } from '@/components/landing/Pilares';
import { Manifesto } from '@/components/landing/Manifesto';
import { Ferramentas } from '@/components/landing/Ferramentas';
import { Sintaxe } from '@/components/landing/Sintaxe';
import { Arcane } from '@/components/landing/Arcane';
import { Aprender } from '@/components/landing/Aprender';
import { RodapeSite } from '@/components/landing/RodapeSite';

export const metadata: Metadata = {
  title: 'DataForge — uma linguagem de programação com vocabulário próprio',
  description:
    'Linguagem interpretada de propósito geral: lexer, parser, analisador estático e interpretador próprios, em Python, sem dependências no runtime. 38 módulos de biblioteca padrão e 227 exercícios verificados.',
  alternates: { canonical: '/' },
};

export default function Landing() {
  return (
    <div className="lp">
      {/* Filha DIRETA de '.lp': o sticky de um elemento so gruda dentro
          da caixa do pai, e dentro do <Heroi> ele parava no fim do
          hero. Aqui o pai e a pagina inteira. */}
      <NavSite />
      <Heroi />
      <Pilares />
      <Manifesto />
      <Ferramentas />
      <Sintaxe />
      <Arcane />
      <Aprender />
      <RodapeSite />
    </div>
  );
}
