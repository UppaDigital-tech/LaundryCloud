# Copyright (c) 2025, LaundryCloud and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import requests
import json
import hashlib
import hmac
from datetime import datetime

# License pricing configuration
def get_regional_pricing():
    """Get pricing based on configured payment gateway"""
    payment_gateway = frappe.conf.get("laundrycloud_payment_gateway", "stripe")
    
    if payment_gateway == "paystack":
        # Get preferred currency from config, default to NGN
        preferred_currency = frappe.conf.get("laundrycloud_currency", "NGN")
        
        if preferred_currency == "GHS":
            # Ghana Cedis pricing
            return {
                "basic": {
                    "name": "Basic Plan",
                    "price": 180,  # GH₵180
                    "currency": "GHS",
                    "max_users": 5,
                    "max_orders_per_month": 1000,
                    "features": {
                        "pos_enabled": True,
                        "delivery_enabled": False,
                        "reports_enabled": False
                    }
                },
                "professional": {
                    "name": "Professional Plan", 
                    "price": 480,  # GH₵480
                    "currency": "GHS",
                    "max_users": 15,
                    "max_orders_per_month": 5000,
                    "features": {
                        "pos_enabled": True,
                        "delivery_enabled": True,
                        "reports_enabled": True
                    }
                },
                "enterprise": {
                    "name": "Enterprise Plan",
                    "price": 1200,  # GH₵1,200
                    "currency": "GHS", 
                    "max_users": -1,  # Unlimited
                    "max_orders_per_month": -1,  # Unlimited
                    "features": {
                        "pos_enabled": True,
                        "delivery_enabled": True,
                        "reports_enabled": True
                    }
                }
            }
        elif preferred_currency == "ZAR":
            # South African Rand pricing
            return {
                "basic": {
                    "name": "Basic Plan",
                    "price": 450,  # R450
                    "currency": "ZAR",
                    "max_users": 5,
                    "max_orders_per_month": 1000,
                    "features": {
                        "pos_enabled": True,
                        "delivery_enabled": False,
                        "reports_enabled": False
                    }
                },
                "professional": {
                    "name": "Professional Plan", 
                    "price": 1200,  # R1,200
                    "currency": "ZAR",
                    "max_users": 15,
                    "max_orders_per_month": 5000,
                    "features": {
                        "pos_enabled": True,
                        "delivery_enabled": True,
                        "reports_enabled": True
                    }
                },
                "enterprise": {
                    "name": "Enterprise Plan",
                    "price": 3000,  # R3,000
                    "currency": "ZAR", 
                    "max_users": -1,  # Unlimited
                    "max_orders_per_month": -1,  # Unlimited
                    "features": {
                        "pos_enabled": True,
                        "delivery_enabled": True,
                        "reports_enabled": True
                    }
                }
            }
        else:
            # Default Nigerian pricing in Naira
            return {
                "basic": {
                    "name": "Basic Plan",
                    "price": 15000,  # ₦15,000
                    "currency": "NGN",
                    "max_users": 5,
                    "max_orders_per_month": 1000,
                    "features": {
                        "pos_enabled": True,
                        "delivery_enabled": False,
                        "reports_enabled": False
                    }
                },
                "professional": {
                    "name": "Professional Plan", 
                    "price": 40000,  # ₦40,000
                    "currency": "NGN",
                    "max_users": 15,
                    "max_orders_per_month": 5000,
                    "features": {
                        "pos_enabled": True,
                        "delivery_enabled": True,
                        "reports_enabled": True
                    }
                },
                "enterprise": {
                    "name": "Enterprise Plan",
                    "price": 100000,  # ₦100,000
                    "currency": "NGN", 
                    "max_users": -1,  # Unlimited
                    "max_orders_per_month": -1,  # Unlimited
                    "features": {
                        "pos_enabled": True,
                        "delivery_enabled": True,
                        "reports_enabled": True
                    }
                }
            }
    else:
        # Default USD pricing
        return {
            "basic": {
                "name": "Basic Plan",
                "price": 29.99,
                "currency": "USD",
                "max_users": 5,
                "max_orders_per_month": 1000,
                "features": {
                    "pos_enabled": True,
                    "delivery_enabled": False,
                    "reports_enabled": False
                }
            },
            "professional": {
                "name": "Professional Plan", 
                "price": 79.99,
                "currency": "USD",
                "max_users": 15,
                "max_orders_per_month": 5000,
                "features": {
                    "pos_enabled": True,
                    "delivery_enabled": True,
                    "reports_enabled": True
                }
            },
            "enterprise": {
                "name": "Enterprise Plan",
                "price": 199.99,
                "currency": "USD", 
                "max_users": -1,  # Unlimited
                "max_orders_per_month": -1,  # Unlimited
                "features": {
                    "pos_enabled": True,
                    "delivery_enabled": True,
                    "reports_enabled": True
                }
            }
        }

