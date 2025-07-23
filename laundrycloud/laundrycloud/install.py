# Copyright (c) 2025, LaundryCloud and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cstr

def after_install():
    """Setup LaundryCloud after installation"""
    setup_roles_and_permissions()
    create_default_services()
    create_default_pos_profile()
    create_sample_data()
    setup_email_templates()
    setup_print_formats()

def setup_roles_and_permissions():
    """Create LaundryCloud specific roles"""
    roles = [
        {
            "role_name": "LaundryCloud Manager",
            "desk_access": 1,
            "role_description": "Full access to LaundryCloud features"
        },
        {
            "role_name": "LaundryCloud User", 
            "desk_access": 1,
            "role_description": "Standard LaundryCloud user with order management access"
        },
        {
            "role_name": "LaundryCloud Driver",
            "desk_access": 1,
            "role_description": "Driver role for pickup and delivery"
        },
        {
            "role_name": "LaundryCloud Customer",
            "desk_access": 0,
            "role_description": "Customer portal access"
        }
    ]
    
    for role in roles:
        if not frappe.db.exists("Role", role["role_name"]):
            doc = frappe.get_doc({
                "doctype": "Role",
                "role_name": role["role_name"],
                "desk_access": role["desk_access"],
                "role_description": role.get("role_description", "")
            })
            doc.insert(ignore_permissions=True)

def create_default_services():
    """Create default laundry services"""
    services = [
        {
            "service_name": "Shirt Wash & Press",
            "category": "Wash & Fold",
            "rate": 5.00,
            "processing_time_hours": 24,
            "description": "Professional wash and press for shirts"
        },
        {
            "service_name": "Pants Dry Clean",
            "category": "Dry Cleaning", 
            "rate": 8.00,
            "processing_time_hours": 48,
            "description": "Dry cleaning for trousers and pants"
        },
        {
            "service_name": "Dress Dry Clean",
            "category": "Dry Cleaning",
            "rate": 12.00,
            "processing_time_hours": 48,
            "description": "Professional dry cleaning for dresses"
        },
        {
            "service_name": "Suit Dry Clean",
            "category": "Dry Cleaning",
            "rate": 20.00,
            "processing_time_hours": 72,
            "description": "Complete suit dry cleaning service"
        },
        {
            "service_name": "Ironing Only",
            "category": "Ironing",
            "rate": 3.00,
            "processing_time_hours": 12,
            "description": "Ironing service for clean garments"
        },
        {
            "service_name": "Comforter Cleaning",
            "category": "Specialty",
            "rate": 25.00,
            "processing_time_hours": 48,
            "description": "Large item cleaning for comforters and blankets"
        }
    ]
    
    for service in services:
        if not frappe.db.exists("Laundry Service", service["service_name"]):
            doc = frappe.get_doc({
                "doctype": "Laundry Service",
                "service_name": service["service_name"],
                "category": service["category"],
                "rate": service["rate"],
                "currency": frappe.defaults.get_global_default("currency") or "USD",
                "processing_time_hours": service["processing_time_hours"],
                "express_time_hours": service["processing_time_hours"] // 2,
                "description": service["description"],
                "is_active": 1,
                "priority": 5,
                "uom": "Nos",
                "company": frappe.defaults.get_global_default("company")
            })
            doc.insert(ignore_permissions=True)

def create_default_pos_profile():
    """Create default POS profile"""
    company = frappe.defaults.get_global_default("company")
    if not company:
        return
        
    if not frappe.db.exists("Laundry POS Profile", "Default LaundryCloud POS"):
        # Get default values
        currency = frappe.defaults.get_global_default("currency") or "USD"
        
        # Try to get default warehouse
        warehouse = frappe.db.get_value("Warehouse", {"company": company, "is_group": 0}, "name")
        if not warehouse:
            warehouse = frappe.db.get_value("Warehouse", {"is_group": 0}, "name")
            
        doc = frappe.get_doc({
            "doctype": "Laundry POS Profile",
            "profile_name": "Default LaundryCloud POS",
            "company": company,
            "currency": currency,
            "warehouse": warehouse,
            "is_default": 1,
            "allow_discount": 1,
            "max_discount_percentage": 20,
            "allow_customer_creation": 1,
            "print_receipt_on_payment": 1,
            "email_receipt": 1,
            "display_items_in_grid": 1,
            "items_per_page": 20,
            "pos_theme": "Blue"
        })
        
        # Add default payment methods
        payment_methods = ["Cash", "Credit Card"]
        for method in payment_methods:
            if frappe.db.exists("Mode of Payment", method):
                doc.append("payment_method_table", {
                    "mode_of_payment": method,
                    "default": 1 if method == "Cash" else 0
                })
        
        doc.insert(ignore_permissions=True)

