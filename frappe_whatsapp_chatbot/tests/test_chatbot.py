import frappe
from frappe.tests import IntegrationTestCase


class TestChatbotDoctypes(IntegrationTestCase):
    """Test that all required doctypes exist."""

    def test_chatbot_settings_exists(self):
        """Test that WhatsApp Chatbot settings doctype exists."""
        self.assertTrue(frappe.db.exists("DocType", "WhatsApp Chatbot"))

    def test_keyword_reply_doctype_exists(self):
        """Test that WhatsApp Keyword Reply doctype exists."""
        self.assertTrue(frappe.db.exists("DocType", "WhatsApp Keyword Reply"))

    def test_chatbot_flow_doctype_exists(self):
        """Test that WhatsApp Chatbot Flow doctype exists."""
        self.assertTrue(frappe.db.exists("DocType", "WhatsApp Chatbot Flow"))

    def test_ai_context_doctype_exists(self):
        """Test that WhatsApp AI Context doctype exists."""
        self.assertTrue(frappe.db.exists("DocType", "WhatsApp AI Context"))

    def test_flow_step_doctype_exists(self):
        """Test that WhatsApp Flow Step doctype exists."""
        self.assertTrue(frappe.db.exists("DocType", "WhatsApp Flow Step"))

    def test_chatbot_session_doctype_exists(self):
        """Test that WhatsApp Chatbot Session doctype exists."""
        self.assertTrue(frappe.db.exists("DocType", "WhatsApp Chatbot Session"))


class TestKeywordMatcher(IntegrationTestCase):
    """Test keyword matching functionality."""

    def setUp(self):
        # Create test keyword reply
        if not frappe.db.exists("WhatsApp Keyword Reply", "Test Greeting"):
            frappe.get_doc({
                "doctype": "WhatsApp Keyword Reply",
                "title": "Test Greeting",
                "keywords": "hello, hi, hey",
                "match_type": "Exact",
                "response_type": "Text",
                "response_text": "Hello! How can I help you?",
                "enabled": 1
            }).insert(ignore_permissions=True)

    def tearDown(self):
        frappe.db.delete("WhatsApp Keyword Reply", {"title": "Test Greeting"})

    def test_exact_match(self):
        """Test exact keyword matching."""
        from frappe_whatsapp_chatbot.chatbot.keyword_matcher import KeywordMatcher

        matcher = KeywordMatcher()
        result = matcher.match("hello")
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "Test Greeting")

    def test_exact_match_case_insensitive(self):
        """Test that exact matching is case insensitive."""
        from frappe_whatsapp_chatbot.chatbot.keyword_matcher import KeywordMatcher

        matcher = KeywordMatcher()
        result = matcher.match("HELLO")
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "Test Greeting")

    def test_no_match(self):
        """Test that non-matching keywords return None."""
        from frappe_whatsapp_chatbot.chatbot.keyword_matcher import KeywordMatcher

        matcher = KeywordMatcher()
        result = matcher.match("goodbye")
        self.assertIsNone(result)


class TestFlowEngine(IntegrationTestCase):
    """Test flow engine functionality."""

    def test_phone_variants(self):
        """Test phone number variant generation."""
        from frappe_whatsapp_chatbot.chatbot.ai_responder import AIResponder

        # Create a mock settings object
        class MockSettings:
            ai_provider = "OpenAI"
            ai_api_key = None
            ai_model = "gpt-4o-mini"
            ai_system_prompt = "Test"
            ai_max_tokens = 500
            ai_temperature = 0.7
            ai_include_history = False
            ai_history_limit = 4

            def get_password(self, field):
                return None

        responder = AIResponder(MockSettings(), phone_number="+919876543210")
        variants = responder.get_phone_variants("+919876543210")

        self.assertIn("+919876543210", variants)
        self.assertIn("919876543210", variants)  # Without +
        self.assertIn("9876543210", variants)  # Last 10 digits (local number)


class TestInputValidation(IntegrationTestCase):
    """Test input validation in flow steps."""

    def test_email_validation_valid(self):
        """Test valid email passes validation."""
        import re
        email = "test@example.com"
        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        self.assertTrue(re.match(pattern, email.strip()))

    def test_email_validation_invalid(self):
        """Test invalid email fails validation."""
        import re
        email = "invalid-email"
        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        self.assertIsNone(re.match(pattern, email.strip()))

    def test_phone_validation_valid(self):
        """Test valid phone passes validation."""
        import re
        phone = "+1234567890"
        cleaned = re.sub(r"[\s\-\(\)]", "", phone)
        self.assertTrue(re.match(r"^\+?\d{10,15}$", cleaned))

    def test_phone_validation_invalid(self):
        """Test invalid phone fails validation."""
        import re
        phone = "123"
        cleaned = re.sub(r"[\s\-\(\)]", "", phone)
        self.assertIsNone(re.match(r"^\+?\d{10,15}$", cleaned))

    def test_number_validation_valid(self):
        """Test valid number passes validation."""
        import re
        number = "123.45"
        cleaned = number.replace(",", "").replace(" ", "")
        self.assertTrue(re.match(r"^-?\d+\.?\d*$", cleaned))

    def test_number_validation_invalid(self):
        """Test invalid number fails validation."""
        import re
        number = "abc"
        cleaned = number.replace(",", "").replace(" ", "")
        self.assertIsNone(re.match(r"^-?\d+\.?\d*$", cleaned))


