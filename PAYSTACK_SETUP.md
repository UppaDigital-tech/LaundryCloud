# 🇳🇬 Paystack Integration for LaundryCloud

## Quick Setup for Paystack

### 1. Get Your Paystack Credentials

1. **Sign up/Login** to [Paystack Dashboard](https://dashboard.paystack.com)
2. **Get your keys** from Settings > API Keys & Webhooks
   - Public Key: `pk_test_...` (for test) or `pk_live_...` (for live)
   - Secret Key: `sk_test_...` (for test) or `sk_live_...` (for live)

### 2. Configure ERPNext

Add to your `site_config.json`:

#### Test Configuration (Nigeria)
```json
{
  "laundrycloud_payment_gateway": "paystack",
  "paystack_public_key": "pk_test_xxxxxxxxxx",
  "paystack_secret_key": "sk_test_xxxxxxxxxx",
  "paystack_webhook_secret": "your_webhook_secret",
  "laundrycloud_currency": "NGN"
}
```

#### Test Configuration (Ghana)
```json
{
  "laundrycloud_payment_gateway": "paystack",
  "paystack_public_key": "pk_test_xxxxxxxxxx",
  "paystack_secret_key": "sk_test_xxxxxxxxxx", 
  "paystack_webhook_secret": "your_webhook_secret",
  "laundrycloud_currency": "GHS"
}
```

#### Test Configuration (South Africa)
```json
{
  "laundrycloud_payment_gateway": "paystack",
  "paystack_public_key": "pk_test_xxxxxxxxxx",
  "paystack_secret_key": "sk_test_xxxxxxxxxx",
  "paystack_webhook_secret": "your_webhook_secret",
  "laundrycloud_currency": "ZAR"
}
```

#### Live Configuration
```json
{
  "laundrycloud_payment_gateway": "paystack",
  "paystack_public_key": "pk_live_xxxxxxxxxx", 
  "paystack_secret_key": "sk_live_xxxxxxxxxx",
  "paystack_webhook_secret": "your_webhook_secret",
  "laundrycloud_currency": "NGN"
}
```

### 3. Setup Webhooks (Optional but Recommended)

1. **Go to** Settings > API Keys & Webhooks in Paystack Dashboard
2. **Add webhook URL**: `https://your-site.com/api/method/laundrycloud.laundrycloud.api.payment.paystack_webhook`
3. **Select events**: `charge.success`
4. **Copy webhook secret** and add to site_config.json

### 4. Multi-Currency Pricing

The system automatically uses local currency pricing when Paystack is configured:

#### Nigeria (NGN) - Default
- **Basic Plan**: ₦15,000/year
- **Professional Plan**: ₦40,000/year  
- **Enterprise Plan**: ₦100,000/year

#### Ghana (GHS)
- **Basic Plan**: GH₵180/year
- **Professional Plan**: GH₵480/year  
- **Enterprise Plan**: GH₵1,200/year

#### South Africa (ZAR)
- **Basic Plan**: R450/year
- **Professional Plan**: R1,200/year  
- **Enterprise Plan**: R3,000/year

### 5. Test the Integration

1. **Start with test keys** first
2. **Create a trial license** to test the system
3. **Make a test payment** using Paystack test cards
4. **Verify license activation** works correctly
5. **Switch to live keys** when ready

## Paystack Test Cards

Use these for testing:

```
Successful Payment:
Card: 4084084084084081
CVV: 408
Expiry: Any future date
PIN: 0000
OTP: 123456

Failed Payment:
Card: 4084084084084094
```

## Features with Paystack

✅ **Automatic license activation** after payment  
✅ **NGN pricing** optimized for Nigerian market  
✅ **Secure webhook verification**  
✅ **Test/Live mode support**  
✅ **Beautiful payment UI**  
✅ **Mobile-friendly checkout**  

## Troubleshooting

### Payment Not Working?
```bash
# Check configuration
bench console
>>> frappe.conf.paystack_public_key
>>> frappe.conf.paystack_secret_key
```

### License Not Activating?
1. Check webhook is configured correctly
2. Verify webhook secret matches
3. Check Error Logs in ERPNext

### Currency Issues?
The system automatically uses NGN when Paystack is configured. No manual changes needed.

## Support

- **Paystack Docs**: https://paystack.com/docs
- **Test Environment**: Use test keys for development
- **Go Live**: Switch to live keys for production

## Nigerian Business Benefits

- **Local payment methods**: Cards, Bank Transfer, USSD
- **No international fees** for customers
- **Familiar checkout** experience
- **NGN pricing** - no currency conversion
- **Fast settlement** to Nigerian banks

## Next Steps

1. ✅ Configure Paystack credentials
2. ✅ Test with test cards
3. ✅ Setup webhooks
4. ✅ Switch to live mode
5. 🚀 Start selling licenses!

---

**Ready to accept payments in Nigeria? Paystack integration is live!** 🇳🇬