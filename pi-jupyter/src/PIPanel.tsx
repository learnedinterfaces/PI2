import { ReactWidget } from '@jupyterlab/apputils';
import { default as React } from 'react';

import { usePIStore, PerNotebookState } from './PIStore';
import { SpecRenderer } from './SpecRenderer';
import { QueryLog } from './QueryLog';
import { CollapsibleSection } from './CollapsibleSection';
import { VersionSwitcher } from './VersionSwitcher';
import { makeSessionID } from './Session';

const PIPanel = () => {
  const notebooks = usePIStore(state => state.notebooks);
  const currentNotebook = usePIStore(state => state.currentNotebook);

  return (
    <div className="jp-PI-PanelRoot">
      {Object.entries(notebooks).map(([notebookID, notebookState]) => (
        <NotebookPanel
          key={notebookID}
          notebookID={notebookID}
          notebookState={notebookState}
          active={notebookID === currentNotebook}
        />
      ))}
    </div>
  );
};

const NotebookPanel = ({
  notebookID,
  notebookState,
  active
}: {
  notebookID: string;
  notebookState: PerNotebookState;
  active: boolean;
}) => {
  const { restored, specs, activeVersion, deleteInterface } = notebookState;

  return (
    <div
      className={
        active ? 'jp-PI-PanelNotebook activeNotebook' : 'jp-PI-PanelNotebook'
      }
    >
      {specs.length > 0 ? (
        <>
          <VersionSwitcher notebookState={notebookState} />
          <CollapsibleSection title="Query Log">
            <QueryLog
              log={specs.find(ispec => ispec.id === activeVersion)?.queryLog}
            />
          </CollapsibleSection>
          <CollapsibleSection
            title="Generated Interface"
            defaultCollapsed={false}
          >
            {
              // Render all of them even though only one is displayed so that
              // the interface doesn't reset when you switch away and back
              specs.map(ispec => (
                <SpecRenderer
                  session={makeSessionID(notebookID, ispec.id)}
                  spec={'spec' in ispec ? ispec.spec : undefined}
                  visible={ispec.id === activeVersion}
                />
              ))
            }
          </CollapsibleSection>
          <CollapsibleSection title="Options">
            <button
              className="jp-PI-Delete"
              onClick={() => activeVersion && deleteInterface(activeVersion)}
            >
              Delete Version
            </button>
          </CollapsibleSection>
        </>
      ) : restored ? (
        <div>Click "Generate Interface"!</div>
      ) : (
        <div>Restoring session...</div>
      )}
    </div>
  );
};

export class PIPanelWidget extends ReactWidget {
  constructor() {
    super();
    this.addClass('jp-PIPanel');
  }

  render(): JSX.Element {
    return <PIPanel />;
  }
}
