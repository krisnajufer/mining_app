import frappe

@frappe.whitelist()
def filter_sales_order_customer(doctype, txt, searchfield, start, page_len, filters):
    txt = f"%{txt}%"
    not_status =  ["Closed", "On Hold"]

    sales_order = frappe.qb.DocType("Sales Order")
    query = (
        frappe.qb.from_(sales_order)
        .select(sales_order.name.as_("value"), sales_order.po_no.as_("text"))
        .where(
            (sales_order.unit_code == filters.get("unit_code"))
            & (sales_order.customer == filters.get("customer"))
            & (sales_order.per_delivered < 99.99)
            & (sales_order.status.notin(not_status))
            & (sales_order.docstatus == 1)
        )
        .where(
            (sales_order.name.like(txt))
            | (sales_order.po_no.like(txt))
        )
    )

    return query.run(debug=False)

def make_ste_receipt(self, method):
    if self.stock_entry:
        return
    
    values = {
        "doctype": "Stock Entry",
        "stock_entry_type": "Material Receipt",
        "company": self.company,
        "posting_date": self.posting_date,
        "posting_time": self.posting_time,
        "unit_code": self.unit_code,
        "to_warehouse": self.set_warehouse,
        "delivery_note": self.name
    }

    ste = frappe.get_doc(values)
    for row in self.items:
        ste.append("items", {
            "item_code": row.item_code,
            "item_name": row.item_name,
            "uom": row.uom,
            "stock_uom": row.uom,
            "qty": row.qty,
            "conversion_factor": 1,
            "t_warehouse": row.warehouse,
            "basic_rate": row.rate,
            "cost_center": self.cost_center
        })
    ste.insert(ignore_permissions=True)
    ste.submit()

    self.stock_entry = ste.name

def cancel_ste_receipt(self, method):
    if not self.stock_entry and self.docstatus == 2:
        return
    
    frappe.get_doc("Stock Entry", self.stock_entry).cancel()