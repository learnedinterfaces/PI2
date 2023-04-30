export function InteractionLibrary() {
    function iactLib() {}

    /*
    "interaction":[
    {
      "id": 1,
      "source": 0,
      "target": 1,
      "m":
      {
        type: "BRUSH",
        space: "mark"
      }
      "h":
      {
          "cn1": "xmin",
          "cn2": "xmax"
      }
    }
     */

    iactLib.register = ( (spec, wf) => {
      function iact() {}

      iact.id = spec["id"];
      iact.source = wf.views[spec["source"]];
      iact.target = wf.views[spec["target"]];
      iact.type = spec["m"]["type"];
      iact.space = spec["m"]["space"];
      iact.delta_query = spec["h"];

      iact.resolve_data = ( (data) => {
        if (data.length === 0) {
            return [{"selected": 0, "xmin": '-inf', "xmax": 'inf', "ymin": '-inf', "ymax": 'inf'}];
        }
        for (let i in data) {
          try {
            const zeroPad = (num, places) => String(num).padStart(places, '0')
            let d = zeroPad(data[i].getYear()+1900, 4) + "-" + zeroPad(data[i].getMonth()+1, 2) + "-" +  zeroPad(data[i].getDate(), 2);
            data[i] = d;
          }
          catch (error) {}
        }
        for (let cn in iact.delta_query) {
            let event = iact.delta_query[cn];
            if (["BRUSHX", "ZOOMX", "PANX"].includes(iact.type)) {
                var xmin = null;
                var xmax = null;
                for (let d in data) {
                    if (xmin == null || data[d] < xmin) xmin = data[d];
                    if (xmax == null || data[d] > xmax) xmax = data[d];
                }
                return [{"xmin": xmin.toString(), "xmax": xmax.toString(), "selected": 1}]
            }
            if (["BRUSHY", "ZOOMY", "PANY"].includes(iact.type)) {
                var ymin = null;
                var ymax = null;
                for (let d in data) {
                    if (ymin == null || data[d] < ymin) ymin = data[d];
                    if (ymax == null || data[d] > ymax) ymax = data[d];
                }
                return [{"ymin": ymin.toString(), "ymax": ymax.toString(), "selected": 1}]
            }
            else if (["BRUSHXY", "ZOOMXY", "PANXY"].includes(iact.type)) {
                return [{"xmin": Math.min(data[0], data[1]).toString(), 
                         "xmax": Math.max(data[0], data[1]).toString(), 
                         "ymin": Math.min(data[2], data[3]).toString(), 
                         "ymax": Math.max(data[2], data[3]).toString(),
                         "selected": 1}]
            }
        }
        return data;
      });

      iact.trigger = ( (data) => {
        data = iact.resolve_data(data);
        iact.target.deltaQuery( (query) => {
          let ids = []
          for (let cn in iact.delta_query) {
            query[cn] = [];
            ids.push(cn)
            for (let d in data) {
              if (iact.delta_query[cn] in data[d])
                query[cn].push(data[d][iact.delta_query[cn]]);
              else
                query[cn].push(iact.delta_query[cn]);
            }
          }
          return [query, ids];
        });
      });

      // essentially does the same as trigger but uses previewDeltaQuery rather than deltaQuery (so the query does not
      // save).
      iact.preview = ( (data) => {
        data = iact.resolve_data(data);
        iact.target.previewDeltaQuery((query) => {
          let ids = [];
          for (let cn in iact.delta_query) {
            query[cn] = [];
            ids.push(cn);

            for (let d in data) {
              if (iact.delta_query[cn] in data[d])
                query[cn].push(data[d][iact.delta_query[cn]]);
              else
                query[cn].push(iact.delta_query[cn]);
            }
          }
          return [query, ids];
        });
      })

      iact.source.addSourceIact(iact);

      return iact;
  });

  return iactLib;
}
