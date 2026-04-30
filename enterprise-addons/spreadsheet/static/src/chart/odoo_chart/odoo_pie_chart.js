import { registries, chartHelpers } from "@odoo/o-spreadsheet";
import { _t } from "@web/core/l10n/translation";
import { ErpChart } from "./odoo_chart";
import { onErpChartItemHover, onErpChartItemClick } from "./odoo_chart_helpers";

const { chartRegistry } = registries;

const {
    getPieChartDatasets,
    CHART_COMMON_OPTIONS,
    getChartLayout,
    getPieChartTooltip,
    getChartTitle,
    getPieChartLegend,
    getChartShowValues,
    getTopPaddingForDashboard,
} = chartHelpers;

export class ErpPieChart extends ErpChart {
    constructor(definition, sheetId, getters) {
        super(definition, sheetId, getters);
        this.isDoughnut = definition.isDoughnut;
    }

    getDefinition() {
        return {
            ...super.getDefinition(),
            isDoughnut: this.isDoughnut,
        };
    }
}

chartRegistry.add("odoo_pie", {
    match: (type) => type === "odoo_pie",
    createChart: (definition, sheetId, getters) => new ErpPieChart(definition, sheetId, getters),
    getChartRuntime: createErpChartRuntime,
    validateChartDefinition: (validator, definition) =>
        ErpPieChart.validateChartDefinition(validator, definition),
    transformDefinition: (definition) => ErpPieChart.transformDefinition(definition),
    getChartDefinitionFromContextCreation: () => ErpPieChart.getDefinitionFromContextCreation(),
    name: _t("Pie"),
});

function createErpChartRuntime(chart, getters) {
    const background = chart.background || "#FFFFFF";
    const { datasets, labels } = chart.dataSource.getData();
    const definition = chart.getDefinition();
    definition.dataSets = datasets.map(() => ({ trend: definition.trend }));

    const chartData = {
        labels,
        dataSetsValues: datasets.map((ds) => ({ data: ds.data, label: ds.label })),
        locale: getters.getLocale(),
        topPadding: getTopPaddingForDashboard(definition, getters),
    };

    const config = {
        type: definition.isDoughnut ? "doughnut" : "pie",
        data: {
            labels: chartData.labels,
            datasets: getPieChartDatasets(definition, chartData),
        },
        options: {
            ...CHART_COMMON_OPTIONS,
            layout: getChartLayout(definition, chartData),
            plugins: {
                title: getChartTitle(definition, getters),
                legend: getPieChartLegend(definition, chartData),
                tooltip: getPieChartTooltip(definition, chartData),
                chartShowValuesPlugin: getChartShowValues(definition, chartData),
            },
            onHover: onErpChartItemHover(),
            onClick: onErpChartItemClick(getters, chart),
        },
    };

    return { background, chartJsConfig: config };
}
