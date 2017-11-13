# Copyright (c) 2013, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []

	columns = get_columns()
	data = get_data()

	return columns, data




# def get_columns():
# 	return [
# 		_("Amazon Order ID") + "::150",
# 		_("Date") + ":Date:80",
# 		_("Customer Name") + "::150",
# 		_("SKU") + "::75",
# 		_("Title") + "::200",
# 		_("Qty") + "::30",
# 		_("MRP") + ":Currency:75",
# 		_("BizOne Principal") + ":Currency:75",
# 		_("Amazon Principal") + ":Currency:75",
# 		_("Shipping") + ":Currency:75",
# 		_("Commission") + ":Currency:75",
# 		_("Commission Tax") + ":Currency:75",
# 		_("Fixed Closing Fee") + ":Currency:75",
# 		_("Fixed Closing Fee Tax") + ":Currency:75",
# 		_("Shipping Commission") + ":Currency:75",
# 		_("Shipping Commission Tax") + ":Currency:75",
# 		_("Received") + ":Currency:75",
# 		_("% Realization") + ":Float:75",
# 		_("Easy Shipping Charges") + ":Currency:85",
# 		_("Easy Shipping Charges Tax") + ":Currency:85",
# 		_("Easy Shipping Charges Total") + ":Currency:85",
# 		_("Remark") + ":HTML:200"
# 	]

# def get_data():
# 	data = []
	
# 	payments = frappe.get_all("EPI Amazon Order Payment", fields=['*'], order_by="posting_date DESC")

# 	print payments

# 	for payment in payments:
#     	#print payment.amazon_order_id
		
# 		#For fetching title.
# 	 	sales_order_id = frappe.db.get_value("Sales Order", {"epi_amazon_order_id": payment.amazon_order_id}, "name")
# 	 	customer = frappe.db.get_value("Sales Order", {"epi_amazon_order_id": payment.amazon_order_id}, "customer")

#  		easy_ship_charges = frappe.db.get_value("Sales Taxes and Charges", {"parent": payment.name, "description": "Amazon Easy Ship Charges"}, "tax_amount")
#  		easy_ship_charges_tax = frappe.db.get_value("Sales Taxes and Charges", {"parent": payment.name, "description": "Amazon Easy Ship Charges Tax"}, "tax_amount")

#  		#Calculate Total Easy Ship
#  		easy_ship_charges_total = easy_ship_charges + easy_ship_charges_tax

# 		row = []
# 		row.append(payment.amazon_order_id)
# 		row.append(payment.posting_date)
# 		row.append(customer)
# 		row.append("")
# 		row.append("")
# 		row.append("")
# 		row.append("")
# 		row.append("")
# 		row.append("")
# 		row.append("")
# 		row.append("")
# 		row.append("")
# 		row.append("")
# 		row.append("")
# 		row.append("")
# 		row.append("")
# 		row.append("")
# 		row.append("")
# 		row.append(easy_ship_charges)
# 		row.append(easy_ship_charges_tax)
# 		row.append(easy_ship_charges_total)
# 		row.append("")
# 		data.append(row)
		
# 		payment_details = frappe.get_all("EPI Amazon Order Payment Item", filters={'parent': payment.name}, fields=['*'])
# 		unique_sku_ids = get_distinct_sku_ids(payment_details)
	
# 		for unique_sku_id in unique_sku_ids:
# 			row = []

# 			title = frappe.db.get_value("Sales Order Item", {"parent": sales_order_id, "epi_ecom_sku_id": unique_sku_id}, "Description")
			
# 			principal = sum([float(x.amount) for x in payment_details if x.sku_id == unique_sku_id and x.description.lower() == "principal"])
# 			qty = sum([float(x.qty) for x in payment_details if x.sku_id == unique_sku_id and x.description.lower() == "principal"])
# 			selling_price = principal / qty
			
# 			mrp_bizone = frappe.db.get_value("Sales Order Item", {"parent": sales_order_id, "epi_ecom_sku_id": unique_sku_id}, "rate")
# 			principal_bizone = (mrp_bizone * qty)


