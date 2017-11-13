import frappe
from api_amazon import get_distinct_values
from api_amazon import get_json_from_flat_file

import csv, json


#VIABLE WORKING CODE
#from flipkart import FlipkartAPI, Authentication
#Sandbox
# app_id = "37DIGITKEY" #ApplicationID
# app_secret = "37DIGITKEY-2" #Application Secret

#Live
# app_id = "37DIGITKEY-live"
# app_secret = "37DIGITKEY-2-live"


#LIVETOKEN_170102: ajfif390-f3rg-voe0-sd08-0ecffbe9bae1

#global token

# def authenticate_and_get_token():
# 	if not token:
# 		try:
# 			auth = Authentication(app_id, app_secret, sandbox=False)
# 			token = auth.get_token_from_client_credentials()
# 		except Exception as e:
# 			raise

# 	return token

# def get_new_token():
# 	newtoken = None
# 	try:
# 		auth = Authentication(app_id, app_secret, sandbox=False)
# 		newtoken = auth.get_token_from_client_credentials()
# 	except Exception as e:
# 		raise

# 	return newtoken


# def get_orders(order_states):
# 	token = "ebd91282-f386-48b9-a89d-0ecffbe9bae1"	
# 	#authenticate_and_get_token()
# 	if not token:
# 		try:
# 			newtoken = get_new_token()

# 			print newtoken
# 			token = newtoken["access_token"]
# 		except Exception as e:
# 			frappe.throw(e)
	

# 	flipkart = FlipkartAPI(token, sandbox=False, debug=True)

# 	orders = flipkart.search_orders(filters={'states': ['Approved']})
	
# 	# distinct_order_ids = get_distinct_values("orderId", orders.items)

# 	# for order_id in distinct_order_ids:
# 	# 	items_for_order = [x for x in orders.items if x['orderId'] == order_id]
# 	return orders	

# #Method to receive auth code.
# # @frappe.whitelist()
# # def auth_code(**kwargs):
# # 	for x in xrange(1,10):
# # 		print kwargs

# # 	frappe.local.response = frappe._dict({ 'kwargs': kwargs})

def read_settlement_file(settlement_csv):
	file_rows = []
	out_rows = []

	csv_path = frappe.utils.get_site_path() + settlement_csv

	#with open('/home/gaurav/Downloads/25a4cbe4397b494a_2016-12-03_2017-01-02.csv', 'rb') as csvfile:
	with open(csv_path, 'rb') as csvfile:
		rdr = csv.reader(csvfile, delimiter=str(','), quotechar=str('|'))
	   
		for row in rdr:
			file_rows.append(row)

		final_json = {}
		json_data = final_json.setdefault("data", [])
		column_headings_row = file_rows[0]

		for i in xrange(1, len(file_rows)):
			record_core = ""

			if len(file_rows[i]) == len(column_headings_row):
				for j in range(0, len(column_headings_row) - 1):
					record_core += '"' +  column_headings_row[j] + '" : "' + file_rows[i][j] + '", '

				record_json_string = "{" + record_core[:-2] + "}"
				json_data.append(json.loads(record_json_string))

		return final_json


def create_flipkart_payment_entries(settlement_csv):
	payments_json = read_settlement_file(settlement_csv)

	#Status is delivered and processing 
	#processed_records =	[r for r in payments_json["data"] if r["Order Status"] == "delivered" and r["Settlement Ref No."] != "Settlement in progress"]
	processed_records =	payments_json["data"] #[r for r in payments_json["data"] if r["Settlement Ref No."] != "Settlement in progress"]

	messages = []
	unique_order_ids = list(set([r["Order ID/FSN"] for r in processed_records]))

	for order_id in unique_order_ids:
		fp_id = frappe.db.get_value("EPI Flipkart Order Payment", {"flipkart_order_id": order_id}, "flipkart_order_id")
		if fp_id:
			messages.append("Order {0} already exists.".format(order_id))
			continue

		order_records = [r for r in processed_records if r["Order ID/FSN"] == order_id]

		fp = frappe.new_doc("EPI Flipkart Order Payment")
		fp.flipkart_order_id = order_id
		fp.order_date = order_records[0]["Order Date"]
		fp.settlement_date = order_records[0]["Settlement Date"]

		for record in order_records:

			fp.append("items", {
				"settlement_ref_no": record["Settlement Ref No."],
				"order_item_id": record["Order item ID"],
				"sku_id": record["Seller SKU"],
				"qty": record["Quantity"],
				"order_item_value": record["Order Item Value (Rs.)"],
				"total_marketplace_fee": record["Total Marketplace Fee (Rs.)"],
				"service_tax": record["Service Tax (Rs.)"],
				"swachh_bharat_cess_tax": record["Sb Cess Tax(Rs.)"],
				"krishi_kalyan_cess_tax": record["KK Cess Tax(Rs.)"],
				"settlement_value": record["Settlement Value (Rs.)"],
				"commission_rate": record["Commission Rate"],
				"commission": record["Commission (Rs.)"],
				"payment_rate": record["Payment Rate"],
				"payment_fee": record["Payment Fee"],
				"fee_discount": record["Fee Discount (Rs.)"],
				"cancellation_fee": record["Cancellation Fee (Rs.)"],
				"fixed_fee": record["Fixed Fee  (Rs.)"],
				"admonetization_fee": record["Admonetaisation Fee (Rs.)"], #Legit typo in flipkart sheet.
				"shipping_fee": record["Shipping Fee (Rs.)"],
				"reverse_shipping_fee": record["Reverse Shipping  Fee (Rs.)"],
				"shipping_fee_reversal": record["Shipping Fee Reversal (Rs.)"],
				"pick_and_pack_fee": record["Pick And Pack Fee"],
				"storage_fee": record["Storage Fee"],
				"removal_fee": record["Removal Fee"],
				"order_status": record["Order Status"]
			})


		try:
			fp.save()
			frappe.db.commit()
			messages.append("{0} imported successfully.".format(record["Order ID/FSN"]))
		except Exception as e:
			messages.append("{0} was not imported. {1}".format(record["Order ID/FSN"], e))

	return messages



@frappe.whitelist()
def get_filter_values():
	payment_items = frappe.get_all("EPI Flipkart Order Payment Item", fields=["settlement_ref_no", "order_item_id", "order_status"])
 	settlements = list(set([x.settlement_ref_no for x in payment_items]))
 	order_statuses = list(set([x.order_status for x in payment_items]))
 	#order_item_ids = list(set([x.order_item_id for x in payment_items]))
 	print "Order Statuses", order_statuses

 	#payments = frappe.get_all("EPI Flipkart Order Payment", fields=["flipkart_order_id"])
 	#order_ids = list(set([x.flipkart_order_id for x in payments]))

 	return { "settlements" : "\n".join(settlements), "order_statuses" : "\n".join(order_statuses) } # "order_ids" : "\n".join(order_ids), "order_item_ids" : "\n".join(order_ids) }
