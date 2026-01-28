import frappe
from frappe.model.document import Document


class WhatsAppChatbotSession(Document):
    """
    WhatsApp Chatbot Session for tracking active conversations.
    
    Manages individual user sessions with conversation state,
    message history, and flow progress for personalized interactions.
    """

    def before_save(self):
        # Update last_activity on every save
        if self.status == "Active":
            self.last_activity = frappe.utils.now_datetime()

    def add_message(self, direction, message, step_name=None):
        """Add a message to the session history."""
        self.append("messages", {
            "direction": direction,
            "message": message,
            "timestamp": frappe.utils.now_datetime(),
            "step_name": step_name
        })
