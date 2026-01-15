import frappe

from erpnext.stock.doctype.delivery_note.delivery_note import DeliveryNote

class DeliveryNote(DeliveryNote):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_updater.append(
            {
                "source_dt": "Delivery Note Item",
                "target_dt": "Delivery Note Internal Item",
                "join_field": "dn_internal_detail",
                "target_field": "delivered_qty",
                "target_parent_dt": "Delivery Note Internal",
                "target_parent_field": "per_delivered",
                "target_ref_field": "qty",
                "source_field": "qty",
                "percent_join_field": "against_delivery_note_internal",
                "status_field": "delivery_status",
                "keyword": "Delivered",
                "overflow_type": "delivery",
            }
        )