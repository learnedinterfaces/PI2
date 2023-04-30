import $ from "jquery";
import { vega, vegaEmbed } from "../vega";
import project from "./project.js";


// Adds flexbox properties to a div component. 
export function makeFlex(flexBox, orientation){
  flexBox = $(flexBox)
  if(orientation === "VLayout"){
    flexBox.css({
      display: "flex",
      "align-items": "center",
      "flex-wrap": "wrap",
      "flex-direction": "column",
      "justify-content": "flex-start",
      "align-content": "center"
    })
  } else if (orientation === "HLayout") {
    flexBox.css({
      display: "flex",
      "align-items": "flex-start",
      "flex-wrap": "wrap",
      "flex-direction": "row",
      "justify-content": "center",
      "align-content": "flex-start"
    })
  }
}

export function showPreview() {
  $("#preview").show()
  $("#default").hide()
}

export function hidePreview() {
  $("#preview").hide()
  $("#default").show()
}

export function brushXHint() {
  showInteractionHint("BRUSH X: Click + drag left to select, click and drag to move, scroll wheel to resize")
}

export function brushYHint() {
  showInteractionHint("BRUSH Y: Click + drag down to select, click and drag to move, scroll wheel to resize")
}

export function brushXYHint() {
  showInteractionHint("BRUSH XY: Click + drag to select, click and drag to move, scroll wheel to resize")
}

export function singleHint() {
  showInteractionHint("SINGLE SELECT: Click to select")
}

export function multiHint() {
  showInteractionHint("MULTI SELECT: Click, Click+SHIFT to multi-select")
}

export function panXHint() {
  showInteractionHint("PAN X: Grab and drag along x-axis")
}

export function panYHint() {
  showInteractionHint("PAN Y: Grab and drag along y-axis")
}

export function panXYHint() {
  showInteractionHint("PAN XY: Grab and drag")
}

export function zoomXHint() {
  showInteractionHint("PAN X: Grab and drag along x-axis<br>ZOOM X: Scroll wheel to zoom in/out")
}

export function zoomYHint() {
  showInteractionHint("PAN Y: Grab and drag along y-axis<br>ZOOM Y: Scroll wheel to zoom in/out")
}

export function zoomXYHint() {
  showInteractionHint("PAN XY: Grab and drag<br>ZOOM XY: Scroll wheel to zoom in/out")
}

export function showInteractionHint(interaction_msg) {
  let int_div = $("<div>")
  int_div.append("<h4>Interactions:</h4><p>" + interaction_msg + "</p>")
  $("#interaction-hint").append(int_div)
}

export function emptyInteractionHint() {
  $("#interaction-hint").empty()
}

export function brushEventListener(vegaview, event, iact) {
  // get mouse X and Y positions
  let canvas = event.srcElement;
  let mouseX = (event.clientX - canvas.getBoundingClientRect().left) + vegaview.scenegraph().root.bounds.x1
  let mouseY = event.clientY - canvas.getBoundingClientRect().top + vegaview.scenegraph().root.bounds.y1

  // grab the coordinates of the brush mark
  for (let i in vegaview.scenegraph().root.items[0].items) {
    i = vegaview.scenegraph().root.items[0].items[i]
    if (i.name === iact.iact_name + '_brush_bg') {
      // check if mouse position is over brushed area. change cursor to move if true
      if (((i.bounds.x1 < mouseX) && (mouseX < i.bounds.x2)) && ((i.bounds.y1 < mouseY) && (mouseY < i.bounds.y2))) {
        document.body.style.cursor = 'move';
      } else {
        document.body.style.cursor = 'crosshair'
      }
    }
  }
}

export function selectEventListener(vegaview, event) {
  // get mouse X and Y positions. Then check when positions overlap with marks to change to a pointer cursor
  let canvas = event.srcElement;
  let mouseX = (event.clientX - canvas.getBoundingClientRect().left) + vegaview.scenegraph().root.bounds.x1
  let mouseY = event.clientY - canvas.getBoundingClientRect().top + vegaview.scenegraph().root.bounds.y1

  for (let i in vegaview.scenegraph().root.items[0].items) {
    i = vegaview.scenegraph().root.items[0].items[i]
    if (i.name === "marks") {
      for (let m in i.items) {
        m = i.items[m]
        if (((m.bounds.x1 < mouseX) && (mouseX < m.bounds.x2)) && ((m.bounds.y1 < mouseY) && (mouseY < m.bounds.y2))) {
          document.body.style.cursor = 'pointer';
          // break after first hit so that it does not immediately change cursor back to default.
          break;
        } else {
          document.body.style.cursor = 'default';
        }
      }
    }
  }
}

