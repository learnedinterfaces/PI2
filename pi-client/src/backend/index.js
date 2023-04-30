import { DBBackend } from "./db.js";
import { DifftreeBackend } from "./difftree.js";

export function BackendLibrary(socket) {
  function backendLib() {}

  backendLib.library = {
    db: DBBackend(),
    difftree: DifftreeBackend()
  };

  backendLib.createBackend = (
      (spec, wf, socket, session) => {
        var id = spec["id"];
        var typ = spec["type"]/*  */;
        wf.backends[id] = backendLib.library[typ].create(spec, socket, session);
      }
  );

  return backendLib;
}
