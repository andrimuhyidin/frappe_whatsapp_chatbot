# Hooks & API

## Document Events

The chatbot hooks into WhatsApp Message creation:

```python
# hooks.py
doc_events = {
    "WhatsApp Message": {
        "after_insert": "frappe_whatsapp_chatbot.chatbot.processor.process_incoming_message"
    }
}
```

### Processing Flow

1. `after_insert` triggered on new WhatsApp Message
2. Check if message is incoming and text/button type
3. Check if chatbot is enabled
4. Process through flow/keyword/AI pipeline
5. Create response WhatsApp Message

## Scheduled Jobs

```python
# hooks.py
scheduler_events = {
    "hourly": [
        "frappe_whatsapp_chatbot.chatbot.session_manager.cleanup_expired_sessions"
    ]
}
```

### cleanup_expired_sessions

- Runs every hour
- Marks inactive sessions as "Timeout"
- Sends timeout messages (if configured)

## Core Classes

### ChatbotProcessor

Main message processor.

```python
from frappe_whatsapp_chatbot.chatbot.processor import ChatbotProcessor

processor = ChatbotProcessor({
    "name": "MSG-001",
    "from": "+1234567890",
    "message": "hello",
    "content_type": "text",
    "whatsapp_account": "Default"
})
processor.process()
```

### FlowEngine

Execute conversation flows.

```python
from frappe_whatsapp_chatbot.chatbot.flow_engine import FlowEngine

engine = FlowEngine("+1234567890", "Default")

# Check if message triggers a flow
flow_name = engine.check_flow_trigger("sales")

# Start a flow
response = engine.start_flow("Contact Sales")

# Process user input in active flow
response = engine.process_input(session, "John Doe")
```

### KeywordMatcher

Match messages against keyword rules.

```python
from frappe_whatsapp_chatbot.chatbot.keyword_matcher import KeywordMatcher

matcher = KeywordMatcher("Default")
match = matcher.match("hello")

if match:
    print(match.response_text)
```

### SessionManager

Manage conversation sessions.

```python
from frappe_whatsapp_chatbot.chatbot.session_manager import SessionManager

manager = SessionManager("+1234567890", "Default")

# Get active session
session = manager.get_active_session()

# Get conversation history (for AI)
history = manager.get_conversation_history(limit=20)
```

### AIResponder

Generate AI responses.

```python
from frappe_whatsapp_chatbot.chatbot.ai_responder import AIResponder

settings = frappe.get_single("WhatsApp Chatbot")
responder = AIResponder(settings)

response = responder.generate_response(
    "What are your business hours?",
    conversation_history
)
```

## Extending the Chatbot

### Custom Response Types

Add custom response handling in `processor.py`:

```python
def build_keyword_response(self, keyword_doc):
    if keyword_doc.response_type == "Custom":
        return self.handle_custom_response(keyword_doc)
    # ... existing code
```

### Custom Input Validators

Add validation in `flow_engine.py`:

```python
def validate_input(self, step, user_input, button_payload):
    if input_type == "CustomType":
        return self.validate_custom(user_input)
    # ... existing code
```

### Custom Complete Actions

Add actions in `flow_engine.py`:

```python
def complete_flow(self, session, flow):
    if flow.on_complete_action == "Custom Action":
        self.custom_action(flow, session_data)
    # ... existing code
```

## Agent Transfer API

Transfer conversations to human agents and resume chatbot when done.

### Transfer to Agent

```python
import frappe

# Via API
frappe.call(
    "frappe_whatsapp_chatbot.api.transfer_to_agent",
    phone_number="+919876543210",
    agent="agent@example.com",  # Optional
    notes="Customer needs billing help"  # Optional
)

# Via Python
from frappe_whatsapp_chatbot.api import transfer_to_agent
result = transfer_to_agent(
    phone_number="+919876543210",
    agent="agent@example.com"
)
# Returns: {"status": "transferred", "name": "AGT-...", ...}
```

### Resume Chatbot

```python
# Via API
frappe.call(
    "frappe_whatsapp_chatbot.api.resume_chatbot",
    phone_number="+919876543210"
)

# Via Python
from frappe_whatsapp_chatbot.api import resume_chatbot
result = resume_chatbot(phone_number="+919876543210")
# Returns: {"status": "resumed", ...}
```

### Check Transfer Status

```python
from frappe_whatsapp_chatbot.api import is_transferred

result = is_transferred(phone_number="+919876543210")
if result["is_transferred"]:
    print(f"Transferred to: {result['agent_name']}")
```

### Get Active Transfers

```python
from frappe_whatsapp_chatbot.api import get_active_transfers

# Get all active transfers
transfers = get_active_transfers()

# Filter by agent
my_transfers = get_active_transfers(agent="agent@example.com")
```

### Using in Server Scripts

Transfer a conversation when a keyword like "agent" is detected:

```python
# Server Script: transfer_to_agent
# Script Type: API

phone_number = doc.get("from") or doc.from_

# Transfer to agent
from frappe_whatsapp_chatbot.api import transfer_to_agent
transfer_to_agent(
    phone_number=phone_number,
    notes="Customer requested human agent"
)

response = "You've been connected to a human agent. They'll respond shortly."
```

## Events & Signals

Currently, the chatbot doesn't emit custom events, but you can:

1. Override document controllers
2. Add custom hooks in your app
3. Use Frappe's `doc_events` to hook into WhatsApp Message

### Example: Log All Bot Responses

```python
# your_app/hooks.py
doc_events = {
    "WhatsApp Message": {
        "after_insert": "your_app.handlers.log_message"
    }
}

# your_app/handlers.py
def log_message(doc, method):
    if doc.type == "Outgoing":
        # Log or process outgoing messages
        pass
```
