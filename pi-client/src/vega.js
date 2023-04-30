export let vegaLite;
export let vega;
export let vl;
export let vegaEmbed;

/**
 * Due to this package being used both as a package import in the Jupyter Lab
 * extension build and as a bundle in the browser, we need to allow the two
 * entry points to provide access to vega libraries in different ways.
 *
 * ALL code depending on vega (views, etc.) should import vega through thiss
 * module in order to get access to the version of the package provided by the
 * current runtime. Do NOT `import * as vl from "vega-lite-api"` directly at
 * the top of any modules!
 *
 * @param {*} _vegaLite
 * @param {*} _vega
 * @param {*} _vl
 * @param {*} _vegaEmbed
 */
export function initializeVega(_vegaLite, _vega, _vl, _vegaEmbed) {
  vegaLite = _vegaLite;
  vega = _vega;
  vl = _vl;
  vegaEmbed = _vegaEmbed;
}
