import { vl } from "../vega.js";
import {
  makeEventEmitter,
  makeDeltaQueryF,
  previewDeltaQueryF,
  emptyInteractionHint,
  fixDataTypes,
  vlApiToSpec,
  makeVLRenderer,
  brushXHint,
  brushYHint,
  brushXYHint,
  singleHint,
  multiHint,
  brushEventListener,
  selectEventListener,
  panXHint,
  panYHint, panXYHint, zoomXHint, zoomYHint, zoomXYHint, panZoomEventListener
} from "./util.js"
import project from "./project.js";

export function Line() {
  function line() {}
  /*
  {
    "type": "Chart",
    "mark": "Line",
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
  line.create = ( (spec, domEl, wf) => {
    function view() {}

    view.inputSchema = {
        "x": {"type": "quantitative", "required": true},
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
    view.schema = spec['schema'];
    view.label = spec["label"];
    view.query = spec["data"]["query"];
    view.backend = wf.backends[spec["data"]["backend"]];
    view.source_iact = [];
    view.manipulationSchema = (m) => {};
    view.mark = vl.markLine({'point': true, tooltip: { content: "data" }}).data([]);


    for (let key in view.mapping) {
      let label = view.label[key];
      var typ = view.inputSchema[key]["type"];
      if (typ === "ordinal") {
        view.mark = view.mark.encode(vl_fields[key]().fieldN(key).title(label));
      }
      else {
        if (label === "date")
          view.mark = view.mark.encode(vl_fields[key]().fieldT(key).title(label));
        else
          view.mark = view.mark.encode(vl_fields[key]().fieldQ(key).title(label)
            .scale({"zero": false}));
      }
    }

    // need to create the marks on top
    //view.mark = view.mark.params(vl.param("cursor").value("move"))

    view.mark = view.mark
        .width(spec.width || view.domEl.width)
        .height(spec.height || view.domEl.height)
        .autosize({'type': 'fit', 'resize': true, 'contains': 'padding'});

    view.render = makeVLRenderer(view)
    view.deltaQuery = makeDeltaQueryF(view)
    view.previewDeltaQuery = previewDeltaQueryF(view);

    view.addSourceIact = ((iact) => {
      view.source_iact.push(iact);
      if (view.source_iact.length != 1) return;
      var sel;
      if (iact.type === "SINGLE") 
        sel = vl.selectSingle().nearest(true);
      else if (iact.type === "MULTI") 
        sel = vl.selectMulti().toggle(false).nearest(true);
      else if (iact.type === "BRUSHX") 
        sel = vl.selectInterval().encodings(['x']);
      else if (iact.type === "BRUSHY") 
        sel = vl.selectInterval().encodings(['y']);
      else if (iact.type === "BRUSHXY") 
        sel = vl.selectInterval().encodings(['x', 'y']);
      else if (iact.type === "PANX") 
        sel = vl.selectInterval().bind("scales").encodings(['x']).zoom(false);
      else if (iact.type === "PANY") 
        sel = vl.selectInterval().bind("scales").encodings(['y']).zoom(false);
      else if (iact.type === "PANXY") 
        sel = vl.selectInterval().bind("scales").encodings(['x', 'y']).zoom(false);
      else if (iact.type === "ZOOMX") 
        sel = vl.selectInterval().bind("scales").encodings(['x']).zoom(true);
      else if (iact.type === "ZOOMY") 
        sel = vl.selectInterval().bind("scales").encodings(['y']).zoom(true);
      else if (iact.type === "ZOOMXY") 
        sel = vl.selectInterval().bind("scales").encodings(['x', 'y']).zoom(true);
      else 
        alert("interaction not supported");

      iact.iact_name = sel.name();
      view.mark = view.mark.select(sel);
      view.vlview = null;
      view.render(null, bindListeners)

    });

    let bindListeners = () => {
      if (view.source_iact.length == 0) return;
      let iact = view.source_iact[0];
      let vegaview = view.vlview.view;

      // bind event listeners for mouse interactions
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

      else if (["PANX", "PANY", "PANXY", "ZOOMX", "ZOOMY", "ZOOMXY"].includes(iact.type)) {
        // changing to pointer needs work...do we expand the area so that we can have more hits? kind of works.
        vegaview.addEventListener('mousemove', (event, item) => {
          panZoomEventListener(vegaview, event)
        })

        vegaview.addEventListener('mouseover', (event, item) => {
          if (iact.type === "PANX") {
            panXHint()
          }
          if (iact.type === "PANY") {
            panYHint()
          }
          if (iact.type === "PANXY") {
            panXYHint()
          }
          if (iact.type === "ZOOMX") {
            zoomXHint()
          }
          if (iact.type === "ZOOMY") {
            zoomYHint()
          }
          if (iact.type === "ZOOMXY") {
            zoomXYHint()
          }
        })

        vegaview.addEventListener('mouseout', (event, item) => {
          emptyInteractionHint()
          document.body.style.cursor = 'default'
        })
      }

      vegaview.addDataListener("source_0", (event, item) => { });
      vegaview.addEventListener('click', (event, item) => {
          if (iact.type === "SINGLE") {
              if (item.datum != null) {
                  data = [item.datum.datum];
                  if ("key" in data[0])
                      data[0]["key"] = parseInt(data[0]["key"]).toString();
                  for (var x in data[0])
                      data[0][x] = data[0][x].toString()
                  for (var ic in view.source_iact)
                      view.source_iact[ic].trigger(data);
              }
          }
          else if (iact.type === "MULTI") {
              var data = vegaview.data(iact.iact_name + "_store");
              if (data.length > 0) {
                  var real_data = []
                  for (var d in data) {
                      var dd = view.data[data[d].values[0] - 1];
                      if ("key" in dd)
                          dd["key"] = parseInt(dd["key"]).toString();
                      for (var x in dd)
                          dd[x] = dd[x].toString()
                      real_data.push(dd)
                  }
                  for (var ic in view.source_iact)
                      view.source_iact[ic].trigger(real_data);
              }
          }
          else {
              var data = vegaview.data(iact.iact_name + "_store");
              if (data.length > 0) {
                  if (["BRUSHXY", "ZOOMXY", "PANXY"].includes(iact.type)) {
                      data = data[0].values[0].concat(data[0].values[1]);
                  }
                  else {
                      data = data[0].values[0];
                  }
                  for (var ic in view.source_iact)
                      view.source_iact[ic].trigger(data);
              }
              else {
                  for (var ic in view.source_iact)
                      view.source_iact[ic].trigger(data);
              }
          }
      });
      vegaview.addEventListener('wheel', (event, item) => {
          if (iact.type === "SINGLE") {
              if (item.datum != null) {
                  data = [item.datum];
                  for (var ic in view.source_iact)
                      view.source_iact[ic].trigger(data);
              }
          }
          else if (iact.type === "MULTI") {
              if (item.datum != null) {
                  data = [item.datum];
                  for (var ic in view.source_iact)
                      view.source_iact[ic].trigger(data);
              }
          }
          else {
              var data = vegaview.data(iact.iact_name + "_store");
              if (data.length > 0) {
                  if (["BRUSHXY", "ZOOMXY", "PANXY"].includes(iact.type)) {
                      data = data[0].values[0].concat(data[0].values[1]);
                  }
                  else {
                      data = data[0].values[0];
                  }
                  for (var ic in view.source_iact)
                      view.source_iact[ic].trigger(data);
              }
          }
      });

    }

    view.backend.execute(view.query, ({ sql, data }) => view.render(data));
    return makeEventEmitter(view);
  });

  return line;
}
