# AI Integration

Use AI-powered responses as a fallback when no keyword or flow matches.

![AI Response](../assets/ai_response.png)

## Setup

### 1. Install Dependencies

Dependencies are installed automatically with the app. If needed manually:

```bash
# For OpenAI
pip install openai

# For Anthropic Claude
pip install anthropic

# For Google Gemini
pip install google-generativeai
```

### 2. Configure in Settings

1. Go to **WhatsApp Chatbot** settings
2. Enable **Enable AI**
3. Select **AI Provider**: OpenAI or Anthropic
4. Enter your **AI API Key**
5. Configure model settings
6. Click **Save**

## Settings

| Setting | Description | Default |
|---------|-------------|---------|
| **AI Provider** | OpenAI, Anthropic, Google, or Custom | - |
| **AI API Key** | Your API key | - |
| **AI Model** | Model to use | gpt-4o-mini |
| **Max Tokens** | Maximum response length | 500 |
| **Temperature** | Creativity (0-1) | 0.7 |
| **System Prompt** | Instructions for the AI | Default assistant prompt |

### Recommended Models

**OpenAI:**
- `gpt-4o-mini` - Fast, cheap, good for most use cases
- `gpt-4o` - More capable, higher cost

**Anthropic:**
- `claude-3-haiku-20240307` - Fast, cheap
- `claude-3-sonnet-20240229` - Balanced
- `claude-3-opus-20240229` - Most capable

**Google:**
- `gemini-2.0-flash` - Fast, free tier available
- `gemini-2.5-flash` - Latest flash model
- `gemini-2.5-pro` - Most capable

## System Prompt

The system prompt tells the AI how to behave.

### Recommended System Prompt

Use this prompt to prevent the AI from claiming to perform actions it cannot do:

```
You are a helpful customer service assistant. Be concise, friendly, and professional.

IMPORTANT RULES:
- You can ONLY provide information from the context given to you
- You CANNOT perform any actions like sending emails, resetting passwords, creating orders, etc.
- If a user asks you to DO something (reset password, send email, place order), tell them you cannot perform actions and guide them to the appropriate channel
- Never claim to have done something you didn't do
- If you don't know something, say so honestly
```

### Basic Example

```
You are a helpful customer service assistant for ABC Company.
Be concise, friendly, and professional.
Our business hours are Monday-Friday, 9 AM - 6 PM.
If you don't know something, say so and offer to connect with a human agent.
Do not make up information about products or prices.
```

## AI Context

Provide knowledge to the AI through **WhatsApp AI Context** documents.

### Static Text Context

Add fixed information like company details, FAQ, policies.

1. Go to **WhatsApp AI Context** → **+ Add**
2. Set **Context Type**: Static Text
3. Enter your content in **Static Content**
4. Click **Save**

Example:
```
Title: Company Info
Context Type: Static Text
Static Content:
ABC Company was founded in 2010.
We specialize in software solutions.
Our main products are:
- Product A: $99/month
- Product B: $199/month
- Product C: $499/month
```

### DocType Query Context

Dynamically include data from your Frappe database.

1. Go to **WhatsApp AI Context** → **+ Add**
2. Set **Context Type**: DocType Query
3. Select the **DocType**
4. Specify **Fields to Include**
5. Add **Filters** if needed
6. Click **Save**

Example:
```
Title: Product Catalog
Context Type: DocType Query
DocType: Item
Fields to Include: item_name, description, standard_rate
Filters: {"disabled": 0, "is_sales_item": 1}
```

### Priority

Higher priority contexts are included first. Use this to ensure important information is always included.

## How It Works

1. User sends a message
2. Chatbot checks for active flow, keyword match, flow trigger
3. If nothing matches and AI is enabled:
   - Build context from AI Context documents
   - Include recent conversation history
   - Send to AI provider
   - Return AI response

## Limitations

- AI responses may occasionally be incorrect
- API costs apply based on your provider
- Response time depends on the AI provider
- No guarantee of consistent responses

## Best Practices

1. **Keep system prompts focused** - Be specific about what the AI should and shouldn't do
2. **Use context wisely** - Include relevant information but don't overload
3. **Set appropriate temperature** - Lower (0.3) for factual, higher (0.7) for conversational
4. **Monitor usage** - Check your API costs regularly
5. **Have fallbacks** - Configure a default response in case AI fails