# 			shipping = sum([float(x.amount) for x in payment_details if x.sku_id == unique_sku_id and x.description.lower() == "shipping"])
# 			commission = sum([float(x.amount) for x in payment_details if x.sku_id == unique_sku_id and x.description.lower() == "commission"])
# 			commission_tax = sum([float(x.amount) for x in payment_details if x.sku_id == unique_sku_id and x.description.lower() == "commission tax"])
# 			fixed_closing_fee = sum([float(x.amount) for x in payment_details if x.sku_id == unique_sku_id and x.description.lower() == "fixed closing fee"])
# 			fixed_closing_fee_tax = sum([float(x.amount) for x in payment_details if x.sku_id == unique_sku_id and x.description.lower() == "fixed closing fee tax"])
# 			shipping_commission = sum([float(x.amount) for x in payment_details if x.sku_id == unique_sku_id and x.description.lower() == "shipping commission"])
# 			shipping_commission_tax = sum([float(x.amount) for x in payment_details if x.sku_id == unique_sku_id and x.description.lower() == "shipping commission tax"])

# 			received = principal + shipping + commission + commission_tax + fixed_closing_fee + fixed_closing_fee_tax + shipping_commission + shipping_commission_tax

# 			if received > 0:
# 				#realization = (((received - shipping) / qty) / selling_price) * 100
# 				realization = (((received - shipping) / qty) / mrp_bizone) * 100
# 			else:
# 				realization = 0.0

# 			row.append("")
# 			row.append("")
# 			row.append("")
# 			row.append(unique_sku_id)
# 			row.append(title)
# 			row.append(qty)
# 			row.append(mrp_bizone)
# 			row.append(principal_bizone)
# 			row.append(principal)
# 			row.append(shipping)
# 			row.append(commission)
# 			row.append(commission_tax)
# 			row.append(fixed_closing_fee)
# 			row.append(fixed_closing_fee_tax)
# 			row.append(shipping_commission)
# 			row.append(shipping_commission_tax)
# 			row.append(received)
# 			row.append(realization)
# 			row.append("")
# 			row.append("")
# 			row.append("")
# 			row.append("")
# 			data.append(row)
	
# 	return data
		

def get_distinct_sku_ids(payment_items):
	distinct_sku_ids = []
	sku_ids = []
	for item in payment_items:
		sku_ids.append(item.sku_id)	
	distinct_sku_ids = set(sku_ids)
	return distinct_sku_ids	


def get_columns():
	return [
		_("Amazon Order ID") + "::150",
		_("Date") + ":Date:80",
		_("Customer Name") + "::150",
		_("SKU") + "::75",
		_("Title") + "::200",
		_("Qty") + "::30",
		_("MRP") + ":Currency:75",
		_("BizOne Principal") + ":Currency:75",
		_("Amazon Principal") + ":Currency:75",
		_("Shipping") + ":Currency:75",
		_("Commission") + ":Currency:75",
		_("Commission Tax") + ":Currency:75",
		_("Fixed Closing Fee") + ":Currency:75",
		_("Fixed Closing Fee Tax") + ":Currency:75",
		_("Shipping Commission") + ":Currency:75",
		_("Shipping Commission Tax") + ":Currency:75",
		_("Easy Shipping Per Title") + ":Currency:85",
		_("Received") + ":Currency:75",
		_("% Realization") + ":Float:75",
		_("BizOne MRP Total") + ":Currency:85",
		_("Easy Shipping Total") + ":Currency:85",
		_("Ratio") + ":Float:85",
		_("Remark") + ":HTML:200"
	]


