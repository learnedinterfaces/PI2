import project from "./project.js";
import { makeEventEmitter } from "./util.js"

export function TextBox() {
    function textbox() {}
    /*
    {
      "type": "textbox",
      "vid": 8,
    }
    */
    textbox.create = (
        (spec, domEl, wf) => {
            function view() {}
            view.spec = spec;
            view.domEl = domEl["parent"];
            view.id = spec["id"];
            view.mapping = spec["mapping"];

            view.inputSchema = [ ];

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
                    var textbox = document.createElement("Input");
                    textbox.type = 'text';

                    var label = document.createElement("label");
                    label.innerHTML = textbox.value;
                    view.domEl.appendChild(textbox);
                    view.domEl.appendChild(label);

                    textbox.onchange = () => {
                        var val = textbox.value;
                        alert(label + " " + val);
                        label.innerHTML = textbox.value;

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
            view.render(null);

            view.source_iact = [];

            view.addSourceIact = ((iact) => view.source_iact.push(iact));


            return makeEventEmitter(view);
        }
    );

    return textbox;
}
