# Conversation Flows

Flows allow multi-step conversations to collect information from users.

## Creating a Flow

1. Go to **WhatsApp Chatbot Flow** → **+ Add**
2. Configure flow settings
3. Add steps in the Steps table
4. Set completion action
5. Click **Save**

## Flow Settings

| Field | Description |
|-------|-------------|
| **Flow Name** | Unique identifier |
| **Enabled** | Enable/disable the flow |
| **WhatsApp Account** | Leave empty for all accounts |
| **Trigger Keywords** | Comma-separated keywords that start this flow |
| **Cancel Keywords** | Words that cancel the flow (default: cancel, stop, quit, exit) |

## Initial Message

| Field | Description |
|-------|-------------|
| **Initial Message** | First message when flow starts |
| **Initial Message Type** | Text or Template |
| **Initial Template** | WhatsApp template (if type is Template) |

## Flow Steps

Each step in the flow is configured in the Steps table. **Drag and drop rows to reorder steps.**

### Step Fields

| Field | Description |
|-------|-------------|
| **Step Name** | Unique identifier (e.g., `ask_name`, `ask_email`) |
| **Message** | Message to send. Use `{variable}` for substitution |
| **Message Type** | Text, Template, or Script |
| **Input Type** | Expected input type |
| **Store As** | Variable name to store user's response |

### Input Types

| Type | Description | Validation |
|------|-------------|------------|
| **None** | No input expected | - |
| **Text** | Any text | None |
| **Number** | Numeric input | Must be a valid number |
| **Email** | Email address | Must contain @ and domain |
| **Phone** | Phone number | 10-15 digits, optional + prefix |
| **Date** | Date input | Common formats (DD-MM-YYYY, etc.) |
| **Select** | Choice from options | Must match one of the options |

### Message Type: Script

Execute Python code to generate dynamic responses. See [Script Responses](../features/scripts.md).

### Validation

| Field | Description |
|-------|-------------|
| **Validation Regex** | Custom regex pattern |
| **Validation Error Message** | Error shown on invalid input |
| **Retry on Invalid Input** | Re-prompt on invalid input |
| **Max Retries** | Maximum retry attempts (default: 3) |

### Navigation

| Field | Description |
|-------|-------------|
| **Next Step** | Explicit next step name (leave empty for sequential) |
| **Conditional Next** | JSON mapping input to next step |
| **Skip Condition** | Python expression to skip this step |

#### Conditional Next Example

```json
{
  "billing": "billing_step",
  "technical": "technical_step",
  "default": "general_step"
}
```

## Completion Settings

| Field | Description |
|-------|-------------|
| **Completion Message** | Message sent when flow completes. Use `{variable}` for substitution |
| **On Complete Action** | None, Create Document, Call API, or Run Script |

### Create Document

| Field | Description |
|-------|-------------|
| **Create DocType** | DocType to create (e.g., Lead, Issue) |
| **Field Mapping** | JSON mapping flow variables to DocType fields |

Example field mapping:
```json
{
  "lead_name": "customer_name",
  "email_id": "customer_email",
  "company_name": "company"
}
```

### Call API

| Field | Description |
|-------|-------------|
| **API Endpoint** | URL to POST collected data to |

### Run Script

| Field | Description |
|-------|-------------|
| **Custom Script** | Python script to execute. Use `data` dict for collected values |

## Variable Substitution

Use `{variable_name}` in messages to substitute collected values.

Example:
```
Message: Thanks {customer_name}! We'll contact you at {customer_email}.
```

## Flow Processing Priority

When a message is received:

1. **Active Session** - If user has an active flow session, continue that flow
2. **Keyword Match** - Check keyword replies (if response type is Flow, start that flow)
3. **Flow Trigger** - Check flow trigger keywords
4. **AI/Default** - Fallback to AI or default response
