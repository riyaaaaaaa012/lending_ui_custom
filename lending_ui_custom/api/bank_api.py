
import frappe
from frappe import _

@frappe.whitelist()
def get_pending_loans():
    """
    API endpoint for banks to get their pending loans for approval.
    Returns list of loans assigned to the bank that need review.
    """
    
    # Get current user
    user = frappe.session.user
    
    # Option 1: If user has a specific role, get their assigned Loan Partner
    # For now, we'll let the user pass the loan_partner as a parameter
    # Or we can map users to loan partners
    
    # Get loan_partner from User defaults or custom field
    # For testing, let's get all loan partners the user has access to
    
    # Simple approach: Get user's allowed Loan Partners based on User Permission
    allowed_partners = frappe.get_all(
        "User Permission",
        filters={
            "user": user,
            "allow": "Loan Partner"
        },
        fields=["for_value"]
    )
    
    # If no specific permissions, user can see all (for Admin)
    if not allowed_partners:
        # Get all pending loans (Admin view)
        loans = frappe.get_all(
            "Loan",
            filters={
                "custom_bank_approval_status": "Pending Bank Review",
                "docstatus": 0  # Draft loans only
            },
            fields=[
                "name",
                "applicant",
                "applicant_name",
                "loan_amount",
                "rate_of_interest",
                "repayment_method",
                "posting_date",
                "status",
                "loan_partner",
                "custom_bank_approval_status"
            ],
            order_by="creation desc"
        )
        
        return {
            "success": True,
            "user": user,
            "loan_partner": "All (Admin access)",
            "total_loans": len(loans),
            "loans": loans
        }
    
    # Get loans for specific partners
    partner_names = [p.for_value for p in allowed_partners]
    
    loans = frappe.get_all(
        "Loan",
        filters={
            "loan_partner": ["in", partner_names],
            "custom_bank_approval_status": "Pending Bank Review",
            "docstatus": 0  # Draft loans only
        },
        fields=[
            "name",
            "applicant",
            "applicant_name",
            "loan_amount",
            "rate_of_interest",
            "repayment_method",
            "posting_date",
            "status",
            "loan_partner",
            "custom_bank_approval_status"
        ],
        order_by="creation desc"
    )
    
    return {
        "success": True,
        "user": user,
        "loan_partners": partner_names,
        "total_loans": len(loans),
        "loans": loans
    }



@frappe.whitelist()
def approve_loan():
    """
    API endpoint for banks to approve or reject loans.
    Updates the loan status and triggers next workflow steps.
    """
    
    # Get request data
    data = frappe.local.form_dict
    loan_id = data.get("loan_id")
    action = data.get("action")  # "approve" or "reject"
    comments = data.get("comments", "")
    
    # Validate inputs
    if not loan_id:
        frappe.throw(_("loan_id is required"))
    
    if action not in ["approve", "reject"]:
        frappe.throw(_("action must be 'approve' or 'reject'"))
    
    # Get the loan document
    loan = frappe.get_doc("Loan", loan_id)
    
    # Security check: Verify user has access to this loan's partner
    user = frappe.session.user
    allowed_partners = frappe.get_all(
        "User Permission",
        filters={
            "user": user,
            "allow": "Loan Partner"
        },
        fields=["for_value"]
    )
    
    # Admin can access all, others need permission
    if allowed_partners:
        partner_names = [p.for_value for p in allowed_partners]
        if loan.loan_partner not in partner_names:
            frappe.throw(_("You don't have permission to access this loan"))
    
    # Update loan based on action
    if action == "approve":
        loan.custom_bank_approval_status = "Approved by Bank"
        loan.add_comment("Comment", f"Approved by {user}: {comments}")
        
        # Optionally auto-submit the loan
        # loan.submit()
        
        message = "Loan approved successfully"
    else:  # reject
        loan.custom_bank_approval_status = "Rejected by Bank"
        loan.add_comment("Comment", f"Rejected by {user}: {comments}")
        message = "Loan rejected"
    
    loan.save(ignore_permissions=True)
    
    return {
        "success": True,
        "message": message,
        "loan_id": loan_id,
        "new_status": loan.custom_bank_approval_status,
        "approved_by": user,
        "timestamp": frappe.utils.now()
    }



@frappe.whitelist()
def confirm_disbursement():
    """
    API endpoint for banks to confirm loan disbursement.
    Called after bank has transferred money to customer.
    """
    
    # Get request data
    data = frappe.local.form_dict
    disbursement_id = data.get("disbursement_id")
    bank_reference = data.get("bank_reference")  # Bank's transaction ID
    disbursed_amount = data.get("disbursed_amount")
    comments = data.get("comments", "")
    
    # Validate inputs
    if not disbursement_id:
        frappe.throw(_("disbursement_id is required"))
    
    if not bank_reference:
        frappe.throw(_("bank_reference is required"))
    
    # Get the disbursement document
    disbursement = frappe.get_doc("Loan Disbursement", disbursement_id)
    
    # Get related loan for security check
    loan = frappe.get_doc("Loan", disbursement.against_loan)
    
    # Security check: Verify user has access to this loan's partner
    user = frappe.session.user
    allowed_partners = frappe.get_all(
        "User Permission",
        filters={
            "user": user,
            "allow": "Loan Partner"
        },
        fields=["for_value"]
    )
    
    # Admin can access all, others need permission
    if allowed_partners:
        partner_names = [p.for_value for p in allowed_partners]
        if loan.loan_partner not in partner_names:
            frappe.throw(_("You don't have permission to access this disbursement"))
    
    # Update disbursement status
    disbursement.custom_bank_confirmation_status = "Confirmed by Bank"
    disbursement.add_comment("Comment", 
        f"Disbursement confirmed by {user}\nBank Reference: {bank_reference}\n{comments}")
    
    # Optionally submit the disbursement
    # disbursement.submit()
    
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



@frappe.whitelist()
def get_pending_disbursements():
    """
    API endpoint for banks to get pending disbursements awaiting confirmation.
    Returns list of disbursements that need bank confirmation.
    """
    
    # Get current user
    user = frappe.session.user
    
    # Get user's allowed Loan Partners based on User Permission
    allowed_partners = frappe.get_all(
        "User Permission",
        filters={
            "user": user,
            "allow": "Loan Partner"
        },
        fields=["for_value"]
    )
    
    # Build filters
    disbursement_filters = {
        "custom_bank_confirmation_status": "Pending Confirmation",
        "docstatus": 0  # Draft disbursements only
    }
    
    # If user has specific permissions, filter by loan partner
    if allowed_partners:
        partner_names = [p.for_value for p in allowed_partners]
        
        # Get loans for these partners
        loans = frappe.get_all(
            "Loan",
            filters={"loan_partner": ["in", partner_names]},
            fields=["name"]
        )
        loan_names = [loan.name for loan in loans]
        
        disbursement_filters["against_loan"] = ["in", loan_names]
    
    # Get disbursements
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
    
    # Enrich with loan partner info
    for d in disbursements:
        loan_partner = frappe.db.get_value("Loan", d.against_loan, "loan_partner")
        d["loan_partner"] = loan_partner
    
    return {
        "success": True,
        "user": user,
        "total_disbursements": len(disbursements),
        "disbursements": disbursements
    }