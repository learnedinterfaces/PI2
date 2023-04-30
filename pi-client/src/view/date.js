import project from "./project.js";
import { makeEventEmitter } from "./util.js"

export function Date() {
    function date() {}
    /*
    {
      "type": "Date",
      "vid": 7,
      "data": {
        "type": "array",
        "data": [ { min : "2018-01-01", max : "2018-12-31"} ]
      }
    }
    */
    date.create = (
        (spec, domEl, wf) => {
            function view() {}

            view.inputSchema = [
                {'name': 'min', 'type': 'date'},
                {'name': 'max', 'type': 'date'}
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
                    var date =  document.createElement("Input");
                    date.type = "date";
                    date.min = data[0].min;
                    date.max = data[0].max;
                    date.value = data[0].value;
                    view.domEl.appendChild(date);


                    date.onchange = () => {
                        var  val = date.value;
                        alert(val);

                        view.source_iact.forEach(
                            (iact) => {
                                if (iact.type === "CLICK") {
                                    if (iact.space === "SPATIAL") {
                                        iact.trigger([{"label": label}]);
                                    } else if (m.space === "DATA") {
                                        iact.trigger([{"label": label, "value": val}]);
                                    }
                                }
                            }
                        );
                    };
                }
            );

            view.render(spec["data"]["data"]);

            view.source_iact = [];

            view.addSourceIact = ((iact) => view.source_iact.push(iact));


            return makeEventEmitter(view);
        }
    );

    return date;
}
