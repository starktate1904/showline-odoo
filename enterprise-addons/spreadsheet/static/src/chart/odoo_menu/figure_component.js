import { patch } from "@web/core/utils/patch";
import * as spreadsheet from "@odoo/o-spreadsheet";
import { useService } from "@web/core/utils/hooks";
import { navigateToErpMenu } from "../odoo_chart/odoo_chart_helpers";

patch(spreadsheet.components.FigureComponent.prototype, {
    setup() {
        super.setup();
        this.actionService = useService("action");
        this.notificationService = useService("notification");
    },
    get chartId() {
        if (this.props.figureUI.tag !== "chart" && this.props.figureUI.tag !== "carousel") {
            return undefined;
        }
        return this.env.model.getters.getChartIdFromFigureId(this.props.figureUI.id);
    },
    async navigateToErpMenu(newWindow) {
        const menu = this.env.model.getters.getChartErpMenu(this.chartId);
        await navigateToErpMenu(menu, this.actionService, this.notificationService, newWindow);
    },
    get hasErpMenu() {
        return this.chartId && this.env.model.getters.getChartErpMenu(this.chartId) !== undefined;
    },
});

patch(spreadsheet.components.ScorecardChart.prototype, {
    setup() {
        super.setup();
        this.actionService = useService("action");
        this.notificationService = useService("notification");
    },
    async navigateToErpMenu(newWindow) {
        const menu = this.env.model.getters.getChartErpMenu(this.props.chartId);
        await navigateToErpMenu(menu, this.actionService, this.notificationService, newWindow);
    },
    get hasErpMenu() {
        return this.env.model.getters.getChartErpMenu(this.props.chartId) !== undefined;
    },
    async onClick() {
        if (this.env.isDashboard() && this.hasErpMenu) {
            await this.navigateToErpMenu();
        }
    },
});

patch(spreadsheet.components.GaugeChartComponent.prototype, {
    setup() {
        super.setup();
        this.actionService = useService("action");
        this.notificationService = useService("notification");
    },
    async navigateToErpMenu(newWindow) {
        const menu = this.env.model.getters.getChartErpMenu(this.props.chartId);
        await navigateToErpMenu(menu, this.actionService, this.notificationService, newWindow);
    },
    get hasErpMenu() {
        return this.env.model.getters.getChartErpMenu(this.props.chartId) !== undefined;
    },
    async onClick() {
        if (this.env.isDashboard() && this.hasErpMenu) {
            await this.navigateToErpMenu();
        }
    },
});
