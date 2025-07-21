// License Manager for LaundryCloud
frappe.provide('laundrycloud.license');

laundrycloud.license = {
    
    init: function() {
        this.check_license_status();
        this.setup_license_notifications();
    },
    
    check_license_status: function() {
        frappe.call({
            method: 'laundrycloud.laundrycloud.license_manager.get_license_info_for_ui',
            callback: function(r) {
                if (r.message) {
                    laundrycloud.license.handle_license_status(r.message);
                }
            }
        });
    },
    
    handle_license_status: function(license_info) {
        if (!license_info.valid) {
            this.show_license_required_dialog(license_info);
        } else {
            this.update_license_indicator(license_info);
            if (license_info.is_trial) {
                this.show_trial_notification(license_info);
            }
        }
    },
    
    show_license_required_dialog: function(license_info) {
        let d = new frappe.ui.Dialog({
            title: __('LaundryCloud License Required'),
            fields: [
                {
                    fieldtype: 'HTML',
                    fieldname: 'license_message',
                    options: `
                        <div class="alert alert-warning">
                            <h4><i class="fa fa-lock"></i> License Required</h4>
                            <p>${license_info.message}</p>
                            <p>To use LaundryCloud features, you need an active license.</p>
                        </div>
                    `
                },
                {
                    fieldtype: 'Section Break'
                },
                {
                    fieldtype: 'Button',
                    fieldname: 'start_trial',
                    label: 'Start 30-Day Free Trial',
                    click: function() {
                        laundrycloud.license.start_trial();
                        d.hide();
                    }
                },
                {
                    fieldtype: 'Column Break'
                },
                {
                    fieldtype: 'Button', 
                    fieldname: 'purchase_license',
                    label: 'Purchase License',
                    click: function() {
                        laundrycloud.license.show_purchase_dialog();
                        d.hide();
                    }
                },
                {
                    fieldtype: 'Section Break'
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'license_key',
                    label: 'License Key',
                    description: 'Enter your license key if you already have one'
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'activation_code',
                    label: 'Activation Code',
                    description: 'Enter the activation code received via email'
                }
            ],
            primary_action_label: __('Activate License'),
            primary_action: function() {
                let values = d.get_values();
                if (values.license_key && values.activation_code) {
                    laundrycloud.license.activate_license(values.license_key, values.activation_code);
                    d.hide();
                } else {
                    frappe.msgprint(__('Please enter both License Key and Activation Code'));
                }
            }
        });
        
        d.show();
    },
    
    show_purchase_dialog: function() {
        frappe.call({
            method: 'laundrycloud.laundrycloud.api.payment.get_license_plans',
            callback: function(r) {
                if (r.message) {
                    laundrycloud.license.show_pricing_dialog(r.message);
                }
            }
        });
    },
    
    show_pricing_dialog: function(plans) {
        let plan_html = '';
        
        Object.keys(plans).forEach(function(key) {
            let plan = plans[key];
            let features = '';
            
            if (plan.features.pos_enabled) features += '<li>✓ Point of Sale</li>';
            if (plan.features.delivery_enabled) features += '<li>✓ Pickup & Delivery</li>';
            if (plan.features.reports_enabled) features += '<li>✓ Advanced Reports</li>';
            
            plan_html += `
                <div class="col-md-4">
                    <div class="card license-plan" data-plan="${key}">
                        <div class="card-header text-center">
                            <h4>${plan.name}</h4>
                            <h2>$${plan.price}<small>/year</small></h2>
                        </div>
                        <div class="card-body">
                            <ul class="list-unstyled">
                                <li><strong>Users:</strong> ${plan.max_users === -1 ? 'Unlimited' : plan.max_users}</li>
                                <li><strong>Orders:</strong> ${plan.max_orders_per_month === -1 ? 'Unlimited' : plan.max_orders_per_month + '/month'}</li>
                                ${features}
                            </ul>
                            <button class="btn btn-primary btn-block select-plan" data-plan="${key}">
                                Select Plan
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        let d = new frappe.ui.Dialog({
            title: __('Choose Your LaundryCloud Plan'),
            size: 'extra-large',
            fields: [
                {
                    fieldtype: 'HTML',
                    fieldname: 'pricing_table',
                    options: `
                        <div class="row">
                            ${plan_html}
                        </div>
                        <div class="row mt-3">
                            <div class="col-12 text-center">
                                <p class="text-muted">
                                    <i class="fa fa-shield"></i> Secure payment processing<br>
                                    <i class="fa fa-sync"></i> Cancel anytime<br>
                                    <i class="fa fa-headphones"></i> 24/7 support included
                                </p>
                            </div>
                        </div>
                    `
                }
            ]
        });
        
        d.$wrapper.find('.select-plan').click(function() {
            let plan_id = $(this).data('plan');
            laundrycloud.license.initiate_payment(plan_id);
            d.hide();
        });
        
        d.show();
    },
    
    initiate_payment: function(plan_id) {
        frappe.prompt([
            {
                fieldtype: 'Data',
                fieldname: 'site_url',
                label: 'Site URL',
                default: window.location.origin,
                reqd: 1
            },
            {
                fieldtype: 'Data',
                fieldname: 'contact_email',
                label: 'Contact Email',
                default: frappe.session.user,
                reqd: 1
            }
        ], function(values) {
            frappe.call({
                method: 'laundrycloud.laundrycloud.api.payment.create_payment_session',
                args: {
                    plan_id: plan_id,
                    site_url: values.site_url,
                    contact_email: values.contact_email
                },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        if (r.message.payment_method === 'stripe' || r.message.payment_method === 'paypal') {
                            // Redirect to payment gateway
                            window.open(r.message.payment_url, '_blank');
                        } else if (r.message.payment_method === 'razorpay') {
                            // Handle Razorpay integration
                            laundrycloud.license.handle_razorpay_payment(r.message);
                        }
                    } else {
                        frappe.msgprint(r.message.message || 'Payment initialization failed');
                    }
                }
            });
        }, __('Payment Details'));
    },
    
    handle_razorpay_payment: function(payment_data) {
        var options = {
            "key": payment_data.key,
            "amount": payment_data.amount,
            "currency": payment_data.currency,
            "name": "LaundryCloud",
            "description": "License Purchase",
            "order_id": payment_data.order_id,
            "handler": function (response) {
                laundrycloud.license.verify_razorpay_payment(response);
            },
            "prefill": {
                "email": frappe.session.user
            },
            "theme": {
                "color": "#3399cc"
            }
        };
        
        var rzp1 = new Razorpay(options);
        rzp1.open();
    },
    
    verify_razorpay_payment: function(response) {
        frappe.call({
            method: 'laundrycloud.laundrycloud.api.payment.verify_payment_and_activate_license',
            args: {
                payment_data: {
                    payment_method: 'razorpay',
                    razorpay_payment_id: response.razorpay_payment_id,
                    razorpay_order_id: response.razorpay_order_id,
                    razorpay_signature: response.razorpay_signature
                }
            },
            callback: function(r) {
                if (r.message && r.message.success) {
                    frappe.show_alert({
                        message: 'License activated successfully!',
                        indicator: 'green'
                    });
                    laundrycloud.license.check_license_status();
                } else {
                    frappe.msgprint('Payment verification failed: ' + r.message.message);
                }
            }
        });
    },
    
    start_trial: function() {
        frappe.call({
            method: 'laundrycloud.laundrycloud.doctype.laundrycloud_license.laundrycloud_license.get_trial_license',
            callback: function(r) {
                if (r.message && r.message.success) {
                    frappe.show_alert({
                        message: `Trial license created! You have ${r.message.trial_days} days to explore LaundryCloud.`,
                        indicator: 'green'
                    });
                    laundrycloud.license.check_license_status();
                } else {
                    frappe.msgprint(r.message.message || 'Failed to create trial license');
                }
            }
        });
    },
    
    activate_license: function(license_key, activation_code) {
        frappe.call({
            method: 'laundrycloud.laundrycloud.doctype.laundrycloud_license.laundrycloud_license.activate_license',
            args: {
                license_key: license_key,
                activation_code: activation_code
            },
            callback: function(r) {
                if (r.message && r.message.success) {
                    frappe.show_alert({
                        message: 'License activated successfully!',
                        indicator: 'green'
                    });
                    laundrycloud.license.check_license_status();
                } else {
                    frappe.msgprint(r.message.message || 'License activation failed');
                }
            }
        });
    },
    
    update_license_indicator: function(license_info) {
        // Add license status indicator to navbar
        let indicator_html = '';
        let indicator_class = 'success';
        
        if (license_info.is_trial) {
            indicator_class = 'warning';
            indicator_html = `<span class="badge badge-warning">Trial (${license_info.days_remaining} days left)</span>`;
        } else {
            indicator_html = `<span class="badge badge-success">${license_info.license_type} License</span>`;
        }
        
        // Remove existing indicator
        $('.navbar .license-indicator').remove();
        
        // Add new indicator
        $('.navbar .navbar-nav').append(`
            <li class="nav-item license-indicator">
                <span class="nav-link">${indicator_html}</span>
            </li>
        `);
    },
    
    show_trial_notification: function(license_info) {
        if (license_info.days_remaining <= 7) {
            frappe.show_alert({
                message: `Your trial expires in ${license_info.days_remaining} days. <a href="#" onclick="laundrycloud.license.show_purchase_dialog()">Upgrade now</a>`,
                indicator: 'orange'
            });
        }
    },
    
    setup_license_notifications: function() {
        // Check license status every hour
        setInterval(function() {
            laundrycloud.license.check_license_status();
        }, 3600000); // 1 hour
    },
    
    check_feature_access: function(feature, callback) {
        frappe.call({
            method: 'laundrycloud.laundrycloud.license_manager.check_feature_permission',
            args: {
                feature: feature
            },
            callback: function(r) {
                callback(r.message);
            }
        });
    },
    
    enforce_feature_access: function(feature, success_callback, failure_callback) {
        this.check_feature_access(feature, function(has_access) {
            if (has_access) {
                if (success_callback) success_callback();
            } else {
                let message = `This feature requires a paid license. <a href="#" onclick="laundrycloud.license.show_purchase_dialog()">Upgrade now</a>`;
                frappe.show_alert({
                    message: message,
                    indicator: 'red'
                });
                if (failure_callback) failure_callback();
            }
        });
    }
};

// Initialize license manager when document is ready
$(document).ready(function() {
    // Only initialize if LaundryCloud app is active
    if (frappe.boot.installed_apps && frappe.boot.installed_apps.includes('laundrycloud')) {
        laundrycloud.license.init();
    }
});

// CSS Styles for license dialogs
frappe.ready(function() {
    $('<style>')
        .prop('type', 'text/css')
        .html(`
            .license-plan {
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-bottom: 20px;
                transition: all 0.3s ease;
            }
            
            .license-plan:hover {
                border-color: #3399cc;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                transform: translateY(-2px);
            }
            
            .license-plan .card-header {
                background: linear-gradient(135deg, #3399cc, #2c7aa0);
                color: white;
                border-radius: 8px 8px 0 0;
            }
            
            .license-plan .select-plan {
                background: #3399cc;
                border: none;
                padding: 10px;
                font-weight: bold;
            }
            
            .license-plan .select-plan:hover {
                background: #2c7aa0;
            }
            
            .navbar .license-indicator .badge {
                font-size: 0.75em;
                padding: 4px 8px;
            }
            
            .alert-license {
                position: fixed;
                top: 60px;
                right: 20px;
                width: 350px;
                z-index: 9999;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
        `)
        .appendTo('head');
});