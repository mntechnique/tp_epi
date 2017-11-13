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


def get_columns():
	return [
		_("Amazon Order ID") + "::150",
		_("Date") + ":Date:80",
		_("SKU") + "::75",
		_("Title") + "::200",
		_("Qty") + "::30",
		_("MRP") + ":Currency:75",
		_("BizOne Principal") + ":Currency:75",
		_("Amazon Principal") + ":Currency:75",
		_("Shipping") + ":Currency:75",
		_("Gift Wrap") + ":Currency:75",
		_("FBA Delivery Services Fee") + ":Currency:75",
		_("Delivery Service Fee Tax") + ":Currency:75",
		_("FBA Pick and Pack Fee") + ":Currency:75",
		_("FBA per unit fulfillment fee Tax") + ":Currency:75",
		_("FBA Weight Handling fee") + ":Currency:75",
		_("FBA Weight based Tax") + ":Currency:75",
		_("Commission") + ":Currency:75",
		_("Commission Tax") + ":Currency:75",
		_("Fixed Closing Fee") + ":Currency:75",
		_("Fixed Closing Fee Tax") + ":Currency:75",
		_("Shipping Chargeback") + ":Currency:75",
		_("Shipping Chargeback Tax") + ":Currency:75",
		_("Gift Wrap Chargeback") + ":Currency:75",
		_("Gift Wrap Chargeback Tax") + ":Currency:75",
		_("Shipping Discount") + ":Currency:75",
		_("Received") + ":Currency:75",
		_("% Realization") + ":Float:75",
		_("Reversal Reimbursement") + ":Float:75",
		_("Free Replacement Refund Item") + ":Float:75",
		_("Remark") + ":HTML:200"
	]