def get_data():

	data = []

	payments = frappe.get_all("EPI Amazon Order Payment",filters={"order_fulfillment_type": "MFN"}, fields=['*'], order_by="posting_date DESC")


	#For each payment, get OrderID, Total of BizOneMRP by title, 
	for payment in payments:
		sales_order_id = frappe.db.get_value("Sales Order", {"epi_amazon_order_id": payment.amazon_order_id}, "name")
	 	customer = frappe.db.get_value("Sales Order", {"epi_amazon_order_id": payment.amazon_order_id}, "customer")

	 	#Get Easy SHip Total
 		easy_ship_charges = frappe.db.get_value("Sales Taxes and Charges", {"parent": payment.name, "description": "Amazon Easy Ship Charges"}, "tax_amount")
 		easy_ship_charges_tax = frappe.db.get_value("Sales Taxes and Charges", {"parent": payment.name, "description": "Amazon Easy Ship Charges Tax"}, "tax_amount")
		

		easy_ship_charges_total = easy_ship_charges + easy_ship_charges_tax

		print sales_order_id
		print "------"
 		print easy_ship_charges_total
 		print "------"
		#Get MRP total for all titles.
		payment_items = frappe.get_all("EPI Amazon Order Payment Item", filters={"parent": payment.name}, fields=['*'])
		unique_sku_ids = get_distinct_sku_ids(payment_items)


		mrp_bizone_order_total = frappe.db.get_value("Sales Order", {"epi_amazon_order_id": payment.amazon_order_id}, "total")
		# total_mrp_bizone_for_order_titles = 0.0
		# for unique_sku_id in unique_sku_ids:
		# 	qty = [x.qty for x in payment_items if x.sku_id == unique_sku_id][0]
		# 	mrp_bizone = frappe.db.get_value("Sales Order Item", {"parent": sales_order_id, "epi_ecom_sku_id": unique_sku_id}, "rate")
		# 	total_mrp_bizone_for_order_titles += (qty * mrp_bizone)

		#Get ratio of mrp_bizone to easy_ship_charges_total for that payment
		ratio_mrp_bizone_to_easy_ship = (abs(easy_ship_charges_total) / mrp_bizone_order_total)

		row = []
		row.append(payment.amazon_order_id)
		row.append(customer)
		row.append("")
		row.append("")
		row.append("")
		row.append("")
		row.append("")
		row.append("")
		row.append("")
		row.append("")
		row.append("")
		row.append("")
		row.append("")
		row.append("")
		row.append("")
		row.append("")
		row.append("")
		row.append("")
		row.append("")
		row.append(mrp_bizone_order_total)
		row.append(easy_ship_charges_total)
		row.append(ratio_mrp_bizone_to_easy_ship)
		row.append("")

		data.append(row)

		for unique_sku_id in unique_sku_ids:
			row = []

			title = frappe.db.get_value("Sales Order Item", {"parent": sales_order_id, "epi_ecom_sku_id": unique_sku_id}, "Description")
			
			principal = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "principal"])
			qty = sum([float(x.qty) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "principal"])
			selling_price = principal / qty
			
			mrp_bizone = frappe.db.get_value("Sales Order Item", {"parent": sales_order_id, "epi_ecom_sku_id": unique_sku_id}, "rate")
			principal_bizone = (mrp_bizone * qty)


			shipping = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "shipping"])
			commission = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "commission"])
			commission_tax = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "commission tax"])
			fixed_closing_fee = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "fixed closing fee"])
			fixed_closing_fee_tax = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "fixed closing fee tax"])
			shipping_commission = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "shipping commission"])
			shipping_commission_tax = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "shipping commission tax"])

			easy_ship_charges_sku = principal_bizone * ratio_mrp_bizone_to_easy_ship

			received = principal + shipping + commission + commission_tax + fixed_closing_fee + fixed_closing_fee_tax + shipping_commission + shipping_commission_tax - easy_ship_charges_sku


			if received > 0:
				realization = ((received / qty) / mrp_bizone) * 100
				#realization = principal_bizone * ratio_mrp_bizone_to_easy_ship
				#realization = (((received - shipping) / qty) / mrp_bizone) * 100
			else:
				realization = 0.0

			row.append("")
			row.append("")
			row.append("")
			row.append(unique_sku_id)
			row.append(title)
			row.append(qty)
			row.append(mrp_bizone)
			row.append(principal_bizone)
			row.append(principal)
			row.append(shipping)
			row.append(commission)
			row.append(commission_tax)
			row.append(fixed_closing_fee)
			row.append(fixed_closing_fee_tax)
			row.append(shipping_commission)
			row.append(shipping_commission_tax)
			row.append(easy_ship_charges_sku)
			row.append(received)
			row.append(realization)
			row.append("")
			row.append("")
			row.append("")
			row.append("")


			data.append(row)

	return data

