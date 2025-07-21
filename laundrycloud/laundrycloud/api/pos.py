# Copyright (c) 2025, LaundryCloud and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, nowdate, cstr
import json

@frappe.whitelist()
def get_active_services(category=None):
    """Get all active laundry services for POS"""
    filters = {"is_active": 1}
    
    if category:
        filters["category"] = category
    
    services = frappe.get_all("Laundry Service",
        filters=filters,
        fields=["name", "service_name", "category", "rate", "currency", "image", "icon", "description"],
        order_by="priority asc, service_name asc"
    )
    
    return services

@frappe.whitelist()
def search_customers(query):
    """Search customers for POS"""
    if len(query) < 2:
        return []
    
    customers = frappe.get_all("Customer",
        filters={
            "disabled": 0,
            "customer_name": ["like", f"%{query}%"]
        },
        fields=["name", "customer_name", "mobile_no", "email_id"],
        limit=10
    )
    
    # Also search by phone number
    phone_customers = frappe.get_all("Customer",
        filters={
            "disabled": 0,
            "mobile_no": ["like", f"%{query}%"]
        },
        fields=["name", "customer_name", "mobile_no", "email_id"],
        limit=10
    )
    
    # Combine and deduplicate
    all_customers = customers + phone_customers
    unique_customers = []
    seen_names = set()
    
    for customer in all_customers:
        if customer.name not in seen_names:
            unique_customers.append(customer)
            seen_names.add(customer.name)
    
    return unique_customers[:10]

@frappe.whitelist()
def get_default_pos_profile():
    """Get default POS profile"""
    profile = frappe.get_all("Laundry POS Profile",
        filters={"is_default": 1},
        fields="*",
        limit=1
    )
    
    if profile:
        return profile[0]
    
    # If no default, get the first available profile
    profile = frappe.get_all("Laundry POS Profile",
        fields="*",
        limit=1
    )
    
    return profile[0] if profile else None

@frappe.whitelist()
def create_order(order_data):
    """Create a new laundry order from POS"""
    try:
        if isinstance(order_data, str):
            order_data = json.loads(order_data)
        
        # Create new laundry order
        order = frappe.new_doc("Laundry Order")
        
        # Set basic order information
        order.customer = order_data.get("customer")
        order.order_type = order_data.get("order_type", "In-Store")
        order.order_date = nowdate()
        order.payment_method = order_data.get("payment_method")
        order.pos_profile = order_data.get("pos_profile")
        
        # Handle walk-in customer
        if not order.customer:
            default_customer = get_default_customer()
            if default_customer:
                order.customer = default_customer
        
        # Add items
        for item_data in order_data.get("items", []):
            order.append("items", {
                "service": item_data.get("service"),
                "service_name": item_data.get("service_name"),
                "quantity": item_data.get("quantity", 1),
                "rate": item_data.get("rate", 0),
                "amount": item_data.get("amount", 0)
            })
        
        # Set totals
        order.subtotal = order_data.get("subtotal", 0)
        order.discount_amount = order_data.get("discount_amount", 0)
        order.tax_amount = calculate_tax_amount(order.subtotal - order.discount_amount)
        order.total_amount = order_data.get("total_amount", 0)
        
        # Set payment information
        payment_method = order_data.get("payment_method")
        if payment_method in ["Cash", "Card", "Digital Wallet"]:
            order.paid_amount = order.total_amount
            order.payment_status = "Paid"
        else:
            order.paid_amount = 0
            order.payment_status = "Unpaid"
        
        # Save and submit order
        order.save()
        order.submit()
        
        # Create payment entry if paid
        if order.payment_status == "Paid":
            create_payment_entry(order, payment_method)
        
        frappe.db.commit()
        
        return {
            "name": order.name,
            "customer_name": order.customer_name,
            "order_date": order.order_date,
            "total_amount": order.total_amount,
            "items": [{"service_name": item.service_name, "quantity": item.quantity, "amount": item.amount} for item in order.items],
            "subtotal": order.subtotal,
            "discount_amount": order.discount_amount,
            "tax_amount": order.tax_amount,
            "barcode": order.barcode
        }
        
    except Exception as e:
        frappe.log_error(f"Error creating POS order: {str(e)}")
        frappe.throw(_("Error creating order: {0}").format(str(e)))

def get_default_customer():
    """Get default customer for walk-in orders"""
    # Check if there's a default customer in POS profile
    pos_profile = get_default_pos_profile()
    if pos_profile and pos_profile.get("default_customer"):
        return pos_profile["default_customer"]
    
    # Look for a walk-in customer
    walk_in_customer = frappe.db.get_value("Customer", {"customer_name": "Walk-In Customer"}, "name")
    if walk_in_customer:
        return walk_in_customer
    
    # Create walk-in customer if it doesn't exist
    try:
        customer = frappe.new_doc("Customer")
        customer.customer_name = "Walk-In Customer"
        customer.customer_type = "Individual"
        customer.save()
        return customer.name
    except:
        return None

def calculate_tax_amount(taxable_amount):
    """Calculate tax amount based on taxable amount"""
    # This should be configurable, for now using 10%
    tax_rate = 0.10
    return flt(taxable_amount * tax_rate, 2)

def create_payment_entry(order, payment_method):
    """Create payment entry for the order"""
    try:
        from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
        
        # Get the sales invoice if it exists
        sales_invoice = frappe.db.get_value("Sales Invoice", {"po_no": order.name}, "name")
        
        if sales_invoice:
            # Create payment entry against sales invoice
            payment_entry = get_payment_entry("Sales Invoice", sales_invoice)
            payment_entry.mode_of_payment = get_mode_of_payment(payment_method)
            payment_entry.paid_amount = order.total_amount
            payment_entry.received_amount = order.total_amount
            payment_entry.reference_no = order.name
            payment_entry.reference_date = order.order_date
            payment_entry.save()
            payment_entry.submit()
            
    except Exception as e:
        frappe.log_error(f"Error creating payment entry: {str(e)}")

