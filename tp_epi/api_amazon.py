import frappe
from mws import mws
import json, time
#from tp_epi.tp_epi.tp_epi.doctype.epi_order_management_tool.epi_order_management_tool import get_epi_omt_settings
#import tp_epi.tp_epi.doctype.epi_order_management_tool.epi_order_management_tool

account_id = '13DIGITID'
access_key = '20CHARACTERKEY'
secret_key = '40CHARACTERKEY'
marketplace_ids = ["13CHARMID"]


@frappe.whitelist()	
def get_afn_orders(created_after_date):
	x = mws.Orders(access_key=access_key, secret_key=secret_key, account_id=account_id, region='IN', domain='https://mws.amazonservices.in', version="2013-09-01")
	orders_response = x.list_orders(marketplaceids=marketplace_ids, fulfillment_channels=["AFN"], created_after=created_after_date)

	return orders_response


@frappe.whitelist()	
def get_orders(created_after_date):
	x = mws.Orders(access_key=access_key, secret_key=secret_key, account_id=account_id, region='IN', domain='https://mws.amazonservices.in', version="2013-09-01")
	orders_response = x.list_orders(marketplaceids=marketplace_ids, fulfillment_channels=["MFN"], created_after=created_after_date)

	return orders_response

@frappe.whitelist()	
def get_order(order_id):
	x = mws.Orders(access_key=access_key, secret_key=secret_key, account_id=account_id, region='IN', domain='https://mws.amazonservices.in', version="2013-09-01")
	order_response = x.get_order(amazon_order_ids=[order_id])

	return order_response


@frappe.whitelist()
def get_report(report_id):
	x = mws.Reports(access_key=access_key, secret_key=secret_key, account_id=account_id, region='IN', domain='https://mws.amazonservices.in', version="2009-01-01")
	response = x.get_report(report_id)

	return response


#Second approach: Create orders from Order reports 
def fetch_and_create_orders_amazon(created_after_date=None, end_date=None):
	#UNCOMMENT
	# missing_sku_count = get_listings_with_null_sku_amazon()
	# if missing_sku_count > 0:
	# 	frappe.throw("There are {0} Listings in EPI without Amazon SKU IDs. <br> Please set them, so that new orders may be downloaded.".format(missing_sku_count))

	from frappe.utils import add_days, nowdate

	def check_create_customer(order):
		cust_id = frappe.db.get_value("Customer", {"epi_amazon_email": order['buyer-email']}, "name")
		customer = None
		if not cust_id:
			customer = frappe.new_doc("Customer")
			customer.customer_name = order['buyer-name']
			customer.customer_type = "Individual"
			customer.customer_group = "Individual"
			customer.customer_details = order["buyer-email"]
			customer.epi_amazon_email = order["buyer-email"]
			customer.territory = "India" 
			customer.insert()
			frappe.db.commit()
		else:
			customer = frappe.get_doc("Customer", cust_id)
			
		return customer

	def check_create_address(order, customer):
		address_id = frappe.db.get_value("Address", {"email_id": order["buyer-email"]}, "name")

		address = None

		if not address_id:
			address = frappe.new_doc("Address")
			address.address_title = order["recipient-name"]
			address.address_type = "Shipping"
			address.is_shipping_address = 1
			address.address_line1 = order["ship-address-1"]

			if "ship-address-2" in order:
				address.address_line2 = order["ship-address-1"]

			address.city = order["ship-city"]
			address.state = order["ship-state"]
			address.email_id = order["buyer-email"] #For referencing.
			
			#if self.header_json["ShippingAddress"].haskey('Phone'):
			if "ship-phone-number" in order:
				address.phone = order["ship-phone-number"]
			
			address.pincode = order["ship-postal-code"]
			
			if order["ship-country"] == "IN":
				address.country = "India"
			else:
				address.city += ", " + order["ship-country"]

			address.customer = customer.name
			address.insert()
			frappe.db.commit()
		else:
			address = frappe.get_doc("Address", address_id)
		
		return address


	
	generated_report_id = request_report_2(report_type="_GET_FLAT_FILE_ORDERS_DATA_", start_date=created_after_date, end_date=end_date)	#"4197914812017123"
	report_response = get_report(generated_report_id)
	orders_json = get_json_from_flat_file(report_response.parsed, record_delimiter="\r\n")


  	#f = open("/home/gaurav/gaurav-work/target/orders_october.txt")
	# contents = f.read()
	# orders_json = get_json_from_flat_file(contents, record_delimiter="\n")

	distinct_orders = interpret_distinct_orders(orders_json)

	so_messages = []

	for order in distinct_orders['orders']:
		existing_so_name = frappe.db.get_value("Sales Order", filters={"epi_amazon_order_id":order["order-id"]}, fieldname="name")
		if not existing_so_name:

			so = frappe.new_doc("Sales Order")
			so.epi_amazon_order_id = order["order-id"]

			# print "AOID:" + order["order-id"]
			# print "~----~"

			customer = check_create_customer(order)

			if not customer:
				frappe.throw("Could not create customer for order {0}".format(order["order-id"]))

			address = check_create_address(order, customer)

			so.customer = customer.name
			so.address = address

			so.transaction_date = frappe.utils.data.getdate(order['purchase-date'])
			so.delivery_date = add_days(so.transaction_date, 10)
			so.selling_price_list = "Standard Selling" 


			# print order["order-items"]
			# print "~----~"

			for item in order["order-items"]:
				so.append("items", {
							"item_code": frappe.db.get_value("Item", {"sku_id_amazon":item["sku"]}, "item_code"),
							"epi_ecom_sku_id": item["sku"],
							"warehouse": 'Finished Goods - TPPL',
							"qty": item["quantity-purchased"],
							"amount": item["item-price"],
							"conversion_factor": 1.0,
							"description": item["product-name"]
						})

			if ("shipping-price" in order):
				if (float(order["shipping-price"]) > 0.0):
					so.append("taxes", {
						"charge_type": "Actual",
						"account_head": "Freight and Forwarding Charges - TPPL",
						"description": "Shipping Charges",
						"tax_amount": item["shipping-price"]
					})
			try:
				so.save()
				frappe.db.commit()
			except Exception as e:
				so_messages.append('Error: Order {0}: {1}'.format(order["order-id"], e))		
			else:
				so_messages.append('Order {0} created against Amazon Order {1}'.format(so.name, order["order-id"]))	
			
		else:
			so_messages.append('Order {0} already created against Amazon Order {1}'.format(existing_so_name, order["order-id"]))

	return so_messages

