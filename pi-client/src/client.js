import { RandomBackend } from "./backend/index.js";
import {makeFlex} from "./view/util.js";
import {default as project} from "./view/project.js";


// Variables to toggle code paths



var isLayoutSpec = (spec) => {
  return spec.type == "HLayout" || spec.type == "VLayout";
}


var piclient = (function(config) {
  var viewLibrary = config.library;
  var backendLibrary = config.backendLibrary; 
  var _div = config.div;

  var viewSpecs = {}; // id --> spec
  var views = {};    // id --> view
  var viewQs = {};   // id --> { cur: ,  latestM: }  
  var interactions = {};   // src view id --> list of interaction objects

  function client() { }

  client.viewLibrary = viewLibrary;
  client.backendLibrary = backendLibrary;

  var setupUtil = (parentEl, specs) => { 
    if (!specs || specs.length == 0) return;

    specs.forEach((spec, i) => {
      var div = document.createElement('div');
      parentEl.appendChild(div);
      if(isLayoutSpec(spec)) { 
        div.id = spec["type"];
        makeFlex(div, div.id);
        setupUtil(div, spec['children']);
      }
      else {
        client.createView(parentEl, spec);
      }
    })
  }

  var newBackendName = () => {
    _backendId++;
    return "backend_" + _backendId;
  }

  client.createView = (div, spec) => {
    if (viewSpecs[spec.ref]) 
      return client.createView(div, viewSpecs[spec.ref]);

    var vid = spec['vid'];
    var view = null;
    let { backend, q } = handleDataSpec(spec['data'], view, socket);
    spec.backend = backend;
    view = viewLibrary.createView(spec.type, spec);
    div.id = 'vis' + vid;
    div.appendChild(view.domEl());

    viewQs[vid] = { 
      cur: q,         // view's current query state
      latestM: null   // cache last manipulation query
    }

    backend.execute(q, ({ sql, data }) => {
      view.render(data); 
    });

    views[vid] = view;
    return view;
  }

  // Instantiates or fetches the appropriate backend
  // and q given the data spec
  //
  // TODO: redesign how backend is specified in view.data 
  //       so that nested backends can be specified inline rather
  //       than only at the top level "backends" spec
  //
  // @spec the data spec
  // @returns { backend: , q: }
  var handleDataSpec = (spec, view, socket) => {
    var backend = null, q = null;
    if (backendLibrary.get(spec['backend'])) {
      backend = backendLibrary.get(spec['backend']);
    } else {
      backend = backendLibrary.createBackend(spec['type'], spec, socket);
    }
    // TODO: consolidate spec documentation to remove spec['params']
    q = spec['query'] || spec['params'];

    return {
      backend: backend,
      q: q
    }
  }

  client.getView = (vid) => {
    return views[vid] || null;
  }


  var setupBackends = (spec, socket) => {
    (spec["backend"] || []).forEach((backendSpec) => {
      backendLibrary.createBackend(backendSpec.type, backendSpec, socket);
    });
    console.log("finished setting up backends.");
  };


  var setupInteractions = function(spec) {
    (spec["interaction"] || []).forEach((iact) => {
      var srcid = iact["source"].toString();
      var tarid = iact.target.toString();
      if (!interactions[srcid])
         interactions[srcid] = []
      interactions[srcid].push(iact);

    });

    (Object.keys(interactions)).forEach((srcid) => {
      var src = views[srcid];

      // m should be same across all interactions
      var m = interactions[srcid][0].m; 
      
      src.on(m, (manipulationData) => {
        console.log(manipulationData);
        (interactions[srcid]).forEach((iact) => {
          processManipulation(manipulationData, iact);
        });
      }, () => {
        (interactions[srcid]).forEach((iact) => {
				  iact.target.forEach((target) => {
            var state = viewQs[target];
            var target = views[target];
            state.cur = target.backend().merge(state.cur, state.latestM)
					});
        });
      }, () => { console.log("abort"); //TODO: replace with actual abort CB
      });      
    });
  };

  var processManipulation = (m, iact) => {
    if (typeof iact.target == "number") 
      iact.target = [iact.target]; 
      iact.target.forEach((target) => {
        var tar = views[target];
        var t = tar.backend().registerTransformation(iact.t);
        var h = project(m, iact.h);
        var q_m = t(h);
        var q_view = viewQs[target].cur;
        var Q = tar.backend().merge(q_view, q_m);
        viewQs[target].latestM = q_m;

        tar.backend().execute(Q, ({ sql, data }) => { 
            console.log(data);
            tar.render(data) 
        })
    });
  };

  client.setup = async function(spec) {
    setupBackends(spec);
    var outerDiv = document.createElement('div');
    outerDiv.id = spec["name"];
    if(isLayoutSpec(spec["wroot"]))
      makeFlex(outerDiv, spec["wroot"]["name"]);

    _div.appendChild(outerDiv);
    //Shaky solution to wait for data to load but not sure what a better way would be. 
    await new Promise(done => setTimeout(() => done(), 250)); 

    (spec.views || []).forEach((spec) => {
      viewSpecs[spec.vid] = spec;
    });

    setupUtil(outerDiv, [spec["wroot"]]);
    setupInteractions(spec);
  }


  return client;
});

export function Client(config) { return piclient(config); };

