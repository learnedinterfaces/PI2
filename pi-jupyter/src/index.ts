import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';

import { PIExtension } from './PIExtension';
import { CellTracker } from './CellTracker';

/**
 * Initialization data for the pi-jupyter extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'pi-jupyter:plugin',
  autoStart: true,
  requires: [INotebookTracker],
  activate: (app: JupyterFrontEnd, notebookTracker: INotebookTracker) => {
    const cellTracker = new CellTracker(notebookTracker);
    cellTracker.initializeTracking();

    app.docRegistry.addWidgetExtension(
      'Notebook',
      new PIExtension(app, notebookTracker, cellTracker)
    );
  }
};

export default plugin;
