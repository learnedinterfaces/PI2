// XXX: We assume that mappings only renames data
// We do not support positional attributes because tuples are objects
export default function project(data, mappings) {
  if (!mappings) return data;
  if (!data) return data;
  var entries = Object.entries(mappings);
  let num = /^-?[\d]+$/;
  var f = (o) => {
    var ret = {};
    for (let [tar, src] of entries) {
      if (num.test(o[src]))
        ret[tar] = parseInt(o[src])
      else
        ret[tar] = o[src]
    }
    return ret;
  };
  if (Array.isArray(data))
    return data.map(f);
	else return f(data);
}
