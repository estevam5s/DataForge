import { CascaDaDocumentacao } from '@/components/CascaDocs';

/**
 * O layout de `/docs` — a casca mora em `components/CascaDocs.tsx`,
 * porque `/api` usa a mesma e não fica sob esta rota.
 */
export default function DocsLayout({ children }: { children: React.ReactNode }) {
  return <CascaDaDocumentacao>{children}</CascaDaDocumentacao>;
}
