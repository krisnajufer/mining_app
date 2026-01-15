# Copyright (c) 2026, Krisna Jufer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, cstr, cint
from frappe.model.utils import get_fetch_values
from frappe.model.mapper import get_mapped_doc
from frappe.contacts.doctype.address.address import get_company_address

from erpnext.stock.doctype.delivery_note.delivery_note import DeliveryNote

from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from erpnext.stock.doctype.item.item import get_item_defaults

class DeliveryNoteInternal(DeliveryNote):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.status_updater = [
			{
				"source_dt": "Delivery Note Internal Item",
				"target_dt": "Sales Order Item",
				"join_field": "so_detail",
				"target_field": "delivered_internal_qty",
				"target_parent_dt": "Sales Order",
				"target_parent_field": "per_delivered_internal",
				"target_ref_field": "qty",
				"source_field": "qty",
				"percent_join_field": "against_sales_order",
				"status_field": "delivery_status_internal",
				"keyword": "Delivered",
				"second_source_dt": "Sales Invoice Item",
				"second_source_field": "qty",
				"second_join_field": "so_detail",
				"overflow_type": "delivery",
				"second_source_extra_cond": """ and exists(select name from `tabSales Invoice`
				where name=`tabSales Invoice Item`.parent and update_stock = 1)""",
			},
			{
				"source_dt": "Delivery Note Internal Item",
				"target_dt": "Sales Invoice Item",
				"join_field": "si_detail",
				"target_field": "delivered_internal_qty",
				"target_parent_dt": "Sales Invoice",
				"target_ref_field": "qty",
				"source_field": "qty",
				"percent_join_field": "against_sales_invoice",
				"overflow_type": "delivery",
				"no_allowance": 1,
			},
			{
				"source_dt": "Delivery Note Internal Item",
				"target_dt": "Pick List Item",
				"join_field": "pick_list_item",
				"target_field": "delivered_internal_qty",
				"target_parent_dt": "Pick List",
				"target_parent_field": "per_delivered_internal",
				"target_ref_field": "picked_qty",
				"source_field": "stock_qty",
				"percent_join_field": "against_pick_list",
				"status_field": "delivery_status_internal",
				"keyword": "Delivered",
			},
		]
		
	def validate(self):
		super().validate()
		self.set_items_missing_values()

	def on_submit(self):
		self.update_prevdoc_status()
		self.update_billing_status()

	def on_cancel(self):
		self.update_prevdoc_status()
		self.update_billing_status()

	def set_items_missing_values(self):
		for row in self.items:
			row.po_customer_no = self.po_customer_no
			row.delivery_no = self.delivery_no

