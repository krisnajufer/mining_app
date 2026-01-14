
import frappe

def get_active_company():
    company = frappe.defaults.get_user_default("Company")

    if not company:
        company = frappe.db.get_single_value(
            "Global Defaults",
            "default_company"
        )

    if not company:
        frappe.throw("Company is not configured")

    return company