def get_data():
	data = []

	payments = frappe.get_all("EPI Amazon Order Payment", filters={"order_fulfillment_type": "AFN"}, fields=['*'], order_by="posting_date DESC")

	#For each payment, get OrderID, Total of BizOneMRP by title, 
	for payment in payments:
		#Get MRP total for all titles.
		payment_items = frappe.get_all("EPI Amazon Order Payment Item", filters={"parent": payment.name}, fields=['*'])
		unique_sku_ids = get_distinct_sku_ids(payment_items)

		mrp_bizone_order_total = 1.0
		for unique_sku_id in unique_sku_ids:
			bizone_mrp = frappe.db.get_value("EPI Catalog Listing", {"sku_id_amazon": unique_sku_id}, "mrp")
			if not bizone_mrp:
				bizone_mrp = frappe.db.get_value("EPI Catalog Listing", {"sku_id_amazon": unique_sku_id}, "selling_price_amazon")
				bizone_mrp = float(bizone_mrp or 0.0)
			if not bizone_mrp:
				bizone_mrp = [float(x.amount) for x in payment_items if (x.sku_id == unique_sku_id) and (x.description.lower() == "principal") and (x.parent == payment.amazon_order_id)]
				bizone_mrp = bizone_mrp[0] if len(bizone_mrp) else 0.0
			
			mrp_bizone_order_total = mrp_bizone_order_total + bizone_mrp

		#Get Other charges for factoring back
 		free_replacement_refund_items = frappe.db.get_value("Sales Taxes and Charges", {"parent": payment.name, "description": "FREE_REPLACEMENT_REFUND_ITEMS"}, "tax_amount") or 0.0
 		reversal_reimbursement = frappe.db.get_value("Sales Taxes and Charges", {"parent": payment.name, "description": "REVERSAL_REIMBURSEMENT"}, "tax_amount") or 0.0

 		
 		ratio_free_replacement_refund_items = (free_replacement_refund_items / mrp_bizone_order_total) if mrp_bizone_order_total > 0.0 else 0.0
 		ratio_reversal_reimbursement = (reversal_reimbursement / mrp_bizone_order_total) if mrp_bizone_order_total > 0.0 else 0.0

		for unique_sku_id in unique_sku_ids:
			row = []
			row.append(payment.amazon_order_id)
			row.append(payment.posting_date)

			listing = frappe.get_doc("EPI Catalog Listing", {"sku_id_amazon": unique_sku_id})
			
			title = listing.item_name_amazon or listing.item_name
			
			principal = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "principal"])
			qty = sum([float(x.qty) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "principal"])
			selling_price = principal / qty
			
			remark = ""
					
			mrp_bizone = listing.mrp or 0.0 #frappe.db.get_value("EPI Catalog Listing", filters=[["sku_id_amazon", "=", unique_sku_id],["selling_price_amazon", "!=", "0.0"] ],fieldname= "mrp")
			if mrp_bizone == 0.0:
				remark = "BizOne MRP is zero. Amazon Selling Price considered as MRP."
				mrp_bizone = selling_price


			principal_bizone = (mrp_bizone * qty)

			shipping = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "shipping"])
			gift_wrap = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "gift wrap"])

			fba_delivery_services_fee = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "fba delivery services fee"])	
			delivery_service_fee_tax = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "delivery service fee tax"])	
			fba_pick_and_pack_fee = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "fba pick & pack fee"])	
			fba_per_unit_fulfillment_fee_tax = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "fba per unit fulfillment fee tax"])
			fba_weight_handling_fee = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "fba weight handling fee"])
			fba_weight_based_fee_tax = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "fba weight based fee tax"])

			commission = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "commission"])
			commission_tax = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "commission tax"])
			fixed_closing_fee = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "fixed closing fee"])
			fixed_closing_fee_tax = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "fixed closing fee tax"])
			shipping_chargeback = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "shipping chargeback"])
			shipping_chargeback_tax = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "shipping chargeback tax"])
			gift_wrap_chargeback = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "gift wrap chargeback"])
 			gift_wrap_chargeback_tax = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "gift wrap chargeback tax"])

 			shipping_discount = sum([float(x.amount) for x in payment_items if x.sku_id == unique_sku_id and x.description.lower() == "shipping discount"])

 			free_replacement_refund_items_per_sku = ratio_free_replacement_refund_items * mrp_bizone
 			reversal_reimbursement_per_sku = ratio_reversal_reimbursement * mrp_bizone

			received = principal + shipping + gift_wrap
			received = received + fba_delivery_services_fee + delivery_service_fee_tax + fba_pick_and_pack_fee + fba_per_unit_fulfillment_fee_tax + fba_weight_handling_fee + fba_weight_based_fee_tax
			received = received + commission + commission_tax + fixed_closing_fee + fixed_closing_fee_tax + shipping_chargeback + shipping_chargeback_tax + gift_wrap_chargeback + gift_wrap_chargeback_tax + shipping_discount
			received = received + reversal_reimbursement_per_sku + free_replacement_refund_items_per_sku

			if received > 0:
				realization = ((received / qty) / mrp_bizone) * 100
			else:
				realization = 0.0

			row.append(unique_sku_id)
			row.append(title)
			row.append(qty)
			row.append(mrp_bizone)
			row.append(principal_bizone)
			row.append(principal)
			row.append(shipping)
			row.append(gift_wrap)
			row.append(fba_delivery_services_fee)
			row.append(delivery_service_fee_tax)
			row.append(fba_pick_and_pack_fee)
			row.append(fba_per_unit_fulfillment_fee_tax)
			row.append(fba_weight_handling_fee)
			row.append(fba_weight_based_fee_tax)
			row.append(commission)
			row.append(commission_tax)
			row.append(fixed_closing_fee)
			row.append(fixed_closing_fee_tax)
			row.append(shipping_chargeback)
			row.append(shipping_chargeback_tax)
			row.append(gift_wrap_chargeback)
			row.append(gift_wrap_chargeback_tax)
			row.append(shipping_discount)
			row.append(received)
			row.append(realization)
			row.append(reversal_reimbursement_per_sku)
			row.append(free_replacement_refund_items_per_sku)
			row.append(remark)

			data.append(row)

	return data


def get_distinct_sku_ids(payment_items):
	distinct_sku_ids = []
	sku_ids = []
	for item in payment_items:
		sku_ids.append(item.sku_id)	
	distinct_sku_ids = set(sku_ids)
	return distinct_sku_ids	

