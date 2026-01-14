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
        child_columns: ["item_code", "item_name", "qty"],
        select_child_items: true
    });
}