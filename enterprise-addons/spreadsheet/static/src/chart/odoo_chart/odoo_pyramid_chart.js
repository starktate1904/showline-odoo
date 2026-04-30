import { registries, chartHelpers } from "@odoo/o-spreadsheet";
import { _t } from "@web/core/l10n/translation";
import { ErpChart } from "./odoo_chart";
import { onErpChartItemHover, onErpChartItemClick } from "./odoo_chart_helpers";

const { chartRegistry } = registries;

const {
    CHART_COMMON_OPTIONS,
    getBarChartDatasets,
    getChartLayout,
    getChartTitle,
    getPyramidChartShowValues,
    getPyramidChartScales,
    getBarChartLegend,
    getPyramidChartTooltip,
} = chartHelpers;

export class ErpPyramidChart extends ErpChart {
    constructor(definition, sheetId, getters) {
        super(definition, sheetId, getters);
        this.axesDesign = definition.axesDesign;
    }

    getDefinition() {
        return {
            ...super.getDefinition(),
            axesDesign: this.axesDesign,
            horizontal: true,
            stacked: true,
        };
    }
}

chartRegistry.add("odoo_pyramid", {
    match: (type) => type === "odoo_pyramid",
    createChart: (definition, sheetId, getters) =>
        new ErpPyramidChart(definition, sheetId, getters),
    getChartRuntime: createErpChartRuntime,
    validateChartDefinition: (validator, definition) =>
        ErpPyramidChart.validateChartDefinition(validator, definition),
    transformDefinition: (definition) => ErpPyramidChart.transformDefinition(definition),
    getChartDefinitionFromContextCreation: () =>
        ErpPyramidChart.getDefinitionFromContextCreation(),
    name: _t("Pyramid"),
});

function createErpChartRuntime(chart, getters) {
    const background = chart.background || "#FFFFFF";
    const { datasets, labels } = chart.dataSource.getData();

    const pyramidDatasets = [];
    if (datasets[0]) {
        const pyramidData = datasets[0].data.map((value) => (value > 0 ? value : 0));
        pyramidDatasets.push({ ...datasets[0], data: pyramidData });
    }
    if (datasets[1]) {
        const pyramidData = datasets[1].data.map((value) => (value > 0 ? -value : 0));
        pyramidDatasets.push({ ...datasets[1], data: pyramidData });
    }

    const definition = chart.getDefinition();
    const locale = getters.getLocale();

    const chartData = {
        labels,
        dataSetsValues: pyramidDatasets.map((ds) => ({ data: ds.data, label: ds.label })),
        locale,
    };

    const config = {
        type: "bar",
        data: {
            labels: chartData.labels,
            datasets: getBarChartDatasets(definition, chartData),
        },
        options: {
            ...CHART_COMMON_OPTIONS,
            indexAxis: "y",
            layout: getChartLayout(definition, chartData),
            scales: getPyramidChartScales(definition, chartData),
            plugins: {
                title: getChartTitle(definition, getters),
                legend: getBarChartLegend(definition, chartData),
                tooltip: getPyramidChartTooltip(definition, chartData),
                chartShowValuesPlugin: getPyramidChartShowValues(definition, chartData),
            },
            onHover: onErpChartItemHover(),
            onClick: onErpChartItemClick(getters, chart),
        },
    };

    return { background, chartJsConfig: config };
}
