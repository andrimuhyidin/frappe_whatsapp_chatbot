# Chatbot Settings

The main configuration for the chatbot is in the **WhatsApp Chatbot** single DocType.

![Chatbot Settings](../assets/chatbot.png)

## General Settings

| Setting | Description |
|---------|-------------|
| **Enabled** | Master switch to enable/disable the chatbot |
| **WhatsApp Account** | Specific account to process messages from |
| **Process All Accounts** | Process messages from all WhatsApp accounts |

## Default Responses

| Setting | Description |
|---------|-------------|
| **Default Response** | Message sent when no keyword or flow matches |

Example default response:
```
Sorry, I didn't understand that. Please try again or type 'help' for assistance.
```

## Business Hours

Restrict chatbot responses to specific hours.

| Setting | Description |
|---------|-------------|
| **Respond Only During Business Hours** | Enable time-based filtering |
| **Business Start Time** | Start of business hours (e.g., 09:00) |
| **Business End Time** | End of business hours (e.g., 18:00) |
| **Out of Hours Message** | Message sent outside business hours |

Example out of hours message:
```
Thank you for your message. Our business hours are Monday-Friday, 9 AM - 6 PM. We'll respond during business hours.
```

## Session Settings

| Setting | Description |
|---------|-------------|
| **Session Timeout (Minutes)** | Time before inactive flow sessions expire (default: 30) |
| **Log Conversations** | Log all chatbot conversations for analytics |

## Excluded Numbers

Add phone numbers that should not receive automated responses.

Use this for:
- VIP customers who should always talk to humans
- Internal team members
- Test numbers

## AI Configuration

See [AI Integration](ai.md) for detailed AI setup.

| Setting | Description |
|---------|-------------|
| **Enable AI** | Use AI for fallback responses |
| **AI Provider** | OpenAI, Anthropic, or Custom |
| **AI API Key** | Your API key |
| **AI Model** | Model name (e.g., gpt-4o-mini) |
| **Max Tokens** | Maximum response length |
| **Temperature** | Creativity (0 = deterministic, 1 = creative) |
| **System Prompt** | Instructions for the AI |
