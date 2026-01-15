from frappe import _


def get_data():
	return {
		"fieldname": "delivery_note_internal",
		# "non_standard_fieldnames": {
		# 	"Stock Entry": "delivery_note_no",
		# 	"Quality Inspection": "reference_name",
		# 	"Auto Repeat": "reference_document",
		# 	"Purchase Receipt": "inter_company_reference",
		# },
		"internal_links": {
			"Sales Order": ["items", "against_sales_order"],
		},
		"transactions": [
			{"label": _("Reference"), "items": ["Sales Order"]},
		],
	}
