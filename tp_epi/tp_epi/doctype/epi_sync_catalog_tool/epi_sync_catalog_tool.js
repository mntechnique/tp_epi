// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt

frappe.ui.form.on('EPI Sync Catalog Tool', {
	refresh: function(frm) {
		frm.add_custom_button(__('Test MySQL Connection'), function(){
			frappe.call({
				method: "connect_mysql",
				doc: frm.doc,
				freeze: true,
				freeze_message: __("Testing connection"),
				callback: function(r){
					if(!r.exc) {
						frappe.msgprint(__(r.message));
					} else {
						frappe.msgprint(__("Connection failed. <br /> " + r.exc));
					}
				}
			});
		});
	},

	btn_import_titles: function(frm) {
		frappe.call({
			method: "import_data_from_bizone",
			doc: frm.doc,
			freeze: true,
			freeze_message: __("Updating EPI Catalog Listings from BizOne titles."),
			callback: function(r){
				if(!r.exc) {
					frappe.msgprint(__(r.message));
				} else {
					frappe.msgprint(__("Updating process could not be completed. <br /> " + r.exc));
				}
			}
		});
	}, 

	btn_write_to_sheet: function(frm) {
		frappe.call({
			method: "write_to_excel",
			doc: frm.doc,
			freeze: true,
			freeze_message: __("Writing to Excel sheet"),
			callback: function(r){
				if(!r.exc) {
					frappe.msgprint(__(r));
				} else {
					frappe.msgprint(__("Could not write to sheet. <br /> " + r.exc));
				}
			}
		});
	},


	btn_upload_to_portal: function(frm) {
		frappe.msgprint('Upload to Portal');		
	},

	ecom_portal: function(frm) {
		//Find file and attach appropriately
		frm.set_value("select_excel_sheet", "");
	}
});