import { CorePlugin, CoreViewPlugin, UIPlugin } from "@odoo/o-spreadsheet";

/**
 * An o-spreadsheet core plugin with access to all custom Erp plugins
 * @type {import("@spreadsheet").ErpCorePluginConstructor}
 **/
export const ErpCorePlugin = CorePlugin;

/**
 * An o-spreadsheet CoreView plugin with access to all custom Erp plugins
 * @type {import("@spreadsheet").ErpUIPluginConstructor}
 **/
export const ErpCoreViewPlugin = CoreViewPlugin;

/**
 * An o-spreadsheet UI plugin with access to all custom Erp plugins
 * @type {import("@spreadsheet").ErpUIPluginConstructor}
 **/
export const ErpUIPlugin = UIPlugin;
