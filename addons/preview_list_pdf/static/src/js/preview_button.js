/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { onWillStart } from "@odoo/owl";

patch(ListController.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.dialogService = useService("dialog");
        this._pdfBtnAdded = false;
        this._lottieLoaded = false;

        onWillStart(async () => {
            try {
                const ok = await this.orm.call("preview.list.license.manager", "is_license_valid", [[]]);
                if (ok) {
                    setTimeout(() => this._addPdfButton(), 200);
                }
            } catch (e) {}
        });
    },

    getStaticActionMenuItems() {
        const items = super.getStaticActionMenuItems(...arguments);
        if (this.model?.root?.resModel) {
            items.previewPdf = {
                isAvailable: () => true,
                sequence: 15,
                icon: "fa fa-file-pdf-o",
                description: _t("Preview as PDF"),
                callback: () => this._openPdf(),
            };
        }
        return items;
    },

    _addPdfButton() {
        if (this._pdfBtnAdded) return;
        const el = this.el || document;
        const main = el.querySelector(".o_control_panel_main");
        const addBtn = main?.querySelector(".o_list_button_add");
        if (!addBtn || el.querySelector(".o_preview_pdf_btn")) {
            this._pdfBtnAdded = true;
            return;
        }
        
        const btn = document.createElement("button");
        btn.className = "btn btn-secondary o_preview_pdf_btn";
        btn.innerHTML = '<i class="fa fa-file-pdf-o me-1"></i>Preview PDF';
        btn.style.marginLeft = "4px";
        btn.onclick = (e) => { e.preventDefault(); this._openPdf(); };
        addBtn.after(btn);
        this._pdfBtnAdded = true;
    },

    _openPdf() {
        if (!this.model?.root) return;
        
        const model = this.model.root.resModel;
        const domain = JSON.stringify(this.model.root.domain || []);
        const columns = this._getColumns();
        
        if (!columns.length) return;
        
        const limit = this.model.root.limit || 80;
        const offset = this.model.root.offset || 0;
        const total = this.model.root.count || 0;
        
        // Show loading overlay with Lottie animation
        this._showLoadingOverlay();
        
        // Generate PDF URL
        const fields = JSON.stringify(columns.map(c => c.name));
        const labels = JSON.stringify(columns.map(c => c.label));
        const params = new URLSearchParams({
            domain, fields, labels,
            limit: String(limit),
            offset: String(offset),
            total: String(total),
        });
        
        const pdfUrl = `/preview/pdf/${encodeURIComponent(model)}?${params.toString()}`;
        
        // Start progress animation
        this._startProgressAnimation();
        
        // Fetch PDF
        fetch(pdfUrl)
            .then(response => {
                if (!response.ok) throw new Error('Failed');
                return response.blob();
            })
            .then(blob => {
                this._hideLoadingOverlay();
                const url = URL.createObjectURL(blob);
                const newWindow = window.open('', '_blank');
                newWindow.document.write(this._getViewerHTML(url, model, limit, offset, total));
                newWindow.document.close();
            })
            .catch(() => {
                this._hideLoadingOverlay();
                window.open(pdfUrl, '_blank');
            });
    },

    _showLoadingOverlay() {
        this._hideLoadingOverlay();
        
        const overlay = document.createElement('div');
        overlay.id = 'pdf_preview_overlay';
        overlay.innerHTML = `
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                        background: rgba(15, 23, 42, 0.55); backdrop-filter: blur(6px); 
                        z-index: 10000; display: flex; align-items: center; justify-content: center;">
                <div style="background: white; border-radius: 12px; padding: 32px 36px 28px 36px; 
                            text-align: center; box-shadow: 0 20px 60px rgba(0,0,0,0.35); 
                            width: 340px;">
                    
                    <!-- Lottie Animation - The hero element -->
                    <div id="pdf_lottie_container" style="width: 120px; height: 120px; margin: 0 auto 4px auto;">
                        <!-- Fallback spinner -->
                        <div id="pdf_fallback_spinner" style="width: 48px; height: 48px; 
                                    border: 4px solid #e0f2fe; 
                                    border-top: 4px solid #00a5cf; 
                                    border-radius: 50%; 
                                    animation: pdf-spin 0.7s linear infinite;
                                    margin: 36px auto;">
                        </div>
                    </div>
                    
                    <h3 style="color: #1e293b; font-size: 15px; font-weight: 600; margin-bottom: 4px; letter-spacing: -0.2px;">
                        Generating PDF Preview
                    </h3>
                    <p id="pdf_progress_text" style="color: #64748b; font-size: 12px; margin-bottom: 16px; min-height: 16px; transition: opacity 0.15s ease;">
                        Preparing your document...
                    </p>
                    
                    <!-- Progress Bar - matches animation color -->
                    <div style="width: 100%; height: 6px; background: #e0f2fe; border-radius: 3px; overflow: hidden;">
                        <div id="pdf_progress_bar" style="width: 0%; height: 100%; 
                                    background: linear-gradient(90deg, #00a5cf 0%, #0891b2 100%); 
                                    border-radius: 3px; transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);">
                        </div>
                    </div>
                    
                    <p id="pdf_percentage" style="color: #0891b2; font-size: 22px; font-weight: 700; margin-top: 10px; letter-spacing: -0.5px;">
                        0%
                    </p>
                </div>
            </div>
            <style>
                @keyframes pdf-spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;
        document.body.appendChild(overlay);
        
        setTimeout(() => this._loadLottieAnimation(), 100);
    },

    _loadLottieAnimation() {
        const container = document.getElementById('pdf_lottie_container');
        if (!container) return;
        
        if (!document.querySelector('script[src*="lottie-player"]')) {
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/@lottiefiles/lottie-player@2.0.8/dist/lottie-player.js';
            script.onload = () => this._renderLottiePlayer(container);
            script.onerror = () => console.warn('Lottie Player failed to load');
            document.head.appendChild(script);
        } else {
            this._renderLottiePlayer(container);
        }
    },

    _renderLottiePlayer(container) {
        const fallback = document.getElementById('pdf_fallback_spinner');
        if (fallback) fallback.style.display = 'none';
        
        const lottieUrl = '/preview_list_pdf/static/src/lottie/document-loading.json';
        
        container.innerHTML = `
            <lottie-player 
                src="${lottieUrl}" 
                background="transparent" 
                speed="1" 
                style="width: 120px; height: 120px; margin: 0 auto;" 
                loop 
                autoplay>
            </lottie-player>
        `;
    },

    _hideLoadingOverlay() {
        const overlay = document.getElementById('pdf_preview_overlay');
        if (overlay) {
            overlay.style.transition = 'opacity 0.25s ease';
            overlay.style.opacity = '0';
            setTimeout(() => {
                if (overlay.parentNode) overlay.remove();
            }, 250);
        }
        if (this._progressInterval) {
            clearInterval(this._progressInterval);
            this._progressInterval = null;
        }
    },

    _startProgressAnimation() {
        let progress = 0;
        const messages = [
            "Preparing your data...",
            "Fetching records from server...",
            "Formatting table layout...",
            "Rendering PDF document...",
            "Almost finished..."
        ];
        let msgIndex = 0;
        
        this._progressInterval = setInterval(() => {
            if (progress < 90) {
                const increment = Math.max(0.5, (90 - progress) * 0.08);
                progress += increment;
                if (progress > 90) progress = 90;
                
                const roundedProgress = Math.round(progress);
                
                const progressBar = document.getElementById('pdf_progress_bar');
                const percentage = document.getElementById('pdf_percentage');
                const progressText = document.getElementById('pdf_progress_text');
                
                if (progressBar) progressBar.style.width = roundedProgress + '%';
                if (percentage) percentage.textContent = roundedProgress + '%';
                if (progressText && progress > 30) {
                    const newMsgIndex = Math.min(Math.floor((progress - 30) / 15), messages.length - 1);
                    if (newMsgIndex !== msgIndex) {
                        msgIndex = newMsgIndex;
                        progressText.style.opacity = '0';
                        setTimeout(() => {
                            progressText.textContent = messages[msgIndex];
                            progressText.style.opacity = '1';
                        }, 150);
                    }
                }
            }
        }, 250);
    },

    _getViewerHTML(pdfUrl, model, limit, offset, total) {
        const showingFrom = offset + 1;
        const showingTo = Math.min(offset + limit, total);
        
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>PDF Preview - ${model}</title>
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f3f4f6; }
                    .toolbar {
                        background: white;
                        padding: 12px 24px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        border-bottom: 1px solid #e5e7eb;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    }
                    .toolbar-left { display: flex; align-items: center; gap: 16px; }
                    .toolbar-title { font-weight: 600; font-size: 16px; color: #1f2937; }
                    .toolbar-info { font-size: 13px; color: #6b7280; }
                    .toolbar-buttons { display: flex; gap: 8px; }
                    .btn {
                        padding: 8px 16px; border-radius: 8px; border: none; cursor: pointer;
                        font-size: 14px; font-weight: 500; display: flex; align-items: center;
                        gap: 6px; transition: all 0.2s;
                    }
                    .btn-primary { background: #4f46e5; color: white; }
                    .btn-primary:hover { background: #4338ca; }
                    .btn-secondary { background: white; color: #374151; border: 1px solid #d1d5db; }
                    .btn-secondary:hover { background: #f9fafb; }
                    .btn-icon { width: 16px; height: 16px; }
                    .pdf-container { height: calc(100vh - 57px); background: #525659; }
                    iframe { width: 100%; height: 100%; border: none; }
                </style>
            </head>
            <body>
                <div class="toolbar">
                    <div class="toolbar-left">
                        <span class="toolbar-title">${model}</span>
                        <span class="toolbar-info">Records: ${showingFrom}-${showingTo} of ${total || 0}</span>
                    </div>
                    <div class="toolbar-buttons">
                        <button class="btn btn-secondary" onclick="window.print()">
                            <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/>
                            </svg>
                            Print
                        </button>
                        <button class="btn btn-primary" onclick="downloadPDF()">
                            <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                            </svg>
                            Download
                        </button>
                    </div>
                </div>
                <div class="pdf-container">
                    <iframe src="${pdfUrl}" type="application/pdf"></iframe>
                </div>
                <script>
                    function downloadPDF() {
                        const a = document.createElement('a');
                        a.href = '${pdfUrl}';
                        a.download = '${model}_preview.pdf';
                        a.click();
                    }
                </script>
            </body>
            </html>
        `;
    },

    _getColumns() {
        const skipPatterns = [
            'avatar', 'image', 'icon', 'logo', 'picture', 'photo',
            'thumb', 'signature', 'barcode', 'qr_code',
        ];
        
        const isImageOrBinaryField = (name) => {
            if (!name) return false;
            const lower = name.toLowerCase();
            return skipPatterns.some(pattern => lower.includes(pattern));
        };
        
        if (this.renderer?.columns) {
            const columns = this.renderer.columns
                .filter(c => c.type === 'field' && c.name && !c.invisible && !isImageOrBinaryField(c.name) && c.name !== 'selector' && c.name !== 'checkbox')
                .map(c => ({ name: c.name, label: c.string || c.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) }));
            if (columns.length > 0) return columns;
        }
        
        if (this.model?.root?.columns) {
            const columns = this.model.root.columns
                .filter(c => c.type === 'field' && c.name && !c.invisible && !isImageOrBinaryField(c.name) && c.name !== 'selector' && c.name !== 'checkbox')
                .map(c => ({ name: c.name, label: c.string || c.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) }));
            if (columns.length > 0) return columns;
        }
        
        const table = document.querySelector('.o_list_table');
        if (table) {
            const columns = [];
            table.querySelectorAll('thead th').forEach(th => {
                if (th.classList.contains('o_list_record_selector')) return;
                const fieldName = th.getAttribute('data-name') || th.dataset?.name;
                if (!fieldName || isImageOrBinaryField(fieldName) || fieldName === 'selector' || fieldName === 'checkbox') return;
                const label = th.textContent.replace(/[\n\r\t]/g, ' ').replace(/\s+/g, ' ').trim();
                if (label) columns.push({ name: fieldName, label });
            });
            if (columns.length > 0) return columns;
        }
        
        console.warn('Preview PDF: No visible columns found');
        return [];
    },
});