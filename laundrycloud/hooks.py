from . import __version__ as app_version

app_name = "laundrycloud"
app_title = "LaundryCloud"
app_publisher = "LaundryCloud"
app_description = "Comprehensive Laundry Management System for ERPNext with POS, Pickup & Delivery, and Customer Management"
app_icon = "octicon octicon-package"
app_color = "blue"
app_email = "info@laundrycloud.com"
app_license = "MIT"
app_version = app_version

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/laundrycloud/css/laundrycloud.css"
app_include_js = "/assets/laundrycloud/js/laundrycloud.min.js"

# include js, css files in header of web template
web_include_css = "/assets/laundrycloud/css/laundrycloud-web.css"
web_include_js = "/assets/laundrycloud/js/laundrycloud-web.min.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "laundrycloud/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Sales Invoice": "public/js/sales_invoice.js",
    "POS Profile": "public/js/pos_profile.js",
    "Customer": "public/js/customer.js",
    "Item": "public/js/item.js",
    "Sales Order": "public/js/sales_order.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
jinja = {
    "methods": "laundrycloud.utils.jinja_methods",
    "filters": "laundrycloud.utils.jinja_filters"
}

# Installation
# ------------

# before_install = "laundrycloud.install.before_install"
after_install = "laundrycloud.install.after_install"
before_uninstall = "laundrycloud.uninstall.before_uninstall"

# Uninstallation
# ----------------

# before_uninstall = "laundrycloud.uninstall.before_uninstall"
# after_uninstall = "laundrycloud.uninstall.after_uninstall"

# Desk Notifications
# -------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "laundrycloud.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Sales Invoice": {
        "on_submit": "laundrycloud.api.sales_invoice.on_submit",
        "on_cancel": "laundrycloud.api.sales_invoice.on_cancel"
    },
    "Delivery Note": {
        "on_submit": "laundrycloud.api.delivery_note.on_submit"
    },
    "Customer": {
        "after_insert": "laundrycloud.api.customer.after_insert"
    }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "all": [
        "laundrycloud.tasks.all"
    ],
    "daily": [
        "laundrycloud.tasks.daily"
    ],
    "hourly": [
        "laundrycloud.tasks.hourly"
    ],
    "weekly": [
        "laundrycloud.tasks.weekly"
    ],
    "monthly": [
        "laundrycloud.tasks.monthly"
    ],
    "cron": {
        "0 9 * * *": [
            "laundrycloud.tasks.send_pickup_reminders"
        ],
        "0 18 * * *": [
            "laundrycloud.tasks.send_ready_notifications"
        ]
    }
}

# Testing
# -------

# before_tests = "laundrycloud.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "laundrycloud.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "laundrycloud.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]


# Request Events
# ----------------
# before_request = ["laundrycloud.utils.before_request"]
# after_request = ["laundrycloud.utils.after_request"]

# Job Events
# ----------
# before_job = ["laundrycloud.utils.before_job"]
# after_job = ["laundrycloud.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"laundrycloud.auth.validate"
# ]

# LaundryCloud specific configurations
website_route_rules = [
    {"from_route": "/laundrycloud/<path:app_path>", "to_route": "laundrycloud"},
]

# Boot configuration
boot_session = "laundrycloud.boot.get_bootinfo"

# Email
email_brand_image = "/assets/laundrycloud/img/laundrycloud-logo.png"

# Website settings
website_context = {
    "favicon": "/assets/laundrycloud/img/favicon.ico",
    "splash_image": "/assets/laundrycloud/img/laundrycloud-logo.png"
}

# Point of Sale settings for LaundryCloud
point_of_sale = {
    "laundrycloud_pos": {
        "title": "LaundryCloud POS",
        "route": "/laundrycloud/pos"
    }
}