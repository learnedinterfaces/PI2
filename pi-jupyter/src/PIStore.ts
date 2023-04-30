import { IObservableJSON } from '@jupyterlab/observables';
import create from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { socket } from './PISocket';
import { makeSessionID } from './Session';

const PI_PERSISTED_SPEC_KEY = 'pi-specs';

interface InterfaceSpec {
  id: string;
  queryLog: string;
  spec: unknown;
}

interface InterfaceInit {
  id: string;
  queryLog: string;
}

export interface PerNotebookState {
  specs: (InterfaceInit | InterfaceSpec)[];
  restored: boolean;
  activeVersion: string | undefined;

  selectVersion: (activeVersion: string) => void;
  deleteInterface: (interfaceID: string) => void;
}

type PIState = {
  notebooks: { [notebookID: string]: PerNotebookState };
  currentNotebook: string | undefined;
  sessionPrefix: string;
};

const initialPerNotebookState = (
  setNotebookState: (
    setter: (previousState: PerNotebookState) => Partial<PerNotebookState>
  ) => void
): PerNotebookState => ({
  specs: [],
  restored: false,
  activeVersion: undefined,

  selectVersion: version =>
    setNotebookState(state => ({
      activeVersion: version
    })),
  deleteInterface: interfaceID =>
    setNotebookState(state => withoutVersion(state, interfaceID))
});

export const usePIStore = create<PIState>()(
  subscribeWithSelector(set => ({
    notebooks: {},
    currentNotebook: undefined,
    sessionPrefix: (Math.random() + 1).toString(36).substring(2, 5)
  }))
);

const updateNotebook = (
  notebookID: string,
  setter: (previousState: PerNotebookState) => Partial<PerNotebookState>
) =>
  usePIStore.setState(state => ({
    notebooks: {
      ...state.notebooks,
      [notebookID]: {
        ...state.notebooks[notebookID],
        ...setter(state.notebooks[notebookID])
      }
    }
  }));

export const addNotebook = (notebookID: string) =>
  updateNotebook(notebookID, () =>
    initialPerNotebookState(setter => updateNotebook(notebookID, setter))
  );

export const setCurrentNotebook = (notebookID: string) =>
  usePIStore.setState({
    currentNotebook: notebookID
  });

const getNotebookState = (notebookID: string) =>
  usePIStore.getState().notebooks[notebookID];

export const useNotebookState = (
  notebookID: string,
  selector: (state: PerNotebookState) => Partial<PerNotebookState>
) => usePIStore(state => state.notebooks[notebookID]);

const withoutVersion = (state: PerNotebookState, interfaceID: string) => {
  let newActiveVersion = state.activeVersion;
  if (interfaceID === newActiveVersion) {
    const activeIndex = state.specs.findIndex(spec => spec.id === interfaceID);
    if (activeIndex === 0 && state.specs.length === 1) {
      // Deleted the last interface
      newActiveVersion = undefined;
    } else if (activeIndex === 0) {
      // Deleted the leftmost interface
      newActiveVersion = state.specs[1].id;
    } else {
      newActiveVersion = state.specs[activeIndex - 1].id;
    }
  }
  return {
    activeVersion: newActiveVersion,
    specs: state.specs.filter(spec => spec.id !== interfaceID)
  };
};

(window as any).usePIStore = usePIStore;

export class SpecManager {
  private notebookID: string;
  private notebookMetadata: IObservableJSON;
  private nextID: number;

  constructor(notebookID: string, notebookMetadata: IObservableJSON) {
    this.notebookID = notebookID;
    this.notebookMetadata = notebookMetadata;
    this.nextID = 1;

    // FIXME: for testing
    (window as any).resetSpecStore = () => addNotebook(this.notebookID);

    // Persist spec changes for all fully generated interfaces
    usePIStore.subscribe(
      state => state.notebooks[this.notebookID],
      state => {
        const specs = state.specs.filter(spec => 'spec' in spec);
        console.log('[jtao] Persisting specs', this.notebookID, specs);
        this.notebookMetadata.set(PI_PERSISTED_SPEC_KEY, specs as any);
      }
    );
  }

  public async addInterface(queryLog: string) {
    const id = `${this.nextID++}`;
    console.log('[jtao] new interface with id', id);
    socket.emit('log', {
      session: makeSessionID(this.notebookID, id),
      payload: { log: queryLog }
    });

    updateNotebook(this.notebookID, state => ({
      specs: [...state.specs, { id, queryLog }],
      activeVersion: id
    }));
  }

  public addSpec(interfaceID: string, queryLog: string, spec: unknown) {
    // FIXME: Should use the actual interface ID instead of assuming the last one in the spec array
    const notebookState = getNotebookState(this.notebookID);

    const currentSpecs = notebookState.specs;
    const lastSpec = currentSpecs[currentSpecs.length - 1];
    const newSpecs = [...currentSpecs.slice(0, -1), { ...lastSpec, queryLog, spec }];

    if ('spec' in lastSpec) {
      console.log(
        '[jtao] Skipping persistence: got a spec but no spec in flight'
      );
      return;
    }

    updateNotebook(this.notebookID, state => ({ specs: newSpecs }));
  }

  public deleteInterface(interfaceID: string) {
    updateNotebook(this.notebookID, state =>
      withoutVersion(state, interfaceID)
    );
  }

  public async restore() {
    // TODO: Server doesn't confirm receipt on restore
    // so there's a race condition between restoring on server
    // and issuing queries on client

    if (getNotebookState(this.notebookID).restored) {
      console.log('[jtao] Already restored');
      return;
    }

    const specs: InterfaceSpec[] =
      (this.notebookMetadata.get(
        PI_PERSISTED_SPEC_KEY
      ) as unknown as InterfaceSpec[]) ?? [];

    // For automatic numbering, e.g. if we restore 3 interfaces, the largest with ID 5,
    // the next one should be #6
    this.nextID =
      specs.reduce((max, spec) => Math.max(parseInt(spec.id), max), 0) + 1;

    console.log(
      '[jtao] Restoring...',
      specs,
      this.notebookMetadata.get(PI_PERSISTED_SPEC_KEY)
    );

    for (const spec of specs) {
      socket.emit('restore', {
        session: makeSessionID(this.notebookID, spec.id),
        payload: { ...spec }
      });
    }

    updateNotebook(this.notebookID, state => ({
      specs,
      activeVersion: specs.length > 0 ? specs[specs.length - 1].id : undefined,
      restored: true
    }));
  }
}
