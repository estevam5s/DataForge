import type { Metadata } from 'next';
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
    'Linguagem interpretada de propósito geral: lexer, parser, analisador estático e interpretador próprios, em Python, sem dependências no runtime. 20 módulos de biblioteca padrão e 190 exercícios verificados.',
  alternates: { canonical: '/' },
};

export default function Landing() {
  return (
    <div className="lp">
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
