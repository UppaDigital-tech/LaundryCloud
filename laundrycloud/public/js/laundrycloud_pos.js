// LaundryCloud POS JavaScript
class LaundryCloudPOS {
    constructor() {
        this.init();
    }

    init() {
        this.setup_pos_interface();
        this.bind_events();
        this.load_pos_profile();
    }

    setup_pos_interface() {
        // Create POS interface layout
        this.create_pos_layout();
        this.setup_service_grid();
        this.setup_cart();
        this.setup_payment_section();
        this.setup_customer_section();
    }

    create_pos_layout() {
        const pos_wrapper = $(`
            <div class="laundrycloud-pos-wrapper">
                <div class="pos-header">
                    <div class="header-left">
                        <h3>LaundryCloud POS</h3>
                        <span class="pos-profile-name"></span>
                    </div>
                    <div class="header-right">
                        <button class="btn btn-primary btn-new-order" id="new-order">New Order</button>
                        <button class="btn btn-secondary btn-settings" id="pos-settings">Settings</button>
                        <button class="btn btn-danger btn-close-pos" id="close-pos">Close POS</button>
                    </div>
                </div>
                <div class="pos-body">
                    <div class="pos-left-panel">
                        <div class="customer-section">
                            <div class="customer-header">
                                <h4>Customer</h4>
                                <button class="btn btn-sm btn-primary" id="add-customer">Add Customer</button>
                            </div>
                            <div class="customer-details">
                                <input type="text" class="form-control" id="customer-search" placeholder="Search customer...">
                                <div class="selected-customer" style="display:none;">
                                    <div class="customer-info">
                                        <strong class="customer-name"></strong>
                                        <div class="customer-phone"></div>
                                        <div class="customer-email"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="services-section">
                            <div class="services-header">
                                <h4>Services</h4>
                                <div class="service-filters">
                                    <select class="form-control" id="service-category">
                                        <option value="">All Categories</option>
                                        <option value="Dry Cleaning">Dry Cleaning</option>
                                        <option value="Wash & Fold">Wash & Fold</option>
                                        <option value="Laundromat">Laundromat</option>
                                        <option value="Ironing">Ironing</option>
                                        <option value="Alterations">Alterations</option>
                                        <option value="Shoe Cleaning">Shoe Cleaning</option>
                                    </select>
                                </div>
                            </div>
                            <div class="services-grid" id="services-grid">
                                <!-- Services will be loaded here -->
                            </div>
                        </div>
                    </div>
                    <div class="pos-right-panel">
                        <div class="cart-section">
                            <div class="cart-header">
                                <h4>Order Items</h4>
                                <button class="btn btn-sm btn-warning" id="clear-cart">Clear</button>
                            </div>
                            <div class="cart-items" id="cart-items">
                                <!-- Cart items will be displayed here -->
                            </div>
                            <div class="cart-totals">
                                <div class="subtotal">
                                    <span>Subtotal:</span>
                                    <span class="amount" id="subtotal">$0.00</span>
                                </div>
                                <div class="tax">
                                    <span>Tax:</span>
                                    <span class="amount" id="tax-amount">$0.00</span>
                                </div>
                                <div class="discount">
                                    <span>Discount:</span>
                                    <input type="number" class="form-control discount-input" id="discount-amount" min="0" value="0">
                                </div>
                                <div class="total">
                                    <span><strong>Total:</strong></span>
                                    <span class="amount" id="total-amount"><strong>$0.00</strong></span>
                                </div>
                            </div>
                        </div>
                        <div class="payment-section">
                            <div class="payment-header">
                                <h4>Payment</h4>
                            </div>
                            <div class="payment-methods">
                                <button class="btn btn-payment cash" data-method="Cash">Cash</button>
                                <button class="btn btn-payment card" data-method="Card">Card</button>
                                <button class="btn btn-payment digital" data-method="Digital Wallet">Digital</button>
                                <button class="btn btn-payment credit" data-method="Credit">Credit</button>
                            </div>
                            <div class="payment-amount">
                                <input type="number" class="form-control" id="payment-amount" placeholder="Payment amount">
                            </div>
                            <div class="order-actions">
                                <button class="btn btn-success btn-lg" id="complete-order">Complete Order</button>
                                <button class="btn btn-info" id="hold-order">Hold Order</button>
                                <button class="btn btn-warning" id="print-receipt">Print Receipt</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `);

        $('body').append(pos_wrapper);
    }

    setup_service_grid() {
        // Load services and display in grid
        frappe.call({
            method: 'laundrycloud.api.pos.get_active_services',
            callback: (r) => {
                if (r.message) {
                    this.render_services(r.message);
                }
            }
        });
    }

    render_services(services) {
        const grid = $('#services-grid');
        grid.empty();

        services.forEach(service => {
            const service_card = $(`
                <div class="service-card" data-service="${service.name}">
                    <div class="service-image">
                        ${service.image ? `<img src="${service.image}" alt="${service.service_name}">` : 
                          `<div class="service-icon"><i class="${service.icon || 'fa fa-tshirt'}"></i></div>`}
                    </div>
                    <div class="service-info">
                        <div class="service-name">${service.service_name}</div>
                        <div class="service-rate">$${service.rate}</div>
                        <div class="service-category">${service.category}</div>
                    </div>
                </div>
            `);
            grid.append(service_card);
        });
    }

