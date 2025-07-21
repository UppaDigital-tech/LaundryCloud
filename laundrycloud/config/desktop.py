from frappe import _

def get_data():
    return [
        {
            "module_name": "LaundryCloud",
            "category": "Modules",
            "label": _("LaundryCloud"),
            "color": "#3498db",
            "icon": "octicon octicon-package",
            "type": "module",
            "description": "Comprehensive Laundry Management System"
        },
        {
            "module_name": "Laundry Management",
            "category": "Modules", 
            "label": _("Laundry Management"),
            "color": "#2ecc71",
            "icon": "fa fa-tshirt",
            "type": "module",
            "description": "Manage laundry orders, services, and items"
        },
        {
            "module_name": "Point of Sale",
            "category": "Modules",
            "label": _("Laundry POS"),
            "color": "#e74c3c",
            "icon": "fa fa-shopping-cart",
            "type": "module", 
            "description": "Point of Sale for laundry services"
        },
        {
            "module_name": "Pickup and Delivery",
            "category": "Modules",
            "label": _("Pickup & Delivery"),
            "color": "#f39c12",
            "icon": "fa fa-truck",
            "type": "module",
            "description": "Manage pickup and delivery services"
        },
        {
            "module_name": "Customer Portal",
            "category": "Modules",
            "label": _("Customer Portal"),
            "color": "#9b59b6",
            "icon": "fa fa-users",
            "type": "module",
            "description": "Customer self-service portal"
        },
        {
            "module_name": "Reports",
            "category": "Modules",
            "label": _("Laundry Reports"),
            "color": "#34495e",
            "icon": "fa fa-chart-bar",
            "type": "module",
            "description": "Business intelligence and reporting"
        },
        {
            "module_name": "Settings",
            "category": "Modules",
            "label": _("Laundry Settings"),
            "color": "#95a5a6",
            "icon": "fa fa-cog",
            "type": "module",
            "description": "Configure LaundryCloud settings"
        }
    ]