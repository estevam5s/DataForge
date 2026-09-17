import type { Metadata } from 'next';
import { NavSite } from '@/components/landing/NavSite';
import { Heroi } from '@/components/landing/Heroi';
import { Pilares } from '@/components/landing/Pilares';
import { Manifesto } from '@/components/landing/Manifesto';
import { Ferramentas } from '@/components/landing/Ferramentas';
import { Sintaxe } from '@/components/landing/Sintaxe';
import { Arcane } from '@/components/landing/Arcane';
import { Aprender } from '@/components/landing/Aprender';
import { Autor } from '@/components/landing/Autor';
import { Numeros } from '@/components/landing/Numeros';
import { Extensao } from '@/components/landing/Extensao';
import { Instalar } from '@/components/landing/Instalar';
import { RodapeSite } from '@/components/landing/RodapeSite';

export const metadata: Metadata = {
  title: 'DataForge — uma linguagem de programação com vocabulário próprio',
  description:
    'Linguagem interpretada de propósito geral: lexer, parser, analisador estático e interpretador próprios, em Python, sem dependências no runtime. 54 módulos de biblioteca padrão e 251 exercícios verificados.',
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
      <Extensao />
      <Numeros />
      <Autor />
      {/* O comando de instalacao fecha a pagina, logo acima do rodape:
          quem rolou ate aqui decidiu, e o proximo passo tem de estar
          embaixo do dedo. */}
      <Instalar />
      <RodapeSite />
    </div>
  );
}