    setup_cart() {
        this.cart = [];
        this.update_cart_display();
    }

    add_to_cart(service) {
        const existing_item = this.cart.find(item => item.service === service.name);
        
        if (existing_item) {
            existing_item.quantity += 1;
            existing_item.amount = existing_item.quantity * existing_item.rate;
        } else {
            this.cart.push({
                service: service.name,
                service_name: service.service_name,
                quantity: 1,
                rate: service.rate,
                amount: service.rate,
                category: service.category
            });
        }
        
        this.update_cart_display();
        this.calculate_totals();
    }

    update_cart_display() {
        const cart_container = $('#cart-items');
        cart_container.empty();

        if (this.cart.length === 0) {
            cart_container.html('<div class="empty-cart">No items in cart</div>');
            return;
        }

        this.cart.forEach((item, index) => {
            const cart_item = $(`
                <div class="cart-item" data-index="${index}">
                    <div class="item-info">
                        <div class="item-name">${item.service_name}</div>
                        <div class="item-category">${item.category}</div>
                    </div>
                    <div class="item-controls">
                        <button class="btn btn-sm btn-qty-minus" data-index="${index}">-</button>
                        <span class="item-quantity">${item.quantity}</span>
                        <button class="btn btn-sm btn-qty-plus" data-index="${index}">+</button>
                    </div>
                    <div class="item-rate">$${item.rate}</div>
                    <div class="item-amount">$${item.amount.toFixed(2)}</div>
                    <button class="btn btn-sm btn-remove-item" data-index="${index}">×</button>
                </div>
            `);
            cart_container.append(cart_item);
        });
    }

    calculate_totals() {
        const subtotal = this.cart.reduce((sum, item) => sum + item.amount, 0);
        const discount = parseFloat($('#discount-amount').val()) || 0;
        const tax_rate = 0.1; // 10% tax (should be configurable)
        const tax_amount = (subtotal - discount) * tax_rate;
        const total = subtotal - discount + tax_amount;

        $('#subtotal').text(`$${subtotal.toFixed(2)}`);
        $('#tax-amount').text(`$${tax_amount.toFixed(2)}`);
        $('#total-amount').text(`$${total.toFixed(2)}`);
    }

