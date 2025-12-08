import frappe
from frappe import _

@frappe.whitelist()
def get_pending_loan_applications():
    """
    API endpoint for banks to get pending loan applications for approval.
    Returns list of applications in "Pending_Bank_Review" state.
    
    Usage:
    GET /api/method/your_app.api.bank_api.get_pending_loan_applications
    """
    
    user = frappe.session.user
    
    try:
        applications = frappe.get_all(
            "Loan Application",
            filters={
                "custom_bank_approval_status": "Pending Bank Review",
                "docstatus": 1
            },
            fields=[
                "name",
                "applicant",
                "loan_product",
                "loan_amount",
                "rate_of_interest",
                "posting_date",
                "custom_bank_approval_status"
            ],
            order_by="creation desc"
        )
        
        return {
            "success": True,
            "user": user,
            "total_applications": len(applications),
            "applications": applications
        }
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Bank API - Get Pending Applications")
        return {
            "success": False,
            "error": str(e)
        }



@frappe.whitelist()
def approve_loan_application():
    """
    API endpoint for banks to approve or reject a loan application.
    Changes the application custom_bank_approval_status from "Pending_Bank_Review" to "Bank_Approved" or "Bank_Rejected"
    
    Parameters:
    - application_id: ID of the Loan Application to approve/reject
    - action: "approve" or "reject"
    - comments: Optional comments from the bank
    
    Usage:
    POST /api/method/your_app.api.bank_api.approve_loan_application
    
    Body (JSON):
    {
        "application_id": "LOAN-APP-2025-00001",
        "action": "approve",
        "comments": "All checks passed"
    }
    """
    
    try:
        # Get request data
        data = frappe.local.form_dict
        application_id = data.get("application_id")
        action = data.get("action")  # "approve" or "reject"
        comments = data.get("comments", "")
        
        # Validate inputs
        if not application_id:
            frappe.throw(_("application_id is required"))
        
        if action not in ["approve", "reject"]:
            frappe.throw(_("action must be 'approve' or 'reject'"))
        
        # Get the loan application
        application = frappe.get_doc("Loan Application", application_id)
        
        # Check if application exists and is in correct state
        if application.docstatus != 1:
            frappe.throw(_(
                f"Application {application_id} is not submitted. "
                f"Current docstatus: {application.docstatus}"
            ))
        
        if application.custom_bank_approval_status != "Pending Bank Review":
            frappe.throw(_(
                f"Application {application_id} is not in 'Pending Bank Review' state. "
                f"Current status: {application.custom_bank_approval_status}"
            ))
        
        # Get current user (bank user)
        user = frappe.session.user
        
        # Update application based on action
        if action == "approve":
            application.custom_bank_approval_status = "Approved by Bank"
            message = " Application approved successfully"
            comment_text = f"Approved by Bank ({user}): {comments}"
            
        else:  # reject
            application.custom_bank_approval_status = "Rejected by Bank"
            message = " Application rejected"
            comment_text = f"Rejected by Bank ({user}): {comments}"
        
        # Add comment to track who approved/rejected and when
        application.add_comment("Comment", comment_text)
        
        # Save with ignore_permissions since bank API user might not have direct edit permission
        application.save(ignore_permissions=True)
        
        return {
            "success": True,
            "message": message,
            "application_id": application_id,
            "new_status": application.custom_bank_approval_status,
            "approved_by": user,
            "timestamp": frappe.utils.now()
        }
    
    except frappe.ValidationError as e:
        frappe.log_error(frappe.get_traceback(), "Bank API - Approve Application")
        return {
            "success": False,
            "error": str(e),
            "error_type": "ValidationError"
        }
    except frappe.DoesNotExistError as e:
        frappe.log_error(frappe.get_traceback(), "Bank API - Approve Application")
        return {
            "success": False,
            "error": f"Application not found: {application_id}",
            "error_type": "DoesNotExistError"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Bank API - Approve Application")
        return {
            "success": False,
            "error": str(e),
            "error_type": "UnexpectedError"
        }



@frappe.whitelist()
def get_pending_disbursements():
    """
    API endpoint for banks to get pending disbursements awaiting confirmation.
    Returns list of disbursements that need bank confirmation.
    """
    
    user = frappe.session.user
    
    try:
        disbursement_filters = {
            "custom_bank_confirmation_status": "Pending Confirmation",
            "docstatus": 0
        }
        
        disbursements = frappe.get_all(
            "Loan Disbursement",
            filters=disbursement_filters,
            fields=[
                "name",
                "against_loan",
                "applicant_type",
                "applicant",
                "disbursement_date",
                "disbursed_amount",
                "custom_bank_confirmation_status",
                "docstatus"
            ],
            order_by="creation desc"
        )
        
        # Enrich with loan info
        for d in disbursements:
            loan = frappe.get_doc("Loan", d.against_loan)
            d["applicant_name"] = loan.applicant_name
        
        return {
            "success": True,
            "user": user,
            "total_disbursements": len(disbursements),
            "disbursements": disbursements
        }
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Bank API - Get Pending Disbursements")
        return {
            "success": False,
            "error": str(e)
        }



@frappe.whitelist()
def confirm_disbursement():
    """
    API endpoint for banks to confirm loan disbursement.
    Called after bank has transferred money to customer.
    
    Parameters:
    - disbursement_id: ID of the Loan Disbursement
    - bank_reference: Bank's transaction reference number
    - disbursed_amount: Amount actually disbursed
    - comments: Optional comments from the bank
    """
    
    try:
        # Get request data
        data = frappe.local.form_dict
        disbursement_id = data.get("disbursement_id")
        bank_reference = data.get("bank_reference")
        disbursed_amount = data.get("disbursed_amount")
        comments = data.get("comments", "")
        
        # Validate inputs
        if not disbursement_id:
            frappe.throw(_("disbursement_id is required"))
        
        if not bank_reference:
            frappe.throw(_("bank_reference is required"))
        
        # Get the disbursement document
        disbursement = frappe.get_doc("Loan Disbursement", disbursement_id)
        
        user = frappe.session.user
        
        # Update disbursement status
        disbursement.custom_bank_confirmation_status = "Confirmed by Bank"
        disbursement.custom_bank_reference = bank_reference
        disbursement.custom_bank_confirmation_timestamp = frappe.utils.now()
        
        disbursement.add_comment("Comment", 
            f"Confirmed by {user}\nBank Reference: {bank_reference}\nAmount: {disbursed_amount}\n{comments}")
        
        disbursement.save(ignore_permissions=True)
        
        return {
            "success": True,
            "message": "Disbursement confirmed successfully",
            "disbursement_id": disbursement_id,
            "bank_reference": bank_reference,
            "disbursed_amount": disbursed_amount,
            "new_status": disbursement.custom_bank_confirmation_status,
            "confirmed_by": user,
            "timestamp": frappe.utils.now()
        }
    
    except frappe.DoesNotExistError:
        frappe.log_error(frappe.get_traceback(), "Bank API - Confirm Disbursement")
        return {
            "success": False,
            "error": f"Disbursement not found: {disbursement_id}",
            "error_type": "DoesNotExistError"
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Bank API - Confirm Disbursement")
        return {
            "success": False,
            "error": str(e),
            "error_type": "UnexpectedError"
        }