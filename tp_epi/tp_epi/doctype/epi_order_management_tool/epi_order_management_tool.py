# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
#from tp_epi.api_amazon import fetch_and_create_orders as createorders_amazon, fetch_settlement_data as createsettlements_amazon
from tp_epi.api_amazon import fetch_and_create_orders_amazon as createorders_amazon
from tp_epi.api_amazon import fetch_settlement_data as createsettlements_amazon

from tp_epi.api_flipkart import create_flipkart_payment_entries as createsettlements_flipkart

class EPIOrderManagementTool(Document):
	def download_orders_amazon(self, created_after_date, end_date):

		created_after_date_string = str(frappe.utils.data.getdate(created_after_date))
		end_date_string = str(frappe.utils.data.getdate(end_date))

		try:
			#Extract date from datetime and convert to string before passing to fetch and create orders
			#createorders_amazon(str(frappe.utils.data.getdate(self.last_downloaded_order_date_amazon)) or '2016-09-01')
			self.last_pull_on = frappe.utils.datetime.datetime.now()
			createorders_amazon(created_after_date=created_after_date_string, end_date=end_date_string)
			self.update_last_downloaded_order_date_amazon()
			
		except Exception, e:
			raise
		else:
			return "Orders downloaded from Amazon."

	def update_last_downloaded_order_date_amazon(self):
	 	#latest_order = frappe.get_all("Amazon Order", fields=["name, amazon_order_date"], order_by="amazon_order_date DESC")[0]
	 	
	 	orders_by_date_desc = frappe.get_all("Sales Order", fields=["name, transaction_date"], order_by="transaction_date DESC")

	 	if not orders_by_date_desc:
	 		frappe.throw("There are no sales orders from which Last downloaded date may be inferred.")

	 	latest_order = orders_by_date_desc[0]

	 	self.last_downloaded_order_date_amazon = latest_order.transaction_date
	 	self.save()
	 	frappe.db.commit()

	def download_settlements_amazon(self, from_date, to_date):
		try:
			#msg = createsettlements_amazon(self.amazon_payment_settlement_report_id)
			msg = createsettlements_amazon(from_date=from_date, to_date=to_date)
		except Exception, e:
			raise
		else:
			return msg
	
	def import_and_create_settlements_flipkart(self, settlement_csv):
		
		for x in xrange(1,10):	
			print "Settlement csv:", settlement_csv

		try:
			msg = createsettlements_flipkart(settlement_csv=settlement_csv)
		except Exception, e:
			raise
		else:
			return msg