    bind_events() {
        // Service card click
        $(document).on('click', '.service-card', (e) => {
            const service_name = $(e.currentTarget).data('service');
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Laundry Service',
                    name: service_name
                },
                callback: (r) => {
                    if (r.message) {
                        this.add_to_cart(r.message);
                    }
                }
            });
        });

        // Cart quantity controls
        $(document).on('click', '.btn-qty-plus', (e) => {
            const index = $(e.target).data('index');
            this.cart[index].quantity += 1;
            this.cart[index].amount = this.cart[index].quantity * this.cart[index].rate;
            this.update_cart_display();
            this.calculate_totals();
        });

        $(document).on('click', '.btn-qty-minus', (e) => {
            const index = $(e.target).data('index');
            if (this.cart[index].quantity > 1) {
                this.cart[index].quantity -= 1;
                this.cart[index].amount = this.cart[index].quantity * this.cart[index].rate;
                this.update_cart_display();
                this.calculate_totals();
            }
        });

        // Remove item
        $(document).on('click', '.btn-remove-item', (e) => {
            const index = $(e.target).data('index');
            this.cart.splice(index, 1);
            this.update_cart_display();
            this.calculate_totals();
        });

        // Clear cart
        $('#clear-cart').click(() => {
            this.cart = [];
            this.update_cart_display();
            this.calculate_totals();
        });

        // Discount change
        $('#discount-amount').on('input', () => {
            this.calculate_totals();
        });

        // Payment method selection
        $('.btn-payment').click((e) => {
            $('.btn-payment').removeClass('active');
            $(e.target).addClass('active');
            this.selected_payment_method = $(e.target).data('method');
        });

        // Complete order
        $('#complete-order').click(() => {
            this.complete_order();
        });

        // Customer search
        $('#customer-search').on('input', debounce((e) => {
            this.search_customers($(e.target).val());
        }, 300));

        // New order
        $('#new-order').click(() => {
            this.new_order();
        });
    }

    search_customers(query) {
        if (query.length < 2) return;

        frappe.call({
            method: 'laundrycloud.api.pos.search_customers',
            args: { query: query },
            callback: (r) => {
                if (r.message) {
                    this.show_customer_results(r.message);
                }
            }
        });
    }

    show_customer_results(customers) {
        // Create dropdown with customer results
        const dropdown = $(`
            <div class="customer-dropdown">
                ${customers.map(customer => `
                    <div class="customer-option" data-customer="${customer.name}">
                        <strong>${customer.customer_name}</strong>
                        <div>${customer.mobile_no || ''}</div>
                    </div>
                `).join('')}
            </div>
        `);
        
        $('.customer-details').append(dropdown);

        // Handle customer selection
        $('.customer-option').click((e) => {
            const customer_name = $(e.currentTarget).data('customer');
            this.select_customer(customer_name);
            $('.customer-dropdown').remove();
        });
    }

    select_customer(customer_name) {
        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'Customer',
                name: customer_name
            },
            callback: (r) => {
                if (r.message) {
                    this.selected_customer = r.message;
                    $('.customer-name').text(r.message.customer_name);
                    $('.customer-phone').text(r.message.mobile_no || '');
                    $('.customer-email').text(r.message.email_id || '');
                    $('.selected-customer').show();
                    $('#customer-search').hide();
                }
            }
        });
    }

    complete_order() {
        if (this.cart.length === 0) {
            frappe.msgprint('Please add items to cart');
            return;
        }

        if (!this.selected_payment_method) {
            frappe.msgprint('Please select a payment method');
            return;
        }

        const order_data = {
            customer: this.selected_customer ? this.selected_customer.name : null,
            order_type: 'In-Store',
            items: this.cart,
            payment_method: this.selected_payment_method,
            subtotal: this.cart.reduce((sum, item) => sum + item.amount, 0),
            discount_amount: parseFloat($('#discount-amount').val()) || 0,
            total_amount: parseFloat($('#total-amount').text().replace('$', '')),
            pos_profile: this.pos_profile
        };

        frappe.call({
            method: 'laundrycloud.api.pos.create_order',
            args: { order_data: order_data },
            callback: (r) => {
                if (r.message) {
                    frappe.msgprint('Order created successfully!');
                    this.new_order();
                    this.print_receipt(r.message);
                }
            }
        });
    }

    new_order() {
        this.cart = [];
        this.selected_customer = null;
        this.selected_payment_method = null;
        
        this.update_cart_display();
        this.calculate_totals();
        
        $('.selected-customer').hide();
        $('#customer-search').show().val('');
        $('.btn-payment').removeClass('active');
        $('#discount-amount').val(0);
        $('#payment-amount').val('');
    }

    print_receipt(order) {
        // Open print dialog with receipt
        const receipt_window = window.open('', '_blank');
        receipt_window.document.write(this.generate_receipt_html(order));
        receipt_window.document.close();
        receipt_window.print();
    }

    generate_receipt_html(order) {
        return `
            <html>
            <head>
                <title>Receipt - ${order.name}</title>
                <style>
                    body { font-family: Arial, sans-serif; width: 300px; margin: 0 auto; }
                    .header { text-align: center; margin-bottom: 20px; }
                    .order-info { margin-bottom: 15px; }
                    .items { margin-bottom: 15px; }
                    .item { display: flex; justify-content: space-between; margin-bottom: 5px; }
                    .totals { border-top: 1px solid #000; padding-top: 10px; }
                    .total-line { display: flex; justify-content: space-between; margin-bottom: 5px; }
                    .footer { text-align: center; margin-top: 20px; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>LaundryCloud</h2>
                    <p>Thank you for your business!</p>
                </div>
                <div class="order-info">
                    <div><strong>Order:</strong> ${order.name}</div>
                    <div><strong>Date:</strong> ${order.order_date}</div>
                    <div><strong>Customer:</strong> ${order.customer_name || 'Walk-in'}</div>
                </div>
                <div class="items">
                    ${order.items.map(item => `
                        <div class="item">
                            <span>${item.service_name} x${item.quantity}</span>
                            <span>$${item.amount.toFixed(2)}</span>
                        </div>
                    `).join('')}
                </div>
                <div class="totals">
                    <div class="total-line">
                        <span>Subtotal:</span>
                        <span>$${order.subtotal.toFixed(2)}</span>
                    </div>
                    <div class="total-line">
                        <span>Discount:</span>
                        <span>-$${order.discount_amount.toFixed(2)}</span>
                    </div>
                    <div class="total-line">
                        <span>Tax:</span>
                        <span>$${order.tax_amount.toFixed(2)}</span>
                    </div>
                    <div class="total-line" style="font-weight: bold; border-top: 1px solid #000; padding-top: 5px;">
                        <span>Total:</span>
                        <span>$${order.total_amount.toFixed(2)}</span>
                    </div>
                </div>
                <div class="footer">
                    <p>Thank you for choosing LaundryCloud!</p>
                    <p>Order tracking: ${order.barcode}</p>
                </div>
            </body>
            </html>
        `;
    }

    load_pos_profile() {
        // Load default POS profile
        frappe.call({
            method: 'laundrycloud.api.pos.get_default_pos_profile',
            callback: (r) => {
                if (r.message) {
                    this.pos_profile = r.message;
                    $('.pos-profile-name').text(r.message.profile_name);
                }
            }
        });
    }
}

// Utility function for debouncing
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize POS when page loads
$(document).ready(() => {
    if (window.location.pathname.includes('/laundrycloud/pos')) {
        window.laundrycloud_pos = new LaundryCloudPOS();
    }
});