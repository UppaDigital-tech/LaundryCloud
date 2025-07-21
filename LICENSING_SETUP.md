# 🔐 LaundryCloud Licensing System Setup

## Overview

LaundryCloud includes a comprehensive licensing system that allows you to monetize your app by requiring users to purchase licenses before accessing full functionality. The system supports:

- **Trial licenses** (30-day free trial)
- **Paid licenses** with multiple tiers
- **Multiple payment gateways** (Stripe, PayPal, Razorpay)
- **Online/offline license validation**
- **Feature-based access control**
- **Usage limit enforcement**

## 🚀 Quick Setup

### 1. Payment Gateway Configuration

Add these to your ERPNext `site_config.json`:

#### Stripe Configuration
```json
{
  "laundrycloud_payment_gateway": "stripe",
  "stripe_publishable_key": "pk_test_...",
  "stripe_secret_key": "sk_test_..."
}
```

#### PayPal Configuration
```json
{
  "laundrycloud_payment_gateway": "paypal",
  "paypal_client_id": "your_paypal_client_id",
  "paypal_secret": "your_paypal_secret",
  "paypal_mode": "sandbox"
}
```

#### Razorpay Configuration
```json
{
  "laundrycloud_payment_gateway": "razorpay",
  "razorpay_key_id": "rzp_test_...",
  "razorpay_key_secret": "your_razorpay_secret"
}
```

#### Paystack Configuration
```json
{
  "laundrycloud_payment_gateway": "paystack",
  "paystack_public_key": "pk_test_...",
  "paystack_secret_key": "sk_test_...",
  "paystack_webhook_secret": "your_webhook_secret"
}
```

### 2. Install Required Dependencies

Add to your `requirements.txt`:
```
stripe>=5.0.0
razorpay>=1.3.0
paystackapi>=2.1.0
```

### 3. Run Migrations

After installation, the licensing DocTypes will be created automatically.

## 💰 Pricing Plans

Default pricing plans are defined in `laundrycloud/laundrycloud/api/payment.py`:

### Basic Plan - $29.99/year
- 5 users max
- 1,000 orders/month
- ✅ POS
- ❌ Delivery
- ❌ Advanced Reports

### Professional Plan - $79.99/year
- 15 users max
- 5,000 orders/month
- ✅ POS
- ✅ Delivery
- ✅ Advanced Reports

### Enterprise Plan - $199.99/year
- Unlimited users
- Unlimited orders
- ✅ All features

## 🔧 Customization

### Modify Pricing Plans

Edit `LICENSE_PLANS` in `laundrycloud/laundrycloud/api/payment.py`:

```python
LICENSE_PLANS = {
    "starter": {
        "name": "Starter Plan",
        "price": 19.99,
        "currency": "USD",
        "max_users": 3,
        "max_orders_per_month": 500,
        "features": {
            "pos_enabled": True,
            "delivery_enabled": False,
            "reports_enabled": False
        }
    }
    # Add more plans...
}
```

### Add New Features

1. **Add feature flag to license**:
```python
# In LaundryCloud License DocType
"inventory_enabled": True
```

2. **Add validation**:
```python
# In license_manager.py
def enforce_license_on_inventory():
    if not check_feature_permission("inventory"):
        frappe.throw(_("Inventory feature requires license upgrade"))
```

3. **Protect your feature**:
```python
# In your feature code
@license_required("inventory")
def create_inventory_item():
    # Your feature code here
    pass
```

### Custom License Validation Server

For enterprise deployments, you can set up a central license validation server:

```python
# In site_config.json
{
  "laundrycloud_license_server": "https://your-license-server.com/api"
}
```

## 🎯 Implementation Guide

### Step 1: Feature Protection

Protect your features with license checks:

```javascript
// Frontend protection
laundrycloud.license.enforce_feature_access('delivery', 
    function() {
        // Feature code here
        open_delivery_screen();
    },
    function() {
        // Show upgrade message
        show_upgrade_dialog();
    }
);
```

```python
# Backend protection
from laundrycloud.laundrycloud.license_manager import license_required

@frappe.whitelist()
@license_required("delivery")
def create_delivery_trip():
    # Your API code here
    pass
```

### Step 2: Usage Limits

