// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt


frappe.query_reports["MRP Percent Realization for Titles Flipkart"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": moment(1, "D").locale("en")
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.str_to_obj(frappe.datetime.get_today())
		},
		{
			"fieldname":"settlement_ref_no",
			"label": __("Settlement"),
			"fieldtype": "Select",
		},
		{
			"fieldname":"order_status",
			"label": __("Order Status"),
			"fieldtype": "Select",
		},
		
	],
	"onload": function get_settlement_ids() {
		return frappe.call({
			method: "tp_epi.api_flipkart.get_filter_values",
			callback: function(r) {
				//cur_page.page.query_report.filters[0].df.options = r.message
				//console.log(r.message);

				var settlement_no_filter = frappe.query_report_filters_by_name.settlement_ref_no;
				settlement_no_filter.df.options = " \n" + r.message.settlements;
				settlement_no_filter.df.default = r.message.settlements.split("\n")[0];
				settlement_no_filter.refresh();
				//settlement_no_filter.set_input(settlement_no_filter.df.default);

				var order_status_filter = frappe.query_report_filters_by_name.order_status;
				order_status_filter.df.options = " \n" + r.message.order_statuses;
				order_status_filter.df.default = r.message.order_statuses.split("\n")[0];
				order_status_filter.refresh();
				//order_status_filter.set_input(order_status_filter.df.default);
			}
		});
	},
}