class TestWhatsAppFlowIntegration(IntegrationTestCase):
    """Test WhatsApp Flow integration with chatbot."""

    def test_flow_step_has_whatsapp_flow_input_type(self):
        """Test that WhatsApp Flow Step has WhatsApp Flow as input type option."""
        meta = frappe.get_meta("WhatsApp Flow Step")
        input_type_field = meta.get_field("input_type")
        self.assertIsNotNone(input_type_field)
        self.assertIn("WhatsApp Flow", input_type_field.options)

    def test_flow_step_has_whatsapp_flow_field(self):
        """Test that WhatsApp Flow Step has whatsapp_flow link field."""
        meta = frappe.get_meta("WhatsApp Flow Step")
        flow_field = meta.get_field("whatsapp_flow")
        self.assertIsNotNone(flow_field)
        self.assertEqual(flow_field.fieldtype, "Link")
        self.assertEqual(flow_field.options, "WhatsApp Flow")

    def test_flow_response_processing(self):
        """Test processing of WhatsApp Flow responses."""
        from frappe_whatsapp_chatbot.chatbot.flow_engine import FlowEngine

        # Create flow engine
        flow_engine = FlowEngine("919876543210", None)

        # Test flow response processing
        flow_response = {
            "name": "John Doe",
            "mobile": "9876543210",
            "date": "2025-01-15"
        }

        # Mock step with field mapping
        class MockStep:
            flow_field_mapping = '{"client_name": "name", "phone": "mobile", "booking_date": "date"}'

        # Mock session
        class MockSession:
            session_data = "{}"

        session_data = flow_engine.process_flow_response(
            MockStep(),
            MockSession(),
            flow_response
        )

        # Verify fields are mapped correctly
        self.assertEqual(session_data.get("client_name"), "John Doe")
        self.assertEqual(session_data.get("phone"), "9876543210")
        self.assertEqual(session_data.get("booking_date"), "2025-01-15")

    def test_flow_response_processing_no_mapping(self):
        """Test flow response processing without field mapping."""
        from frappe_whatsapp_chatbot.chatbot.flow_engine import FlowEngine

        flow_engine = FlowEngine("919876543210", None)

        flow_response = {
            "name": "Jane Doe",
            "email": "jane@example.com"
        }

        class MockStep:
            flow_field_mapping = None

        class MockSession:
            session_data = "{}"

        session_data = flow_engine.process_flow_response(
            MockStep(),
            MockSession(),
            flow_response
        )

        # Without mapping, fields should be stored as-is
        self.assertEqual(session_data.get("name"), "Jane Doe")
        self.assertEqual(session_data.get("email"), "jane@example.com")

    def test_chatbot_processor_handles_flow_content_type(self):
        """Test that ChatbotProcessor handles flow content type."""
        from frappe_whatsapp_chatbot.chatbot.processor import ChatbotProcessor

        message_data = {
            "name": "test_msg",
            "from": "919876543210",
            "message": "Flow completed",
            "content_type": "flow",
            "whatsapp_account": None,
            "type": "Incoming",
            "flow_response": '{"name": "Test User", "phone": "1234567890"}'
        }

        processor = ChatbotProcessor(message_data)

        # Verify flow response is parsed
        self.assertIsNotNone(processor.flow_response)
        self.assertEqual(processor.flow_response.get("name"), "Test User")

    def test_flow_engine_build_step_message_for_whatsapp_flow(self):
        """Test that FlowEngine builds correct message for WhatsApp Flow steps."""
        from frappe_whatsapp_chatbot.chatbot.flow_engine import FlowEngine

        flow_engine = FlowEngine("919876543210", None)

        # Mock step with WhatsApp Flow input type
        class MockStep:
            step_name = "collect_info"
            message = "Please fill out the booking form"
            input_type = "WhatsApp Flow"
            whatsapp_flow = "Test Booking Flow"
            flow_cta = "Open Booking Form"
            flow_screen = "booking"
            message_type = "Text"
            response_script = None
            buttons = None
            options = None

        class MockSession:
            session_data = "{}"

        response = flow_engine.build_step_message(MockStep(), {}, MockSession())

        # Response should be a dict with flow message structure
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get("content_type"), "flow")
        self.assertEqual(response.get("flow"), "Test Booking Flow")
        self.assertEqual(response.get("flow_cta"), "Open Booking Form")


class TestFlowEngineValidation(IntegrationTestCase):
    """Test flow engine input validation for WhatsApp Flow."""

    def test_whatsapp_flow_validation_always_valid(self):
        """Test that WhatsApp Flow input type validation always passes.

        WhatsApp Flow responses are validated by WhatsApp itself,
        so our validation should always return True.
        """
        from frappe_whatsapp_chatbot.chatbot.flow_engine import FlowEngine

        flow_engine = FlowEngine("919876543210", None)

        class MockStep:
            input_type = "WhatsApp Flow"
            validation_regex = None
            validation_error = None

        # Any input should pass for WhatsApp Flow type
        self.assertTrue(flow_engine.validate_input(MockStep(), "any input"))
        self.assertTrue(flow_engine.validate_input(MockStep(), ""))
        self.assertTrue(flow_engine.validate_input(MockStep(), None))