export function panZoomEventListener(vegaview, event) {
  let canvas = event.srcElement;
  let mouseX = (event.clientX - canvas.getBoundingClientRect().left) + vegaview.scenegraph().root.bounds.x1
  console.log(mouseX);
  let mouseY = event.clientY - canvas.getBoundingClientRect().top + vegaview.scenegraph().root.bounds.y1

  for (let i in vegaview.scenegraph().root.items[0].items) {
    i = vegaview.scenegraph().root.items[0].items[i]
    if (i.name === "marks") {
      for (let point in i.items) {
        point = i.items[point]
        if (((point.bounds.x1 < mouseX) && (mouseX < point.bounds.x2)) && ((point.bounds.y1 < mouseY) && (mouseY < point.bounds.y2))) {
          console.log("bound1:" + point.bounds.x1)
          console.log("mouse:" + mouseX)
          console.log("bound2:" + point.bounds.x2)
          document.body.style.cursor = 'default';
          break;
        } else {
          document.body.style.cursor = 'grab';
        }
      }
    }
  }
}

export let makeEventEmitter = (o) => {
  o._listeners = {};
  o.on = (name, cb) => {
    o._listeners[name] = o._listeners[name] || []
    o._listeners[name].push(cb)
  }
  o.emit = (name, data) => {
    (o._listeners[name] || []).forEach((cb) => cb(data))
  }
  return o;
}

export let makeDeltaQueryF = (view) => 
  (f) => {
    let results = f(view.query)
    view.querry = results[0]
    let changed_node_ids = results[1]
    view.backend.execute(view.query, ({ sql, data }) => view.render(data), changed_node_ids)
  }

export let previewDeltaQueryF = (view) =>
  (f) => {
    let query = {};
    Object.assign(query, view.query)
    let result = f(query);
    let changed_node_ids = result[1];
    // render the box but with new query
    view.backend.to_sql(result[0], changed_node_ids, ({preview}) => console.log(preview));
  }

// Post-process the spec for formatting and customization reasons
export let vlApiToSpec = (vlobj, data) => {
  let vlspec = vlobj.toSpec()
  vlspec.axis = {
    titleFontSize: 15, labelFontSize: 15,
    labelOverlap: "parity",
  }
  for (let key in vlspec.encoding) {
    vlspec.encoding[key].axis = {
      titleFontSize: 15, labelFontSize: 15,
      // https://github.com/vega/vega/issues/1019#issuecomment-333033862
      labelOverlap: "parity",
      ...(key === "x" && { labelAngle: 0 })
    }
  }

  // add spacing to quantitative positional attributes
  let enc = vlspec.encoding
  if (enc && enc.x && enc.x.scale && enc.x.type === "quantitative") {
    enc.x.scale.padding = 15;
    enc.x.scale.nice = true;
  }
  if (enc && enc.y && enc.y.scale && enc.y.type === "quantitative") {
    enc.y.scale.padding = 15;
    enc.y.scale.nice = true;
  }

  if (data)
    vlspec.data = { name: "source_0", values: data }

  return vlspec;
}


// Renderer expects view to define the following attributes
//
// * mapping
// * vlview (the embedded vega lite object)
// * mark  (the VL APi object)
// * domEl
// * inputSchema
// * label
//
export let makeVLRenderer = (view) => {
  let render = ( (table, onViewLoad) => {
    let data = null;
    if (table) {
      data = project(table, view.mapping);
      data = fixDataTypes(data, view)
    }

    if (data && view.vlview) {
      let changeset = view.vlview.view.changeset()
        .remove(()=>true)
        .insert(data)
      view.vlview.view.change('source_0', changeset).run()
    }
    if (!view.vlview) {
      let vlspec = vlApiToSpec(view.mark, data)

      vegaEmbed(view.domEl, vlspec, {renderer: "canvas"})
        .then((vlview) => {
          view.vlview = vlview;
          if (onViewLoad) onViewLoad()
        })
    }
  });
  return render;
}

// cast numeric attributes to numbers
export let fixDataTypes = (data, view) => {
  for (let i in data) {
    for (let k in data[i]) {
      if (view.inputSchema[k]["type"] === "quantitative") {
        if (view.label[k] !== "date")
          data[i][k] = parseFloat(data[i][k]);
      }
      if (view.inputSchema[k]["type"] === "geojson") {
        var originalData = data[i];
        data[i] = JSON.parse(data[i][k]);
        for (let j in originalData) { // insert all other columns into this json at the same level as geometry
          if (j != "geography") {
            data[i][j] = originalData[j];
          }
        }
      }
      if (k === "color") {
        var x = parseInt(data[i][k]);
        if (!isNaN(x)) data[i][k] = x;
      }
    }
  }
  return data;
}



