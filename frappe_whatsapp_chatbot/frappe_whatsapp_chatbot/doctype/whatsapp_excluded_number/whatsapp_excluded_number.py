import frappe
from frappe.model.document import Document


class WhatsAppExcludedNumber(Document):
    """
    WhatsApp Excluded Number for chatbot bypass.
    
    Stores phone numbers that should be excluded from
    automated chatbot responses for manual handling.
    """

    pass
