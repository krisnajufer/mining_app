# Copyright (c) 2026, Krisna Jufer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.accounts.utils import (
    update_cost_center
)

from mining_app.utils.defaults import (
	get_active_company
)

class Unit(Document):
	def on_update(self):
		self.process_cost_center()
		self.process_warehouse()

	def after_delete(self):
		self.delete_cost_center()
		self.delete_warehouse()

	def process_cost_center(self):
		self.update_cost_center()
		self.make_cost_center()

	def process_warehouse(self):
		self.update_warehouse()
		self.make_warehouse()
		
	def make_cost_center(self):
		filters = {"cost_center_name": self.unit_code, "company": self.company}
		exist_cost_center = frappe.db.get_value("Cost Center", filters)
		if exist_cost_center or self.cost_center:
			return
		abbr = frappe.db.get_value("Company", self.company, "abbr")
		filter_name = f"{self.company} - {abbr}"
		parent_cost_center = frappe.db.get_value("Cost Center", filter_name)

		cost_center = frappe.new_doc("Cost Center")
		cost_center.cost_center_name = self.unit_code
		cost_center.parent_cost_center = parent_cost_center
		cost_center.company = self.company
		cost_center.save()
		self.db_set("cost_center", cost_center.name)

	def update_cost_center(self):
		if not self.cost_center:
			return
		current_cost_center = frappe.get_doc("Cost Center",  self.cost_center)

		if self.company != current_cost_center.company:
			abbr = frappe.db.get_value("Company", self.company, "abbr")
			filter_name = f"{self.company} - {abbr}"
			parent_cost_center = frappe.db.get_value("Cost Center", filter_name)

			current_cost_center.company = self.company
			current_cost_center.parent_cost_center = parent_cost_center
			current_cost_center.save()
			new_name = update_cost_center(current_cost_center.name, self.unit_code, None, self.company, 0)
			self.db_set("cost_center", new_name)

	def make_warehouse(self):
		filters = {"warehouse_name": self.unit_code, "company": self.company}
		exist_warehouse = frappe.db.get_value("Warehouse", filters)
		if exist_warehouse or self.warehouse:
			return
		abbr = frappe.db.get_value("Company", self.company, "abbr")
		filter_name = f"All Warehouses - {abbr}"
		parent_warehouse = frappe.db.get_value("Warehouse", filter_name)

		warehouse = frappe.new_doc("Warehouse")
		warehouse.warehouse_name = self.unit_code
		warehouse.parent_warehouse = parent_warehouse
		warehouse.company = self.company
		warehouse.save()
		self.db_set("warehouse", warehouse.name)

	def update_warehouse(self):
		if not self.warehouse:
			return
		
		current_warehouse = frappe.get_doc("Warehouse",  self.warehouse)
		if self.company == current_warehouse.company:
			return
		
		frappe.db.set_value("Unit", self.name, "warehouse", None, update_modified=False)
		old_warehouse = self.warehouse
		warehouse = frappe.get_doc("Warehouse", old_warehouse)
		warehouse.delete(ignore_permissions=True)
		self.reload()
		self.make_warehouse()

	def delete_cost_center(self):
		cost_center = frappe.get_doc("Cost Center", self.cost_center)
		cost_center.delete()

	def delete_warehouse(self):
		warehouse = frappe.get_doc("Warehouse", self.warehouse)
		warehouse.delete()