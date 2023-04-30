import { terser } from "rollup-plugin-terser";
import * as meta from "./package.json";
import resolve from "rollup-plugin-node-resolve";
import commonjs from "rollup-plugin-commonjs";

const config = {
  input: "src/browser.js",
  external: Object.keys(meta.dependencies || {}).filter((key) =>
    /^pi-/.test(key)
  ),
  output: {
    file: `../pi-server/static/js/${meta.name}.js`,
    name: "pi",
    format: "umd",
    indent: false,
    extend: true,
    globals: Object.assign(
      {},
      ...Object.keys(meta.dependencies || {})
        //.filter(key => /^pi-/.test(key))
        .map((key) => ({ [key]: key }))
    ),
  },
  plugins: [resolve(), commonjs()],
  onwarn(message, warn) {
    if (message.code === "CIRCULAR_DEPENDENCY") return;
    warn(message);
  },
};

config.output.globals["ramda"] = "R";

export default [
  config,
  {
    ...config,
    output: {
      ...config.output,
      file: `../pi-server/static/js/${meta.name}.min.js`,
    },
    plugins: [
      ...config.plugins,
      terser({
        output: {
          preamble: config.output.banner,
        },
      }),
      resolve({
        jsnext: true,
        main: true,
        browser: true,
      }),
      resolve(),
      commonjs(),
    ],
  },
];