def get_mode_of_payment(payment_method):
    """Get ERPNext mode of payment based on payment method"""
    mode_mapping = {
        "Cash": "Cash",
        "Card": "Credit Card",
        "Digital Wallet": "Digital Wallet",
        "Bank Transfer": "Bank Transfer"
    }
    
    mode_name = mode_mapping.get(payment_method, "Cash")
    
    # Check if mode exists, create if not
    if not frappe.db.exists("Mode of Payment", mode_name):
        mode = frappe.new_doc("Mode of Payment")
        mode.mode_of_payment = mode_name
        mode.save()
    
    return mode_name

@frappe.whitelist()
def get_order_summary(order_id):
    """Get order summary for POS receipt"""
    order = frappe.get_doc("Laundry Order", order_id)
    
    return {
        "order_id": order.name,
        "customer_name": order.customer_name,
        "order_date": order.order_date,
        "items": [
            {
                "service_name": item.service_name,
                "quantity": item.quantity,
                "rate": item.rate,
                "amount": item.amount
            }
            for item in order.items
        ],
        "subtotal": order.subtotal,
        "discount_amount": order.discount_amount,
        "tax_amount": order.tax_amount,
        "total_amount": order.total_amount,
        "payment_method": order.payment_method,
        "barcode": order.barcode,
        "qr_code": order.qr_code
    }

@frappe.whitelist()
def get_service_details(service_name):
    """Get detailed information about a service"""
    service = frappe.get_doc("Laundry Service", service_name)
    
    return {
        "name": service.name,
        "service_name": service.service_name,
        "category": service.category,
        "rate": service.rate,
        "currency": service.currency,
        "description": service.description,
        "processing_time_hours": service.processing_time_hours,
        "requires_special_care": service.requires_special_care,
        "applicable_garments": service.applicable_garments,
        "image": service.image,
        "icon": service.icon
    }

@frappe.whitelist()
def get_customer_history(customer):
    """Get customer order history"""
    orders = frappe.get_all("Laundry Order",
        filters={"customer": customer},
        fields=["name", "order_date", "status", "total_amount", "payment_status"],
        order_by="order_date desc",
        limit=10
    )
    
    return orders

@frappe.whitelist()
def apply_discount(order_total, discount_type, discount_value, max_discount=None):
    """Calculate discount amount"""
    discount_amount = 0
    
    if discount_type == "Percentage":
        discount_amount = flt(order_total * discount_value / 100, 2)
    elif discount_type == "Amount":
        discount_amount = flt(discount_value, 2)
    
    # Apply maximum discount limit
    if max_discount and discount_amount > max_discount:
        discount_amount = max_discount
    
    # Ensure discount doesn't exceed order total
    if discount_amount > order_total:
        discount_amount = order_total
    
    return {
        "discount_amount": discount_amount,
        "final_total": order_total - discount_amount
    }

@frappe.whitelist()
def validate_barcode(barcode):
    """Validate and get service by barcode"""
    # Check if barcode belongs to a service
    service = frappe.db.get_value("Laundry Service", {"service_code": barcode}, ["name", "service_name", "rate", "category"])
    
    if service:
        return {
            "type": "service",
            "data": {
                "name": service[0],
                "service_name": service[1],
                "rate": service[2],
                "category": service[3]
            }
        }
    
    # Check if barcode belongs to an existing order
    order = frappe.db.get_value("Laundry Order", {"barcode": barcode}, ["name", "customer_name", "status", "total_amount"])
    
    if order:
        return {
            "type": "order",
            "data": {
                "name": order[0],
                "customer_name": order[1],
                "status": order[2],
                "total_amount": order[3]
            }
        }
    
    return {"type": "unknown", "data": None}

@frappe.whitelist()
def get_pos_analytics():
    """Get POS analytics for dashboard"""
    from frappe.utils import add_days, getdate
    
    today = getdate()
    week_start = add_days(today, -7)
    month_start = add_days(today, -30)
    
    # Today's sales
    today_sales = frappe.db.sql("""
        SELECT COUNT(*) as orders, SUM(total_amount) as revenue
        FROM `tabLaundry Order`
        WHERE order_date = %s AND docstatus = 1
    """, today, as_dict=True)[0]
    
    # This week's sales
    week_sales = frappe.db.sql("""
        SELECT COUNT(*) as orders, SUM(total_amount) as revenue
        FROM `tabLaundry Order`
        WHERE order_date >= %s AND docstatus = 1
    """, week_start, as_dict=True)[0]
    
    # This month's sales
    month_sales = frappe.db.sql("""
        SELECT COUNT(*) as orders, SUM(total_amount) as revenue
        FROM `tabLaundry Order`
        WHERE order_date >= %s AND docstatus = 1
    """, month_start, as_dict=True)[0]
    
    # Top services
    top_services = frappe.db.sql("""
        SELECT loi.service_name, SUM(loi.quantity) as total_quantity, SUM(loi.amount) as total_amount
        FROM `tabLaundry Order Item` loi
        JOIN `tabLaundry Order` lo ON loi.parent = lo.name
        WHERE lo.order_date >= %s AND lo.docstatus = 1
        GROUP BY loi.service_name
        ORDER BY total_quantity DESC
        LIMIT 5
    """, week_start, as_dict=True)
    
    return {
        "today": today_sales,
        "week": week_sales,
        "month": month_sales,
        "top_services": top_services
    }