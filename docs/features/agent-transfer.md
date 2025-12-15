# Agent Transfer (Pause Chatbot)

Transfer conversations to human agents and pause chatbot responses for specific users.

## How It Works

```
Customer sends message
        │
        ▼
┌───────────────────┐
│ Is Transferred?   │
└───────────────────┘
        │
   Yes  │  No
   ▼    │   ▼
┌─────────┐  ┌─────────────┐
│ STOP    │  │ Process     │
│ (Human  │  │ normally    │
│ handles)│  │ (Chatbot)   │
└─────────┘  └─────────────┘
```

When a conversation is transferred to an agent:

1. **Chatbot stops responding** to that phone number
2. **Human agent handles** the conversation manually (via WhatsApp Chat or WhatsApp Business app)
3. **When resolved**, resume chatbot for that number

---

## Transfer to Agent

### From a Flow Script

Use this when a user requests human assistance during a flow:

```python
from frappe_whatsapp_chatbot.frappe_whatsapp_chatbot.doctype.whatsapp_agent_transfer.whatsapp_agent_transfer import WhatsAppAgentTransfer

# Transfer to agent
WhatsAppAgentTransfer.transfer_to_agent(
    phone_number="+919876543210",
    whatsapp_account="Main WhatsApp",  # optional
    agent="agent@company.com",          # optional - assign to specific user
    notes="Customer needs help with billing"  # optional
)

response = "I'm connecting you with a support agent. They'll respond shortly."
```

### From Keyword Reply Script

Create a keyword reply with **Response Type: Script** for keywords like "agent", "human", "talk to someone":

```python
from frappe_whatsapp_chatbot.frappe_whatsapp_chatbot.doctype.whatsapp_agent_transfer.whatsapp_agent_transfer import WhatsAppAgentTransfer

WhatsAppAgentTransfer.transfer_to_agent(
    phone_number=doc.from,
    whatsapp_account=doc.whatsapp_account
)

response = "A human agent will assist you shortly. Please wait."
```

### From Python Code

```python
import frappe
from frappe_whatsapp_chatbot.frappe_whatsapp_chatbot.doctype.whatsapp_agent_transfer.whatsapp_agent_transfer import WhatsAppAgentTransfer

# Transfer with all options
transfer = WhatsAppAgentTransfer.transfer_to_agent(
    phone_number="+919876543210",
    whatsapp_account="Main WhatsApp",
    agent="support@company.com",
    notes="Billing dispute - needs manager approval"
)

print(f"Transfer created: {transfer.name}")
```

---

## Resume Chatbot

After the human agent resolves the issue, resume the chatbot.

### From Python Code

```python
from frappe_whatsapp_chatbot.frappe_whatsapp_chatbot.doctype.whatsapp_agent_transfer.whatsapp_agent_transfer import WhatsAppAgentTransfer

# Resume chatbot for this number
resumed = WhatsAppAgentTransfer.resume_chatbot(
    phone_number="+919876543210",
    whatsapp_account="Main WhatsApp"  # optional
)

if resumed:
    print("Chatbot resumed successfully")
else:
    print("No active transfer found")
```

### From Frappe Desk

1. Go to **WhatsApp Agent Transfer** list
2. Find the active transfer record (Status = "Active")
3. Change **Status** to "Resumed"
4. Save

The chatbot will immediately start responding to that number again.

---

## Check Transfer Status

Check if a phone number is currently transferred to an agent:

```python
from frappe_whatsapp_chatbot.frappe_whatsapp_chatbot.doctype.whatsapp_agent_transfer.whatsapp_agent_transfer import WhatsAppAgentTransfer

# Returns True if transferred, False otherwise
is_transferred = WhatsAppAgentTransfer.is_transferred("+919876543210")

if is_transferred:
    print("Conversation is with human agent")
else:
    print("Chatbot is active")
```

---

## WhatsApp Agent Transfer Fields

| Field | Type | Description |
|-------|------|-------------|
| Phone Number | Data | Customer's phone number (required) |
| WhatsApp Account | Link | Associated WhatsApp account |
| Status | Select | **Active** (chatbot paused) or **Resumed** (chatbot active) |
| Transferred At | Datetime | When transfer was created (auto-set) |
| Agent | Link (User) | User handling the conversation |
| Agent Name | Data | Agent's full name (auto-fetched) |
| Notes | Small Text | Reason for transfer or additional context |
| Resumed At | Datetime | When chatbot was resumed (auto-set) |
| Resumed By | Link (User) | User who resumed the chatbot (auto-set) |

---

## Example: Support Escalation Flow

Create a flow that allows users to request human assistance:

```
Flow Name: Support Escalation
Trigger Keywords: agent, human, help, support

Steps:
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: ask_reason                                              │
│ Message: I'll connect you with a human agent.                   │
│          What do you need help with?                            │
│ Input Type: Select                                              │
│ Options: Billing|Technical|Complaint|Other                      │
│ Store As: reason                                                │
├─────────────────────────────────────────────────────────────────┤
│ Step 2: transfer                                                │
│ Message Type: Script                                            │
│ Response Script:                                                │
│                                                                 │
│   from frappe_whatsapp_chatbot.frappe_whatsapp_chatbot.doctype  │
│       .whatsapp_agent_transfer.whatsapp_agent_transfer          │
│       import WhatsAppAgentTransfer                              │
│                                                                 │
│   WhatsAppAgentTransfer.transfer_to_agent(                      │
│       phone_number=phone_number,                                │
│       notes=f"Reason: {data.get('reason')}"                     │
│   )                                                             │
│                                                                 │
│   response = "You're now connected to our support team. "       │
│   response += "A human agent will respond shortly."             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Completion Message: Thank you for your patience!
```

---

## Integration with WhatsApp Chat

If you have [WhatsApp Chat](https://github.com/shridarpatil/whatsapp_chat) installed, agents can:

1. See transferred conversations in the chat interface
2. Respond directly from Frappe Desk
3. Resume chatbot when done

---

## Best Practices

1. **Always send a message** when transferring - let the user know a human will respond
2. **Add notes** explaining why the transfer happened - helps agents understand context
3. **Assign to specific agents** when possible - for specialized issues (billing, technical, etc.)
4. **Resume promptly** - don't leave chatbot paused longer than necessary
5. **Monitor active transfers** - check the WhatsApp Agent Transfer list regularly
