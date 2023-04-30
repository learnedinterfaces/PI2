import $ from "jquery";
import project from "./project.js";
import { makeEventEmitter, showPreview, hidePreview } from "./util.js"

export function CheckBox() {
    function checkbox() {}
    /*
   {
      "type": "checkbox",
      "vid": 8,
      "width": 100,
      "height"": 50,
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
    },
    */
    checkbox.create = ( (spec, domEl, wf) => {
      function view() {}
      view.spec = spec;
      view.domEl = domEl["parent"];
      view.id = spec["id"];
      view.mapping = spec["mapping"];
      view.checkboxes = []

      view.inputSchema = [
          {'name': 'label', 'type': 'string'},
          {'name': 'value', 'type': 'any', required: false}
      ];



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
        var data = project(table, view.mapping);
        let orientation = view.spec.orientation || "V"; // H or V
        view.checkboxes = []

        let getCheckedData = () => {
          let ret = []
          R.zip(view.checkboxes, data).forEach(([checkbox, row]) => {
            if (!checkbox[0].checked) return
            ret.push({
              label: row.label, 
              value: row.value
            })
          })
          return ret;
        }

        data.forEach( (row, i) => {
          let checkbox = $(`<input class="form-check-input" 
            type="checkbox" id="${view.id}-${i}" name="${view.id}"
            value="${row.value}"/>`)
          let label = $(`<label class="form-check-label" 
            for="${view.id}-${i}">${row.label}</label>`)
          let div = $("<div class='form-check form-check-inline'/>");

          if (orientation === "H")
            div.addClass("form-check-inline")

          div.append(checkbox).append(label)
          $(view.domEl).append(div)
          view.checkboxes.push(checkbox)

          checkbox.on("change", () => {
            let data = getCheckedData()
            view.onInteraction(data)
          })

          checkbox.hover(() => {
            let data = getCheckedData()
            view.source_iact.forEach( (iact) => {
              iact.preview(data)
            })
            showPreview()
          }, () => {
            hidePreview()
          })

        });
      });

      view.onInteraction = (data) => {
        view.source_iact.forEach( (iact) => {
          iact.trigger(data)
        });
      }

      view.render(spec["data"]);
      view.source_iact = [];
      view.addSourceIact = ((iact) => view.source_iact.push(iact));

      return makeEventEmitter(view);
  });

  return checkbox;
}
