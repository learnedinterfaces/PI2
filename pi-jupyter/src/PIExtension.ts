// https://github.com/jupyterlab/extension-examples/blob/master/toolbar-button/README.md

import { IDisposable, DisposableDelegate } from '@lumino/disposable';
import { ToolbarButton } from '@jupyterlab/apputils';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import {
  NotebookPanel,
  INotebookModel,
  INotebookTracker
} from '@jupyterlab/notebook';
// import { reactIcon } from '@jupyterlab/ui-components';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { MainAreaWidget } from '@jupyterlab/apputils';

import { PIPanelWidget } from './PIPanel';
import { CellTracker } from './CellTracker';
import { SpecManager, setCurrentNotebook, addNotebook } from './PIStore';
import { extractNotebookID, extractInterfaceID } from './Session';
import { socket } from './PISocket';

export class PIExtension
  implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel>
{
  private app: JupyterFrontEnd;
  private notebookTracker: INotebookTracker;
  private cellTracker: CellTracker;
  private specManagers: { [notebookID: string]: SpecManager };

  private initializedCallbacks: boolean;
  private piPanel: PIPanelWidget | null;
  private containerWidget: MainAreaWidget | null;

  constructor(
    app: JupyterFrontEnd,
    notebookTracker: INotebookTracker,
    cellTracker: CellTracker
  ) {
    this.app = app;
    this.notebookTracker = notebookTracker;
    this.cellTracker = cellTracker;
    this.specManagers = {};

    this.initializedCallbacks = false;
    this.piPanel = null;
    this.containerWidget = null;
  }

  private ensureNotebook(notebook: NotebookPanel | null) {
    if (!notebook || notebook.id in this.specManagers) {
      return;
    }
    const meta = notebook.model?.metadata;
    if (!meta) {
      return;
    }

    console.log('[jtao] Creating SpecManager for notebook', notebook.id);

    addNotebook(notebook.id);
    const specManager = new SpecManager(notebook.id, meta);
    this.specManagers[notebook.id] = specManager;
    specManager.restore();
  }

  private ensureCallbacks() {
    if (this.initializedCallbacks) {
      return;
    }

    this.initializedCallbacks = true;

    socket.on(
      'spec',
      async ({ session, log, spec }: { session: string; log: string, spec: unknown }) => {
        // TODO: PI Server really ought to include session ID with response to
        // support multiple interfaces simultaneously in flight.
        // This is extra confusing when multiplexing the socket for multiple notebooks.

        // FIXME:
        // Actually, this is even a problem when restoring. This needs to be fixed.

        const notebookID = extractNotebookID(session);
        const specManager = this.specManagers[notebookID];
        if (!specManager) {
          console.log(
            '[jtao] Got a spec for an untracked notebook',
            session,
            notebookID
          );
          return;
        }
        specManager.addSpec(extractInterfaceID(session), log, spec);
      }
    );

    socket.on('failed', ({ session }: { session: string }) => {
      console.log('[jtao] failed to generate interface', session);
      const notebookID = extractNotebookID(session);
      const specManager = this.specManagers[notebookID];
      if (!specManager) {
        console.log(
          '[jtao] Interface generation failure for an untracked notebook',
          session,
          notebookID
        );
        return;
      }
      specManager.deleteInterface(extractInterfaceID(session));
    });

    // Whenever a notebook is selected (open on app start or opened mid-session),
    // make sure it has a SpecManager and the specs are restored
    this.notebookTracker.currentChanged.connect((_, notebook) => {
      console.log('[jtao] Switching to notebook', notebook?.id);
      notebook?.sessionContext.ready.then(() => {
        console.log('[jtao] Setting notebook active', notebook?.id);
        this.ensureNotebook(notebook);
        setCurrentNotebook(notebook.id);
      });
    });
  }

  createNew(
    panel: NotebookPanel,
    context: DocumentRegistry.IContext<INotebookModel>
  ): IDisposable {
    // CreateNew is called whenever a notebook is opened.
    // So we make the callbacks/button/panel singletons
    this.ensureCallbacks();

    // Create panel widget
    if (this.piPanel === null) {
      this.piPanel = new PIPanelWidget();
      this.containerWidget = new MainAreaWidget<PIPanelWidget>({
        content: this.piPanel
      });

      this.containerWidget.title.label = 'Generated Interfaces';
      this.app.shell.add(this.containerWidget, 'right');
    }

    // Create button widget per-notebook since the toolbar is per-notebook
    const activate = () => {
      console.log('[jtao] You clicked the button');
      const currentNotebookID = this.notebookTracker.currentWidget?.id;
      if (currentNotebookID !== undefined) {
        // When you click the button, send the selected logs to the panel to generate an interface
        const queryLog = this.cellTracker.getQueryLog(currentNotebookID);

        this.specManagers[currentNotebookID].addInterface(queryLog);
      }

      // Automatically open the panel when you press the button
      this.containerWidget?.show();
      this.piPanel?.show();
    };

    const piButton = new ToolbarButton({
      className: 'jp-PI-Button',
      label: 'Generate Interface',
      onClick: activate,
      tooltip: 'Generate Interface from selected SQL cells'
      // icon: reactIcon
    });

    panel.toolbar.addItem('piGenerate', piButton);

    return new DisposableDelegate(() => {
      // We don't actually want to dispose the panel
      // Otherwise, closing one notebook would destroy the panel across all notebooks
      console.log('[jtao] Extension instance being disposed');
      piButton.dispose();
    });
  }
}
