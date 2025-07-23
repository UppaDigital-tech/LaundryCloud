# LaundryCloud - ERPNext Laundry Management System

LaundryCloud is a comprehensive laundry management system built for ERPNext, inspired by CleanCloud's functionality but designed to seamlessly integrate with ERPNext's ecosystem. This app provides everything needed to run a modern laundry business, from point-of-sale operations to pickup & delivery management.

## Features

### 🏪 Point of Sale (POS)
- **Modern POS Interface**: Touch-friendly interface similar to POSAwesome
- **Service-based Sales**: Designed specifically for laundry services rather than products
- **Multiple Payment Methods**: Cash, Card, Digital Wallet, Credit
- **Customer Management**: Quick customer search and selection
- **Receipt Printing**: Automatic receipt generation with QR codes
- **Barcode Support**: Scan services and track orders via barcodes
- **Real-time Calculations**: Automatic tax, discount, and total calculations

### 📦 Order Management
- **Comprehensive Order Tracking**: From receipt to delivery
- **Multiple Order Types**: In-Store, Pickup & Delivery, Locker, Subscription
- **Service Categories**: Dry Cleaning, Wash & Fold, Laundromat, Ironing, Alterations, Shoe Cleaning
- **QR Code Generation**: Automatic QR codes for order tracking
- **Status Workflow**: Draft → Received → In Progress → Ready → Delivered → Completed
- **Customer Notifications**: Email and SMS notifications for status updates

### 🚚 Pickup & Delivery
- **Route Management**: Optimize delivery routes
- **Driver Assignment**: Assign drivers to pickup/delivery orders
- **Time Slot Management**: Flexible pickup and delivery scheduling
- **Address Management**: Store pickup and delivery addresses
- **Tracking**: Real-time order tracking for customers

### 👥 Customer Management
- **Customer Profiles**: Store customer preferences and history
- **Loyalty Programs**: Built-in loyalty point system
- **Subscription Services**: Recurring pickup schedules
- **Communication**: Automated notifications via email/SMS
- **Order History**: Complete order history and preferences

### 💼 Business Intelligence
- **Dashboard Analytics**: Sales, orders, and performance metrics
- **Service Performance**: Track popular services and revenue
- **Customer Analytics**: Customer behavior and retention
- **Financial Reports**: Revenue, profit, and payment analysis
- **Operational Reports**: Order status, delivery performance

### 🔧 Service Management
- **Service Catalog**: Define laundry services with pricing
- **Category Management**: Organize services by type
- **Pricing Rules**: Flexible pricing based on quantity, weight, or special requirements
- **Processing Times**: Set standard and express processing times
- **Special Care Instructions**: Handle delicate items with special requirements

### 🏭 Operations Management
- **Machine Management**: Track washing machines and equipment
- **Wash Cycles**: Define and track different wash cycles
- **Staff Management**: Employee tracking and productivity
- **Inventory**: Track cleaning supplies and materials
- **Quality Control**: Photo documentation and condition notes

## Installation

### Prerequisites
- ERPNext version 14.0 or later
- Python 3.8+
- Node.js 14+

### Installation Steps

1. **Get the app from GitHub:**
   ```bash
   bench get-app https://github.com/your-org/laundrycloud.git
   ```

2. **Install the app on your site:**
   ```bash
   bench --site your-site-name install-app laundrycloud
   ```

3. **Build and restart:**
   ```bash
   bench build --app laundrycloud
   bench restart
   ```

### Manual Installation

If you don't have bench available, follow these steps:

1. **Clone or download this repository to your ERPNext apps directory**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add the app to your site's apps.txt file**

4. **Run database migrations:**
   ```bash
   frappe migrate
   ```

## Configuration

### 1. Initial Setup

After installation, configure the following:

1. **Company Settings**: Set up your laundry business information
2. **POS Profile**: Create a LaundryCloud POS Profile with payment methods
3. **Services**: Add your laundry services with pricing
4. **Staff Users**: Create user accounts for your staff
5. **Customer Data**: Import existing customers or start fresh

### 2. POS Configuration

1. Go to **LaundryCloud > Point of Sale > Laundry POS Profile**
2. Create a new profile with:
   - Company and branch information
   - Payment methods (Cash, Card, etc.)
   - Default customer for walk-ins
   - Receipt settings
3. Set one profile as default

### 3. Service Setup

1. Go to **LaundryCloud > Laundry Management > Laundry Service**
2. Create services for each offering:
   - Service name and category
   - Pricing and currency
   - Processing times
   - Special requirements
3. Add service images and icons for better POS experience

### 4. Pickup & Delivery Setup

1. Configure delivery zones and charges
2. Set up driver accounts (Employee records)
3. Define time slots for pickup and delivery
4. Set up notification templates

## Usage

### Using the POS System

