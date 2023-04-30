import { makeEventEmitter, makeDeltaQueryF, previewDeltaQueryF, fixDataTypes, vlApiToSpec, makeVLRenderer } from "./util.js"
import project from "./project.js";

export function Table() {
    function table() {}

    table.create = (
        (spec, domEl, wf) => {
            function view() {}

            view.inputSchema = [
                {'name': '$0', 'type': 'any'},
                {'name': '$1', 'type': 'any'},
                {'name': '$2', 'type': 'any'},
                {'name': '$3', 'type': 'any'},
                {'name': '$4', 'type': 'any'},
                {'name': '$5', 'type': 'any'},
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

            view.render = (
                (table) => {
                    let data = project(table, view.mapping);
                    table = document.createElement("table");
                    if (data.length > 0) {
                        var rd = data[0];
                        var row = document.createElement("tr");
                        table.appendChild(row);
                        for (let i in rd) {
                            var cell = document.createElement("th");
                            row.appendChild(cell);
                            cell.innerHTML = view.spec.label[i];
                        }
                    }
                    for (rd in data.slice(0, 30)) {
                        row = document.createElement("tr");
                        table.appendChild(row);
                        var r = data[rd];
                        for (let i in r) {
                            cell = document.createElement("td");
                            row.appendChild(cell);
                            cell.innerHTML = parseFloat(r[i]).toFixed(2);
                        }
                    }
                    view.domEl.innerHTML = "";
                    view.domEl.appendChild(table);
                    if (data.length > 30) {
                        let more = document.createElement("p");
                        more.innerHTML = (data.length - 30).toString() + " more rows are omitted..."
                        view.domEl.appendChild(more);
                    }
                }
            );

            view.manipulationSchema = (m) => {};

            view.query = spec["data"]["query"];
            view.backend = wf.backends[spec["data"]["backend"]];
            view.backend.execute(view.query, ({ sql, data }) => view.render(data));

            view.deltaQuery = makeDeltaQueryF(view)
            view.previewDeltaQuery = previewDeltaQueryF(view);


            return makeEventEmitter(view);
        }
    );

    return table;
}
