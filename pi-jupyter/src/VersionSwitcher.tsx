import * as React from 'react';

import { PerNotebookState } from './PIStore';

export function VersionSwitcher({
  notebookState
}: {
  notebookState: PerNotebookState;
}) {
  const { specs, activeVersion, selectVersion } = notebookState;
  const versions = specs.map(spec => spec.id);

  return (
    <div className="jp-PI-VersionSwitcher">
      {versions.map(v => (
        <button
          className={
            v === activeVersion
              ? 'jp-PI-Version selectedVersion'
              : 'jp-PI-Version'
          }
          key={v}
          onClick={() => selectVersion(v)}
        >
          {v}
        </button>
      ))}
    </div>
  );
}
