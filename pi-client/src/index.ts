import * as vegaLite from "vega-lite/build/vega-lite";
import * as vega from "vega/build/vega";
import * as vl from "vega-lite-api";
import vegaEmbed from "vega-embed";

import { initializeVega } from "./vega.js";
import { PIWorkflow as _PIWorkflow } from "./PIWorkflow.js";

// Entry point for library usage
export function PIWorkflow(socket, session, config) {
  vl.register(vega, vegaLite, {
    view: { renderer: "canvas" },
  });
  // Initialize vega from package imports
  initializeVega(vegaLite, vega, vl, vegaEmbed);
  return _PIWorkflow(socket, session, config);
}