LICENSE_PLANS = get_regional_pricing()

@frappe.whitelist()
def get_license_plans():
    """Get available license plans"""
    return get_regional_pricing()

@frappe.whitelist()
def create_payment_session(plan_id, site_url, contact_email):
    """Create payment session for license purchase"""
    try:
        current_plans = get_regional_pricing()
        if plan_id not in current_plans:
            return {
                "success": False,
                "message": "Invalid plan selected"
            }
        
        plan = current_plans[plan_id]
        
        # Create payment session based on configured gateway
        payment_gateway = frappe.conf.get("laundrycloud_payment_gateway", "stripe")
        
        if payment_gateway == "stripe":
            return create_stripe_session(plan, site_url, contact_email)
        elif payment_gateway == "paypal":
            return create_paypal_session(plan, site_url, contact_email)
        elif payment_gateway == "razorpay":
            return create_razorpay_session(plan, site_url, contact_email)
        elif payment_gateway == "paystack":
            return create_paystack_session(plan, site_url, contact_email)
        else:
            return {
                "success": False,
                "message": "Payment gateway not configured"
            }
            
    except Exception as e:
        frappe.log_error(f"Payment session creation error: {str(e)}")
        return {
            "success": False,
            "message": "Failed to create payment session"
        }

def create_stripe_session(plan, site_url, contact_email):
    """Create Stripe payment session"""
    import stripe
    
    stripe.api_key = frappe.conf.get("stripe_secret_key")
    
    if not stripe.api_key:
        return {
            "success": False,
            "message": "Stripe not configured"
        }
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': plan['currency'].lower(),
                    'product_data': {
                        'name': f"LaundryCloud {plan['name']}",
                        'description': f"Annual license for {site_url}",
                    },
                    'unit_amount': int(plan['price'] * 100),  # Stripe uses cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{site_url}/app/laundrycloud-license?session_id={{CHECKOUT_SESSION_ID}}&status=success",
            cancel_url=f"{site_url}/app/laundrycloud-license?status=cancelled",
            client_reference_id=f"{site_url}:{contact_email}",
            metadata={
                'site_url': site_url,
                'contact_email': contact_email,
                'plan_id': plan['name'].lower().replace(' ', '_'),
                'app': 'laundrycloud'
            }
        )
        
        return {
            "success": True,
            "payment_url": session.url,
            "session_id": session.id,
            "payment_method": "stripe"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Stripe error: {str(e)}"
        }

