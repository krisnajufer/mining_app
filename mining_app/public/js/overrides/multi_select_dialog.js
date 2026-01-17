frappe.ui.form.MultiSelectDialog = class CustomMultiSelectDialog extends frappe.ui.form.MultiSelectDialog {
	async add_parent_filters(filters) {
		const parent_names = await this.get_filtered_parents_for_child_search();
		if (parent_names.length) {
			filters.push(["parent", "in", parent_names]);
		}

		return parent_names
	}
    async get_child_result() {
		let filters = [["parentfield", "=", this.child_fieldname]];

		const parent_filters = await this.add_parent_filters(filters);
		this.add_custom_child_filters(filters);
		
        if (this.get_query().filters && parent_filters.length < 1) {
			return []
		}
        
		return frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: this.child_doctype,
				filters: filters,
				fields: ["name", "parent", ...this.child_columns],
				parent: this.doctype,
				limit_page_length: this.child_page_length + 5,
				order_by: "parent",
			},
		});
	}
}