# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import database
from frappe.model.document import Document

class EPICatalogListing(Document):
	def on_update(self):
		#self.update_item_counterpart()
		item_code_string = "TEID{0}".format(self.item_code)
		self.add_or_update_item(item_code_string)
		self.add_or_update_item_price_list(item_code_string)

	# def after_insert(self):
	# 	self.update_item_counterpart()
			

	# def update_item_counterpart(self):
	# 	item_code_string = "TEID{0}".format(self.item_code)
		
	# 	found_item_code = frappe.db.get_value("Item", item_code_string, "item_code")
	# 	found_item_price_name = frappe.db.get_value("Item Price", {"item_code": item_code_string}, "name")
	# 	# for x in xrange(1,10):
	# 	# 	print 'item code string: ' + item_code_string
	# 	# 	print 'found item code: ' + found_item_code

	# 	if found_item_code and found_item_price_name:
	# 		item = frappe.get_doc("Item", found_item_code)
	# 		item.sku_id_amazon = self.sku_id_amazon
	# 		item.epi_title_amazon = self.item_name_amazon
	# 		item.epi_title_flipkart = self.item_name_flipkart
	# 		item.sku_id_flipkart = self.sku_id_flipkart
	# 		item.standard_rate = self.mrp
	# 		item.save()

	# 		item_price = frappe.get_doc("Item Price", {"item_code": item_code_string, "price_list": "Standard Selling"})
	# 		item_price.price_list_rate = self.mrp
	# 		item_price.save()

	# 		frappe.db.commit()
	# 	else:
	# 		item = frappe.new_doc("Item")
			
	# 		item.item_code = "TEID{0}".format(self.item_code)
	# 		item.sku_id_amazon = self.sku_id_amazon
	# 		item.epi_title_amazon = self.item_name_amazon
	# 		item.epi_title_flipkart = self.item_name_flipkart
	# 		item.sku_id_flipkart = self.sku_id_flipkart
	# 		item.standard_rate = self.mrp
	# 		item.item_name = self.item_name
	# 		item.item_group = "Products"
			
	# 		if self.is_active == 0:
	# 			item.disabled = 1
			
	# 		try:
	# 			item.save()
	# 		except Exception as e:
	# 			raise

	# 		item_price = frappe.new_doc("Item Price")
	# 		item_price.price_list = "Standard Selling"
	# 		item_price.selling = 1
	# 		item_price.item_code = item.name
	# 		item_price.price_list_rate = self.mrp
	# 		item_price.save()

	# 		frappe.db.commit()


	# 		#frappe.throw("Item Code mismatch for EPI Catalog Listing #{0}. <br><br> Please check whether EPI Title ID matches the item code. <br> (e.g. Item Code should be TEID11001 for EPI Catalog Listing SKUID 11001)".format(self.item_code))


	def add_or_update_item(self, item_code_string):
		found_item_code = frappe.db.get_value("Item", item_code_string, "item_code")

		if found_item_code:
			item = frappe.get_doc("Item", found_item_code)
			item.sku_id_amazon = self.sku_id_amazon
			item.epi_title_amazon = self.item_name_amazon
			item.epi_title_flipkart = self.item_name_flipkart
			item.sku_id_flipkart = self.sku_id_flipkart
			item.standard_rate = self.mrp
			try:
				item.save()
				frappe.db.commit()
			except Exception as e:
				raise

		else:
			item = frappe.new_doc("Item")
			
			item.item_code = item_code_string
			item.sku_id_amazon = self.sku_id_amazon
			item.epi_title_amazon = self.item_name_amazon
			item.epi_title_flipkart = self.item_name_flipkart
			item.sku_id_flipkart = self.sku_id_flipkart
			item.standard_rate = self.mrp
			item.item_name = self.item_name
			item.item_group = "Products"
			
			if self.is_active == 0:
				item.disabled = 1
			
			try:
				item.save()
				frappe.db.commit()
			except Exception as e:
				raise
			


	def add_or_update_item_price_list(self, item_code_string):
		found_item_price_name = frappe.db.get_value("Item Price", {"item_code": item_code_string}, "name")

		if found_item_price_name:
			item_price = frappe.get_doc("Item Price", {"item_code": item_code_string, "price_list": "Standard Selling"})
			item_price.price_list_rate = self.mrp
			try:
				item_price.save()
				frappe.db.commit()
			except Exception as e:
				raise
		else:
			item_price = frappe.new_doc("Item Price")
			item_price.price_list = "Standard Selling"
			item_price.selling = 1
			item_price.item_code = item_code_string
			item_price.price_list_rate = self.mrp
			
			try:
				item_price.save()
				frappe.db.commit()
			except Exception as e:
				raise