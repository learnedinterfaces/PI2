import { usePIStore } from './PIStore';

const sessionPattern =
  /(?<prefix>\w+)\/(?<notebookID>[^\/]+)\/(?<interfaceID>\d+)/;

export const makeSessionID = (notebookID: string, interfaceID: string) =>
  `${usePIStore.getState().sessionPrefix}/${notebookID}/${interfaceID}`;

export const extractNotebookID = (sessionID: string) =>
  (sessionPattern.exec(sessionID)?.groups ?? {})['notebookID'];

export const extractInterfaceID = (sessionID: string) =>
  (sessionPattern.exec(sessionID)?.groups ?? {})['interfaceID'];
