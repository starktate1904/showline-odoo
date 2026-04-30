import { registries, chartHelpers } from "@odoo/o-spreadsheet";
import { _t } from "@web/core/l10n/translation";
import { ErpChart } from "./odoo_chart";
import { onGeoErpChartItemHover, onGeoErpChartItemClick } from "./odoo_chart_helpers";

const { chartRegistry } = registries;

const {
    getGeoChartDatasets,
    CHART_COMMON_OPTIONS,
    getChartLayout,
    getChartTitle,
    getGeoChartScales,
    getGeoChartTooltip,
} = chartHelpers;

export class ErpGeoChart extends ErpChart {
    constructor(definition, sheetId, getters) {
        super(definition, sheetId, getters);
        this.colorScale = definition.colorScale;
        this.missingValueColor = definition.missingValueColor;
        this.region = definition.region;
    }

    getDefinition() {
        return {
            ...super.getDefinition(),
            colorScale: this.colorScale,
            missingValueColor: this.missingValueColor,
            region: this.region,
        };
    }
}

chartRegistry.add("odoo_geo", {
    match: (type) => type === "odoo_geo",
    createChart: (definition, sheetId, getters) => new ErpGeoChart(definition, sheetId, getters),
    getChartRuntime: createErpChartRuntime,
    validateChartDefinition: (validator, definition) =>
        ErpGeoChart.validateChartDefinition(validator, definition),
    transformDefinition: (definition) => ErpGeoChart.transformDefinition(definition),
    getChartDefinitionFromContextCreation: () => ErpGeoChart.getDefinitionFromContextCreation(),
    name: _t("Geo"),
});

function createErpChartRuntime(chart, getters) {
    const background = chart.background || "#FFFFFF";
    const { datasets, labels } = chart.dataSource.getData();

    const definition = chart.getDefinition();
    const locale = getters.getLocale();

    const chartData = {
        labels,
        dataSetsValues: datasets.map((ds) => ({ data: ds.data, label: ds.label })),
        locale,
        availableRegions: getters.getGeoChartAvailableRegions(),
        geoFeatureNameToId: getters.geoFeatureNameToId,
        getGeoJsonFeatures: getters.getGeoJsonFeatures,
    };

    const config = {
        type: "choropleth",
        data: {
            datasets: getGeoChartDatasets(definition, chartData),
        },
        options: {
            ...CHART_COMMON_OPTIONS,
            layout: getChartLayout(definition, chartData),
            scales: getGeoChartScales(definition, chartData),
            plugins: {
                title: getChartTitle(definition, getters),
                tooltip: getGeoChartTooltip(definition, chartData),
                legend: { display: false },
            },
            onHover: onGeoErpChartItemHover(),
            onClick: onGeoErpChartItemClick(getters, chart),
        },
    };

    return { background, chartJsConfig: config };
}
