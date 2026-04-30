/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

patch(ListController.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.dialog = useService("dialog");
    },

    async renderButtons() {
        await super.renderButtons?.(...arguments);
        if (!this.el || !this.model?.root?.resModel || this.el.querySelector(".o_preview_pdf_btn")) {
            return;
        }
        const isValid = await this.orm.call("preview.list.license.manager", "_is_license_valid", []);
        if (!isValid) {
            return;
        }
        const button = document.createElement("button");
        button.className = "btn btn-secondary o_preview_pdf_btn";
        button.type = "button";
        button.textContent = "Preview PDF";
        button.addEventListener("click", () => {
            const model = this.model.root.resModel;
            const domain = encodeURIComponent(JSON.stringify(this.model.root.domain || []));
            const url = `/preview/pdf/${model}?domain=${domain}`;
            this.actionService.doAction({
                type: "ir.actions.act_url",
                url,
                target: "new",
            });
        });
        const cpButtons = this.el.querySelector(".o_cp_buttons");
        if (cpButtons) {
            cpButtons.appendChild(button);
        }
    },
});
