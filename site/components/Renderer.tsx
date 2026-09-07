import type { Bloco } from '@/lib/content';
import { CodeBlock } from './CodeBlock';
import { Callout, Card, CardGrid, H2, H3 } from './Doc';
import { Inline } from './Inline';

/** Converte a lista de blocos de uma página no markup correspondente. */
export function Renderer({ blocos }: { blocos: Bloco[] }) {
  return (
    <>
      {blocos.map((b, i) => {
        if ('h2' in b) return <H2 key={i}>{b.h2}</H2>;
        if ('h3' in b) return <H3 key={i}>{b.h3}</H3>;
        if ('p' in b)
          return (
            <p key={i}>
              <Inline texto={b.p} />
            </p>
          );
        if ('code' in b)
          return <CodeBlock key={i} code={b.code} lang={b.lang} title={b.title} />;
        if ('hr' in b) return <hr key={i} />;
        if ('list' in b) {
          const Tag = b.ordered ? 'ol' : 'ul';
          return (
            <Tag key={i}>
              {b.list.map((item, k) => (
                <li key={k}>
                  <Inline texto={item} />
                </li>
              ))}
            </Tag>
          );
        }
        if ('table' in b)
          return (
            <div key={i} className="my-6 overflow-x-auto">
              <table>
                <thead>
                  <tr>
                    {b.table.head.map((h, k) => (
                      <th key={k}>
                        <Inline texto={h} />
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {b.table.rows.map((linha, k) => (
                    <tr key={k}>
                      {linha.map((celula, j) => (
                        <td key={j}>
                          <Inline texto={celula} />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        if ('callout' in b)
          return (
            <Callout key={i} tipo={b.callout.tipo} titulo={b.callout.titulo}>
              <p>
                <Inline texto={b.callout.texto} />
              </p>
            </Callout>
          );
        if ('cards' in b)
          return (
            <CardGrid key={i}>
              {b.cards.map((c) => (
                <Card key={c.href} href={c.href} title={c.title} meta={c.meta}>
                  {c.desc && <Inline texto={c.desc} />}
                </Card>
              ))}
            </CardGrid>
          );
        return null;
      })}
    </>
  );
}
