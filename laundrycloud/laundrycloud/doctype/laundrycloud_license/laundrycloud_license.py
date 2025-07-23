# Copyright (c) 2025, LaundryCloud and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, add_days, get_datetime, now_datetime
import hashlib
import secrets
import uuid
import platform
import requests
import json

class LaundryCloudLicense(Document):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def validate(self):
        self.validate_license_data()
        self.generate_license_key()
        self.set_hardware_fingerprint()
        self.set_trial_dates()
        
    def before_save(self):
        self.generate_validation_hash()
        
    def on_submit(self):
        self.activate_license()
        
    def validate_license_data(self):
        """Validate license information"""
        if not self.site_url:
            frappe.throw(_("Site URL is required"))
            
        if not self.contact_email:
            frappe.throw(_("Contact email is required"))
            
        # Validate site URL format
        if not (self.site_url.startswith('http://') or self.site_url.startswith('https://')):
            self.site_url = 'https://' + self.site_url
            
    def generate_license_key(self):
        """Generate unique license key"""
        if not self.license_key:
            # Generate a unique license key
            prefix = "LC"
            if self.license_type == "Trial":
                prefix = "LCT"
            elif self.license_type == "Enterprise":
                prefix = "LCE"
            elif self.license_type == "Lifetime":
                prefix = "LCL"
                
            unique_id = secrets.token_hex(8).upper()
            self.license_key = f"{prefix}-{unique_id[:4]}-{unique_id[4:8]}-{unique_id[8:12]}"
            
    def set_hardware_fingerprint(self):
        """Generate hardware fingerprint for license binding"""
        if not self.hardware_fingerprint:
            # Create a unique identifier based on installation
            site_name = frappe.local.site
            installation_data = f"{self.site_url}:{site_name}:{platform.machine()}"
            self.hardware_fingerprint = hashlib.sha256(installation_data.encode()).hexdigest()[:16]
            
        if not self.installation_id:
            self.installation_id = str(uuid.uuid4())
            
    def set_trial_dates(self):
        """Set trial period dates"""
        if self.is_trial and not self.trial_start_date:
            self.trial_start_date = nowdate()
            self.trial_end_date = add_days(nowdate(), self.trial_period_days or 30)
            self.expiry_date = self.trial_end_date
            
    def generate_validation_hash(self):
        """Generate validation hash for security"""
        data = f"{self.license_key}:{self.site_url}:{self.hardware_fingerprint}"
        self.validation_hash = hashlib.sha256(data.encode()).hexdigest()
        
    def activate_license(self):
        """Activate the license"""
        self.status = "Active"
        self.activation_date = nowdate()
        
        # Generate activation code
        if not self.activation_code:
            self.activation_code = secrets.token_hex(16).upper()
            
        # Set server validation URL
        self.server_validation_url = "https://api.laundrycloud.com/validate"
        
        # Create or update license cache
        self.update_license_cache()
        
        frappe.msgprint(_("License activated successfully!"))
        
    def update_license_cache(self):
        """Update local license cache for faster validation"""
        license_cache = {
            "license_key": self.license_key,
            "status": self.status,
            "expiry_date": self.expiry_date,
            "features": {
                "pos_enabled": self.pos_enabled,
                "delivery_enabled": self.delivery_enabled,
                "reports_enabled": self.reports_enabled
            },
            "limits": {
                "max_users": self.max_users,
                "max_orders_per_month": self.max_orders_per_month
            },
            "last_validated": now_datetime()
        }
        
        # Store in site config (you might want to encrypt this)
        frappe.conf.laundrycloud_license = license_cache
        
    @frappe.whitelist()
    def validate_license_online(self):
        """Validate license with remote server"""
        try:
            validation_data = {
                "license_key": self.license_key,
                "site_url": self.site_url,
                "hardware_fingerprint": self.hardware_fingerprint,
                "validation_hash": self.validation_hash
            }
            
            # Make API call to validation server
            response = requests.post(
                self.server_validation_url,
                json=validation_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("valid"):
                    self.last_validated = now_datetime()
                    self.status = result.get("status", "Active")
                    self.save()
                    return True
                else:
                    self.status = "Suspended"
                    self.save()
                    return False
            else:
                # If server is unreachable, allow offline validation for limited time
                return self.validate_offline()
                
        except Exception as e:
            frappe.log_error(f"License validation error: {str(e)}")
            return self.validate_offline()
            
    def validate_offline(self):
        """Offline license validation"""
        # Allow offline for up to 7 days
        if self.last_validated:
            days_since_validation = (get_datetime() - get_datetime(self.last_validated)).days
            if days_since_validation > 7:
                return False
                
        # Check expiry date
        if self.expiry_date and get_datetime(self.expiry_date) < get_datetime():
            self.status = "Expired"
            self.save()
            return False
            
        return self.status == "Active"
        
    @frappe.whitelist()
    def check_feature_access(self, feature):
        """Check if a specific feature is enabled"""
        if not self.validate_offline():
            return False
            
        feature_map = {
            "pos": self.pos_enabled,
            "delivery": self.delivery_enabled,
            "reports": self.reports_enabled
        }
        
        return feature_map.get(feature, False)
        
    @frappe.whitelist()
    def check_usage_limits(self, limit_type):
        """Check usage limits"""
        if limit_type == "users":
            active_users = frappe.db.count("User", {"enabled": 1, "user_type": "System User"})
            return active_users <= self.max_users
            
        elif limit_type == "orders":
            from frappe.utils import get_first_day, get_last_day
            first_day = get_first_day(nowdate())
            last_day = get_last_day(nowdate())
            
            monthly_orders = frappe.db.count("Laundry Order", {
                "order_date": ["between", [first_day, last_day]],
                "docstatus": 1
            })
            
            return monthly_orders <= self.max_orders_per_month
            
        return True
        
    def log_feature_usage(self, feature, user):
        """Log feature usage for analytics"""
        usage_log = {
            "timestamp": now_datetime(),
            "feature": feature,
            "user": user,
            "site_url": self.site_url
        }
        
        # Append to usage log
        current_log = self.feature_usage_log or "[]"
        try:
            log_data = json.loads(current_log)
        except:
            log_data = []
            
        log_data.append(usage_log)
        
        # Keep only last 1000 entries
        if len(log_data) > 1000:
            log_data = log_data[-1000:]
            
        self.feature_usage_log = json.dumps(log_data)
        self.last_usage_date = nowdate()
        self.save()

# API Functions for License Management

@frappe.whitelist()
def get_license_status():
    """Get current license status"""
    license_doc = frappe.db.get_value("LaundryCloud License", 
        {"site_url": ["like", f"%{frappe.local.site}%"], "status": "Active"}, 
        ["name", "license_key", "status", "expiry_date", "license_type"]
    )
    
    if not license_doc:
        return {
            "valid": False,
            "status": "No License",
            "message": "No valid license found. Please contact support."
        }
    
    license = frappe.get_doc("LaundryCloud License", license_doc[0])
    
    return {
        "valid": license.validate_offline(),
        "status": license.status,
        "license_type": license.license_type,
        "expiry_date": license.expiry_date,
        "features": {
            "pos_enabled": license.pos_enabled,
            "delivery_enabled": license.delivery_enabled,
            "reports_enabled": license.reports_enabled
        }
    }

@frappe.whitelist()
def activate_license(license_key, activation_code):
    """Activate license with key and code"""
    try:
        # Find license by key
        license_name = frappe.db.get_value("LaundryCloud License", 
            {"license_key": license_key}, "name")
        
        if not license_name:
            return {
                "success": False,
                "message": "Invalid license key"
            }
        
        license_doc = frappe.get_doc("LaundryCloud License", license_name)
        
        # Verify activation code
        if license_doc.activation_code != activation_code:
            return {
                "success": False,
                "message": "Invalid activation code"
            }
        
        # Activate license
        license_doc.activate_license()
        
        return {
            "success": True,
            "message": "License activated successfully",
            "license_info": {
                "license_type": license_doc.license_type,
                "expiry_date": license_doc.expiry_date,
                "features": {
                    "pos_enabled": license_doc.pos_enabled,
                    "delivery_enabled": license_doc.delivery_enabled,
                    "reports_enabled": license_doc.reports_enabled
                }
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Activation failed: {str(e)}"
        }

@frappe.whitelist()
def check_feature_access(feature):
    """Check if user has access to specific feature"""
    license_status = get_license_status()
    
    if not license_status.get("valid"):
        return False
    
    features = license_status.get("features", {})
    feature_map = {
        "pos": features.get("pos_enabled", False),
        "delivery": features.get("delivery_enabled", False), 
        "reports": features.get("reports_enabled", False)
    }
    
    return feature_map.get(feature, False)

@frappe.whitelist()
def get_trial_license():
    """Generate trial license for new installations"""
    site_url = frappe.local.site
    
    # Check if trial already exists
    existing_trial = frappe.db.exists("LaundryCloud License", {
        "site_url": ["like", f"%{site_url}%"],
        "is_trial": 1
    })
    
    if existing_trial:
        return {
            "success": False,
            "message": "Trial license already exists for this site"
        }
    
    # Create trial license
    trial_license = frappe.new_doc("LaundryCloud License")
    trial_license.license_type = "Trial"
    trial_license.is_trial = 1
    trial_license.site_url = f"https://{site_url}"
    trial_license.contact_email = frappe.session.user
    trial_license.license_plan = "Trial"
    trial_license.trial_period_days = 30
    trial_license.max_users = 3
    trial_license.max_orders_per_month = 100
    trial_license.pos_enabled = 1
    trial_license.delivery_enabled = 0  # Limited in trial
    trial_license.reports_enabled = 0   # Limited in trial
    
    trial_license.save()
    trial_license.submit()
    
    return {
        "success": True,
        "message": "Trial license created successfully",
        "license_key": trial_license.license_key,
        "trial_days": trial_license.trial_period_days
    }