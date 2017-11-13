// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt

frappe.ui.form.on('EPI Order Management Tool', {
	refresh: function(frm) {

	},
	btn_download_amazon_orders: function(frm) {
		frappe.call({
			method: "download_orders_amazon",
			doc: frm.doc,
			args: { created_after_date: frm.doc.last_downloaded_order_date_amazon, end_date: frm.doc.download_amazon_orders_upto },
			freeze: true,
			freeze_message: __("Pulling orders."),
			callback: function(r){
				if(!r.exc) {
					frappe.msgprint(__(r.message));
					cur_frm.refresh_fields();
				} else {
					frappe.msgprint(__("Could not pull orders at this time. Please try again in 5 minutes. <br /> " + r.exc));
				}
			}
		});
	},
	btn_download_amazon_settlement_statement: function(frm) {
		// if (frm.doc.amazon_payment_settlement_report_id != "") {
		// 	freeze_msg = "Retrieving settlements from Report ID '" + frm.doc.amazon_payment_settlement_report_id + "'";
		// } else {
		// 	freeze_msg = "Retrieving settlements from latest settlement report."
		// }

		frappe.call({
			method: "download_settlements_amazon",
			doc: frm.doc,
			args: { from_date: frm.doc.amazon_payment_settlement_fromdate, 
					to_date: frm.doc.amazon_payment_settlement_todate 
			},
			freeze: true,
			freeze_message: __("Retrieving payment settlement data..."),
			callback: function(r){
				if(!r.exc) {
					frappe.msgprint(__(r.message));
					cur_frm.refresh_fields();
				} else {
					frappe.msgprint(__("Could not pull settlement statement at this time. Please try again in 5 minutes. <br /> " + r.exc));
				}
			}
		});
	},
	btn_import_flipkart_settlement_data: function(frm) {
		frappe.call({
			method: "import_and_create_settlements_flipkart",
			doc: frm.doc,
			args: { 
				settlement_csv: frm.doc.settlement_sheet_flipkart
			},
			freeze: true,
			freeze_message: __("Creating payment settlement entries for Flipkart..."),
			callback: function(r){
				if(!r.exc) {
					frappe.msgprint(__(r.message));
					cur_frm.refresh_fields();
				} else {
					frappe.msgprint(__("Could not process settlement statement at this time.<br /> " + r.exc));
				}
			}
		});
	},
});
