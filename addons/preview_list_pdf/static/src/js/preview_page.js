/** @odoo-module **/

import { Component, onMounted, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

export class PreviewListPdfPage extends Component {
    static template = "preview_list_pdf.PreviewPage";
    static props = { ...standardActionServiceProps };

    setup() {
        this.state = useState({
            loading: true,
            pdfUrl: "",
            error: "",
        });
        onMounted(() => this._loadPdf());
    }

    get params() {
        return this.props.action?.params || {};
    }

    get model() {
        return this.params.model || "unknown.model";
    }

    get limit() {
        return Number(this.params.limit || 80);
    }

    get offset() {
        return Number(this.params.offset || 0);
    }

    get total() {
        return Number(this.params.total || 0);
    }

    async _loadPdf() {
        try {
            const params = new URLSearchParams({
                domain: this.params.domain || "[]",
                fields: this.params.fields || "[]",
                labels: this.params.labels || "[]",
                limit: String(this.limit),
                offset: String(this.offset),
                total: String(this.total),
            });
            this.state.pdfUrl = `/preview/pdf/${encodeURIComponent(this.model)}?${params.toString()}`;
            this.state.loading = false;
        } catch (error) {
            this.state.error = error?.message || _t("Unable to generate preview URL.");
            this.state.loading = false;
        }
    }

    downloadPdf() {
        if (!this.state.pdfUrl) return;
        const link = document.createElement("a");
        link.href = `${this.state.pdfUrl}&download=1`;
        link.download = `${this.model}_preview.pdf`;
        link.click();
    }

    printPdf() {
        const frame = this.el?.querySelector("iframe");
        if (frame?.contentWindow) {
            frame.contentWindow.print();
        }
    }

    goBack() {
        window.history.back();
    }
}

registry.category("actions").add("preview_list_pdf_page", PreviewListPdfPage);
