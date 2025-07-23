# Copyright (c) 2025, LaundryCloud and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate, add_days, get_datetime, cstr
import qrcode
import io
import base64
from PIL import Image

class LaundryOrder(Document):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def validate(self):
        self.validate_customer()
        self.validate_items()
        self.calculate_totals()
        self.validate_pickup_delivery()
        self.set_expected_delivery_date()
        self.generate_barcode_qr()
        
    def before_save(self):
        self.set_created_modified_by()
        
    def on_submit(self):
        self.update_status("Received")
        self.create_sales_invoice_if_paid()
        self.send_order_confirmation()
        
    def on_cancel(self):
        self.update_status("Cancelled")
        self.send_cancellation_notification()
        
    def validate_customer(self):
        """Validate customer information"""
        if not self.customer:
            frappe.throw(_("Customer is required"))
            
        # Fetch customer details if not already present
        if self.customer and not self.customer_name:
            customer_doc = frappe.get_doc("Customer", self.customer)
            self.customer_name = customer_doc.customer_name
            if customer_doc.mobile_no:
                self.customer_phone = customer_doc.mobile_no
            if customer_doc.email_id:
                self.customer_email = customer_doc.email_id
                
    def validate_items(self):
        """Validate order items"""
        if not self.items:
            frappe.throw(_("At least one item is required"))
            
        for item in self.items:
            if not item.service or not item.quantity:
                frappe.throw(_("Service and quantity are required for all items"))
                
            # Validate service exists
            if not frappe.db.exists("Laundry Service", item.service):
                frappe.throw(_("Service {0} does not exist").format(item.service))
                
    def calculate_totals(self):
        """Calculate order totals"""
        subtotal = 0
        for item in self.items:
            item.amount = flt(item.rate) * flt(item.quantity)
            subtotal += item.amount
            
        self.subtotal = subtotal
        
        # Calculate total
        total = subtotal + flt(self.tax_amount) + flt(self.delivery_charges) - flt(self.discount_amount)
        self.total_amount = total
        
        # Calculate outstanding amount
        self.outstanding_amount = flt(self.total_amount) - flt(self.paid_amount)
        
        # Update payment status
        if self.outstanding_amount <= 0:
            self.payment_status = "Paid"
        elif self.paid_amount > 0:
            self.payment_status = "Partially Paid"
        else:
            self.payment_status = "Unpaid"
            
    def validate_pickup_delivery(self):
        """Validate pickup and delivery information"""
        if self.order_type == "Pickup & Delivery":
            if not self.pickup_address or not self.delivery_address:
                frappe.throw(_("Pickup and delivery addresses are required for pickup & delivery orders"))
                
            if not self.pickup_date or not self.pickup_time:
                frappe.throw(_("Pickup date and time are required"))
                
    def set_expected_delivery_date(self):
        """Set expected delivery date based on service type and priority"""
        if not self.expected_delivery_date:
            days_to_add = 2  # Default 2 days
            
            # Adjust based on service type
            if self.service_type == "Express":
                days_to_add = 1
            elif self.service_type == "Dry Cleaning":
                days_to_add = 3
            elif self.service_type == "Alterations":
                days_to_add = 5
                
            # Adjust based on priority
            if self.priority == "Urgent":
                days_to_add = max(1, days_to_add - 1)
            elif self.priority == "High":
                days_to_add = max(1, days_to_add - 0.5)
                
            self.expected_delivery_date = add_days(self.order_date, days_to_add)
            
    def generate_barcode_qr(self):
        """Generate barcode and QR code for the order"""
        if not self.barcode:
            # Generate unique barcode
            self.barcode = f"LC{self.name.replace('-', '')}"
            
        # Generate QR code with order information
        qr_data = {
            "order_id": self.name,
            "customer": self.customer_name,
            "phone": self.customer_phone,
            "total": str(self.total_amount),
            "status": self.status
        }
        
        qr_string = "\n".join([f"{k}: {v}" for k, v in qr_data.items()])
        
        # Create QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_string)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        qr_img.save(buffer, format='PNG')
        qr_code_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Save as file
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"qr_code_{self.name}.png",
            "content": qr_code_b64,
            "decode": True,
            "attached_to_doctype": "Laundry Order",
            "attached_to_name": self.name,
            "is_private": 0
        })
        file_doc.save()
        
        self.qr_code = file_doc.file_url
        
    def set_created_modified_by(self):
        """Set created and modified by fields"""
        if self.is_new():
            self.created_by = frappe.session.user
        self.modified_by = frappe.session.user
        
    def update_status(self, new_status):
        """Update order status"""
        old_status = self.status
        self.status = new_status
        self.save()
        
        # Log status change
        frappe.get_doc({
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "Laundry Order",
            "reference_name": self.name,
            "content": f"Status changed from {old_status} to {new_status}",
            "comment_by": frappe.session.user
        }).insert(ignore_permissions=True)
        
        # Send notifications
        self.send_status_notification(new_status)
        
    def create_sales_invoice_if_paid(self):
        """Create sales invoice if order is paid"""
        if self.payment_status in ["Paid", "Partially Paid"]:
            si = frappe.new_doc("Sales Invoice")
            si.customer = self.customer
            si.posting_date = nowdate()
            si.due_date = nowdate()
            si.po_no = self.name
            si.po_date = self.order_date
            
            for item in self.items:
                si.append("items", {
                    "item_code": item.service,
                    "item_name": item.service_name,
                    "qty": item.quantity,
                    "rate": item.rate,
                    "amount": item.amount
                })
                
            if self.delivery_charges:
                si.append("items", {
                    "item_code": "DELIVERY",
                    "item_name": "Delivery Charges",
                    "qty": 1,
                    "rate": self.delivery_charges,
                    "amount": self.delivery_charges
                })
                
            si.save()
            if self.payment_status == "Paid":
                si.submit()
                
            frappe.msgprint(_("Sales Invoice {0} created successfully").format(si.name))
            
    def send_order_confirmation(self):
        """Send order confirmation to customer"""
        if self.customer_email:
            subject = f"Order Confirmation - {self.name}"
            message = f"""
            Dear {self.customer_name},
            
            Your laundry order {self.name} has been received and is being processed.
            
            Order Details:
            - Order Date: {self.order_date}
            - Expected Delivery: {self.expected_delivery_date}
            - Total Amount: {self.total_amount}
            - Status: {self.status}
            
            Thank you for choosing LaundryCloud!
            """
            
            frappe.sendmail(
                recipients=[self.customer_email],
                subject=subject,
                message=message
            )
            
    def send_status_notification(self, status):
        """Send status notification to customer"""
        if self.customer_email:
            status_messages = {
                "Received": "Your order has been received and is being processed.",
                "In Progress": "Your order is currently being processed.",
                "Washing": "Your items are currently being washed.",
                "Drying": "Your items are currently being dried.",
                "Ironing": "Your items are currently being ironed.",
                "Ready for Pickup": "Your order is ready for pickup!",
                "Out for Delivery": "Your order is out for delivery.",
                "Delivered": "Your order has been delivered successfully.",
                "Completed": "Your order has been completed. Thank you!",
                "Cancelled": "Your order has been cancelled."
            }
            
            if status in status_messages:
                subject = f"Order Update - {self.name}"
                message = f"""
                Dear {self.customer_name},
                
                Order {self.name} Status Update:
                {status_messages[status]}
                
                Current Status: {status}
                
                Thank you for choosing LaundryCloud!
                """
                
                frappe.sendmail(
                    recipients=[self.customer_email],
                    subject=subject,
                    message=message
                )
                
    def send_cancellation_notification(self):
        """Send cancellation notification to customer"""
        if self.customer_email:
            subject = f"Order Cancelled - {self.name}"
            message = f"""
            Dear {self.customer_name},
            
            Your laundry order {self.name} has been cancelled.
            
            If you have any questions, please contact us.
            
            Thank you for choosing LaundryCloud!
            """
            
            frappe.sendmail(
                recipients=[self.customer_email],
                subject=subject,
                message=message
            )
            
    @frappe.whitelist()
    def mark_ready_for_pickup(self):
        """Mark order as ready for pickup"""
        self.update_status("Ready for Pickup")
        frappe.msgprint(_("Order marked as ready for pickup"))
        
    @frappe.whitelist()
    def mark_out_for_delivery(self):
        """Mark order as out for delivery"""
        self.update_status("Out for Delivery")
        frappe.msgprint(_("Order marked as out for delivery"))
        
    @frappe.whitelist()
    def mark_delivered(self):
        """Mark order as delivered"""
        self.update_status("Delivered")
        self.actual_delivery_date = nowdate()
        self.save()
        frappe.msgprint(_("Order marked as delivered"))
        
    @frappe.whitelist()
    def mark_completed(self):
        """Mark order as completed"""
        self.update_status("Completed")
        frappe.msgprint(_("Order marked as completed"))

# API Methods
@frappe.whitelist()
def get_customer_orders(customer):
    """Get orders for a specific customer"""
    orders = frappe.get_all("Laundry Order",
        filters={"customer": customer},
        fields=["name", "order_date", "expected_delivery_date", "status", "total_amount"],
        order_by="order_date desc"
    )
    return orders

@frappe.whitelist()
def create_quick_order(customer, items, order_type="In-Store"):
    """Create a quick order"""
    order = frappe.new_doc("Laundry Order")
    order.customer = customer
    order.order_type = order_type
    order.order_date = nowdate()
    
    for item_data in items:
        order.append("items", item_data)
        
    order.save()
    order.submit()
    
    return order.name

@frappe.whitelist()
def get_order_tracking(order_id):
    """Get order tracking information"""
    order = frappe.get_doc("Laundry Order", order_id)
    
    return {
        "order_id": order.name,
        "customer_name": order.customer_name,
        "status": order.status,
        "order_date": order.order_date,
        "expected_delivery_date": order.expected_delivery_date,
        "actual_delivery_date": order.actual_delivery_date,
        "total_amount": order.total_amount,
        "payment_status": order.payment_status,
        "qr_code": order.qr_code,
        "barcode": order.barcode
    }