/** @odoo-module **/

import { Component, useState, xml } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class ExportDialog extends Component {
    static template = "zimbabwe_payroll.ExportDialog";
    
    setup() {
        this.action = useService("action");
        
        this.state = useState({
            isGenerating: false,
            selectedFormat: null,
        });
        
        this.reportType = this.props.report_type;
        this.payRunId = this.props.pay_run_id;
    }

    get title() {
        if (this.reportType === 'nssa') return "Export NSSA Report";
        if (this.reportType === 'zimra_itf') return "Export ZIMRA ITF Report";
        return "Export Report";
    }

    closeDialog() {
        this.props.close();
    }

    async download(format) {
        this.state.isGenerating = true;
        this.state.selectedFormat = format;
        
        const url = `/zimbabwe_payroll/export/${this.reportType}/${this.payRunId}?format=${format}`;
        
        try {
            // Initiate the download directly via browser
            // We use standard action service to handle file downloads beautifully
            await this.action.doAction({
                type: 'ir.actions.act_url',
                url: url,
                target: 'new',
            });
            
            // Wait a brief moment for visual feedback
            setTimeout(() => {
                this.closeDialog();
            }, 1500);
            
        } catch (error) {
            console.error("Export failed:", error);
            this.state.isGenerating = false;
        }
    }
}

// Client action handler
function exportModalAction(env, action) {
    env.services.dialog.add(ExportDialog, {
        report_type: action.params.report_type,
        pay_run_id: action.params.pay_run_id,
    });
    return { type: 'ir.actions.act_window_close' };
}

registry.category("actions").add("zimbabwe_payroll.export_modal", exportModalAction);
