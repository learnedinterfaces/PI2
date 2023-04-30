import { PIWorkflow as _PIWorkflow } from "./PIWorkflow";
import { initializeVega } from "./vega";

export function PIWorkflow(socket, session, config) {
  // Initialize vega from included <script> globals
  initializeVega(null, vega, vl, vegaEmbed);
  return _PIWorkflow(socket, session, config);
}
