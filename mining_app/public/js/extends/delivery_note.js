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