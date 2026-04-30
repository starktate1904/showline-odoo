import { CommonErpChartConfigPanel } from "../common/config_panel";
import { components } from "@odoo/o-spreadsheet";

const { Checkbox } = components;

export class ErpFunnelChartConfigPanel extends CommonErpChartConfigPanel {
    static template = "spreadsheet_edition.ErpFunnelChartConfigPanel";
    static components = {
        ...CommonErpChartConfigPanel.components,
        Checkbox,
    };

    onUpdateCumulative(cumulative) {
        this.props.updateChart(this.props.chartId, {
            cumulative,
        });
    }
}
