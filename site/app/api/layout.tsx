import { CascaDaDocumentacao } from '@/components/CascaDocs';

/**
 * `/api` é documentação, e agora parece documentação.
 *
 * Ela renderizava um `DocPage` solto: sem cabeçalho, sem barra
 * lateral, sem largura máxima. O título encostava na borda esquerda
 * da janela, o texto ocupava a tela inteira, e não havia como sair da
 * página a não ser pelo botão de voltar do navegador — numa rota que
 * a própria documentação cita em cinco lugares.
 *
 * A rota está em `nav.ts`, então a barra lateral já a destaca.
 */
export default function LayoutDaApi({ children }: { children: React.ReactNode }) {
  return <CascaDaDocumentacao>{children}</CascaDaDocumentacao>;
}