def create_paypal_session(plan, site_url, contact_email):
    """Create PayPal payment session"""
    paypal_client_id = frappe.conf.get("paypal_client_id")
    paypal_secret = frappe.conf.get("paypal_secret")
    paypal_mode = frappe.conf.get("paypal_mode", "sandbox")  # sandbox or live
    
    if not paypal_client_id or not paypal_secret:
        return {
            "success": False,
            "message": "PayPal not configured"
        }
    
    # PayPal API endpoint
    base_url = "https://api.sandbox.paypal.com" if paypal_mode == "sandbox" else "https://api.paypal.com"
    
    try:
        # Get access token
        auth_response = requests.post(
            f"{base_url}/v1/oauth2/token",
            headers={
                "Accept": "application/json",
                "Accept-Language": "en_US",
            },
            data="grant_type=client_credentials",
            auth=(paypal_client_id, paypal_secret)
        )
        
        access_token = auth_response.json().get("access_token")
        
        # Create payment
        payment_data = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": plan['currency'],
                    "value": str(plan['price'])
                },
                "description": f"LaundryCloud {plan['name']} for {site_url}"
            }],
            "application_context": {
                "return_url": f"{site_url}/app/laundrycloud-license?status=success",
                "cancel_url": f"{site_url}/app/laundrycloud-license?status=cancelled"
            }
        }
        
        payment_response = requests.post(
            f"{base_url}/v2/checkout/orders",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
            json=payment_data
        )
        
        payment_result = payment_response.json()
        approval_url = next(link["href"] for link in payment_result["links"] if link["rel"] == "approve")
        
        return {
            "success": True,
            "payment_url": approval_url,
            "order_id": payment_result["id"],
            "payment_method": "paypal"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"PayPal error: {str(e)}"
        }

def create_razorpay_session(plan, site_url, contact_email):
    """Create Razorpay payment session"""
    razorpay_key = frappe.conf.get("razorpay_key_id")
    razorpay_secret = frappe.conf.get("razorpay_key_secret")
    
    if not razorpay_key or not razorpay_secret:
        return {
            "success": False,
            "message": "Razorpay not configured"
        }
    
    import razorpay
    
    try:
        client = razorpay.Client(auth=(razorpay_key, razorpay_secret))
        
        # Create order
        order_data = {
            "amount": int(plan['price'] * 100),  # Razorpay uses paise
            "currency": plan['currency'],
            "receipt": f"laundrycloud_{int(datetime.now().timestamp())}",
            "notes": {
                "site_url": site_url,
                "contact_email": contact_email,
                "plan": plan['name']
            }
        }
        
        order = client.order.create(data=order_data)
        
        return {
            "success": True,
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key": razorpay_key,
            "payment_method": "razorpay"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Razorpay error: {str(e)}"
        }

def create_paystack_session(plan, site_url, contact_email):
    """Create Paystack payment session"""
    paystack_public_key = frappe.conf.get("paystack_public_key")
    paystack_secret_key = frappe.conf.get("paystack_secret_key")
    
    if not paystack_public_key or not paystack_secret_key:
        return {
            "success": False,
            "message": "Paystack not configured"
        }
    
    try:
        # Initialize transaction
        transaction_data = {
            "email": contact_email,
            "amount": int(plan['price'] * 100),  # Paystack uses kobo (cents)
            "currency": plan['currency'],
            "reference": f"laundrycloud_{int(datetime.now().timestamp())}",
            "callback_url": f"{site_url}/app/laundrycloud-license?status=success",
            "metadata": {
                "site_url": site_url,
                "contact_email": contact_email,
                "plan_id": plan['name'].lower().replace(' ', '_'),
                "app": "laundrycloud"
            }
        }
        
        # Make API call to Paystack
        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            headers={
                "Authorization": f"Bearer {paystack_secret_key}",
                "Content-Type": "application/json"
            },
            json=transaction_data
        )
        
        result = response.json()
        
        if result.get("status"):
            return {
                "success": True,
                "payment_url": result["data"]["authorization_url"],
                "reference": result["data"]["reference"],
                "access_code": result["data"]["access_code"],
                "payment_method": "paystack",
                "public_key": paystack_public_key
            }
        else:
            return {
                "success": False,
                "message": f"Paystack error: {result.get('message', 'Unknown error')}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Paystack error: {str(e)}"
        }

