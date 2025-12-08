# Example: Lead Collection

Collect lead information and create a Lead document.

## Overview

When users type "sales" or "demo", collect their details and create a Lead in Frappe.

## Flow Configuration

### Basic Settings

```
Flow Name: Contact Sales
Enabled: ✓
Trigger Keywords: sales, contact, demo, pricing, quote
Initial Message: Great! I'd be happy to connect you with our sales team. Let me get a few details.
```

### Steps

#### Step 1: Ask Name

| Field | Value |
|-------|-------|
| Step Name | ask_name |
| Message | What's your name? |
| Message Type | Text |
| Input Type | Text |
| Store As | customer_name |

#### Step 2: Ask Email

| Field | Value |
|-------|-------|
| Step Name | ask_email |
| Message | Thanks {customer_name}! What's your email address? |
| Message Type | Text |
| Input Type | Email |
| Store As | customer_email |

#### Step 3: Ask Company

| Field | Value |
|-------|-------|
| Step Name | ask_company |
| Message | And which company are you from? |
| Message Type | Text |
| Input Type | Text |
| Store As | company_name |

#### Step 4: Ask Interest (Optional)

| Field | Value |
|-------|-------|
| Step Name | ask_interest |
| Message | What product are you interested in? |
| Message Type | Text |
| Input Type | Select |
| Options | Product A\|Product B\|Product C\|Not Sure |
| Store As | product_interest |

### Completion Settings

```
Completion Message:
Thank you {customer_name}!

Our sales team will contact you at {customer_email} within 24 hours.

In the meantime, check out our product demos at https://company.com/demos

On Complete Action: Create Document
Create DocType: Lead
Field Mapping:
{
    "lead_name": "customer_name",
    "email_id": "customer_email",
    "company_name": "company_name",
    "notes": "product_interest"
}
```

## Conversation Flow

```
User: sales

Bot: Great! I'd be happy to connect you with our sales team. Let me get a few details.
Bot: What's your name?

User: John Doe

Bot: Thanks John Doe! What's your email address?

User: john@acme.com

Bot: And which company are you from?

User: Acme Corporation

Bot: What product are you interested in?
     Options: Product A, Product B, Product C, Not Sure

User: Product A

Bot: Thank you John Doe!
     Our sales team will contact you at john@acme.com within 24 hours.
     In the meantime, check out our product demos at https://company.com/demos

→ Lead document created automatically
```

## Lead Document Created

| Field | Value |
|-------|-------|
| Lead Name | John Doe |
| Email | john@acme.com |
| Company Name | Acme Corporation |
| Notes | Product A |

## Enhancements

### Add Phone Number

Add another step:
```
Step Name: ask_phone
Message: What's your phone number? (optional, type "skip" to skip)
Input Type: Text
Store As: phone_number
```

Update field mapping:
```json
{
    "lead_name": "customer_name",
    "email_id": "customer_email",
    "company_name": "company_name",
    "phone": "phone_number",
    "notes": "product_interest"
}
```

### Add Source Tracking

Use a script instead of Create Document:

```python
lead = frappe.get_doc({
    'doctype': 'Lead',
    'lead_name': data.get('customer_name'),
    'email_id': data.get('customer_email'),
    'company_name': data.get('company_name'),
    'source': 'WhatsApp Chatbot',
    'notes': data.get('product_interest')
})
lead.insert(ignore_permissions=True)
frappe.db.commit()
```
