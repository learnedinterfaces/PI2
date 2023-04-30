import noUiSlider from 'nouislider';
import { makeEventEmitter, showPreview, hidePreview } from "./util.js"

export function RangeSlider() {
    function rangeslider() {}

    rangeslider.create = (
        (spec, domEl, wf) => {
            function view() {}

            view.spec = spec;
            view.domEl = domEl["parent"];
            view.id = spec["id"];

            view.manipulationSchema = (m) => {};
            view.deltaQuery = (delta) => {};

            view.render = (
                (data) => {
                    noUiSlider.create(view.domEl, {
                        start: [data.min, data.max],
                        behaviour: 'hover',
                        tooltips: true,
                        connect: true,
                        range: {
                            'min': data.min,
                            'max': data.max
                        }
                    });
                    view.domEl.style.padding = "50px";
                    view.domEl.style.margin = "0px";

                    view.domEl.noUiSlider.on("change", function() {
                        var range = view.domEl.noUiSlider.get();
                        view.source_iact.forEach(
                            (iact) => {
                                iact.trigger([{"left": range[0], "right": range[1]}]);
                            }
                        );
                    });

                    $("#" + view.id).hover(() => {
                      let range = view.domEl.noUiSlider.get();
                      view.source_iact.forEach(
                        (iact) => {
                          iact.preview([{"left": range[0], "right": range[1]}]);
                        }
                      )
                      showPreview()
                    }, () => {
                      hidePreview()
                    })

                }
            );

            view.render(spec["data"]);

            view.source_iact = [];

            view.addSourceIact = ((iact) => view.source_iact.push(iact));

            return makeEventEmitter(view);
        }
    );

    return rangeslider;
}
