import $ from "jquery";
import project from "./project.js";
import { makeEventEmitter, showPreview, hidePreview } from "./util.js"

export function Toggle() {
    function toggle() {}
    /*
    {
      "type": "Toggle",
      "id": 2,
    }
    */
    toggle.create = ((spec, domEl, wf) => {
      function view() {}
      view.spec = spec;
      view.domEl = domEl["parent"];
      view.id = spec.id;

      view.render = ((table) => {
        let el = $(`<label class="switch">
          <input type="checkbox" value='0'/>
          <span class="slider"></span>
        </label>`);
        view.toggle = el.find("input");
        $(view.domEl).append(el);
        if ("children" in domEl)
            $(view.domEl).append(domEl["children"][0]);
        el.find("input").on("change", (event) => {
          view.source_iact.forEach((iact) => {
            var input = event.currentTarget;
            var value = 1 - parseInt(input.value);
            input.value = value.toString();
            iact.trigger([{value}]);
          });
        });

        el.hover(() => {
          view.source_iact.forEach((iact) => {
            var input = el.find("input")[0]
            var value = 1 - parseInt(input.value);
            iact.preview([{value}]);
          });
          showPreview()
        }, () => {
          hidePreview()
        })
      });


      view.source_iact = [];
      view.addSourceIact = ((iact) => view.source_iact.push(iact));
      view.manipulationSchema = (m) => {};
      view.deltaQuery = (delta) => {};

      view.onNestedInteraction = (idx) => {
        if (view.toggle[0].value === "0") {
            view.toggle.trigger("click");
        }
        view.emit("interact", view);
      };

      view.render([]);
      return makeEventEmitter(view);
  });

  return toggle;
}