def interpret_distinct_orders(orders_json):
	#Interpret orders_json and get final json as:
	# {
	# 	'order_id': 123
	# 	'items': []
	# }

	orders = orders_json["data"]

	unique_order_ids = get_distinct_values("order-id", orders)
	distinct_orders = {"orders": []}

	for order_id in unique_order_ids:
		records_by_order = [x for x in orders if x["order-id"]==order_id]
		candidate_record = records_by_order[0]

		distinct_orders["orders"].append({"order-id": order_id, \
			"buyer-name": candidate_record['buyer-name'], \
			"buyer-email": candidate_record['buyer-email'], \
			"buyer-phone-number": candidate_record['buyer-phone-number'], \
			"delivery-Instructions": candidate_record['delivery-Instructions'], \
			"delivery-end-date": candidate_record['delivery-end-date'], \
			"delivery-start-date": candidate_record['delivery-start-date'], \
			"delivery-time-zone": candidate_record['delivery-time-zone'], \
			"purchase-date": candidate_record["purchase-date"], \
			"payments-date": candidate_record["payments-date"], \
			"recipient-name": candidate_record["recipient-name"], \
			"ship-address-1": candidate_record["ship-address-1"], \
			"ship-address-2": candidate_record["ship-address-2"], \
			"ship-address-3": candidate_record["ship-address-3"], \
			"ship-city": candidate_record["ship-city"], \
			"ship-state": candidate_record["ship-state"], \
			"ship-country": candidate_record["ship-country"], \
			"ship-phone-number": candidate_record["ship-phone-number"], \
			"ship-postal-code": candidate_record["ship-postal-code"], \
			"ship-service-level": candidate_record["ship-service-level"], \
			"shipping-price": candidate_record["shipping-price"], \
			"order-items": records_by_order })

	return distinct_orders


#Settlement data cannot be fetched by date range. Amazon schedules this on its own. Latest must be picked.

