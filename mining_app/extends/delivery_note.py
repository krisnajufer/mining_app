import frappe

@frappe.whitelist()
def filter_sales_order_customer(doctype, txt, searchfield, start, page_len, filters):
    sales_order = frappe.qb.DocType("Sales Order")
    txt = f"%{txt}%"

    query = (
        frappe.qb.from_(sales_order)
        .select(sales_order.name.as_("value"), sales_order.po_no.as_("text"))
        .where(
            (sales_order.unit_code == filters.get("unit_code"))
            & (sales_order.customer == filters.get("customer"))
            & (sales_order.per_delivered < 100)
        )
        .where(
            (sales_order.name.like(txt))
            | (sales_order.po_no.like(txt))
        )
    )

    return query.run(debug=True)