import frappe

from erpnext.selling.doctype.sales_order.sales_order import SalesOrder

class SalesOrder(SalesOrder):

    def validate(self):
        super().validate()
        self.set_items_missing_values()

    def set_items_missing_values(self):
        for row in self.items:
            row.po_no = self.po_no