def create_sample_data():
    """Create sample customers and data"""
    # Create walk-in customer
    if not frappe.db.exists("Customer", {"customer_name": "Walk-In Customer"}):
        doc = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": "Walk-In Customer",
            "customer_type": "Individual",
            "customer_group": frappe.db.get_value("Customer Group", {"is_group": 0}, "name") or "Individual"
        })
        doc.insert(ignore_permissions=True)
    
    # Create sample customer
    if not frappe.db.exists("Customer", {"customer_name": "John Doe"}):
        doc = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": "John Doe",
            "customer_type": "Individual",
            "customer_group": frappe.db.get_value("Customer Group", {"is_group": 0}, "name") or "Individual",
            "mobile_no": "+1234567890",
            "email_id": "john.doe@example.com"
        })
        doc.insert(ignore_permissions=True)

def setup_email_templates():
    """Setup email templates for notifications"""
    templates = [
        {
            "name": "LaundryCloud Order Confirmation",
            "subject": "Order Confirmation - {{ doc.name }}",
            "response": """
            <p>Dear {{ doc.customer_name }},</p>
            <p>Thank you for your order! Your laundry order <strong>{{ doc.name }}</strong> has been received.</p>
            <h4>Order Details:</h4>
            <ul>
                <li>Order Date: {{ doc.order_date }}</li>
                <li>Expected Delivery: {{ doc.expected_delivery_date }}</li>
                <li>Total Amount: {{ doc.get_formatted("total_amount") }}</li>
                <li>Status: {{ doc.status }}</li>
            </ul>
            <p>You can track your order using the order number above.</p>
            <p>Thank you for choosing LaundryCloud!</p>
            """
        },
        {
            "name": "LaundryCloud Order Ready",
            "subject": "Your Order is Ready - {{ doc.name }}",
            "response": """
            <p>Dear {{ doc.customer_name }},</p>
            <p>Great news! Your laundry order <strong>{{ doc.name }}</strong> is ready for pickup.</p>
            {% if doc.order_type == "Pickup & Delivery" %}
            <p>We will deliver your order to the specified address.</p>
            {% else %}
            <p>Please visit our store to collect your order.</p>
            {% endif %}
            <p>Thank you for choosing LaundryCloud!</p>
            """
        }
    ]
    
    for template in templates:
        if not frappe.db.exists("Email Template", template["name"]):
            doc = frappe.get_doc({
                "doctype": "Email Template",
                "name": template["name"],
                "subject": template["subject"],
                "response": template["response"],
                "use_html": 1
            })
            doc.insert(ignore_permissions=True)

def setup_print_formats():
    """Setup print formats for receipts"""
    # This would typically involve creating custom print formats
    # For now, we'll rely on standard formats and customization
    pass

def before_uninstall():
    """Cleanup before uninstalling"""
    frappe.db.sql("DELETE FROM `tabEmail Template` WHERE name LIKE 'LaundryCloud%'")
    frappe.db.sql("DELETE FROM `tabRole` WHERE role_name LIKE 'LaundryCloud%'")

# Fixtures for the app
fixtures = [
    {
        "dt": "Role",
        "filters": [
            [
                "name",
                "in",
                [
                    "LaundryCloud Manager",
                    "LaundryCloud User", 
                    "LaundryCloud Driver",
                    "LaundryCloud Customer"
                ]
            ]
        ]
    },
    {
        "dt": "Email Template",
        "filters": [
            [
                "name",
                "like",
                "LaundryCloud%"
            ]
        ]
    }
]