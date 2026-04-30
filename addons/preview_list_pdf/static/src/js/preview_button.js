/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { onWillStart } from "@odoo/owl";

patch(ListController.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.previewListPdfLicensed = false;
        onWillStart(async () => {
            this.previewListPdfLicensed = await this.orm.call(
                "preview.list.license.manager",
                "is_license_valid",
                [[]]
            );
        });
    },

    getStaticActionMenuItems() {
        const items = super.getStaticActionMenuItems(...arguments);
        if (!this.previewListPdfLicensed || !this.model?.root?.resModel) {
            return items;
        }
        const columns = (this.props?.archInfo?.columns || []).filter((col) => col.type === "field" && col.name);
        const fieldNames = columns.map((col) => col.name);
        const labels = columns.map((col) => col.string || col.name);
        const model = this.model.root.resModel;
        const domain = this.model.root.domain || [];
        const menuItems = items?.other || [];
        menuItems.push({
            key: "preview_list_pdf",
            description: _t("Preview List PDF"),
            icon: "fa fa-print",
            callback: () => {
                const url =
                    `/preview/pdf/${encodeURIComponent(model)}` +
                    `?domain=${encodeURIComponent(JSON.stringify(domain))}` +
                    `&fields=${encodeURIComponent(JSON.stringify(fieldNames))}` +
                    `&labels=${encodeURIComponent(JSON.stringify(labels))}`;
                this.actionService.doAction({
                    type: "ir.actions.act_url",
                    url,
                    target: "new",
                });
            },
        });
        items.other = menuItems;
        return items;
    },
});
