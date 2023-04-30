import $ from "jquery";
import project from "./project.js";
import { makeEventEmitter, showPreview, hidePreview } from "./util.js"

export function Radio() {
    function radio() {}
    /*
    {
      "type": "Radio",
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
    radio.create = ((spec, domEl, wf) => {
      function view() {}

      view.inputSchema = [
          {'name': 'label', 'type': 'string'},
          {'name': 'value', 'type': 'any', required: false}
      ];

      view.spec = spec;
      view.domEl = domEl["parent"];
      view.id = spec["id"];
      view.mapping = spec["mapping"];
      view.radios = []


      // define an identity mapping if no mapping specified
      if (!view.mapping) {
          view.mapping = {};
          view.inputSchema.forEach((item) => 
            view.mapping[item["name"]] = item["name"]
          );
      }

      view.manipulationSchema = (m) => {};
      view.deltaQuery = (delta) => {};

      view.render = ((table) => {
        let data = project(table, view.mapping);
        let orientation = view.spec.orientation || "V"; // H or V

        data.forEach((row,i) => {
          let radio = $(`<input class='form-check-input' 
            type="radio" id='${view.id}-${i}' name="${view.id}"
            value="${row.value}"/>`);
          var label;
          if ("children" in domEl) {
            label = domEl['children'][i];
          } else {
            label = $(`<label class="form-check-label" 
              for="${view.id}-${i}">${row.label}</label>`)
          }

          let div = $("<div class='form-check'/>");
          if (orientation == "H")
            div.addClass("form-check-inline")
          div.append(radio).append(label)
          $(view.domEl).append(div)

          view.radios.push(radio)

          radio.on("click change", () => {
            view.emit("interact", view)
            view.source_iact.forEach((iact) => {
              iact.trigger([{label: row.label, value: row.value}]);
            });
          });

          radio.hover(() => {
            view.source_iact.forEach((iact) => {
              iact.preview([{label: row.label, value: row.value}]);
            });
            showPreview()
          }, () => {
            hidePreview()
          })
        });
      });

      view.onNestedInteraction = (idx) => {
        if (!view.radios[idx]) return;
        view.radios[idx].prop("checked", true).trigger("click")
        view.emit("interact", view)
      }

      view.render(spec["data"]);

      view.source_iact = [];

      view.addSourceIact = ((iact) => view.source_iact.push(iact));


      return makeEventEmitter(view);
  });

  return radio;
}
