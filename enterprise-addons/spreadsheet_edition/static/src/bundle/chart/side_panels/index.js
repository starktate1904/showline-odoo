import * as spreadsheet from "@odoo/o-spreadsheet";
import { CommonErpChartConfigPanel } from "./common/config_panel";
import { ErpBarChartConfigPanel } from "./odoo_bar/odoo_bar_config_panel";
import { ErpLineChartConfigPanel } from "./odoo_line/odoo_line_config_panel";
import { ErpGeoChartConfigPanel } from "./odoo_geo/odoo_geo_config_panel";
import { ErpFunnelChartConfigPanel } from "./odoo_funnel/odoo_funnel_config_panel";

const { chartSidePanelComponentRegistry } = spreadsheet.registries;
const {
    ComboChartDesignPanel,
    PieChartDesignPanel,
    ChartWithAxisDesignPanel,
    LineChartDesignPanel,
    RadarChartDesignPanel,
    WaterfallChartDesignPanel,
    GeoChartDesignPanel,
    FunnelChartDesignPanel,
    SunburstChartDesignPanel,
    TreeMapChartDesignPanel,
    GenericZoomableChartDesignPanel,
} = spreadsheet.components;

chartSidePanelComponentRegistry
    .add("odoo_line", {
        configuration: ErpLineChartConfigPanel,
        design: LineChartDesignPanel,
    })
    .add("odoo_bar", {
        configuration: ErpBarChartConfigPanel,
        design: GenericZoomableChartDesignPanel,
    })
    .add("odoo_pie", {
        configuration: CommonErpChartConfigPanel,
        design: PieChartDesignPanel,
    })
    .add("odoo_radar", {
        configuration: CommonErpChartConfigPanel,
        design: RadarChartDesignPanel,
    })
    .add("odoo_sunburst", {
        configuration: CommonErpChartConfigPanel,
        design: SunburstChartDesignPanel,
    })
    .add("odoo_treemap", {
        configuration: CommonErpChartConfigPanel,
        design: TreeMapChartDesignPanel,
    })
    .add("odoo_waterfall", {
        configuration: CommonErpChartConfigPanel,
        design: WaterfallChartDesignPanel,
    })
    .add("odoo_pyramid", {
        configuration: CommonErpChartConfigPanel,
        design: ChartWithAxisDesignPanel,
    })
    .add("odoo_scatter", {
        configuration: CommonErpChartConfigPanel,
        design: GenericZoomableChartDesignPanel,
    })
    .add("odoo_combo", {
        configuration: CommonErpChartConfigPanel,
        design: ComboChartDesignPanel,
    })
    .add("odoo_geo", {
        configuration: ErpGeoChartConfigPanel,
        design: GeoChartDesignPanel,
    })
    .add("odoo_funnel", {
        configuration: ErpFunnelChartConfigPanel,
        design: FunnelChartDesignPanel,
    });
