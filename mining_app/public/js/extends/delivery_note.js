frappe.ui.form.on("Delivery Note", {
    refresh(frm){
        filterUnit(frm);
        filterUnitTerritory(frm);
        filterSalesOrder(frm);
    },
    company(frm){
        filterUnit(frm);
    },
    unit(frm){
        filterUnitTerritory(frm);
        filterSalesOrder(frm);
    },
    customer(frm){
        filterSalesOrder(frm);
    },
    sales_order(frm){
        showDialogPickSO(frm);
    },
    is_internal_delivery_note(frm){
        showDialogPickDNI(frm);
    }
})

function filterUnit(frm){
    frm.set_query("unit_code", (doc) => {
        return {
            filters : {
                company : ["=", doc.company],
                is_active: ["=", 1]
            }
        }
    })
}

function filterUnitTerritory(frm){
    frm.set_query("unit_territory", (doc) => {
        return {
            filters : {
                unit_code : ["=", doc.unit_code],
                is_active: ["=", 1]
            }
        }
    })
}

function filterSalesOrder(frm) {
    frm.set_query("sales_order", (doc) => {
        return {
            query: "mining_app.extends.delivery_note.filter_sales_order_customer",
            filters: {
                unit_code: doc.unit_code,
                customer: doc.customer
            }
        }
    })
}

function showDialogPickSO(frm) {
    if (!frm.doc.sales_order) {
        return
    }
    erpnext.utils.map_current_doc({
        method: "erpnext.selling.doctype.sales_order.sales_order.make_delivery_note",
        args: {
            for_reserved_stock: 1,
        },
        source_doctype: "Sales Order",
        target: frm,
        setters: {
            customer: frm.doc.customer
        },
        get_query_filters: {
            docstatus: 1,
            name: frm.doc.sales_order
        },
        allow_child_item_selection: true,
        child_fieldname: "items",
        child_columns: ["item_code", "item_name", "qty"]
    });
}

function showDialogPickDNI(frm) {
    if (!frm.doc.is_internal_delivery_note) {
        return
    }
    erpnext.utils.map_current_doc({
        method: "mining_app.mining_selling.doctype.delivery_note_internal.delivery_note_internal.make_delivery_note",
        args: {
            for_reserved_stock: 1,
        },
        source_doctype: "Delivery Note Internal",
        target: frm,
        setters: {
            customer: frm.doc.customer
        },
        get_query_filters: {
            docstatus: 1,
            sales_order: frm.doc.sales_order
        },
        allow_child_item_selection: true,
        child_fieldname: "items",
        child_columns: ["po_customer_no", "delivery_no", "item_code", "item_name", "qty"],
    });
}