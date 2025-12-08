# Quick Start

Get your chatbot up and running in 5 minutes.

## Step 1: Enable the Chatbot

1. Go to **WhatsApp Chatbot** (search in the sidebar)
2. Check **Enabled**
3. Enable **Process All Accounts** (or select a specific WhatsApp Account)
4. Set a **Default Response** message (shown when no rules match)
5. Click **Save**

![Chatbot Settings](assets/chatbot.png)

## Step 2: Create Your First Keyword Reply

1. Go to **WhatsApp Keyword Reply** → **+ Add WhatsApp Keyword Reply**
2. Fill in:
   - **Title**: `Greeting`
   - **Keywords**: `hello, hi, hey`
   - **Match Type**: `Exact`
   - **Response Type**: `Text`
   - **Response Text**: `Hello! How can I help you today?`
3. Click **Save**

## Step 3: Test It

Send "hello" to your WhatsApp Business number. You should receive the automated reply!

![Chat Response](assets/chat_response.png)

## What's Next?

Now that your basic chatbot is working, explore these features:

### Add More Keywords

Create keyword replies for common questions:

| Keywords | Response |
|----------|----------|
| `hours, timing` | "We're open Mon-Fri, 9 AM - 6 PM" |
| `address, location` | "We're at 123 Main Street..." |
| `price, cost` | "Check our pricing at example.com/pricing" |

### Create a Conversation Flow

Collect information through multi-step conversations:

1. Go to **WhatsApp Chatbot Flow** → **+ Add**
2. Set **Trigger Keywords**: `contact, sales`
3. Add steps to collect name, email, company
4. Set **On Complete Action**: `Create Document` → `Lead`

See [Conversation Flows](configuration/flows.md) for detailed guide.

### Enable AI Responses

Use AI for intelligent fallback responses:

1. Go to **WhatsApp Chatbot** settings
2. Enable **Enable AI**
3. Select **OpenAI** or **Anthropic**
4. Enter your API key

See [AI Integration](configuration/ai.md) for setup guide.

## Troubleshooting

**Chatbot not responding?**
- Check if **Enabled** is checked in WhatsApp Chatbot settings
- Verify your WhatsApp Account is selected
- Check **Error Log** for any exceptions

**Keywords not matching?**
- Try **Match Type**: `Contains` for partial matches
- Keywords are case-insensitive by default

See [Troubleshooting](reference/troubleshooting.md) for more help.