def fetch_settlement_data(settlement_report_id=None, from_date=None, to_date=None):
	messages = []
	if not settlement_report_id:
		#Fetch report list for settlement Reports
		resp = get_report_request_list(report_types=["_GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2_"], fromdate=from_date, todate=to_date)

		if not "ReportRequestInfo" in resp.parsed:
			frappe.throw("Settlement reports between {0} and {1} are unavailable".format(from_date, to_date))

		print resp.parsed["ReportRequestInfo"]
		
		for report_request in resp.parsed["ReportRequestInfo"]:
		
			latest_settlement_report_id = report_request["GeneratedReportId"]["value"]

			#Introduce time wait. 
			time.sleep(10)

			report_response = get_report(latest_settlement_report_id)
			
			# filename = "/home/gaurav/Desktop/settlement_{0}.txt".format(latest_settlement_report_id)
			# with open(filename, "w") as f:
			# 	settlements = f.write(report_response.parsed)
			# 	f.close()

			#Create Purchase Receipts from settlements data.
			settlements_json = get_json_from_flat_file(report_response.parsed, record_delimiter="\n")
			settlements_json_records = settlements_json["data"]

			# settlements_json = get_json_from_flat_file(settlements, record_delimiter="\n")
			# settlements_json_records = settlements_json["data"]

			#NEWCODE
			#Get MFN records from settlement records
			order_records = [x for x in settlements_json_records] # if (x['fulfillment-id']=="MFN")] 
			#[x for x in settlements_json_records if (x['fulfillment-id']=="MFN")]	

			if len(order_records) == 0:
				messages.append("No orders found in settlement statement report #{0}".format(latest_settlement_report_id))
				
			#Missing SKU Check
			unique_skus = []
			for order_rec in order_records:
				if order_rec['sku'] not in unique_skus:
					unique_skus.append(order_rec['sku'])
			missing_skus = []
			for skuid in unique_skus:
 				if skuid and not frappe.db.get_value("EPI Catalog Listing", {"sku_id_amazon": skuid}, "name"):
					missing_skus.append('<li>{0}</li>'.format(skuid))

			if len(missing_skus) > 0:
				frappe.throw("There are no titles in EPI for the following Amazon SKUs: <br><ol>{0}</ol><br> Please ensure they exist in BizOne and sync again via EPI Catalog Sync Tool.".format("".join(missing_skus)))


			#Separate out order payments+deductions, EasyShip entries and Refunds
			payments_and_deductions = [x for x in order_records if (x['transaction-type']=="Order") and (x['amount-type'] in ["ItemPrice", "ItemFees", "Promotion"])]
			other_transactions = [x for x in order_records if (x['transaction-type']=="other-transaction") and (x['amount-type'] in ["other-transaction", "FBA Inventory Reimbursement"]) and (x['amount-description'].lower() not in ["current reserve amount", "previous reserve amount balance"])]
			refunds = [x for x in order_records if (x['transaction-type']=="Refund")]

			
			unique_orders = []
			for order_rec in order_records:
				if order_rec['order-id'] not in [ur['order-id'] for ur in unique_orders]:
					unique_orders.append({"order-id": order_rec['order-id'], "fulfillment-id": order_rec['fulfillment-id']})

			print unique_orders
			print "Count: ", len(unique_orders)
			time.sleep(3)

			#Create new purchase invoices for each unique order, update only details for existing PI.
			for order in unique_orders:

				order_id = order["order-id"]

				if order_id == "":
					continue

				order_payments_and_deductions = [x for x in payments_and_deductions if x["order-id"] == order_id]
				order_other_transactions = [x for x in other_transactions if x["order-id"] == order_id]
				order_refunds = [x for x in refunds if x["order-id"] == order_id] #Will apply only to existing orders.
				
				#To handle cases where there are no 
				if len(order_payments_and_deductions) == 0:
					continue

				existing_pi_id = frappe.db.get_value("EPI Amazon Order Payment", {"amazon_order_id": order_id}, "name")

				if not existing_pi_id:

					pi = frappe.new_doc("EPI Amazon Order Payment")
					pi.amazon_order_id = order_id
					pi.credit_to = "Creditors - TPPL"
					#pi.posting_date = frappe.utils.dateorder_payments_and_deductions[0]['posted-date'])# if len(order_payments_and_deductions) > 0 else frappe.utils.datetime.date.today()
					posting_date_str = order_payments_and_deductions[0]['posted-date']
					pi.posting_date =  frappe.utils.data.getdate(frappe.utils.datetime.datetime.strptime(posting_date_str, "%d.%m.%Y"))

					print " ID:", order_id, ", posting-date: ", order_payments_and_deductions[0]['posted-date']

					pi.order_fulfillment_type = order['fulfillment-id']

					for pd in order_payments_and_deductions:
						pi.append("items", {
							"sku_id": pd["sku"],
							"description": pd["amount-description"],
							"qty": pd["quantity-purchased"],
							"amount": float(pd["amount"]),
						})
					#Easy Ship Charges and Easy Ship Charge Tax
					for other_charge in order_other_transactions:
						pi.append("taxes", {
							"category": "Total",
							"add_deduct_tax": "Add",
							"charge_type": "Actual",
							"tax_amount": float(other_charge["amount"]),
							"account_head": "Amazon Charges - TPPL",
							"cost_center": "Main - TPPL",
							"description": other_charge["amount-description"]
						})
					try:		
						pi.save()
						frappe.db.commit()
						messages.append("Purchase Invoice {0} created against Amazon Order {1}".format(pi.name, order_id))
					except Exception as e:
						messages.append("Could not create settlement (Purchase) entries against order {0}. <br> {1}".format(order_id, e))
				elif len(order_refunds) > 0: #Implies that the order has been refunded/adjusted
					pi = frappe.get_doc("EPI Amazon Order Payment", existing_pi_id)


					for refund in order_refunds:
						pi.append("items", {
							"sku_id": refund["sku"],
							"description": refund["amount-description"],
							"qty": frappe.db.get_value("EPI Amazon Order Payment Item", {"parent": existing_pi_id, "sku_id": refund["sku"]}, "qty"),
							"amount": float(refund["amount"]),
						})

						# print "Refundqty:" + (refund["quantity-purchased"] or '')
						# print "SKUQty:" + str(frappe.db.get_value("EPI Amazon Payment Item", {"parent": existing_pi_id, "epi_ecom_sku_id": refund["sku"]}, "qty")) or ''

					try:
						pi.save()
						frappe.db.commit()
					except Exception as e:
						messages.append("Could not update settlement (Purchase) entries against order {0}. <br> {1}".format(order_id, e))

		return messages





