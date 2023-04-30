import { vl } from "../vega.js";
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

export function Geoshape() {
  function geoshape() {}
  geoshape.create = ( (spec, domEl, wf) => {
    function view() {}

    view.inputSchema = {
        "geography": {"type": "geojson", "required": true},
        "color": {"type": "quantitative", "required": false},
        "key": {"type": "ordinal", "required": false}
    };

    let vl_fields = {
        "geography": vl.shape,
        "color": vl.color,
        "key": vl.key
    };

    view.spec = spec;
    view.domEl = domEl["parent"];
    view.id = spec["id"];
    view.mapping = spec["mapping"];
    view.schema = spec['schema'];
    view.label = spec["label"];
    view.query = spec["data"]["query"];
    view.backend = wf.backends[spec["data"]["backend"]];
    view.source_iact = [];
    view.mark = vl.markGeoshape({filled: true, tooltip: true}).data([]);

    for (let key in view.mapping) {
      let label = view.label[key];
      var typ = view.inputSchema[key]["type"];
      if (typ === "ordinal") {
        view.mark = view.mark.encode(vl_fields[key]().fieldN(key).title(label));
      }
      else if (typ === "geojson") {
        view.mark = view.mark.project(vl.projection('albersUsa'));
      }
      else {
        if (label === "date")
          view.mark = view.mark.encode(vl_fields[key]().fieldT(key).title(label));
        else
          view.mark = view.mark.encode(vl_fields[key]().fieldQ(key).title(label)
              .scale({"zero": false, "scheme": "reds"
              }));
      }
    }

    if ("color" in view.mapping)
      view.mark = view.mark.encode(vl.tooltip([vl.fieldN("key"), vl.fieldQ("color")]));
    else
      view.mark = view.mark.encode(vl.tooltip([vl.fieldN("key")]));

    view.mark = view.mark
      .width(spec.width || view.domEl.width)
      .height(spec.height || view.domEl.height)
      .autosize({'type': 'fit', 'resize': true, 'contains': 'padding'});

      
    view.render = makeVLRenderer(view)
    view.manipulationSchema = (m) => {};
    view.deltaQuery = makeDeltaQueryF(view)


    view.addSourceIact = ((iact) => {
      view.source_iact.push(iact);
      if (view.source_iact.length != 1) return; 
      var sel;
      if (iact.type === "SINGLE") {
        sel = vl.selectSingle();
        sel.empty(false);
        view.mark = view.mark.encode(vl.size().value(80), vl.color().fieldQ("color").scale({"zero": false, "scheme": "reds"}).if(vl.not(sel), vl.color().value('lightgray'))).params(sel);
        iact.selected = [];
      }
      else if (iact.type === "MULTI") {
        sel = vl.selectPoint();
        sel.empty(false);
        view.mark = view.mark.encode(vl.size().value(80), vl.color().value('lightgray').if(vl.not(sel), vl.color().fieldN("color"))).params(sel);
        iact.selected = [];
      }
      else 
        alert("interaction not supported " + iact.type);

      iact.iact_name = sel.name();
      view.mark = view.mark.select(sel);
      view.vlview = null;
      view.render(null, bindListeners)
  });


    let bindListeners = () => {
      if (view.source_iact.length == 0) return;
      let iact = view.source_iact[0];
      let vegaview = view.vlview.view;

      if (['SINGLE', 'MULTI'].includes(iact.type)) {
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
      vegaview.addEventListener('mouseup', (event, item) => {
        if (iact.type === "SINGLE") {
            var data = vegaview.data(iact.iact_name + "_store");
            var viewdata = vegaview.data("source_0");
            if (data.length > 0) {
                var real_data = []
                for (var d in data) {
                    var dd = viewdata[(data[d]._vgsid_ - 1) % viewdata.length];

                    //var dd = viewdata[data[d].values[0] - 1];
                    for (var x in dd)
                        dd[x] = dd[x].toString()
                    real_data.push(dd)
                }
                for (var ic in view.source_iact)
                    view.source_iact[ic].trigger(real_data);
            }
            else {
                for (var ic in view.source_iact)
                    view.source_iact[ic].trigger([]);
            }
        }
        else if (iact.type === "MULTI") {
            var data = vegaview.data(iact.iact_name + "_store");
            var viewdata = vegaview.data("source_0");
            if (data.length > 0) {
                var real_data = []
                for (var d in data) {
                    var dd = viewdata[data[d].values[0] - 1];
                    for (var x in dd)
                        dd[x] = dd[x].toString()
                    real_data.push(dd)
                }
                for (var ic in view.source_iact)
                    view.source_iact[ic].trigger(real_data);
            }
            else {
                for (var ic in view.source_iact)
                    view.source_iact[ic].trigger([]);
            }
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
    }

    view.backend.execute(view.query, ({ sql, data} ) => view.render(data));
    return makeEventEmitter(view);
  });

  return geoshape;
}
