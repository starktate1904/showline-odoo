import { AddDocumentsAttachmentPlugin } from "@documents/editor/plugins/add_documents_attachment_plugin";
import { createXlsxAttachment } from "@documents_spreadsheet/helpers";
import { patch } from "@web/core/utils/patch";

patch(AddDocumentsAttachmentPlugin.prototype, {

    /**
     * Convert Erp Spreadsheet to .xlsx format
     */
    async _processAttachments(attachmentRecords) {
        return createXlsxAttachment(this.config.embeddedComponentInfo?.env, this.services.orm, attachmentRecords);
    }
});
