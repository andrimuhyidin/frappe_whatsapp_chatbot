import frappe
from frappe.tests.utils import FrappeTestCase
from frappe_whatsapp_chatbot.chatbot.processor import ChatbotProcessor
from unittest.mock import MagicMock, patch

class TestCustomResponse(FrappeTestCase):
    def setUp(self):
        # Setup settings
        if not frappe.db.exists("WhatsApp Chatbot"):
             self.settings = frappe.new_doc("WhatsApp Chatbot")
             self.settings.whatsapp_account = "Test Account"
             self.settings.enabled = 1
             self.settings.save(ignore_permissions=True)
        
        # Create a Keyword Reply with Custom response
        self.keyword = frappe.new_doc("WhatsApp Keyword Reply")
        self.keyword.title = "Test Custom Reply"
        self.keyword.keywords = "custom"
        self.keyword.match_type = "Exact"
        self.keyword.response_type = "Custom"
        
        # We will use a real dotted path that exists or mock it
        # For testing, we can use frappe.utils.now as a dummy valid path
        # But better to mock execute_script
        self.keyword.custom_endpoint = "frappe.utils.now" 
        self.keyword.enabled = 1
        self.keyword.save(ignore_permissions=True)

    def tearDown(self):
        frappe.db.delete("WhatsApp Keyword Reply", self.keyword.name)

    @patch('frappe_whatsapp_chatbot.chatbot.processor.ChatbotProcessor.execute_script')
    def test_custom_response_execution(self, mock_execute):
        # Setup mock return
        mock_execute.return_value = "Custom Response Executed"
        
        # Create processor instance
        msg_data = {
            "name": "MSG001",
            "from": "1234567890",
            "message": "custom", # Matches keyword
            "content_type": "text",
            "whatsapp_account": "Test Account"
        }
        
        processor = ChatbotProcessor(msg_data)
        
        # We need to mock get_chatbot_settings and others to isolate process
        with patch.object(processor, 'get_chatbot_settings') as mock_settings:
            mock_settings.return_value = frappe.get_doc("WhatsApp Chatbot")
            
            with patch.object(processor, 'should_process', return_value=True):
                 with patch.object(processor, 'send_response') as mock_send:
                     
                     # force settings to return what we want
                     processor.settings = mock_settings.return_value
                     
                     # Run process
                     processor.process()
                     
                     # Verify execute_script was called with our endpoint
                     mock_execute.assert_called_with("frappe.utils.now")
                     
                     # Verify send_response got the result
                     mock_send.assert_called_with("Custom Response Executed")
