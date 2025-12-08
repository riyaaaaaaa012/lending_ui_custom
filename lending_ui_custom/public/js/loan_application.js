frappe.ui.form.on('Loan Application', {
    refresh: function(frm) {
        // Show "Create Loan" button only when status is "Approved by Bank"
        if (frm.doc.bank_approval_status === "Approved by Bank") {
            frm.add_custom_button(__('Create Loan'), function() {
                create_loan_from_application(frm);
            }, __('Actions'));
        }
    }
});

function create_loan_from_application(frm) {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Loan',
            filters: {
                loan_application: frm.doc.name
            },
            fields: ['name']
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                frappe.msgprint({
                    title: __('Already Exists'),
                    message: __('Loan {0} already exists for this application', [r.message[0].name]),
                    indicator: 'orange'
                });
                return;
            }
            
            frappe.call({
                method: 'frappe.client.insert',
                args: {
                    doc: {
                        doctype: 'Loan',
                        applicant_type: frm.doc.applicant_type,
                        applicant: frm.doc.applicant,
                        loan_product: frm.doc.loan_product,
                        loan_amount: frm.doc.loan_amount,
                        rate_of_interest: frm.doc.rate_of_interest,
                        repayment_method: frm.doc.repayment_method,
                        repayment_periods: frm.doc.repayment_periods,
                        monthly_repayment_amount: frm.doc.monthly_repayment_amount,
                        loan_application: frm.doc.name
                    }
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint({
                            title: __('Success'),
                            message: __('Loan {0} created successfully', [r.message.name]),
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    }
                }
            });
        }
    });
}