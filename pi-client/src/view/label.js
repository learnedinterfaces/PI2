import $ from "jquery";
import project from "./project.js";
import { makeEventEmitter } from "./util.js"

// Static Label
// TODO: could be dynamic label 
export function Label() {
  function label() {}

  
  // spec: {
  //   "type": "Label",
  //   "id": 2,
  //   "data": "text string"{
  // }
  label.create = ((spec, domEl, wf) => {
    function view() {}


    view.spec = spec;
    view.domEl = domEl["parent"];
    view.dom = $(view.domEl)
    view.id = spec["id"];

    // render
    let label = $(`<span>${spec.data}</span>`);
    view.dom.append(label)

    view.dom.on("click", () => {
      view.emit("interact", view)
    })

    // dummy methods since Labels don't support interactions..?
    view.inputSchema = [ ];
    view.manipulationSchema = (m) => {};
    view.deltaQuery = (delta) => {};
    view.render = () => {}
    view.source_iact = [];
    view.addSourceIact = (iact) => {}

    return makeEventEmitter(view);
  });

  return label;
}
