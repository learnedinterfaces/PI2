import * as React from 'react';

interface IQueryLogProps {
  log?: string;
}

export function QueryLog({ log }: IQueryLogProps) {
  return (
    <div className="jp-PI-QueryLog">
      {log !== undefined && log.split('\n').map(line => <p>{line}</p>)}
    </div>
  );
}