1. **Access POS**: Navigate to `/laundrycloud/pos` or use the POS button
2. **Select Customer**: Search and select existing customer or create new
3. **Add Services**: Click on service cards to add to cart
4. **Adjust Quantities**: Use +/- buttons to modify quantities
5. **Apply Discounts**: Enter discount amount if applicable
6. **Select Payment**: Choose payment method
7. **Complete Order**: Click "Complete Order" to finalize

### Managing Orders

1. **View Orders**: Go to **LaundryCloud > Laundry Management > Laundry Order**
2. **Track Progress**: Update order status as items move through workflow
3. **Schedule Delivery**: Set pickup and delivery times
4. **Customer Communication**: Automatic notifications sent on status changes

### Reports and Analytics

1. **Dashboard**: Overview of daily/weekly/monthly performance
2. **Order Reports**: Detailed order analysis and trends
3. **Customer Reports**: Customer behavior and loyalty analysis
4. **Financial Reports**: Revenue, payment, and profitability analysis

## Customization

### Adding Custom Fields

Use ERPNext's customization features to add fields:

1. Go to **Setup > Customize > Custom Field**
2. Select the DocType to customize
3. Add your custom fields
4. The app will automatically include them in forms

### Custom Print Formats

1. Create custom print formats for receipts and invoices
2. Set them in the POS Profile configuration
3. Use Jinja templating for dynamic content

### Workflows

1. Create custom workflows for order processing
2. Define states and transitions
3. Set up approval processes if needed

## API Integration

LaundryCloud provides REST APIs for:

- Order creation and management
- Customer data synchronization
- Service catalog access
- Payment processing
- Status tracking

See the API documentation for detailed endpoints and usage.

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

### Community Support
- GitHub Issues: Report bugs and request features
- ERPNext Community Forum: Ask questions and share experiences

### Professional Support
- Implementation services
- Custom development
- Training and consultation
- Priority support

## License

This project is licensed under the MIT License - see the [LICENSE](license.txt) file for details.

## Acknowledgments

- Inspired by CleanCloud's comprehensive laundry management features
- Built on the excellent ERPNext framework
- UI/UX inspired by POSAwesome for ERPNext
- Thanks to the ERPNext community for their continuous support

## Architecture

### DocTypes Overview

#### Core Documents
- **Laundry Order**: Main order document with customer, items, and status
- **Laundry Order Item**: Child table for order line items
- **Laundry Service**: Service catalog with pricing and details
- **Laundry POS Profile**: POS configuration and settings

#### Management Documents
- **Pickup Delivery**: Delivery route and driver management
- **Customer Subscription**: Recurring service subscriptions
- **Laundry Machine**: Equipment tracking and maintenance
- **Wash Cycle**: Wash cycle definitions and tracking

#### Support Documents
- **Service Category**: Organize services by type
- **Delivery Zone**: Geographic delivery areas
- **Driver Schedule**: Driver availability and routes

### Technology Stack

- **Backend**: Python, Frappe Framework
- **Frontend**: JavaScript, jQuery, Vue.js components
- **Database**: MariaDB/MySQL
- **Styling**: CSS3, Bootstrap, Custom themes
- **APIs**: RESTful APIs with Frappe's built-in framework

### Integration Points

- **ERPNext Sales**: Automatic Sales Invoice creation
- **ERPNext Accounts**: Payment Entry integration
- **ERPNext CRM**: Customer management
- **ERPNext HR**: Employee and driver management
- **ERPNext Stock**: Inventory management for supplies

## Roadmap

### Version 1.1
- [ ] Mobile app for customers
- [ ] Advanced analytics dashboard
- [ ] Integration with popular payment gateways
- [ ] Multi-language support

### Version 1.2
- [ ] IoT integration for machines
- [ ] AI-powered demand forecasting
- [ ] Advanced loyalty programs
- [ ] WhatsApp integration

### Version 2.0
- [ ] Multi-tenant support
- [ ] Franchise management
- [ ] Advanced reporting engine
- [ ] Third-party marketplace integration

## Getting Started Quickly

### Demo Data
The app includes sample data for quick testing:
- Demo services and pricing
- Sample customers
- Test orders and workflows

### Quick Setup Checklist
- [ ] Install LaundryCloud app
- [ ] Create Company and Branch
- [ ] Set up Laundry POS Profile
- [ ] Add 3-5 basic services
- [ ] Create a test customer
- [ ] Process a test order through POS
- [ ] Test order workflow and notifications

## Troubleshooting

### Common Issues

1. **POS not loading**: Check JavaScript console for errors, ensure app assets are built
2. **Services not appearing**: Verify services are marked as "Active"
3. **Payment errors**: Check Mode of Payment configuration
4. **Email notifications not working**: Configure Email Account in ERPNext

### Performance Optimization

1. **Database Indexing**: Ensure proper indexes on search fields
2. **Caching**: Enable Redis caching for better performance
3. **Image Optimization**: Compress service images for faster loading
4. **Background Jobs**: Use Frappe's background job system for heavy operations

For more detailed documentation, visit our [Wiki](https://github.com/your-org/laundrycloud/wiki) or contact our support team.