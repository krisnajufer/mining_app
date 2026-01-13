import frappe
from frappe.utils import nowdate

def process_price_customer(self, method):
    process_price_list(self.name, self.customer_item_preference)
    process_item_price(self.name, self.customer_item_preference)

def process_price_list(customer_name:str, customer_item_preference:list) -> None:
    make_price_list(customer_name, customer_item_preference)
    enabled_price_list(customer_name, customer_item_preference)
    disabled_price_list(customer_name, customer_item_preference, True)

def price_list_not_exist(customer_name:str, customer_item_preference:list , disabled:bool = False) -> list[str]:
    check_pl = []
    pl_not_exist = []
    for row in customer_item_preference:
        check_pl.append(f"{row.unit_code} - {customer_name}")
    
    price_list = frappe.qb.DocType("Price List")

    query = (
        frappe.qb.from_(price_list)
        .select(price_list.price_list_name)
    )

    if disabled:
        query = (query.where(price_list.customer == customer_name))
        existing = query.run(pluck=True, debug=False)
        pl_not_exist = list(set(existing) - set(check_pl))
    else:
        query = (query.where(price_list.price_list_name.isin(check_pl)))
        existing = query.run(pluck=True, debug=False)
        pl_not_exist = list(set(check_pl) - set(existing))
    
    return pl_not_exist

def make_price_list(customer_name:str, customer_item_preference:list) -> None:
    pl_to_create  = price_list_not_exist(customer_name, customer_item_preference)
    if not pl_to_create :
        return
    currency = frappe.db.get_single_value("Global Defaults", "default_currency")
    for val in pl_to_create : 
        doc = frappe.new_doc("Price List")
        doc.enabled = 1
        doc.price_list_name = val
        doc.currency = currency
        doc.selling = 1
        doc.unit_code = val.split(" - ")[0]
        doc.customer = customer_name
        doc.insert(ignore_permissions=True)

def disabled_price_list(customer_name:str, customer_item_preference:list , disabled:bool = False) -> None:
    pl_to_disabled = price_list_not_exist(customer_name, customer_item_preference, True)
    if not pl_to_disabled:
        return
    for val in pl_to_disabled:
        doc = frappe.get_doc("Price List", val)
        doc.enabled = 0
        doc.save()

def enabled_price_list(customer_name:str, customer_item_preference:list) -> None:
    for row in customer_item_preference:
        price_list_name = f"{row.unit_code} - {customer_name}"
        price_list = frappe.db.get_value("Price List", {"name":price_list_name, "enabled": 0}, "*", as_dict=True)
        if not price_list:
            continue
        frappe.db.set_value("Price List", price_list.name, "enabled", 1)

def process_item_price(customer_name:str, customer_item_preference:list):
    for row in customer_item_preference:
        filters = {
            "item_code": row.item_code,
            "unit_code": row.unit_code,
            "customer": customer_name,
            "price_list": f"{row.unit_code} - {customer_name}",
            "selling": 1,
        }
        price_list = frappe.db.get_value("Price List", {"name": filters["price_list"], "enabled": 1}, "*", as_dict=True)
        if not price_list:
            continue

        item_price_name = frappe.db.get_value("Item Price", filters, "name")
        if item_price_name:
            doc = frappe.get_doc("Item Price", item_price_name)
            doc.price_list_rate = row.item_price
            doc.save()
        else:
            currency = frappe.db.get_single_value("Global Defaults", "default_currency")
            stock_uom = frappe.db.get_value("Item", row.item_code, "stock_uom")
            doc = frappe.new_doc("Item Price")
            doc.unit_code = row.unit_code
            doc.item_code = row.item_code
            doc.uom = stock_uom
            doc.price_list = price_list.name
            doc.selling = 1
            doc.price_list_rate = row.item_price
            doc.currency = currency
            doc.valid_from = nowdate()
            doc.customer = customer_name
            doc.insert(ignore_permissions=True)
