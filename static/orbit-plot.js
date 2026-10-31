/* Initialize the optional orbit chart after its local Plotly bundle loads. */
(function () {
    "use strict";

    var chart = document.getElementById("orbit-plot");
    var payload = document.getElementById("orbit-plot-data");
    var error = document.getElementById("orbit-plot-error");
    if (!chart || !payload) {
        return;
    }

    function showError() {
        chart.hidden = true;
        if (error) {
            error.hidden = false;
        }
    }

    try {
        if (!window.Plotly) {
            showError();
            return;
        }
        var figure = JSON.parse(payload.textContent);
        window.Plotly.newPlot(chart, figure.data, figure.layout, figure.config)
            .catch(showError);
    } catch (exception) {
        showError();
    }
}());