def get_report_list(from_date=None, to_date=None, types=None, max_count=None):
	x = mws.Reports(access_key=access_key, secret_key=secret_key, account_id=account_id, region='IN', domain='https://mws.amazonservices.in', version="2009-01-01")
	report_list_response = x.get_report_list(fromdate=from_date, todate=to_date, types=types, max_count=max_count)
	return report_list_response

def get_json_from_flat_file(flat_file_string, record_delimiter="\r\n"):
	records = flat_file_string.split(record_delimiter)
	processed_records = [r.split("\t") for r in records]
	columns = processed_records[0]

	final_json = {}
	json_data = final_json.setdefault("data", [])
	
	for i in xrange(1, len(processed_records) - 1):
		record_core = ""

		if len(processed_records[i]) == len(columns):
			for j in range(0, len(columns) - 1):
				record_core += '"' + columns[j] + '" : "' + processed_records[i][j] + '", '
			
			record_json_string = "{" + record_core[:-2] + "}"
			json_data.append(json.loads(record_json_string))
		
	return final_json

def get_distinct_values(fieldname, list_of_json):
	all_instances = []
	for item_json in list_of_json:
		all_instances.append(item_json[fieldname])
	print set(all_instances)
	return set(all_instances)

#-Scheduled tasks-#
def reminder_sku_update():
	listings_needing_attention = get_listings_with_null_sku_amazon()	
		
	frappe.publish_realtime(event="msgprint", message="Amazon SKU IDs need to be set in {0} EPI Catalog listings.".format(listings_needing_attention)) 

def refresh_orders():
	created_after_date = frappe.db.get_value("EPI Order Management Tool", None, "last_downloaded_order_date_amazon")
	fetch_and_create_orders_amazon(created_after_date=created_after_date)
#----------------#




