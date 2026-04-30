import { components } from "@odoo/o-spreadsheet";
import { patch } from "@web/core/utils/patch";

patch(components.ChartJsComponent.prototype, {
    createChart(chartData) {
        if (this.env.model.getters.isDashboard()) {
            chartData = this.addErpMenuPluginToChartData(chartData);
        }
        super.createChart(chartData);
    },
    updateChartJs(chartData) {
        if (this.env.model.getters.isDashboard()) {
            chartData = this.addErpMenuPluginToChartData(chartData);
        }
        super.updateChartJs(chartData);
    },
    addErpMenuPluginToChartData(chartData) {
        chartData.chartJsConfig.options.plugins.chartErpMenuPlugin = {
            env: this.env,
            menu: this.env.model.getters.getChartErpMenu(this.props.chartId),
        };
        return chartData;
    },
});
