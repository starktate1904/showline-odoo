import { registries, chartHelpers } from "@odoo/o-spreadsheet";
import { _t } from "@web/core/l10n/translation";
import { ErpChart } from "./odoo_chart";
import { onErpChartItemHover, onErpChartItemClick } from "./odoo_chart_helpers";

const { chartRegistry } = registries;

const {
    getFunnelChartDatasets,
    CHART_COMMON_OPTIONS,
    getChartLayout,
    getChartTitle,
    getChartShowValues,
    getFunnelChartScales,
    getFunnelChartTooltip,
    makeDatasetsCumulative,
} = chartHelpers;

export class ErpFunnelChart extends ErpChart {
    constructor(definition, sheetId, getters) {
        super(definition, sheetId, getters);
        this.cumulative = definition.cumulative;
        this.funnelColors = definition.funnelColors;
    }

    getDefinition() {
        return {
            ...super.getDefinition(),
            cumulative: this.cumulative,
            funnelColors: this.funnelColors,
        };
    }
}

chartRegistry.add("odoo_funnel", {
    match: (type) => type === "odoo_funnel",
    createChart: (definition, sheetId, getters) =>
        new ErpFunnelChart(definition, sheetId, getters),
    getChartRuntime: createErpChartRuntime,
    validateChartDefinition: (validator, definition) =>
        ErpFunnelChart.validateChartDefinition(validator, definition),
    transformDefinition: (definition) => ErpFunnelChart.transformDefinition(definition),
    getChartDefinitionFromContextCreation: () => ErpFunnelChart.getDefinitionFromContextCreation(),
    name: _t("Funnel"),
});

function createErpChartRuntime(chart, getters) {
    const definition = chart.getDefinition();
    const background = chart.background || "#FFFFFF";
    let { datasets, labels } = chart.dataSource.getData();
    if (definition.cumulative) {
        datasets = makeDatasetsCumulative(datasets, "desc");
    }

    const locale = getters.getLocale();

    const chartData = {
        labels,
        dataSetsValues: datasets.map((ds) => ({ data: ds.data, label: ds.label })),
        locale,
    };

    const config = {
        type: "funnel",
        data: {
            labels: chartData.labels,
            datasets: getFunnelChartDatasets(definition, chartData),
        },
        options: {
            ...CHART_COMMON_OPTIONS,
            indexAxis: "y",
            layout: getChartLayout(definition, chartData),
            scales: getFunnelChartScales(definition, chartData),
            plugins: {
                title: getChartTitle(definition, getters),
                legend: { display: false },
                tooltip: getFunnelChartTooltip(definition, chartData),
                chartShowValuesPlugin: getChartShowValues(definition, chartData),
            },
            onHover: onErpChartItemHover(),
            onClick: onErpChartItemClick(getters, chart),
        },
    };

    return { background, chartJsConfig: config };
}
