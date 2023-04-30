import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';

export class CellTracker {
  private trackedCells: {
    [notebookId: string]: {
      [cellId: string]: {
        checked: boolean;
      };
    };
  };
  private notebookTracker: INotebookTracker;

  constructor(notebookTracker: INotebookTracker) {
    this.notebookTracker = notebookTracker;
    this.trackedCells = {};
  }

  private maintainCellCheckboxes(notebook: NotebookPanel) {
    const notebookId = notebook.id;

    if (!(notebookId in this.trackedCells)) {
      this.trackedCells[notebookId] = {};
    }

    notebook.content?.widgets.forEach(cell => {
      const cellId = cell.model.id;
      if (cellId in this.trackedCells[notebookId]) {
        return;
      }

      this.trackedCells[notebookId][cellId] = { checked: false };

      const cellCheck = document.createElement('input');
      cellCheck.setAttribute('class', 'jp-PI-CellCheckbox');
      cellCheck.setAttribute('type', 'checkbox');
      cellCheck.setAttribute('title', 'Add to Generated Interface');
      cellCheck.addEventListener('change', event => {
        this.trackedCells[notebookId][cellId].checked = (
          event.target as HTMLInputElement
        ).checked;
      });
      cell.node.querySelector('.jp-Cell-inputArea')?.appendChild(cellCheck);
    });
  }

  public initializeTracking() {
    // For some reason, cells aren't all initialized when the extension loads.
    setTimeout(
      () =>
        this.notebookTracker.currentWidget &&
        this.maintainCellCheckboxes(this.notebookTracker.currentWidget),
      10000
    );

    this.notebookTracker.widgetUpdated.connect((notebookTracker, notebook) => {
      this.maintainCellCheckboxes(notebook);
    });

    this.notebookTracker.widgetAdded.connect((_, notebook) =>
      this.maintainCellCheckboxes(notebook)
    );

    this.notebookTracker.currentChanged.connect((notebookTracker, notebook) => {
      if (!notebook) {
        return;
      }

      this.maintainCellCheckboxes(notebook);
    });

    this.notebookTracker.activeCellChanged.connect(notebookTracker => {
      if (notebookTracker.currentWidget) {
        this.maintainCellCheckboxes(notebookTracker.currentWidget);
      }
    });

    this.notebookTracker.selectionChanged.connect(notebookTracker => {
      if (notebookTracker.currentWidget) {
        this.maintainCellCheckboxes(notebookTracker.currentWidget);
      }
    });
  }

  public getQueryLog(notebookId: string): string {
    const notebookCells = this.trackedCells[notebookId];
    if (!notebookCells) {
      return '';
    }

    const notebook = this.notebookTracker.find(
      notebook => notebook.id === notebookId
    );
    if (!notebook || !notebook.model) {
      return '';
    }

    let queryLog = '';
    const cellIter = notebook.model.cells.iter();
    let cell = cellIter.next();
    while (cell) {
      if (notebookCells[cell.id].checked) {
        const cellContent = cell.value.text;
        const query =
          cellContent.match(/"(?<query>select [\s\S]+)"/)?.groups?.query ??
          cellContent.match(/'''\s*(?<query>select [\s\S]+)\s*'''/)?.groups
            ?.query ??
          cellContent;
        queryLog +=
          query
            .replace(/%LOAD.+$/, '')
            .replace(/\n/g, ' ')
            .trim() + '\n';
      }
      cell = cellIter.next();
    }
    return queryLog;
  }
}
