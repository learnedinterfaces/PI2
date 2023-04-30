import project from "./project.js";
import { makeEventEmitter, hidePreview, showPreview } from "./util.js"

export function Dropdown() {
    function dropdown() {}
    /*
    {
      "type": "Dropdown",
      "vid": 7,
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
    */
    dropdown.create = (
        (spec, domEl, wf) => {
            function view() {}

            view.inputSchema = [
                {'name': 'label', 'type': 'string'},
                {'name': 'value', 'type': 'any', required: false}
            ];

            view.spec = spec;
            view.domEl = domEl["parent"];
            view.id = spec["id"];
            view.mapping = spec["mapping"];

            view.widget = document.createElement("select");
            view.domEl.appendChild(view.widget);

            // define an identity mapping if no mapping specified
            if (!view.mapping) {
                view.mapping = {};
                view.inputSchema.forEach(
                    (item) => view.mapping[item["name"]] = item["name"]
                );
            }

            view.manipulationSchema = (m) => {};
            view.deltaQuery = (delta) => {};

            view.render = (
                (table) => {
                    let data = project(table, view.mapping);
                    data.forEach(
                        (row) => {
                            var option = document.createElement("option");
                            option.value = row.value;
                            option.innerHTML = row.label;
                            view.widget.appendChild(option);
                        });
                }
            );

            view.render(spec["data"]);

            view.source_iact = [];

            view.addSourceIact = ((iact) => view.source_iact.push(iact));

            view.widget.onchange = () => {
                var label = view.widget.options[view.widget.selectedIndex].innerHTML;
                var val = parseInt(view.widget.value);
                view.emit("interact", view)

                view.source_iact.forEach(
                    (iact) => {
                        iact.trigger([{"label": label, "value": val}]);
                    }
                );
            };

            view.widget.onmouseover = function() {
              view.source_iact.forEach((iact) => {
                iact.preview([{label: view.widget.options[view.widget.selectedIndex].innerHTML, value: parseInt(view.widget.value)}]);
              });
              showPreview()
            }
            view.widget.onmouseleave = function() {
              hidePreview()
            }

            return makeEventEmitter(view);
        }
    );

    return dropdown;
}
