import frappe
import json
import hashlib


class AIResponder:
    """Generate AI-powered responses (optional feature)."""

    def __init__(self, settings, phone_number=None):
        self.settings = settings
        self.phone_number = phone_number
        self.provider = settings.ai_provider
        self.api_key = settings.get_password("ai_api_key") if settings.ai_api_key else None
        self.model = settings.ai_model or "gpt-4o-mini"
        self.system_prompt = settings.ai_system_prompt or "You are a helpful assistant."
        self.max_tokens = settings.ai_max_tokens or 500
        self.temperature = settings.ai_temperature or 0.7
        self.include_history = settings.ai_include_history or False
        self.history_limit = settings.ai_history_limit or 4
        self.cache_ttl = 300  # 5 minutes cache for identical queries
        self.retry_count = 0
        self.max_retries = 3

    def _get_cache_key(self, message):
        """Generate cache key for response caching."""
        # Hash the message + phone for uniqueness
        key_data = f"{self.phone_number}:{message.lower().strip()}"
        return f"wa_ai_response:{hashlib.md5(key_data.encode()).hexdigest()}"

    def generate_response(self, message, conversation_history=None):
        """Generate AI response for message with caching."""
        if not self.api_key:
            frappe.log_error("AI API key not configured")
            return None

        self.current_message = message  # Store for context filtering

        # Check cache first
        cache_key = self._get_cache_key(message)
        cached_response = frappe.cache.get(cache_key)
        if cached_response:
            return cached_response

        response = None
        try:
            if self.provider == "OpenAI":
                response = self.openai_response(message, conversation_history)
            elif self.provider == "Anthropic":
                response = self.anthropic_response(message, conversation_history)
            elif self.provider == "Google":
                response = self.google_response(message, conversation_history)
            elif self.provider == "Custom":
                response = self.custom_response(message, conversation_history)
            
            # Cache successful response
            if response:
                frappe.cache.set(cache_key, response, expires_in_sec=self.cache_ttl)
                return response
                
        except Exception as e:
            self.retry_count += 1
            frappe.log_error(f"AIResponder generate_response error (attempt {self.retry_count}): {str(e)}")
            
            # Retry logic
            if self.retry_count < self.max_retries:
                return self.generate_response(message, conversation_history)
            else:
                frappe.log_error(f"AIResponder max retries exceeded for: {message[:50]}")

        return None


    def build_context(self):
        """Build context from AI Context documents."""
        try:
            contexts = frappe.get_all(
                "WhatsApp AI Context",
                filters={"enabled": 1},
                fields=["*"],
                order_by="priority desc"
            )

            context_parts = []
            message_lower = (getattr(self, 'current_message', '') or '').lower()

            for ctx in contexts:
                try:
                    # Check trigger keywords - skip if message doesn't match
                    if ctx.trigger_keywords:
                        keywords = [k.strip().lower() for k in ctx.trigger_keywords.split(",") if k.strip()]
                        if keywords and not any(kw in message_lower for kw in keywords):
                            continue  # Skip this context - no matching keywords

                    if ctx.context_type == "Static Text" and ctx.static_content:
                        context_parts.append(f"[{ctx.title}]\n{ctx.static_content}")
                    elif ctx.context_type == "DocType Query":
                        data = self.query_doctype(ctx)
                        if data:
                            # Compact JSON to save tokens
                            context_parts.append(f"[{ctx.title}]\n{json.dumps(data, separators=(',', ':'), default=str)}")
                except Exception as e:
                    frappe.log_error(f"AIResponder context '{ctx.title}' error: {str(e)}")
                    continue
            
            # --- Knowledge Base Integration (RAG Lite) ---
            try:
                # Simple keyword search in Knowledge Base
                # In production, this should be Vector Search
                kb_items = frappe.get_all("WhatsApp Knowledge Base", 
                                       filters={"is_active": 1},
                                       fields=["topic", "content", "keywords"])
                
                relevant_kb = []
                for kb in kb_items:
                    # Check if keywords match message
                    if kb.keywords:
                        kb_kws = [k.strip().lower() for k in kb.keywords.split(",") if k.strip()]
                        if any(kw in message_lower for kw in kb_kws):
                            relevant_kb.append(f"Q: {kb.topic}\nA: {kb.content}")
                    # Also check topic string match (simple)
                    elif kb.topic.lower() in message_lower:
                        relevant_kb.append(f"Q: {kb.topic}\nA: {kb.content}")
                
                if relevant_kb:
                    context_parts.append("[Knowledge Base]\n" + "\n---\n".join(relevant_kb))
                    
            except Exception as e:
                frappe.log_error(f"Knowledge Base Search Error: {e}")
            # ---------------------------------------------

            return "\n\n".join(context_parts) if context_parts else ""

        except Exception as e:
            frappe.log_error(f"AIResponder build_context error: {str(e)}")
            return ""

    def query_doctype(self, ctx):
        """Query DocType for context."""
        try:
            # Get the target DocType to query (field renamed to avoid conflict with Frappe's doctype attribute)
            target_doctype = ctx.query_doctype
            if not target_doctype:
                return None

            # Handle filters that might already be parsed
            filters = ctx.filters or {}
            if isinstance(filters, str):
                filters = json.loads(filters) if filters else {}

            # Add user-specific filter if enabled
            if ctx.user_specific and ctx.phone_field and self.phone_number:
                # Normalize phone number for matching (remove + and spaces)
                phone_variants = self.get_phone_variants(self.phone_number)
                filters[ctx.phone_field] = ["in", phone_variants]

            fields = ["name"]

            if ctx.fields_to_include:
                fields = [f.strip() for f in ctx.fields_to_include.split(",") if f.strip()]

            limit = ctx.max_results or 10

            return frappe.get_all(
                target_doctype,
                filters=filters,
                fields=fields,
                limit=limit
            )
        except Exception as e:
            frappe.log_error(f"AIResponder query_doctype error: {str(e)}")
            return None

    def get_phone_variants(self, phone):
        """Get different variants of phone number for matching."""
        if not phone:
            return []

        # Clean the phone number
        clean = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

        variants = [phone, clean]

        # With/without + prefix
        if clean.startswith("+"):
            variants.append(clean[1:])
        else:
            variants.append("+" + clean)

        # With/without country code (assuming 10 digit local numbers)
        if len(clean) > 10:
            variants.append(clean[-10:])

        return list(set(variants))

    def openai_response(self, message, conversation_history):
        """Generate response using OpenAI."""
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)

            messages = [{"role": "system", "content": self.system_prompt}]

            # Add context
            context = self.build_context()
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Here is relevant information you can use to answer questions:\n{context}"
                })

            # Add conversation history if enabled
            if self.include_history and conversation_history:
                for msg in conversation_history[-self.history_limit:]:
                    role = "user" if msg["direction"] == "Incoming" else "assistant"
                    # Truncate long messages
                    msg_text = msg["message"][:200] if len(msg["message"]) > 200 else msg["message"]
                    messages.append({"role": role, "content": msg_text})

            # Add current message
            messages.append({"role": "user", "content": message})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            return response.choices[0].message.content

        except ImportError:
            frappe.log_error("OpenAI library not installed. Run: pip install openai")
            return None
        except Exception as e:
            frappe.log_error(f"OpenAI API error: {str(e)}")
            return None

    def anthropic_response(self, message, conversation_history):
        """Generate response using Anthropic Claude."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)

            # Build messages
            messages = []

            # Add conversation history if enabled
            if self.include_history and conversation_history:
                for msg in conversation_history[-self.history_limit:]:
                    role = "user" if msg["direction"] == "Incoming" else "assistant"
                    # Truncate long messages
                    msg_text = msg["message"][:200] if len(msg["message"]) > 200 else msg["message"]
                    messages.append({"role": role, "content": msg_text})

            messages.append({"role": "user", "content": message})

            # Build system prompt with context
            system = self.system_prompt
            context = self.build_context()
            if context:
                system += f"\n\nHere is relevant information you can use to answer questions:\n{context}"

            response = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system,
                messages=messages
            )

            return response.content[0].text

        except ImportError:
            frappe.log_error("Anthropic library not installed. Run: pip install anthropic")
            return None
        except Exception as e:
            frappe.log_error(f"Anthropic API error: {str(e)}")
            return None

    def google_response(self, message, conversation_history):
        """Generate response using Google AI (Gemini)."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)

            model = genai.GenerativeModel(
                model_name=self.model or "gemini-2.0-flash",
                system_instruction=self.system_prompt
            )

            # Build conversation history if enabled
            history = []
            if self.include_history and conversation_history:
                for msg in conversation_history[-self.history_limit:]:
                    role = "user" if msg["direction"] == "Incoming" else "model"
                    # Truncate long messages to save tokens
                    msg_text = msg["message"][:200] if len(msg["message"]) > 200 else msg["message"]
                    history.append({"role": role, "parts": [msg_text]})

            # Add context to the message
            context = self.build_context()
            full_message = message
            if context:
                full_message = f"Context:\n{context}\n\nQuestion: {message}"

            chat = model.start_chat(history=history)
            response = chat.send_message(
                full_message,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature
                )
            )

            # Handle empty response
            if response.candidates and response.candidates[0].content.parts:
                return response.text
            else:
                # Retry without history if MAX_TOKENS
                chat = model.start_chat(history=[])
                response = chat.send_message(
                    full_message,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=self.max_tokens,
                        temperature=self.temperature
                    )
                )
                return response.text

        except ImportError:
            frappe.log_error("Google AI library not installed. Run: pip install google-generativeai")
            return None
        except Exception as e:
            frappe.log_error(f"Google AI API error: {str(e)}")
            return None

    def custom_response(self, message, conversation_history):
        """Generate response using custom endpoint."""
        # Placeholder for custom AI provider integration
        frappe.log_error("Custom AI provider not implemented")
        return None
