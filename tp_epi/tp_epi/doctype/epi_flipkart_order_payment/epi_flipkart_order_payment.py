# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class EPIFlipkartOrderPayment(Document):
	def validate(self):
		self.total_amount = sum([float(item.settlement_value) for item in self.items])

