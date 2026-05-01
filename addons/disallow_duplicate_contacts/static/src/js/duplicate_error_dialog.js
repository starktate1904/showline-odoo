/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, useState, onWillUnmount } from "@odoo/owl";

export class DuplicateErrorDialog extends Component {
    static template = "disallow_duplicate_contacts.DuplicateErrorDialog";
    static props = {
        close: Function,
        title: { type: String, optional: true },
        message: { type: String, optional: true },
        duplicateName: { type: String, optional: true },
        duplicateId: { type: Number, optional: true },
        reason: { type: String, optional: true },
    };

    setup() {
        this.state = useState({
            animationLoaded: false,
            lottieError: false,
        });
        this._lottieScriptLoaded = false;
        
        onMounted(() => {
            this._loadLottieAnimation();
        });
    }

    _loadLottieAnimation() {
        // Check if Lottie Player script is already in the DOM
        if (document.querySelector('script[src*="lottie-player"]')) {
            this._lottieScriptLoaded = true;
            this.state.animationLoaded = true;
            this._renderAnimation();
            return;
        }

        // Load Lottie Player from CDN
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/@lottiefiles/lottie-player@2.0.8/dist/lottie-player.js';
        script.onload = () => {
            this._lottieScriptLoaded = true;
            this.state.animationLoaded = true;
            this._renderAnimation();
        };
        script.onerror = () => {
            // Fallback: show static icon if Lottie fails
            this.state.lottieError = true;
            this.state.animationLoaded = true;
        };
        document.head.appendChild(script);
    }

    _renderAnimation() {
        // Small delay to ensure DOM is ready
        setTimeout(() => {
            const container = this.el?.querySelector('#ddc_error_lottie');
            if (!container) return;

            const lottieUrl = '/disallow_duplicate_contacts/static/src/lottie/error-animation.json';
            
            container.innerHTML = `
                <lottie-player 
                    src="${lottieUrl}" 
                    background="transparent" 
                    speed="1" 
                    style="width: 90px; height: 90px; margin: 0 auto;" 
                    loop 
                    autoplay>
                </lottie-player>
            `;
        }, 150);
    }

    onClose() {
        if (this.props.close) {
            this.props.close();
        }
    }

    onViewDuplicate() {
        if (this.props.duplicateId) {
            // Close the dialog first
            if (this.props.close) {
                this.props.close();
            }
            // Open the duplicate contact in a new tab
            const baseUrl = window.location.origin;
            window.open(
                `${baseUrl}/web#id=${this.props.duplicateId}&model=res.partner&view_type=form`,
                '_blank'
            );
        }
    }
}

// Register the component (if needed as a standalone action)
// registry.category("actions").add("ddc_duplicate_error_dialog", DuplicateErrorDialog);