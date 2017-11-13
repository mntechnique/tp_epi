# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "tp_epi"
app_title = "TP EPI"
app_publisher = "MN Technique"
app_description = "ECommerce Portal Integration utility. Allows Titles in local database and product catalogs on ECommerce Portals to be kept in sync."
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "support@mntechnique.com"
app_version = "0.0.1"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/tp_epi/css/tp_epi.css"
# app_include_js = "/assets/tp_epi/js/tp_epi.js"

# include js, css files in header of web template
# web_include_css = "/assets/tp_epi/css/tp_epi.css"
# web_include_js = "/assets/tp_epi/js/tp_epi.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "tp_epi.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "tp_epi.install.before_install"
# after_install = "tp_epi.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "tp_epi.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	# "all": [
	# 	"tp_epi.tasks.all"
	# ],
	"daily": [
		"tp_epi.api_amazon.refresh_orders"
	],
	"hourly": [
		"tp_epi.api_amazon.reminder_sku_update"
	]
	# "weekly": [
	# 	"tp_epi.tasks.weekly"
	# ]
	# "monthly": [
	# 	"tp_epi.tasks.monthly"
	# ]
}

# Testing
# -------

# before_tests = "tp_epi.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "tp_epi.event.get_events"
# }

fixtures = [{"dt":"Custom Script", "filters": [["name", "in", ["Project-Client", "Purchase Invoice-Client"]]]},
			{"dt":"Custom Field", "filters": [["name", "in", ["Item-sku_id_flipkart", "Item-sku_id_amazon", "Item-sb_epi_skus",
			"Item-epi_title_flipkart", "Item-epi_title_amazon", 
			"Customer-epi_flipkart_email", "Customer-epi_amazon_email", "Customer-sb_epi_portal_emails", 
			"Sales Order-epi_amazon_order_id", "Purchase Invoice-epi_amazon_order_id", "Sales Invoice-epi_amazon_order_id",
			"Sales Invoice Item-epi_ecom_sku_id", "Purchase Invoice Item-epi_ecom_sku_id", "Sales Order Item-epi_ecom_sku_id",
			]]]},
			"Property Setter"]