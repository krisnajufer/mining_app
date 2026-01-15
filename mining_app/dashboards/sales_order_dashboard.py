import frappe
from frappe import _


def get_data(data):
	data.get("non_standard_fieldnames").update({"Delivery Note Internal": "against_sales_order"})
	data.get("transactions")[0].get("items").append("Delivery Note Internal")
	return data

