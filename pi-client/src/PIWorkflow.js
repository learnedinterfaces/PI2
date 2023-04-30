import { BackendLibrary } from "./backend/index.js";
import { ViewLibrary } from "./view/index.js";
import $ from "jquery";

const defaultConfig = {
  enableHelp: false,
};

// The main entrance of PI users
export function PIWorkflow(socket, session, config = defaultConfig) {
  function workflow() {}

  workflow.viewLib = ViewLibrary();
  workflow.backendLib = BackendLibrary();

  workflow.clear = () => {
    workflow.views = {};
    workflow.backends = {};
    workflow.domEls = {};
    workflow.interactions = {};
    workflow.widgetHierarchy = {};
  };
  workflow.clear();

  workflow.init = (spec, div) => {
    if ("spec" in spec) {
      spec = spec.spec;
    }
    workflow.spec = spec;
    workflow.div = div;
    console.log(spec);

    if (config.enableHelp) {
      // create widget helper button
      workflow.div.innerHTML +=
        '<button id="widget-help-btn" class="btn btn-info">Widget Help</button>';

      // create widget helper window
      workflow.div.innerHTML +=
        '<div id="draggable-help">\n' +
        "         <h4>Queries:</h4>" +
        '        <div id="default"></div>\n' +
        '        <div id="preview"></div>\n' +
        '        <div id="interaction-hint"></div>' +
        "    </div>";

      // create binding for button
      $("#draggable-help").dialog({
        autoOpen: false,
      });
      $("#widget-help-btn").click(function () {
        if (!$("#draggable-help").dialog("isOpen"))
          $("#draggable-help").dialog("open");
      });
    }

    // create backends
    spec["backends"].forEach((backend_spec) =>
      workflow.backendLib.createBackend(backend_spec, workflow, socket, session)
    );
    // build layout
    workflow.viewLib.buildLayout(spec["layout"], workflow);

    //create views
    spec["views"].forEach((view_spec) =>
      workflow.viewLib.createView(view_spec, workflow)
    );

    // bind nested view listeners
    for (let pid in workflow.widgetHierarchy) {
      let parv = workflow.views[pid];
      for (let { idx, ref: cid } of workflow.widgetHierarchy[pid]) {
        let cv = workflow.views[cid];
        cv.on("interact", () => {
          if (parv.onNestedInteraction) {
            parv.onNestedInteraction(idx);
          }
        });
      }
    }

    // register interactions
    spec["interactions"].forEach((interaction_spec) =>
      workflow.viewLib.registerInteraction(interaction_spec, workflow)
    );
  };

  return workflow;
}
