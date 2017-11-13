# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import database
import MySQLdb

import os

from xlutils.copy import copy # http://pypi.python.org/pypi/xlutils
from xlrd import open_workbook # http://pypi.python.org/pypi/xlrd
from xlwt import easyxf # http://pypi.python.org/pypi/xlwt


class EPISyncCatalogTool(Document):

	def connect_mysql(self):
		# Open database connection
		try:
			db = MySQLdb.connect("1.1.1.1","user","password","dbname")
		except Exception, e:
			raise

			return e
		else:
			# prepare a cursor object using cursor() method
			cursor = db.cursor()

			# execute SQL query using execute() method.
			cursor.execute("SELECT VERSION();")

			# Fetch a single row using fetchone() method.
			data = cursor.fetchone()

			# disconnect from server
			db.close()

			return "Connection succeeded. DB Version is {ver}".format(ver=data) 

	def fetch_bizone_titles(self):

		#data = frappe.db.sql("SELECT * FROM `tab_view_title_book_price`")

		# Open database connection
		db = MySQLdb.connect("1.1.1.1","user","password","dbname")

		# prepare a cursor object using cursor() method
		cursor = db.cursor()

		# execute SQL query using execute() method.
		cursor.execute("SELECT DISTINCT A.TITLE_I_D, TITLE_NAME, A.EDITION_I_D, EDITION_NAME, MRP, NO_OF_PAGES, Active FROM view_title_book_price AS A INNER JOIN (select MAX(EDITION_I_D) AS LatestEditionID FROM view_title_book_price where BOOK_TYPE_I_D = 2 GROUP BY TITLE_I_D) AS B ON A.EDITION_I_D = B.LatestEditionID")

		# Fetch a single row using fetchone() method.
		data = cursor.fetchall()

		# disconnect from server
		db.close()

		data_list = []

		for row in data:
			row_list = list(row)
			data_dict = frappe._dict({
				"TITLE_I_D": row_list[0],
				"TITLE_NAME": row_list[1],
				"EDITION_I_D": row_list[2],
				"EDITION_NAME": row_list[3],
				"MRP": row_list[4],
				"NO_OF_PAGES": row_list[5],
				"Active": row_list[6]
			})

			data_list.append(data_dict)

		return data_list
	
	def fetch_epi_titles(self):
		return frappe.get_all("EPI Catalog Listing", fields=['*'])

	def import_data_from_bizone(self):
		#Populate data in python
		titles = self.fetch_bizone_titles()

		successcount = 0
		updated = 0
		inserted = 0

		#Items needed to create sales order. 
		for title in titles:
				
			listing = None
			#item = None

			listing_id = frappe.db.get_value("EPI Catalog Listing", {"bizone_teid": title["EDITION_I_D"]}, "name")
			#item_id = frappe.db.get_value("Item", {"item_code": "TEID" + title["EDITION_I_D"]}, "name")

			if listing_id:
				listing = frappe.get_doc("EPI Catalog Listing", listing_id)
				updated += 1
			else:
				listing = frappe.new_doc("EPI Catalog Listing")
				inserted += 1

			#listing = frappe.new_doc("EPI Catalog Listing")
			
			listing.item_code = title["EDITION_I_D"]
			listing.bizone_teid = title["EDITION_I_D"]
			listing.bizone_titleid = title["TITLE_I_D"]
			listing.edition_name = title["EDITION_NAME"] #TitleID ?
			listing.item_name = title["TITLE_NAME"]
			listing.mrp = title["MRP"]
			listing.title = title["TITLE_NAME"]
			listing.edition = title["EDITION_I_D"]
			listing.number_of_pages = title["NO_OF_PAGES"]
			listing.is_active = title["Active"] 

			try:
				listing.save()
				frappe.db.commit()
			except Exception as e:
				raise

			# if item_id:
			# 	item = frappe.get_doc("Item", item_id)
			# else:
			# 	item = frappe.new_doc("Item")

			# if not item.item_code:
			# 	item.item_code = "TEID" + title["EDITION_I_D"]

			# item.item_name = title["TITLE_NAME"]
			# item.item_group = "Products"
			# item.standard_rate = title["MRP"]
			# if title["Active"] == 0:
			# 	item.disabled = 1

			# try:
			# 	item.save()
			# 	frappe.db.commit()
			# except Exception as e:
			# 	frappe.throw(frappe.throw({"Item #" + listing_id : e}))
			
			successcount += 1	

		return "{successful} / {total} titles successfully imported from BizOne. <br> ({ins} new | {upd} updated)".format(successful=successcount, total=len(titles), ins=inserted, upd=updated)
			#MISSING FIELDS: TitleID, AUthor, Publisher, Language, Product DImensions, Publishing_date.

	def write_to_excel(self):
		if not self.select_excel_sheet:
			return "Select an excel sheet first."
		if self.ecom_portal == "Flipkart":
			return self.make_sheet_flipkart()
		elif self.ecom_portal == "Amazon":
			return self.make_sheet_amazon()

	def make_sheet_flipkart(self):
		#file_path = frappe.utils.get_files_path(".{path}".format(path=self.select_excel_sheet))
		file_path = frappe.utils.get_site_path() + self.select_excel_sheet

		#START_ROW = 3 # 0 based (subtract 1 from excel row number)

		rb = open_workbook(file_path,formatting_info=True)
		
		r_sheet = rb.sheet_by_name('regionalbooks') # read only copy to introspect the file
		wb = copy(rb) # a writable copy (I can't read values out of this, only write to it)
		
		w_sheet = wb.get_sheet(4) # the sheet to write to within the writable copy

		titles = self.fetch_epi_titles()

		#frappe.msgprint(len(titles))

		row_index = 7 #Replace with 4 during live test. SHeet not empty by default.
		for title in titles:
			w_sheet.write(row_index, 6, title['item_code'])
			w_sheet.write(row_index, 7, title['item_name'])
			w_sheet.write(row_index, 8, title['author'])
			w_sheet.write(row_index, 9, title['edition'])
			w_sheet.write(row_index, 10, title['language'])
			w_sheet.write(row_index, 11, title['publisher'])
			#w_sheet.write(row_index, 12, title['publishing_date'])
			if title['publishing_date']:
				w_sheet.write(row_index, 12, frappe.utils.datetime.datetime.strftime(title['publishing_date'], "%Y"))
			w_sheet.write(row_index, 13, title['binding'])
			w_sheet.write(row_index, 14, 'Academic Test & Preparation')
			w_sheet.write(row_index, 15, title['number_of_pages'])
			
			w_sheet.write(row_index, 16, title['main_image_url'])
			w_sheet.write(row_index, 17, title['other_image_url_1'])
			w_sheet.write(row_index, 18, title['other_image_url_2'])
			w_sheet.write(row_index, 19, title['other_image_url_3'])
			w_sheet.write(row_index, 20, title['other_image_url_4'])

			w_sheet.write(row_index, 21, '1 Book') #Packing Qty
			w_sheet.write(row_index, 22, title['product_description'])

			w_sheet.write(row_index, 23, title['di_keywords']) #Prefix 'di_' stands for Discovery Information

			#Process key specs
			if title['key_specs']:
				key_specs = title['key_specs'].split(', ')

				colidx = 24
				for spec in key_specs:
					w_sheet.write(row_index, colidx, spec)
					colidx += 1

			w_sheet.write(row_index, 34, title['di_tags'])

			w_sheet.write(row_index, 40, title['fk_board'])
			w_sheet.write(row_index, 41, title['fk_standard'])
			w_sheet.write(row_index, 42, title['fk_exam'])
			w_sheet.write(row_index, 44, title['fk_university'])

			w_sheet.write(row_index, 51, title['fk_category'])

			w_sheet.write(row_index, 52, title['dim_width'])
			w_sheet.write(row_index, 53, title['dim_length'])
			w_sheet.write(row_index, 54, title['dim_depth'])
			w_sheet.write(row_index, 55, title['dim_weight'])

			row_index += 1
		
		
		wb.save(file_path + '.out' + os.path.splitext(file_path)[-1])		
		
		return "Flipkart sheet ready."


	def make_sheet_amazon(self):
		#file_path = frappe.utils.get_files_path(".{path}".format(path=self.select_excel_sheet))
		file_path = frappe.utils.get_site_path() + self.select_excel_sheet

		#START_ROW = 3 # 0 based (subtract 1 from excel row number)

		rb = open_workbook(file_path,formatting_info=True)
		
		r_sheet = rb.sheet_by_name('Template') # read only copy to introspect the file
		wb = copy(rb) # a writable copy (I can't read values out of this, only write to it)
		
		w_sheet = wb.get_sheet(3) # the sheet to write to within the writable copy

		titles = self.fetch_epi_titles()

		
		row_index = 3 #Replace with 4 during live test. SHeet not empty by default.
		for title in titles:
			w_sheet.write(row_index, 0, title['item_name'])
			w_sheet.write(row_index, 1, title['product_description'])
			w_sheet.write(row_index, 5, title['edition'])
			w_sheet.write(row_index, 6, title['binding'])
			w_sheet.write(row_index, 7, title['publisher'])
			
		# 	#Process authors
			if title['author']:
				authors = title['author'].split(', ')

				colidx = 8
				limit = 3
				for author in authors:
					w_sheet.write(row_index, colidx, author)
					colidx += 1
					limit -= 1
					if limit == 0:
						break

			if title['publishing_date']:
				w_sheet.write(row_index, 11, frappe.utils.datetime.datetime.strftime(title['publishing_date'], "%Y"))
			
			w_sheet.write(row_index, 14, 'New')

			w_sheet.write(row_index, 19, '1')
			w_sheet.write(row_index, 20, 'FALSE') #Is Giftwrap available.

			w_sheet.write(row_index, 28, title['mrp'])
			#w_sheet.write(row_index, 31, title['qty']) QUANTITY???

			w_sheet.write(row_index, 32, title['dim_weight'])
			w_sheet.write(row_index, 33, 'GM')
			w_sheet.write(row_index, 34, title['dim_depth'])
			w_sheet.write(row_index, 35, 'IN')
			w_sheet.write(row_index, 36, title['dim_length'])
			w_sheet.write(row_index, 37, 'IN')
			w_sheet.write(row_index, 38, title['dim_width'])
			w_sheet.write(row_index, 39, 'IN')
			w_sheet.write(row_index, 40, title['dim_weight'])
			w_sheet.write(row_index, 41, 'GM')

			#Process browse nodes.
			if title['am_recommended_browse_nodes']:
				browse_nodes = title['am_recommended_browse_nodes'].split(', ')

				colidx = 43
				limit = 2 #Only two browse nodes allowed in sheet.
				for node in browse_nodes:
					w_sheet.write(row_index, colidx, node)
					colidx += 1
					limit -= 1
					if limit == 0:
						break

		# 		# colidx = 44
		# 		# i = 0
		# 		# while colidx <= 45:
		# 		# 	#i = (colidx - 45) + 1 #(currentidx - limit) + 1, It1: (44 - 45) + 1 = 0, It2: (45 - 45) + 1 = 1
		# 		# 	w_sheet.write(row_index, colidx, browse_nodes[i])
		# 		# 	colidx += 1
		# 		# 	i += 1
			
			#Process search terms
			if title['di_keywords']:
				keywords = title['di_keywords'].split(', ')

				colidx = 45
				limit = 5
				for keyword in keywords:
					w_sheet.write(row_index, colidx, keyword)
					colidx += 1
					limit -= 1
					if limit == 0:
						break

		# 	#Process key specs
			if title['key_specs']:
				key_specs = title['key_specs'].split(',')

				colidx = 50
				limit = 5
				for spec in key_specs:
					w_sheet.write(row_index, colidx, spec)
					colidx += 1
					limit -= 1
					if limit == 0:
						break

		# 	#w_sheet.write(row_index, 55, title['swatch_image_url'])
			w_sheet.write(row_index, 56, title['other_image_url_1'])
			w_sheet.write(row_index, 57, title['other_image_url_2'])
			w_sheet.write(row_index, 58, title['other_image_url_3'])
			w_sheet.write(row_index, 59, title['other_image_url_4'])
			w_sheet.write(row_index, 60, title['other_image_url_5'])
			w_sheet.write(row_index, 61, title['other_image_url_6'])
			w_sheet.write(row_index, 62, title['main_image_url'])

			w_sheet.write(row_index, 76, title['number_of_pages'])
			w_sheet.write(row_index, 78, title['language'])
			
			row_index += 1
		
		wb.save(file_path + '.out' + os.path.splitext(file_path)[-1])		
		
		#return "{rowindex}".format(rowindex=row_index) #
		return "Amazon sheet ready."


	def make_sheet_flipkart_mrp(self):
		import csv

		with open('names.csv', 'wb') as csvfile:
			fieldnames = ["Flipkart Serial Number", "Seller SKU ID", "MRP", "Your Selling Price", "Your Stock Count", "Local Shipping Charge (per qty)", "Zonal Shipping Charge (per qty)", "National Shipping Charge (per qty), Procurement SLA", "Listing Status", "Selling Region Restriction", "Procurement Type"]
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)	

			writer.writeheader()
			writer.writerow({'first_name': 'Baked', 'last_name': 'Beans'})
			writer.writerow({'first_name': 'Lovely', 'last_name': 'Spam'})
			writer.writerow({'first_name': 'Wonderful', 'last_name': 'Spam'})



