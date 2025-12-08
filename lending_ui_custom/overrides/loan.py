import frappe
from frappe import _

# def validate_loan_before_submit(doc, method):
#     """
#     BLOCK loan submission until bank approves.
#     This enforces the bank approval workflow.
#     """
    
#     # Check if bank has approved
#     if hasattr(doc, 'custom_bank_approval_status'):
        
#         if doc.custom_bank_approval_status == "Approved by Bank":
#             #  Bank approved - allow submission
#             return
        
#         elif doc.custom_bank_approval_status == "Rejected by Bank":
#             #  Bank rejected - block with clear message
#             frappe.throw(_(
#                 "Cannot submit loan. Bank has REJECTED this application."
#             ))
        
#         else:
#             #  Still pending - block submission
#             frappe.throw(_(
#                 f"Cannot submit loan. Waiting for bank approval.\n\n"
#                 f"Current Status: {doc.custom_bank_approval_status}\n"
#                 f"Loan Partner: {doc.loan_partner}\n\n"
#                 f"Please wait for the bank to review and approve via API."
#             ))
    
#     else:
#         # Field doesn't exist - something wrong
#         frappe.throw(_("Cannot submit loan. Bank approval field not configured."))



def validate_disbursement_before_submit(doc, method):
    """
    BLOCK disbursement submission until bank confirms money transfer.
    """
    
    if hasattr(doc, 'custom_bank_confirmation_status'):
        
        if doc.custom_bank_confirmation_status == "Confirmed by Bank":
            # Bank confirmed - allow submission
            return
        
        elif doc.custom_bank_confirmation_status == "Rejected by Bank":
            # Bank rejected disbursement
            frappe.throw(_(
                "Cannot submit disbursement. Bank has REJECTED this transfer."
            ))
        
        else:
            # Still pending
            frappe.throw(_(
                f"Cannot submit disbursement. Waiting for bank confirmation.\n\n"
                f"Current Status: {doc.custom_bank_confirmation_status}\n"
                f"Disbursed Amount: {doc.disbursed_amount}\n\n"
                f"Bank must transfer funds and call confirm_disbursement API."
            ))
    
    else:
        frappe.throw(_("Cannot submit disbursement. Bank confirmation field not configured."))



def prevent_loan_creation_without_approval(doc, method):
    """
    When creating a Loan, ensure Application is "Bank Approved".
    This validates BEFORE Loan is saved.
    """
    
    if not doc.loan_application:
        return
    
    application = frappe.get_doc("Loan Application", doc.loan_application)
    
    # Check if application is submitted
    if application.docstatus != 1:
        frappe.throw(_(
            "Loan Application must be submitted first."
        ))
    
    # Check if bank approved - use correct field name and value
    if application.custom_bank_approval_status != "Approved by Bank":
        frappe.throw(_(
            f"Cannot create Loan.\n\n"
            f"Bank Approval Status: {application.custom_bank_approval_status}\n\n"
            f"Loan can only be created when status is 'Approved by Bank'."
        ))