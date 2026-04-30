import { CommonErpChartConfigPanel } from "../common/config_panel";
import { components } from "@odoo/o-spreadsheet";

const { Checkbox } = components;

export class ErpLineChartConfigPanel extends CommonErpChartConfigPanel {
    static template = "spreadsheet_edition.ErpLineChartConfigPanel";
    static components = {
        ...CommonErpChartConfigPanel.components,
        Checkbox,
    };

    get stackedLabel() {
        const definition = this.props.definition;
        return definition.fillArea
            ? this.chartTerms.StackedAreaChart
            : this.chartTerms.StackedLineChart;
    }

    onUpdateStacked(stacked) {
        this.props.updateChart(this.props.chartId, {
            stacked,
        });
    }
    onUpdateCumulative(cumulative) {
        this.props.updateChart(this.props.chartId, {
            cumulative,
        });
    }
    onUpdateCumulatedStart(cumulatedStart) {
        this.props.updateChart(this.props.chartId, {
            cumulatedStart,
        });
    }
}
