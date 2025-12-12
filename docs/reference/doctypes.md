# DocTypes Reference

## WhatsApp Chatbot

**Type:** Single DocType (Settings)

Global chatbot configuration.

| Field | Type | Description |
|-------|------|-------------|
| enabled | Check | Enable/disable chatbot |
| whatsapp_account | Link | Default WhatsApp Account |
| process_all_accounts | Check | Process all accounts |
| default_response | Small Text | Fallback message |
| business_hours_only | Check | Restrict to business hours |
| business_start_time | Time | Start time |
| business_end_time | Time | End time |
| out_of_hours_message | Small Text | Out of hours message |
| enable_ai | Check | Enable AI responses |
| ai_provider | Select | OpenAI/Anthropic/Custom |
| ai_api_key | Password | API key |
| ai_model | Data | Model name |
| ai_max_tokens | Int | Max response tokens |
| ai_temperature | Float | Temperature (0-1) |
| ai_system_prompt | Text | System prompt |
| session_timeout_minutes | Int | Session timeout |
| log_conversations | Check | Enable logging |
| excluded_numbers | Table | Excluded phone numbers |

---

## WhatsApp Keyword Reply

**Type:** DocType (List)

Keyword-to-response mappings.

| Field | Type | Description |
|-------|------|-------------|
| title | Data | Rule name |
| enabled | Check | Enable/disable |
| priority | Int | Match priority |
| whatsapp_account | Link | Specific account |
| keywords | Small Text | Comma-separated keywords |
| match_type | Select | Exact/Contains/Starts With/Regex |
| case_sensitive | Check | Case sensitivity |
| response_type | Select | Text/Template/Media/Flow/Script |
| response_text | Text | Text response |
| response_template | Link | WhatsApp Template |
| template_parameters | JSON | Template params |
| media_type | Select | Image/Video/Audio/Document |
| media_url | Data | Media URL |
| media_caption | Small Text | Media caption |
| trigger_flow | Link | Flow to trigger |
| script | Data | Server Script name or method path |
| conditions | Code | Python conditions |
| active_from | Datetime | Active start |
| active_until | Datetime | Active end |

---

## WhatsApp Chatbot Flow

**Type:** DocType (List)

Conversation flow definitions.

| Field | Type | Description |
|-------|------|-------------|
| flow_name | Data | Unique name |
| enabled | Check | Enable/disable |
| description | Small Text | Description |
| whatsapp_account | Link | Specific account |
| trigger_keywords | Small Text | Trigger keywords |
| initial_message | Text | First message |
| initial_message_type | Select | Text/Template |
| initial_template | Link | Initial template |
| steps | Table | Flow steps |
| completion_message | Text | Completion message |
| on_complete_action | Select | None/Create Document/Call API/Run Script |
| create_doctype | Link | DocType to create |
| field_mapping | JSON | Field mappings |
| api_endpoint | Data | API URL |
| custom_script | Code | Python script |
| timeout_message | Small Text | Timeout message |
| cancel_keywords | Data | Cancel keywords |

---

## WhatsApp Flow Step

**Type:** Child Table (for Flow)

Individual flow steps.

| Field | Type | Description |
|-------|------|-------------|
| step_name | Data | Unique step ID |
| message | Text | Message to send |
| message_type | Select | Text/Template/Script |
| template | Link | WhatsApp Template |
| response_script | Small Text | Python script |
| input_type | Select | None/Text/Number/Email/Phone/Date/Select |
| options | Small Text | Select options (pipe-separated) |
| validation_regex | Data | Regex pattern |
| validation_error | Small Text | Error message |
| store_as | Data | Variable name |
| next_step | Data | Next step name |
| conditional_next | JSON | Conditional routing |
| skip_condition | Code | Skip expression |
| retry_on_invalid | Check | Retry on error |
| max_retries | Int | Max retries |

---

## WhatsApp Chatbot Session

**Type:** DocType (List)

Active/completed conversation sessions.

| Field | Type | Description |
|-------|------|-------------|
| phone_number | Data | User's phone |
| whatsapp_account | Link | WhatsApp Account |
| status | Select | Active/Completed/Cancelled/Timeout |
| current_flow | Link | Current flow |
| current_step | Data | Current step name |
| session_data | JSON | Collected data |
| step_retries | Int | Retry count |
| messages | Table | Message history |
| started_at | Datetime | Start time |
| completed_at | Datetime | End time |
| last_activity | Datetime | Last activity |

---

## WhatsApp AI Context

**Type:** DocType (List)

Knowledge base for AI responses.

| Field | Type | Description |
|-------|------|-------------|
| title | Data | Context name |
| enabled | Check | Enable/disable |
| priority | Int | Include priority |
| context_type | Select | Static Text/DocType Query |
| static_content | Long Text | Static text |
| doctype | Link | DocType to query |
| fields_to_include | Data | Fields (comma-separated) |
| filters | JSON | Query filters |

---

## WhatsApp Excluded Number

**Type:** Child Table (for Settings)

Phone numbers to exclude.

| Field | Type | Description |
|-------|------|-------------|
| phone_number | Data | Phone number |

---

## WhatsApp Agent Transfer

**Type:** DocType (List)

Track conversations transferred to human agents. When active, chatbot stops auto-responding to the phone number.

| Field | Type | Description |
|-------|------|-------------|
| phone_number | Data | Customer's phone number |
| whatsapp_account | Link | WhatsApp Account |
| status | Select | Active/Resumed |
| transferred_at | Datetime | When transferred |
| agent | Link | Assigned user |
| agent_name | Data | Agent's full name |
| notes | Small Text | Transfer notes |
| resumed_at | Datetime | When chatbot resumed |
| resumed_by | Link | Who resumed |

### Usage

```python
# Transfer to agent
from frappe_whatsapp_chatbot.api import transfer_to_agent
transfer_to_agent(phone_number="+919876543210", agent="agent@example.com")

# Resume chatbot
from frappe_whatsapp_chatbot.api import resume_chatbot
resume_chatbot(phone_number="+919876543210")
```

---

## WhatsApp Session Message

**Type:** Child Table (for Session)

Message history in session.

| Field | Type | Description |
|-------|------|-------------|
| direction | Select | Incoming/Outgoing |
| message | Text | Message content |
| step_name | Data | Step name |
| timestamp | Datetime | Time |