def get_listings_with_null_sku_amazon():
	titles_with_unset_sku = frappe.db.sql("""SELECT count(*) as NullCount FROM `tabEPI Catalog Listing` WHERE sku_id_amazon is null""")[0][0]
	return titles_with_unset_sku

def request_report(report_type):
	x = mws.Reports(access_key=access_key, secret_key=secret_key, account_id=account_id, region='IN', domain='https://mws.amazonservices.in', version="2009-01-01")
	response = x.request_report(report_type=report_type, start_date='2016-10-01', end_date='2016-10-31')

	return response

def get_report_request_list(report_types=None, request_ids=None, max_count=None, fromdate=None, todate=None):
	x = mws.Reports(access_key=access_key, secret_key=secret_key, account_id=account_id, region='IN', domain='https://mws.amazonservices.in', version="2009-01-01")
	response = x.get_report_request_list(types=report_types, requestids=request_ids, max_count=max_count, fromdate=fromdate, todate=todate)

	return response

#TODO: standardize. Works.
def request_report_2(report_type, start_date, end_date):
	#Request new report.
	rpts = mws.Reports(access_key=access_key, secret_key=secret_key, account_id=account_id, region='IN', domain='https://mws.amazonservices.in', version="2009-01-01")
	report_response = rpts.request_report(report_type=report_type, start_date=start_date, end_date=end_date, marketplaceids=marketplace_ids)
	
	#Amazon should be able to generate report in 15 seconds. 
	time.sleep(15)

	#Check if report has been generated. Pull report request list and check status of requested report.
	report_request_id = report_response.parsed["ReportRequestInfo"]["ReportRequestId"]["value"]
	generated_report_id = None
	epi_report_status = "" 

	#Request report. If report is Done, break and fetch the actual report.
	for x in xrange(1,10):
		report_request_list_response = rpts.get_report_request_list(requestids=[report_request_id])
		
		report_status = report_request_list_response.parsed["ReportRequestInfo"]["ReportProcessingStatus"]["value"]

		if report_status == "_SUBMITTED_" or report_status == "_IN_PROGRESS_":
			print "Report request {0} {1}. Waiting...".format(report_request_id, report_status)
			time.sleep(15) #Wait 15 seconds for report to get generated.
			continue
		elif report_status == "_CANCELLED_":
			print "Report request {0} {1}.".format(report_request_id, report_status)
			epi_report_status = "Report request cancelled by Amazon"
			break
		elif report_status == "_DONE_NO_DATA_":
			print "Report request {0} {1}.".format(report_request_id, report_status)
			epi_report_status = "No new data."
			break
		elif report_status == "_DONE_":
			generated_report_id =  report_request_list_response.parsed["ReportRequestInfo"]["GeneratedReportId"]["value"]
			print "Report request {0} {1}. Generated report id : {2}".format(report_request_id, report_status, generated_report_id)
			break

	return generated_report_id

#Retrieves results for _GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_, 
def update_sales_order_item_status_amazon(from_date, to_date):
	report_id = request_report_2(report_type="_GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_", start_date=from_date, end_date=to_date)
	response = get_report(report_id)

	response_json = get_json_from_flat_file(response.parsed)

	mfn_order_records = [x for x in response_json["data"] if x["fulfillment-channel"]=="Merchant"]

	distinct_mfn_order_ids = get_distinct_values("amazon-order-id", mfn_order_records)

	for order_id in distinct_mfn_order_ids:
		#Find Sales Order
		existing_soid = frappe.db.get_value("Sales Order", {"epi_amazon_order_id": order_id}, "name")

		if existing_soid:
			so = frappe.get_doc("Sales Order", existing_soid)
	
			records_for_order = [x for x in mfn_order_records if x["amazon-order-id"] == order_id]

			for record in records_for_order:
				for item in so.items:
					if item.epi_ecom_sku_id == record["sku"]:
						item.epi_status = record["item-status"]
						
			so.save()
			frappe.db.commit()

# def check_missing_mrp_selling_price():
# 	listings_with_missing_mrp_selling_price = frappe.db.execute_sql("""SELECT COUNT(*) FROM tabEPI Catalog Listing (WHERE mrp = 0.0) or (selling_price_amazon = 0.0) """)
# 	if listings_with_missing_mrp_selling_price > 0:
# 		