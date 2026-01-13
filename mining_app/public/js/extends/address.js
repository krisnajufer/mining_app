frappe.ui.form.on("Address", {
    city_id(frm){
        setCity(frm)
    }
})

function setCity(frm) {
    let city_id = frm.doc.city_id;
    if (!city_id) return
    frm.set_value("city", city_id);
    frm.refresh_field("city")
}