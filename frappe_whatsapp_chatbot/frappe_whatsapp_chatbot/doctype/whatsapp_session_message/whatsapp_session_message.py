import frappe
from frappe.model.document import Document


class WhatsAppSessionMessage(Document):
    """
    WhatsApp Session Message child table entry.
    
    Stores individual messages within a chatbot session
    for conversation history and context tracking.
    """

    pass
