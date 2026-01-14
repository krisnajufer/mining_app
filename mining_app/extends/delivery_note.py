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

    return query.run(debug=True)