@frappe.whitelist()
def make_delivery_note(source_name, target_doc=None, kwargs=None):
	from erpnext.stock.doctype.packed_item.packed_item import make_packing_list
	from erpnext.stock.doctype.stock_reservation_entry.stock_reservation_entry import (
		get_sre_details_for_voucher,
		get_sre_reserved_qty_details_for_voucher,
		get_ssb_bundle_for_voucher,
	)

	if not kwargs:
		kwargs = {
			"for_reserved_stock": frappe.flags.args and frappe.flags.args.for_reserved_stock,
			"skip_item_mapping": frappe.flags.args and frappe.flags.args.skip_item_mapping,
		}

	kwargs = frappe._dict(kwargs)

	sre_details = {}
	if kwargs.for_reserved_stock:
		sre_details = get_sre_reserved_qty_details_for_voucher("Delivery Note Internal", source_name)

	mapper = {
		"Delivery Note Internal": {"doctype": "Delivery Note", "validation": {"docstatus": ["=", 1]}},
		"Sales Taxes and Charges": {"doctype": "Sales Taxes and Charges", "reset_value": True},
		"Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
	}

	# 0 qty is accepted, as the qty is uncertain for some items
	# has_unit_price_items = frappe.db.get_value("Delivery Note Internal", source_name, "has_unit_price_items")

	def is_unit_price_row(source):
		# return has_unit_price_items and source.qty == 0
		return source.qty == 0

	def select_item(d):
		filtered_items = kwargs.get("filtered_children", [])
		child_filter = d.name in filtered_items if filtered_items else True
		return child_filter

	def set_missing_values(source, target):
		if kwargs.get("ignore_pricing_rule"):
			# Skip pricing rule when the dn is creating from the pick list
			target.ignore_pricing_rule = 1

		target.run_method("set_missing_values")
		target.run_method("set_po_nos")
		target.run_method("calculate_taxes_and_totals")
		target.run_method("set_use_serial_batch_fields")

		if source.company_address:
			target.update({"company_address": source.company_address})
		else:
			# set company address
			target.update(get_company_address(target.company))

		if target.company_address:
			target.update(get_fetch_values("Delivery Note", "company_address", target.company_address))

		# if invoked in bulk creation, validations are ignored and thus this method is nerver invoked
		if frappe.flags.bulk_transaction:
			# set target items names to ensure proper linking with packed_items
			target.set_new_name()

		make_packing_list(target)

	def condition(doc):
		if doc.name in sre_details:
			del sre_details[doc.name]
			return False

		# make_mapped_doc sets js `args` into `frappe.flags.args`
		if frappe.flags.args and frappe.flags.args.delivery_dates:
			if cstr(doc.delivery_date) not in frappe.flags.args.delivery_dates:
				return False

		return (
			(abs(doc.delivered_qty) < abs(doc.qty)) or is_unit_price_row(doc)
		) and doc.delivered_by_supplier != 1

	def update_item(source, target, source_parent):
		target.base_amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(source.base_rate)
		target.amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(source.rate)
		target.qty = (
			flt(source.qty) if is_unit_price_row(source) else flt(source.qty) - flt(source.delivered_qty)
		)

		item = get_item_defaults(target.item_code, source_parent.company)
		item_group = get_item_group_defaults(target.item_code, source_parent.company)

		if item:
			target.cost_center = (
				frappe.db.get_value("Project", source_parent.project, "cost_center")
				or item.get("buying_cost_center")
				or item_group.get("buying_cost_center")
			)

	if not kwargs.skip_item_mapping:
		mapper["Delivery Note Internal Item"] = {
			"doctype": "Delivery Note Item",
			"field_map": {
				"rate": "rate",
				"name": "delivery_note_internal_item",
				"parent": "against_delivery_note_internal",
				"so_detail": "so_detail",
				"against_sales_order": "against_sales_order",
			},
			# "condition": lambda d: condition(d) and select_item(d),
			"condition": lambda d:select_item(d),
			# "postprocess": update_item,
		}

	so = frappe.get_doc("Delivery Note Internal", source_name)
	target_doc = get_mapped_doc("Delivery Note Internal", so.name, mapper, target_doc)

	if not kwargs.skip_item_mapping and kwargs.for_reserved_stock:
		sre_list = get_sre_details_for_voucher("Delivery Note Internal", source_name)

		if sre_list:

			def update_dn_item(source, target, source_parent):
				update_item(source, target, so)

			so_items = {d.name: d for d in so.items if d.stock_reserved_qty}

			for sre in sre_list:
				if not condition(so_items[sre.voucher_detail_no]):
					continue

				dn_item = get_mapped_doc(
					"Delivery Note Internal Item",
					sre.voucher_detail_no,
					{
						"Delivery Note Internal Item": {
							"doctype": "Delivery Note Item",
							"field_map": {
								"rate": "rate",
								"name": "delivery_note_internal_item",
								"parent": "against_delivery_note_internal",
								"so_detail": "so_detail",
								"against_sales_order": "against_sales_order",
							},
							"postprocess": update_dn_item,
						}
					},
					ignore_permissions=True,
				)

				dn_item.qty = flt(sre.reserved_qty) / flt(dn_item.get("conversion_factor", 1))

				if sre.reservation_based_on == "Serial and Batch" and (sre.has_serial_no or sre.has_batch_no):
					dn_item.serial_and_batch_bundle = get_ssb_bundle_for_voucher(sre)

				target_doc.append("items", dn_item)
			else:
				# Correct rows index.
				for idx, item in enumerate(target_doc.items):
					item.idx = idx + 1

	# Should be called after mapping items.
	set_missing_values(so, target_doc)

	return target_doc