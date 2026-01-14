import frappe

@frappe.whitelist()
def get_default_price_list(unit_code, customer):
    filters = {
        "enabled": 1,
        "name": f"{unit_code} - {customer}"
    }

    price_list_name = frappe.db.get_value("Price List", filters, "price_list_name")

    return price_list_name

@frappe.whitelist()
def filter_item_customer(doctype, txt, searchfield, start, page_len, filters):
    customer_item_preference = frappe.qb.DocType("Customer Item Preference")
    txt = f"%{txt}%"
    query = (
        frappe.qb.from_(customer_item_preference)
        .select(customer_item_preference.item_code.as_("value"), customer_item_preference.item_name.as_("text"))
        .where(
            (customer_item_preference.parent == filters.get("customer")) 
            & (customer_item_preference.unit_code == filters.get("unit_code"))
        )
        .where(
            (customer_item_preference.item_code.like(txt)) 
            | (customer_item_preference.item_name.like(txt)) 
            | (customer_item_preference.item_alias.like(txt)))
    )

    return query.run(debug=False)

@frappe.whitelist()
def get_customer_item_alias(unit_code:str, customer:str, item_code:str):
    filters = {
        "parent": customer,
        "unit_code": unit_code,
        "item_code": item_code
    }

    item_alias = frappe.db.get_value("Customer Item Preference", filters, "item_alias")

    return item_alias