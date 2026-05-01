/** @odoo-module **/

import { Component, onMounted, useState, onWillUnmount } from "@odoo/owl";
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
            progress: 0,
            progressText: "Initializing...",
        });
        this.progressInterval = null;
        this.loadingMessages = [
            "Preparing data...",
            "Fetching records...",
            "Formatting table...",
            "Generating PDF...",
            "Almost ready...",
        ];
        this.currentMessageIndex = 0;
        this.messageInterval = null;
        
        onMounted(() => this._loadPdf());
        onWillUnmount(() => this._cleanup());
    }

    _cleanup() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        if (this.messageInterval) {
            clearInterval(this.messageInterval);
        }
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

    _startProgressAnimation() {
        let progress = 0;
        const totalSteps = this.loadingMessages.length;
        
        this.progressInterval = setInterval(() => {
            if (progress < 90) {
                // Smooth progress increase
                const increment = (90 - progress) * 0.1 + Math.random() * 3;
                progress += increment;
                if (progress > 90) progress = 90;
                this.state.progress = Math.round(progress);
            }
        }, 200);
        
        // Rotate through loading messages
        this.messageInterval = setInterval(() => {
            this.currentMessageIndex = (this.currentMessageIndex + 1) % this.loadingMessages.length;
            this.state.progressText = this.loadingMessages[this.currentMessageIndex];
        }, 1500);
    }

    _stopProgressAnimation() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        if (this.messageInterval) {
            clearInterval(this.messageInterval);
            this.messageInterval = null;
        }
        this.state.progress = 100;
        this.state.progressText = "Complete!";
        setTimeout(() => {
            this.state.loading = false;
        }, 300);
    }

    async _loadPdf() {
        this._startProgressAnimation();
        
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
            
            // Pre-fetch to check if PDF is ready
            const response = await fetch(this.state.pdfUrl, { 
                method: 'HEAD',
                signal: AbortSignal.timeout(10000) // 10 second timeout
            });
            
            if (!response.ok) throw new Error("Failed to generate PDF");
            
            this._stopProgressAnimation();
        } catch (error) {
            this._stopProgressAnimation();
            this.state.error = error?.message || _t("Unable to generate preview. Please try again.");
            this.state.loading = false;
        }
    }

    downloadPdf() {
        if (!this.state.pdfUrl) return;
        const link = document.createElement("a");
        link.href = `${this.state.pdfUrl}&download=1`;
        link.download = `${this.model}_preview.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    printPdf() {
        const frame = this.el?.querySelector('.o_preview_pdf_viewer iframe');
        if (frame?.contentWindow) {
            frame.contentWindow.focus();
            frame.contentWindow.print();
        }
    }

    goBack() {
        this._cleanup();
        window.history.back();
    }
}

registry.category("actions").add("preview_list_pdf_page", PreviewListPdfPage);