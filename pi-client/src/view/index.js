import $ from "jquery";
import * as R from "ramda";
import { Dropdown } from "./dropdown.js";
import { Button } from "./button.js";
import { Radio } from "./radio.js";
import { Label } from "./label.js";
import { CheckBox } from "./checkbox.js";
import { RangeSlider } from "./rangeslider.js";
import { Slider } from "./slider.js";
import { Bar } from "./bar.js";
import { Line } from "./line.js";
import { Point } from "./point.js";
import { Circle } from "./circle.js";
import { Square } from "./square.js";
import { Area } from "./area.js";
import { Geoshape } from "./geoshape.js";
import { Table } from "./table.js";
import { Toggle } from "./toggle.js";
import { makeFlex } from "./util.js";
import { InteractionLibrary } from "./interaction.js";

// Walk the spec's layout tree to construct DIV containers 
// for the layout and views
//
// Views referenced in the layout spec have a "ref" attribute
// that we will use to store the DIV container, so that
// we can retrieve it in createView below
//
// Layout Widgets (tabs, Adder, radio) are special in that they 
// need to be instantiated with the DIV containers of its options
// They are identified by node.widget
//
// @spec: layout spec 
// @wf: reference to workflow
//
// @returns DIV container for spec
//
function build_layout(spec, wf) {
  let div = $(`<div id="${spec.id}" ></div>`)
    .css({ 
      width: `${spec.width}px`,
      height: `${spec.height}px`
    })
    .addClass(spec.type)
    .addClass("layout")
  makeFlex(div[0], spec.type)

  if (spec.type == "HLayout" || spec.type == "VLayout") {
    let childDivs = spec.children.map((child) => build_layout(child, wf))
    div.append(...childDivs)

    if (spec.widget) {
      wf.domEls[spec.widget.ref] = { parent: div[0], children: childDivs }
    } 
  } else if (spec.type == "ref") {
    wf.domEls[spec.ref] = { parent: div[0] }
  } else { 
    // View spec embedded in layout
    // We will transform it into a ref, add the spec to the
    // wf.spec.views list, since Views are handled after layout
    wf.spec.views.push(spec)
    wf.domEls[spec.id] = { parent: div[0] }
  }


  return div;
}

// Nested views are only supported for ANY and MULTI (adder), thus its children are indexed.
//
// Construct a dictionary where the keys are ancestor view ids, and 
// the values are lists of index, and descendant view ids.  e.g.,
//
// If the layout is
//  
//      cradio
//       0: cars
//       1: hlayout
//          - slider
//          - toggle
//
//  cradio.id: [ 
//    { idx: 0, ref: label.id}
//    { idx: 1, ref: slider.id},
//    { idx: 1, ref: toggle.id}, ... 
//  ]
function nested_widget_hierarchy(spec, wf, hier, idx, parent) {
  if (spec.type === "HLayout" || spec.type === "VLayout") {
    let newparent = parent

    if (spec.widget) {
      if (parent) 
        hier[parent].push({ idx, ref: spec.widget.ref})

      newparent = spec.widget.ref;
      hier[newparent] = []
      spec.children.forEach((c, i) => nested_widget_hierarchy(c, wf, hier, i, newparent))
     }
    else {
      spec.children.forEach((c, i) => nested_widget_hierarchy(c, wf, hier, idx, newparent))
    }
  } else if (parent) {
    let ref = (spec.ref != null)? spec.ref : spec.id;
    if (parent) hier[parent].push({ idx, ref })
  }
}

export function ViewLibrary() {
  function viewLib() {}

  viewLib.library = {
    //Label: Label,
    Bar: Bar(),
    Line: Line(),
    Label: Label(),
    Point: Point(),
    Circle: Circle(),
    Square: Square(),
    Area: Area(),
    Geoshape: Geoshape(),
    Dropdown: Dropdown(),
    Button: Button(),
    RangeSlider: RangeSlider(),
    Checkbox: CheckBox(),
    Slider: Slider(),
    Toggle: Toggle(),
    Table: Table(),
    Radio: Radio(),
  };

  viewLib.iactLib = InteractionLibrary();

  viewLib.buildLayout = ((specRoot, wf) => {
    $(wf.div).append(build_layout(specRoot, wf))

    let hierarchy = {}
    nested_widget_hierarchy(specRoot, wf, hierarchy, 0, null)
    wf.widgetHierarchy = hierarchy

  });

  viewLib.createView = ( (spec, wf) => {
    var id = spec["id"];
    var domEl = wf.domEls[id]; // The element that contains this view
    var typ = spec["type"];
    if (!viewLib.library[typ]) {
      console.error(`Library.createView: View type ${typ} not found`);
      return
    }
    wf.views[id] = viewLib.library[typ].create(spec, domEl, wf);


    if (typ == "Button") {
      let parent = $(domEl.parentNode)
      if (!parent.hasClass("btn-group"))
        parent.addClass("btn-group")
    }
  });

  viewLib.registerInteraction = (
      (spec, wf) => {
          let id = spec["id"];
          wf.interactions[id] = viewLib.iactLib.register(spec, wf);
      }
  );

  return viewLib;
}
