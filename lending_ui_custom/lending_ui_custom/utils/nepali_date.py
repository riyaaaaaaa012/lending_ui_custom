import frappe

# BS-AD conversion lookup table (simplified version)
# For production, use a proper library like nepali-datetime
BS_AD_CONVERSION = {
    # Format: (BS_year, BS_month): (days_in_month, AD_year, AD_month, AD_day_of_first)
    # This is a simplified example - you'll need the complete conversion table
}

def ad_to_bs(ad_date_str):
    """
    Convert AD date to BS date
    Args:
        ad_date_str: Date string in format 'YYYY-MM-DD'
    Returns:
        BS date string in format 'YYYY-MM-DD (BS)'
    """
    try:
        from datetime import datetime
        
        # Parse AD date
        ad_date = datetime.strptime(str(ad_date_str), '%Y-%m-%d')
        
        # Simple conversion logic (placeholder)
        # For accurate conversion, use a library or complete lookup table
        bs_year = ad_date.year + 56  # Approximate BS year (off by ~1)
        bs_month = ad_date.month
        bs_day = ad_date.day
        
        # Format BS date
        return f"{bs_year:04d}-{bs_month:02d}-{bs_day:02d}"
        
    except Exception as e:
        frappe.log_error(f"Error converting AD to BS: {str(e)}")
        return ad_date_str


def bs_to_ad(bs_date_str):
    """
    Convert BS date to AD date
    Args:
        bs_date_str: Date string in format 'YYYY-MM-DD'
    Returns:
        AD date string in format 'YYYY-MM-DD'
    """
    try:
        from datetime import datetime
        
        # Parse BS date
        parts = str(bs_date_str).split('-')
        bs_year = int(parts[0])
        bs_month = int(parts[1])
        bs_day = int(parts[2])
        
        # Simple conversion (placeholder)
        ad_year = bs_year - 56
        ad_month = bs_month
        ad_day = bs_day
        
        return f"{ad_year:04d}-{ad_month:02d}-{ad_day:02d}"
        
    except Exception as e:
        frappe.log_error(f"Error converting BS to AD: {str(e)}")
        return bs_date_str


@frappe.whitelist()
def get_bs_date(ad_date):
    """
    API endpoint to get BS date from AD date
    """
    return {
        "ad_date": ad_date,
        "bs_date": ad_to_bs(ad_date)
    }