@frappe.whitelist()
def verify_payment_and_activate_license(payment_data):
    """Verify payment and activate license"""
    try:
        payment_method = payment_data.get("payment_method")
        
        if payment_method == "stripe":
            return verify_stripe_payment(payment_data)
        elif payment_method == "paypal":
            return verify_paypal_payment(payment_data)
        elif payment_method == "razorpay":
            return verify_razorpay_payment(payment_data)
        elif payment_method == "paystack":
            return verify_paystack_payment(payment_data)
        else:
            return {
                "success": False,
                "message": "Invalid payment method"
            }
            
    except Exception as e:
        frappe.log_error(f"Payment verification error: {str(e)}")
        return {
            "success": False,
            "message": "Payment verification failed"
        }

def verify_stripe_payment(payment_data):
    """Verify Stripe payment"""
    import stripe
    
    stripe.api_key = frappe.conf.get("stripe_secret_key")
    session_id = payment_data.get("session_id")
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == "paid":
            # Extract metadata
            metadata = session.metadata
            site_url = metadata.get("site_url")
            contact_email = metadata.get("contact_email")
            plan_id = metadata.get("plan_id")
            
            # Create license
            license_doc = create_license_from_payment(
                site_url, contact_email, plan_id, 
                session.amount_total / 100, "USD", 
                session.id, "Stripe"
            )
            
            return {
                "success": True,
                "message": "Payment verified and license activated",
                "license_key": license_doc.license_key,
                "activation_code": license_doc.activation_code
            }
        else:
            return {
                "success": False,
                "message": "Payment not completed"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Stripe verification error: {str(e)}"
        }

def verify_razorpay_payment(payment_data):
    """Verify Razorpay payment"""
    razorpay_key = frappe.conf.get("razorpay_key_id")
    razorpay_secret = frappe.conf.get("razorpay_key_secret")
    
    payment_id = payment_data.get("razorpay_payment_id")
    order_id = payment_data.get("razorpay_order_id")
    signature = payment_data.get("razorpay_signature")
    
    # Verify signature
    body = f"{order_id}|{payment_id}"
    expected_signature = hmac.new(
        razorpay_secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()
    
    if signature == expected_signature:
        # Payment is valid, create license
        import razorpay
        client = razorpay.Client(auth=(razorpay_key, razorpay_secret))
        
        try:
            payment = client.payment.fetch(payment_id)
            order = client.order.fetch(order_id)
            
            if payment["status"] == "captured":
                notes = order.get("notes", {})
                site_url = notes.get("site_url")
                contact_email = notes.get("contact_email") 
                plan_name = notes.get("plan")
                
                license_doc = create_license_from_payment(
                    site_url, contact_email, plan_name.lower().replace(' ', '_'),
                    payment["amount"] / 100, payment["currency"],
                    payment_id, "Razorpay"
                )
                
                return {
                    "success": True,
                    "message": "Payment verified and license activated",
                    "license_key": license_doc.license_key,
                    "activation_code": license_doc.activation_code
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Razorpay verification error: {str(e)}"
            }
    
    return {
        "success": False,
        "message": "Payment verification failed"
    }

def verify_paystack_payment(payment_data):
    """Verify Paystack payment"""
    paystack_secret_key = frappe.conf.get("paystack_secret_key")
    reference = payment_data.get("reference")
    
    if not paystack_secret_key or not reference:
        return {
            "success": False,
            "message": "Missing Paystack configuration or reference"
        }
    
    try:
        # Verify transaction with Paystack
        response = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}",
            headers={
                "Authorization": f"Bearer {paystack_secret_key}",
                "Content-Type": "application/json"
            }
        )
        
        result = response.json()
        
        if result.get("status") and result["data"]["status"] == "success":
            # Payment successful, extract metadata
            metadata = result["data"]["metadata"]
            site_url = metadata.get("site_url")
            contact_email = metadata.get("contact_email")
            plan_id = metadata.get("plan_id")
            
            # Convert amount from kobo to main currency
            amount = result["data"]["amount"] / 100
            currency = result["data"]["currency"]
            
            # Create license
            license_doc = create_license_from_payment(
                site_url, contact_email, plan_id,
                amount, currency,
                reference, "Paystack"
            )
            
            return {
                "success": True,
                "message": "Payment verified and license activated",
                "license_key": license_doc.license_key,
                "activation_code": license_doc.activation_code
            }
        else:
            return {
                "success": False,
                "message": f"Payment verification failed: {result.get('message', 'Transaction not successful')}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Paystack verification error: {str(e)}"
        }

