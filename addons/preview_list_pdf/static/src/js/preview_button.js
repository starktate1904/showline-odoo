/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { onWillStart, onMounted, onPatched } from "@odoo/owl";

patch(ListController.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.previewListPdfLicensed = false;
        this._previewButtonInjected = false;
        this._injectRetries = 0;

        onWillStart(async () => {
            try {
                this.previewListPdfLicensed = await this.orm.call(
                    "preview.list.license.manager",
                    "is_license_valid",
                    [[]]
                );
            } catch (error) {
                this.previewListPdfLicensed = false;
            }
        });

        onMounted(() => this._tryInjectButton());
        onPatched(() => this._tryInjectButton());
    },

    getStaticActionMenuItems() {
        const items = super.getStaticActionMenuItems(...arguments);
        if (this.previewListPdfLicensed && this.model?.root?.resModel) {
            items.preview_list_pdf = {
                isAvailable: () => true,
                sequence: 15,
                icon: "fa fa-file-pdf-o",
                description: _t("Preview as PDF"),
                callback: () => this._openPreviewPage(),
            };
        }
        return items;
    },

    _tryInjectButton() {
        if (this._previewButtonInjected) return;
        if (!this.previewListPdfLicensed) return;
        if (!this.model?.root?.resModel) return;
        if (this._injectRetries >= 20) return;

        const injected = this._injectButton();
        if (!injected) {
            this._injectRetries++;
            setTimeout(() => this._tryInjectButton(), 500);
        }
    },

    _injectButton() {
        const root = this.rootRef?.el || this.el || document;
        if (!root?.querySelector) return false;
        const container = root.querySelector(".o_control_panel .o_cp_buttons") || document.querySelector(".o_control_panel .o_cp_buttons");
        if (!container) return false;
        if (container.querySelector(".o_preview_pdf_btn")) {
            this._previewButtonInjected = true;
            return true;
        }

        const button = document.createElement("button");
        button.type = "button";
        button.className = "btn btn-secondary o_preview_pdf_btn";
        button.title = _t("Preview this list as PDF");
        button.innerHTML = '<i class="fa fa-file-pdf-o me-1"></i>Preview PDF';
        button.addEventListener("click", (e) => {
            e.preventDefault();
            this._openPreviewPage();
        });
        container.appendChild(button);
        this._previewButtonInjected = true;
        return true;
    },

    _openPreviewPage() {
        if (!this.model?.root?.resModel) {
            return;
        }
        const columns = (this.props?.archInfo?.columns || []).filter((col) => col.type === "field" && col.name);
        const fieldNames = columns.map((col) => col.name);
        const labels = columns.map((col) => col.string || col.name);
        const model = this.model.root.resModel;
        const domain = this.model.root.domain || [];
        const limit = this.model.root.limit || this.model.root.pager?.limit || 80;
        const offset = this.model.root.offset || this.model.root.pager?.offset || 0;
        const total = this.model.root.count || this.model.root.pager?.total || 0;
        if (!fieldNames.length) {
            fieldNames.push("display_name");
            labels.push("Name");
        }
        this.actionService.doAction({
            type: "ir.actions.client",
            tag: "preview_list_pdf_page",
            name: `${_t("PDF Preview")} - ${model}`,
            params: {
                model,
                domain: JSON.stringify(domain),
                fields: JSON.stringify(fieldNames),
                labels: JSON.stringify(labels),
                limit,
                offset,
                total,
            },
        });
    },
});
