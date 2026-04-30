import {
    navigateToErpMenu,
    isChartJSMiddleClick,
} from "@spreadsheet/chart/odoo_chart/odoo_chart_helpers";

export const chartErpMenuPlugin = {
    id: "chartErpMenuPlugin",
    afterEvent(chart, { event }, { env, menu }) {
        const isDashboard = env?.model.getters.isDashboard();
        event.native.target.style.cursor = menu && isDashboard ? "pointer" : "";

        const middleClick = isChartJSMiddleClick(event);
        if (
            (event.type !== "click" && !middleClick) ||
            !menu ||
            !isDashboard ||
            event.native.defaultPrevented
        ) {
            return;
        }
        navigateToErpMenu(menu, env.services.action, env.services.notification, middleClick);
    },
};
