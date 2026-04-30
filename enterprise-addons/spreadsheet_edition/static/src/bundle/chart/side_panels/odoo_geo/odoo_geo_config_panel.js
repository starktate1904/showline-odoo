import { CommonErpChartConfigPanel } from "../common/config_panel";
import { components } from "@odoo/o-spreadsheet";

const { GeoChartRegionSelectSection } = components;

export class ErpGeoChartConfigPanel extends CommonErpChartConfigPanel {
    static template = "spreadsheet_edition.ErpGeoChartConfigPanel";
    static components = {
        ...CommonErpChartConfigPanel.components,
        GeoChartRegionSelectSection,
    };
}