Enforce usage limits automatically:

```python
# This is called automatically on document save
def check_usage_limits():
    license_doc = get_active_license()
    if not license_doc.check_usage_limits("orders"):
        frappe.throw(_("Monthly order limit exceeded"))
```

### Step 3: Trial Management

Users can start a 30-day trial:

```javascript
// Start trial
laundrycloud.license.start_trial();

// Check if trial
if (license_info.is_trial && license_info.days_remaining <= 7) {
    show_upgrade_reminder();
}
```

## 🔐 Security Features

### License Binding
- Hardware fingerprint binding
- Site URL validation
- Installation ID tracking

### Validation Methods
- **Online validation**: Checks with remote server
- **Offline validation**: Works for up to 7 days offline
- **Hash verification**: Prevents tampering

### Anti-Piracy
- Regular license validation
- Usage analytics
- Automatic suspension for violations

## 🎨 User Experience

### Licensing UI Flow

1. **First Access**: User sees license requirement dialog
2. **Trial Option**: 30-day free trial with one click
3. **Purchase Flow**: Beautiful pricing table with payment integration
4. **Activation**: Simple license key + activation code entry
5. **Status Indicator**: Always-visible license status in navbar

### Payment Flow

1. User selects plan from pricing table
2. Redirected to payment gateway (Stripe/PayPal/Razorpay)
3. Payment processed securely
4. License auto-activated upon successful payment
5. Activation details sent via email

## 📊 Analytics & Monitoring

### License Analytics

Track license usage:
- Active installations
- Feature usage statistics
- Payment conversion rates
- Trial-to-paid conversion

### Usage Monitoring

Monitor per-license:
- Monthly order volume
- Active user count
- Feature access patterns
- Login frequency

## 🚨 Troubleshooting

### Common Issues

**Payment Gateway Not Working**
```bash
# Check configuration
bench console
>>> frappe.conf.stripe_secret_key
>>> frappe.conf.laundrycloud_payment_gateway
```

**License Validation Failing**
```python
# Force license refresh
frappe.call({
    method: 'laundrycloud.laundrycloud.license_manager.validate_license',
    callback: function(r) { console.log(r.message); }
});
```

**Trial Not Working**
```sql
-- Check existing trials
SELECT * FROM `tabLaundryCloud License` WHERE is_trial = 1;
```

### Debug Mode

Enable debugging in `site_config.json`:
```json
{
  "laundrycloud_license_debug": true
}
```

## 🔄 Migration & Updates

### Updating License System

When updating the licensing system:

1. **Backup licenses**:
```bash
bench backup --only-database
```

2. **Run patches**:
```bash
bench migrate
```

3. **Update payment gateway configs** if needed

### License Migration

Moving licenses between installations:

1. Export license data
2. Update site URLs in licenses
3. Re-activate with new hardware fingerprint

## 💡 Advanced Features

### Custom License Types

Add custom license types:
```python
# In LaundryCloud License DocType
license_type_options = "Trial\nCommercial\nEnterprise\nLifetime\nEducational\nNon-Profit"
```

### White-Label Licensing

Customize for your brand:
```javascript
// In license_manager.js
const BRAND_CONFIG = {
    name: "Your App Name",
    support_email: "support@yourapp.com",
    purchase_url: "https://yourapp.com/purchase"
};
```

### API Integration

Integrate with external systems:
```python
@frappe.whitelist()
def sync_license_with_crm(license_key):
    # Sync with external CRM/billing system
    pass
```

## 📞 Support

### For Developers

- **Documentation**: Full API docs in code comments
- **Examples**: See existing implementations
- **Testing**: Use sandbox payment gateways

### For End Users

- **Trial**: 30-day free trial available
- **Support**: Email support included with all plans
- **Migration**: Assistance with license transfers

## 🎉 Getting Started

1. **Configure payment gateway** (choose one: Stripe/PayPal/Razorpay)
2. **Customize pricing plans** if needed
3. **Test with sandbox credentials**
4. **Deploy to production**
5. **Start selling licenses!**

The licensing system is designed to be plug-and-play. Most users can get started with just payment gateway configuration.

---

**Ready to monetize your LaundryCloud app? Get started with the licensing system today!** 🚀