def create_license_from_payment(site_url, contact_email, plan_id, amount, currency, payment_ref, payment_method):
    """Create license after successful payment"""
    
    # Find plan configuration
    current_plans = get_regional_pricing()
    plan = None
    for key, value in current_plans.items():
        if key == plan_id or value['name'].lower().replace(' ', '_') == plan_id:
            plan = value
            break
    
    if not plan:
        frappe.throw(_("Invalid plan configuration"))
    
    # Create license
    license_doc = frappe.new_doc("LaundryCloud License")
    license_doc.license_type = "Commercial"
    license_doc.site_url = site_url
    license_doc.contact_email = contact_email
    license_doc.license_plan = plan['name']
    license_doc.max_users = plan['max_users']
    license_doc.max_orders_per_month = plan['max_orders_per_month']
    license_doc.pos_enabled = plan['features']['pos_enabled']
    license_doc.delivery_enabled = plan['features']['delivery_enabled']
    license_doc.reports_enabled = plan['features']['reports_enabled']
    license_doc.amount_paid = amount
    license_doc.currency = currency
    license_doc.payment_reference = payment_ref
    license_doc.payment_method = payment_method
    license_doc.purchase_date = frappe.utils.nowdate()
    license_doc.expiry_date = frappe.utils.add_years(frappe.utils.nowdate(), 1)  # 1 year license
    
    license_doc.save()
    license_doc.submit()
    
    return license_doc

@frappe.whitelist()
def get_payment_status(payment_id, payment_method):
    """Get payment status"""
    # Implementation depends on payment gateway
    pass

# Webhook handlers for payment notifications
@frappe.whitelist(allow_guest=True)
def stripe_webhook():
    """Handle Stripe webhooks"""
    # Verify webhook signature and process events
    pass

@frappe.whitelist(allow_guest=True) 
def paypal_webhook():
    """Handle PayPal webhooks"""
    # Process PayPal IPN notifications
    pass

@frappe.whitelist(allow_guest=True)
def razorpay_webhook():
    """Handle Razorpay webhooks"""
    # Process Razorpay webhook events
    pass

@frappe.whitelist(allow_guest=True)
def paystack_webhook():
    """Handle Paystack webhooks"""
    import hashlib
    import hmac
    
    try:
        # Get webhook secret from config
        webhook_secret = frappe.conf.get("paystack_webhook_secret")
        if not webhook_secret:
            frappe.log_error("Paystack webhook secret not configured")
            return
        
        # Get request data
        payload = frappe.request.data
        signature = frappe.request.headers.get("x-paystack-signature")
        
        if not signature or not payload:
            frappe.log_error("Invalid Paystack webhook request")
            return
        
        # Verify signature
        expected_signature = hmac.new(
            webhook_secret.encode(),
            payload,
            hashlib.sha512
        ).hexdigest()
        
        if signature != expected_signature:
            frappe.log_error("Invalid Paystack webhook signature")
            return
        
        # Process webhook event
        import json
        event_data = json.loads(payload)
        
        if event_data.get("event") == "charge.success":
            # Handle successful charge
            data = event_data.get("data", {})
            reference = data.get("reference")
            metadata = data.get("metadata", {})
            
            if metadata.get("app") == "laundrycloud":
                # Verify and activate license
                payment_data = {
                    "payment_method": "paystack",
                    "reference": reference
                }
                
                result = verify_paystack_payment(payment_data)
                frappe.log_error(f"Paystack webhook processed: {result}")
        
    except Exception as e:
        frappe.log_error(f"Paystack webhook error: {str(e)}")