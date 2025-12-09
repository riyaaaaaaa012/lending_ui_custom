import frappe
from frappe import _

def on_loan_application_submit(doc, method):
    """
    When application is submitted, set initial workflow state.
    """
    
    doc.custom_bank_approval_status = "Pending Bank Review"
    doc.db_set('custom_bank_approval_status', 'Pending Bank Review')
    
    frappe.msgprint(
        _(" Application submitted. Waiting for bank review."),
        alert=True
    )