frappe.ui.form.on("Sales Order", {
    refresh(frm){
        setDefaultPriceList(frm, frm.doc.unit_code, frm.doc.customer);
        filterItemCustomer(frm);
    },

    unit_code(frm){
        setDefaultPriceList(frm, frm.doc.unit_code, frm.doc.customer);
        filterItemCustomer(frm);
    },

    customer(frm){
        setDefaultPriceList(frm, frm.doc.unit_code, frm.doc.customer);
        filterItemCustomer(frm);
    }
})

frappe.ui.form.on("Sales Order Item", {
    item_code(frm, cdt, cdn){
        setItemAlias(frm, cdt, cdn);
    }
})

async function setDefaultPriceList(frm, unit_code, customer) {
    if (!unit_code || !customer) {
        return false;
    }

    let resDefaultPriceList = await frappe.call({
        method: 'mining_app.extends.sales_order.get_default_price_list',
        args: {
            unit_code,
            customer
        }
    });

    if (resDefaultPriceList.message) {
        frm.set_value("selling_price_list", resDefaultPriceList.message);
        frm.refresh_field("selling_price_list")
    }
}

function filterItemCustomer(frm){
    frm.set_query("item_code", "items", (doc) => {
        return {
            query: "mining_app.extends.sales_order.filter_item_customer",
            filters: {
                unit_code: doc.unit_code,
                customer: doc.customer
            }
        }
    })
}

async function setItemAlias(frm, cdt, cdn) {
    const curRow = locals[cdt][cdn]
    let unitCode = frm.doc.unit_code;
    let customer = frm.doc.customer;
    let itemCode = curRow.item_code
    if (!unitCode || !customer || !itemCode) {
        return false;
    }

    let resItemAlias = await frappe.call({
        method: 'mining_app.extends.sales_order.get_customer_item_alias',
        args: {
            unit_code : unitCode,
            customer: customer,
            item_code: itemCode
        }
    });

    if (resItemAlias.message) {
        frappe.model.set_value(cdt, cdn, "customer_item_name", resItemAlias.message);
        frm.refresh_field("items");
    }
}
