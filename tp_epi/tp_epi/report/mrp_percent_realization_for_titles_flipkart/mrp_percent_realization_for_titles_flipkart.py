# Copyright (c) 2013, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import csv
from frappe import _


def execute(filters=None):
	columns, data = [], []

	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns():
	return [
		_("Settlement No") + "::150",
		_("Settlement Date") + ":Date:80",
		_("Order No") + "::100",
		_("Order Item No") + "::100",
		_("Order Date") + ":Date:80",
		_("Status") + "::50",
		_("SKU") + "::75",
		_("Title") + "::200",
		_("MRP") + ":Currency:75",
		_("Qty") + "::30",
		_("BizOne Principal") + ":Currency:75",
		_("Order Total") + ":Currency:75",
		_("Total Marketplace Fee") + ":Currency:75",
		_("Service Tax") + ":Currency:75",
		_("Swachh Bharat Cess Tax") + ":Currency:75",
		_("Krishi Kalyan Cess Tax") + ":Currency:75",
		_("Settlement Value") + ":Currency:75",
		_("Realization") + ":Percent:75"
	]

def get_data(filters=None):
	if not filters:
		filters = {}

	#Place flipkart order id as header filter.
	header_filters = []
	# if filters.get("flipkart_order_id"):
	# 	header_filters = {"flipkart_order_id" : filters.pop("flipkart_order_id")}
	if filters.get("from_date") and filters.get("to_date"):
		fromdate = frappe.utils.get_datetime(filters.get("from_date"));
		todate = frappe.utils.get_datetime(filters.get("to_date"));

		if fromdate > todate:
			frappe.msgprint("From Date exceeds To Date")
			return []

		header_filters.append(["settlement_date", ">=", fromdate])
		header_filters.append(["settlement_date", "<=", todate])


	out = []

	payments = frappe.get_all("EPI Flipkart Order Payment", filters=header_filters, fields=["*"], order_by="settlement_date")


	order_item_value_total = 0.0
	settlement_total = 0.0

	for payment in payments:

		data_filters = [["parent", "=", payment["name"]]]
		
		if filters.get("settlement_ref_no"):
			data_filters.append(["settlement_ref_no", "=", filters.get("settlement_ref_no")])

		if filters.get("order_status"):
			data_filters.append(["order_status", "=", filters.get("order_status")])

	
		payment_items = frappe.get_all("EPI Flipkart Order Payment Item", filters=data_filters, fields=["*"], order_by="sku_id")
	
		for pi in payment_items:
			row = []

			row.append(pi.settlement_ref_no)
			row.append(payment.settlement_date)
			
			row.append(payment.flipkart_order_id)
			row.append(pi.order_item_id)

			row.append(payment.order_date)
			row.append(pi.order_status)
			row.append(pi.sku_id)

			bizone_mrp = 0.0
			title_id = frappe.db.get_value("EPI Catalog Listing", filters={"sku_id_flipkart": pi.sku_id}, fieldname="name")
			if title_id:
				title = frappe.get_doc("EPI Catalog Listing", title_id)

				row.append(title.item_name_flipkart or title.item_name)
				row.append(title.mrp)
				bizone_mrp = title.mrp
			else:
				row.append("-")
				row.append(0.0)

			row.append(pi.qty)

			bizone_principal = pi.qty * bizone_mrp

			row.append(bizone_principal)

			row.append(pi.order_item_value)
			order_item_value_total += pi.order_item_value

			row.append(pi.total_marketplace_fee)
			row.append(pi.service_tax)
			row.append(pi.swachh_bharat_cess_tax)
			row.append(pi.krishi_kalyan_cess_tax)

			row.append(pi.settlement_value)
			settlement_total += pi.settlement_value

			realization = 0.0
			if bizone_principal > 0.0:
				realization = (pi.settlement_value * 100) / bizone_principal

			row.append(realization)

			out.append(row)

	#out.append(["", "", "", "", "", "","", "", order_item_value_total, "", "", "", "", settlement_total, ""])

	return out
