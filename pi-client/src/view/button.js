import $ from "jquery";
import project from "./project.js";
import { makeEventEmitter, showPreview, hidePreview } from "./util.js"

export function Button() {
    function button() {}
    /*
    {
      "type": "Button",
      "id": 2,
      "data": {
        "type": "array",
        "data": [
          {
            "label": 1,
            "value": 1
          },
          {
            "label": 2,
            "value": 2
          }
        ]
      }
    }
    */
    button.create = ((spec, domEl, wf) => {
      function view() {}

      view.inputSchema = [
          {'name': 'label', 'type': 'string'},
          {'name': 'value', 'type': 'any', required: false}
      ];

      view.spec = spec;
      view.domEl = domEl["parent"];
      view.id = spec["id"];
      view.mapping = spec["mapping"];

      // define an identity mapping if no mapping specified
      if (!view.mapping) {
        view.mapping = {};
        view.inputSchema.forEach( (item) => 
          view.mapping[item["name"]] = item["name"]
        );
      }

      view.manipulationSchema = (m) => {};
      view.deltaQuery = (delta) => {};

      view.render = ((table) => {
        let data = project(table, view.mapping);
        data.forEach((row) => {
          let button = $(`<button class="btn btn-outline-primary"
            value='${row.value}'>${row.label}</button>`)
          $(view.domEl).append(button);
          button.on("click", () => {
            view.emit("interact", view)
            view.source_iact.forEach((iact) => {
              iact.trigger([{
                label: row.label, 
                value: parseInt(row.value)
              }]);
            });
          })

          button.hover(() => {
            view.source_iact.forEach((iact) => {
              iact.preview([{label: row.label, value: parseInt(row.value)}]);
            });
            showPreview()
          }, () => {
            hidePreview()
          })
        });


      });

      view.render(spec["data"]);

      view.source_iact = [];

      view.addSourceIact = ((iact) => view.source_iact.push(iact));


      return makeEventEmitter(view);
    });

    return button;
}
