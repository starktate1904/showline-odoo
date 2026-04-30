import { CommonErpChartConfigPanel } from "../common/config_panel";
import { components } from "@odoo/o-spreadsheet";

const { Checkbox } = components;

export class ErpBarChartConfigPanel extends CommonErpChartConfigPanel {
    static template = "spreadsheet_edition.ErpBarChartConfigPanel";

    static components = {
        ...CommonErpChartConfigPanel.components,
        Checkbox,
    };

    onUpdateStacked(stacked) {
        this.props.updateChart(this.props.chartId, {
            stacked,
        });
    }
}
