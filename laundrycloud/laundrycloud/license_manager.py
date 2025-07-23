# Copyright (c) 2025, LaundryCloud and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate, get_datetime

def validate_license():
    """Main license validation function"""
    try:
        # Check if license exists and is valid
        license_doc = get_active_license()
        
        if not license_doc:
            return {
                "valid": False,
                "message": "No valid license found",
                "show_trial_option": True
            }
        
        # Validate license
        if license_doc.validate_offline():
            return {
                "valid": True,
                "license_type": license_doc.license_type,
                "expiry_date": license_doc.expiry_date,
                "features": {
                    "pos_enabled": license_doc.pos_enabled,
                    "delivery_enabled": license_doc.delivery_enabled,
                    "reports_enabled": license_doc.reports_enabled
                }
            }
        else:
            return {
                "valid": False,
                "message": "License expired or invalid",
                "show_purchase_option": True
            }
            
    except Exception as e:
        frappe.log_error(f"License validation error: {str(e)}")
        return {
            "valid": False,
            "message": "License validation failed"
        }

def get_active_license():
    """Get active license for current site"""
    site_url = frappe.local.site
    
    # Try to find active license
    license_name = frappe.db.get_value("LaundryCloud License", {
        "site_url": ["like", f"%{site_url}%"],
        "status": ["in", ["Active", "Trial"]]
    }, "name")
    
    if license_name:
        return frappe.get_doc("LaundryCloud License", license_name)
    
    return None

def check_feature_permission(feature):
    """Check if user has permission for specific feature"""
    license_status = validate_license()
    
    if not license_status.get("valid"):
        return False
    
    features = license_status.get("features", {})
    return features.get(f"{feature}_enabled", False)

def check_usage_limits():
    """Check if usage is within license limits"""
    license_doc = get_active_license()
    
    if not license_doc:
        return False
    
    # Check user limit
    if not license_doc.check_usage_limits("users"):
        frappe.throw(_("User limit exceeded. Please upgrade your license."))
    
    # Check order limit
    if not license_doc.check_usage_limits("orders"):
        frappe.throw(_("Monthly order limit exceeded. Please upgrade your license."))
    
    return True

def enforce_license_on_pos():
    """Enforce license check for POS access"""
    if not check_feature_permission("pos"):
        frappe.throw(_("""
        POS feature is not available in your current license. 
        Please upgrade to access this feature.
        Contact: support@laundrycloud.com
        """))

def enforce_license_on_delivery():
    """Enforce license check for delivery features"""
    if not check_feature_permission("delivery"):
        frappe.throw(_("""
        Pickup & Delivery feature is not available in your current license. 
        Please upgrade to access this feature.
        Contact: support@laundrycloud.com
        """))

def enforce_license_on_reports():
    """Enforce license check for advanced reports"""
    if not check_feature_permission("reports"):
        frappe.throw(_("""
        Advanced Reports are not available in your current license. 
        Please upgrade to access this feature.
        Contact: support@laundrycloud.com
        """))

def get_license_info_for_ui():
    """Get license information for displaying in UI"""
    license_status = validate_license()
    
    if not license_status.get("valid"):
        return {
            "valid": False,
            "message": license_status.get("message"),
            "trial_available": license_status.get("show_trial_option", False),
            "purchase_url": "https://laundrycloud.com/purchase"
        }
    
    license_doc = get_active_license()
    
    return {
        "valid": True,
        "license_type": license_doc.license_type,
        "expiry_date": license_doc.expiry_date,
        "days_remaining": (get_datetime(license_doc.expiry_date) - get_datetime()).days if license_doc.expiry_date else None,
        "features": license_status.get("features"),
        "is_trial": license_doc.is_trial,
        "upgrade_url": "https://laundrycloud.com/upgrade"
    }

def log_feature_usage(feature):
    """Log feature usage for analytics"""
    license_doc = get_active_license()
    
    if license_doc:
        license_doc.log_feature_usage(feature, frappe.session.user)

# Decorator for protecting features
def license_required(feature=None):
    """Decorator to protect functions with license check"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if feature and not check_feature_permission(feature):
                frappe.throw(_(f"License required for {feature} feature"))
            
            # Log usage
            if feature:
                log_feature_usage(feature)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator