from frappe import _

def get_data():
	return [
		{
			"label": _("Catalog Listings"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "EPI Sync Catalog Tool",
					"label": "EPI Sync Catalog Tool",
					"description": _("Keep EPI titles in sync with BizOne titles."),
				},
				{
					"type": "doctype",
					"name": "EPI Catalog Listing",
					"label": "EPI Catalog Listing",
					"description": _("List of titles (catalog listings) in EPI"),
				},
			]
		},
		{
			"label": _("Order Payments"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "EPI Amazon Order Payment",
					"label": "EPI Amazon Order Payment",
					"description": _("List of settlement records for Amazon."),
				},
				{
					"type": "doctype",
					"name": "EPI Flipkart Order Payment",
					"label": "EPI Flipkart Order Payment",
					"description": _("List of settlement records for Flipkart."),
				},
				{
					"type": "doctype",
					"name": "EPI Order Management Tool",
					"label": "EPI Order Management Tool",
					"description": _("EPI Order Management Tool"),
				},
			]
		},
		{
			"label": _("Amazon Reports"),
			"items": [
				{
					"type": "report",
					"name": "EPI MRP Percent Realization for Amazon Fulfilled Orders",
					"label": "EPI MRP Percent Realization for Amazon Fulfilled Orders",
					"description": _("EPI MRP Percent Realization for Amazon Fulfilled Orders"),
					"route": "query-report/EPI MRP Percent Realization for Amazon Fulfilled Orders",
					"doctype": "DocType"
				},
				{
					"type": "report",
					"name": "EPI MRP Percent Realization for Amazon Seller Fulfilled Orders",
					"label": "EPI MRP Percent Realization for Amazon Seller Fulfilled Orders",
					"description": _("Percent realization on MRP for Seller Fulfilled Orders."),
					"route": "query-report/EPI MRP Percent Realization for Amazon Seller Fulfilled Orders",
					"doctype": "DocType"
				},
			]
		},
		{
			"label": _("Flipkart Reports"),
			"icon": "icon-star",
			"items": [
				{
					"type": "report",
					"name": "MRP Percent Realization for Titles Flipkart",
					"label": "MRP Percent Realization for Titles Flipkart",
					"description": _("MRP Percent Realization for Titles Flipkart."),
					"route": "query-report/MRP Percent Realization for Titles Flipkart",
					"doctype": "DocType"
				},
			]
		},
	]
