import { vl } from "../vega";
import {
  makeEventEmitter,
  makeDeltaQueryF,
  fixDataTypes,
  vlApiToSpec,
  makeVLRenderer,
  emptyInteractionHint,
  brushXHint,
  brushYHint,
  brushXYHint,
  singleHint, multiHint, brushEventListener, selectEventListener
} from "./util.js"
import project from "./project.js";

export function Bar() {
  function bar() {}
  /*
  {
    "type": "Chart",
    "mark": "Bar",
    "vid": 10,
    "data": {
      "backend": "dt",
      "query":  {"0": 0, "11": 0, "46": 0, "25": "-Infinity", "30": "Infinity"}
    },
    "mapping": {
      'x': $1,
      "y": $2,
    },
  },
  */
  bar.create = ( (spec, domEl, wf) => {
    function view() {}

    view.inputSchema = {
        "x": {"type": "ordinal", "required": true},
        "y": {"type": "quantitative", "required": true},
        "color": {"type": "ordinal", "required": false},
        "key": {"type": "ordinal", "required": false}
    };

    let vl_fields = {
        "x": vl.x,
        "y": vl.y,
        "color": vl.color,
        "key": vl.key
    };

    view.spec = spec;
    view.domEl = domEl["parent"];
    view.id = spec["id"];
    view.mapping = spec["mapping"];
    view.label = spec["label"];
    view.query = spec["data"]["query"];
    view.backend = wf.backends[spec["data"]["backend"]];
    view.source_iact = [];
    view.mark = vl.markBar({tooltip: { content: "data" }}).data([]);

    for (let key in view.mapping) {
      let label = view.label[key];
      var typ = view.inputSchema[key]["type"];
      if (typ === "ordinal") {
        view.mark = view.mark.encode(vl_fields[key]().fieldO(key).title(label));
      } else {
        if (label === "date")
          view.mark = view.mark.encode(vl_fields[key]().fieldT(key).title(label));
        else
          view.mark = view.mark.encode(vl_fields[key]().fieldQ(key).title(label));
      }
    }

    view.mark = view.mark
      .width(spec.width || view.domEl.height)
      .height(spec.height || view.domEl.height)
      .autosize({'type': 'fit', 'resize': true, 'contains': 'padding'});


    view.render = makeVLRenderer(view);
    view.manipulationSchema = (m) => {};
    view.deltaQuery = makeDeltaQueryF(view);


    view.addSourceIact = ((iact) => {
      view.source_iact.push(iact);
      if (view.source_iact.length != 1) return

      let sel;
      if (iact.type === "SINGLE") 
        sel = vl.selectSingle();
      else if (iact.type === "MULTI")  {
        sel = vl.selectPoint();
        sel.empty(false);
        view.mark = view.mark.encode(vl.color().value('lightgray').if(sel, vl.color().value('#4682b4')));
        iact.selected = [];
      }
      else
        sel = vl.selectInterval().encodings(['x']);

      iact.iact_name = sel.name();
      view.mark = view.mark.select(sel);
      view.vlview = null;
      view.render(null, bindListeners);
    });


    let bindListeners = () => {
      if (view.source_iact.length == 0) return;
      let iact = view.source_iact[0];
      let vegaview = view.vlview.view;

      if (["BRUSHX", "BRUSHY", "BRUSHXY"].includes(iact.type)) {
        vegaview.addEventListener('mousemove', (event, item) => {
          brushEventListener(vegaview, event, iact)
        })

        vegaview.addEventListener('mouseover', (event, item) => {
          if (iact.type === "BRUSHX") {
            brushXHint()
          }
          else if (iact.type === "BRUSHY") {
            brushYHint()
          }
          else if (iact.type === "BRUSHXY") {
            brushXYHint()
          }
        })

        vegaview.addEventListener('mouseout', (event, item) => {
          document.body.style.cursor = 'default'
          emptyInteractionHint()
        })
      }

      else if (['SINGLE', 'MULTI'].includes(iact.type)) {
        vegaview.addEventListener('mousemove', (event, item) => {
          selectEventListener(vegaview, event)
        })

        vegaview.addEventListener('mouseover', (event, item) => {
          if (iact.type === "SINGLE") {
            singleHint()
          }
          if (iact.type === "MULTI") {
            multiHint()
          }
        })

        vegaview.addEventListener('mouseout', (event, item) => {
          document.body.style.cursor = 'default'
          emptyInteractionHint()
        })
      }

      vegaview.addDataListener("source_0", (event, item) => { });
      vegaview.addEventListener('click', (event, item) => {
        if (iact.type === "SINGLE") {
          if (item.datum != null) {
            data = [item.datum];
            for (var ic in view.source_iact)
              view.source_iact[ic].trigger(data);
          }
        }
        else if (iact.type === "MULTI") {
          var data = vegaview.data(iact.iact_name + "_store");
          var viewdata = vegaview.data("source_0");
          var real_data = []
          for (var d in data) {
            var dd = viewdata[data[d].values[0] - 1];
            if ("key" in dd)
               dd["key"] = parseInt(dd["key"]).toString();
            for (var x in dd)
               dd[x] = dd[x].toString()
            real_data.push(dd)
          }
          for (var ic in view.source_iact)
            view.source_iact[ic].trigger(real_data);
        }
        else {
          var data = vegaview.data(iact.iact_name + "_store");
          if (data.length > 0) {
            data = data[0].values[0];
            for (var ic in view.source_iact)
              view.source_iact[ic].trigger(data);
          }
          else {
            for (var ic in view.source_iact)
              view.source_iact[ic].trigger(data);
          }
        }
      });
    };

    view.backend.execute(view.query, ({ sql, data }) => view.render(data));
    return makeEventEmitter(view);
  });

  return bar;
}
