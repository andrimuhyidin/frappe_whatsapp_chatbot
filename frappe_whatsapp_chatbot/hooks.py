from . import __version__ as app_version
app_name = "frappe_whatsapp_chatbot"
app_title = "Frappe WhatsApp Chatbot"
app_publisher = "Shridhar Patil"
app_description = "WhatsApp Chatbot for Frappe with keyword replies, conversation flows, and optional AI"
app_email = "shrip.dev@gmail.com"
app_license = "MIT with Commons Clause"
required_apps = ["shridarpatil/frappe_whatsapp"]

# Module Setup
# ------------
setup = {
    "module_icon": "cpu",
    "module_name": "Frappe Whatsapp Chatbot",
    "type": "module",
    "color": "#9B59B6",
    "category": "Integrations"
}

# Document Events
doc_events = {
    "WhatsApp Message": {
        "after_insert": "frappe_whatsapp_chatbot.chatbot.processor.process_incoming_message"
    }
}

# Scheduler Events
scheduler_events = {
    "hourly": [
        "frappe_whatsapp_chatbot.chatbot.session_manager.cleanup_expired_sessions"
    ]
}

# Fixtures - export these DocTypes when exporting fixtures
fixtures = []

# Website route rules
website_route_rules = []

# Desk modules
# Each module is linked to a workspace
# modules = [
#     {"module_name": "Frappe WhatsApp Chatbot", "category": "Modules"}
# ]
