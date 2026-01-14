frappe.ui.form.on("Delivery Note", {
    refresh(frm){
        filterUnit(frm);
        filterUnitTerritory(frm);
    },
    company(frm){
        filterUnit(frm);
    },
    unit(frm){
        filterUnitTerritory(frm);
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