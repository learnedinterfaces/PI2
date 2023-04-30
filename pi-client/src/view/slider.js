import project from "./project.js";
import { makeEventEmitter, showPreview, hidePreview } from "./util.js"

export function Slider() {
    function slider() {}
    /*
    {
      "type": "Slider",
      "vid": 6,
      "data": {
        "type": "array",
        "data": [ { min: 0, max: 1000} ]
      }
    },
    */
    slider.create = (
        (spec, domEl, wf) => {
            function view() {}

            view.inputSchema = [
                {'name': 'min', 'type': 'number'},
                {'name': 'max', 'type': 'number'}
            ];

            view.spec = spec;
            view.domEl = domEl["parent"];
            view.id = spec["id"];
            view.mapping = spec["mapping"];

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
                    var slider = document.createElement("Input");
                    slider.type = 'range';
                    slider.min = data.min;
                    slider.max = data.max;

                    var label = document.createElement("label");

                    label.innerHTML = slider.value;
                    view.domEl.appendChild(slider);
                    view.domEl.appendChild(label);


                    slider.onchange = () => {
                        var  val = slider.value;
                        //alert(label + " " + val);
                        label.innerHTML = val;

                        view.source_iact.forEach(
                            (iact) => {
                                if (iact.type === "SINGLE") {
                                    iact.trigger([{"label": label, "value": val}]);
                                }
                            }
                        );
                    };

                    slider.onmouseover = () => {
                      let val = slider.value;

                      view.source_iact.forEach(
                        (iact) => {
                          if (iact.type === "SINGLE") {
                            iact.preview([{"label": label, "value": val}])
                          }
                        }
                      )
                      showPreview();
                    }

                    slider.onmouseleave = () => {
                      hidePreview()
                    }
                }
            );
            view.render(spec["data"]);

            view.source_iact = [];

            view.addSourceIact = ((iact) => view.source_iact.push(iact));


            return makeEventEmitter(view);
        }
    );

    return slider;
}
