import os
from typing import Generator
from config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    GROQ_FALLBACK_MODEL,
)


class LLM:
    """
    Intelligent Multi-Provider Cloud LLM Engine.
    Automatically detects available API keys (.env) in priority order:
    1. Groq (Llama 3.3 70B)
    2. Google Gemini (Gemini 1.5 Flash / Gemini 2.0 Flash)
    3. OpenRouter (Free Cloud Llama / DeepSeek / Gemini)
    4. OpenAI (GPT-4o mini)
    """

    def __init__(self, api_key: str = None, temperature: float = 0.2):
        self.temperature = temperature
        self.provider = "none"

        # Load keys from env
        groq_key = (api_key or GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")).strip()
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()

        # Determine active provider
        if groq_key and groq_key != "your_groq_api_key_here" and not groq_key.startswith("your_"):
            self.provider = "groq"
            self.api_key = groq_key
            self.model_name = GROQ_MODEL
            self.fallback_model = GROQ_FALLBACK_MODEL
            from groq import Groq
            self.client = Groq(api_key=self.api_key)

        elif gemini_key and gemini_key != "your_gemini_api_key_here":
            self.provider = "gemini"
            self.api_key = gemini_key
            self.model_name = "gemini-1.5-flash"
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={"temperature": self.temperature}
            )

        elif openrouter_key and openrouter_key != "your_openrouter_api_key_here":
            self.provider = "openrouter"
            self.api_key = openrouter_key
            self.model_name = "meta-llama/llama-3.3-70b-instruct:free"
            from openai import OpenAI
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key
            )

        elif openai_key and openai_key != "your_openai_api_key_here":
            self.provider = "openai"
            self.api_key = openai_key
            self.model_name = "gpt-4o-mini"
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)

        else:
            self.provider = "unconfigured"
            self.api_key = ""

    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Synchronous generation."""
        if self.provider == "unconfigured":
            return (
                "⚠️ **No valid API Key detected.**\n\n"
                "Please add your API key to the `.env` file:\n"
                "- **Groq**: `GROQ_API_KEY=gsk_...` (Get free at https://console.groq.com/keys)\n"
                "- **Gemini**: `GEMINI_API_KEY=AIza...` (Get free at https://aistudio.google.com)\n"
                "- **OpenRouter**: `OPENROUTER_API_KEY=sk-or-...` (Get free at https://openrouter.ai/keys)"
            )

        try:
            if self.provider == "groq":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                for model in [self.model_name, self.fallback_model]:
                    try:
                        resp = self.client.chat.completions.create(
                            model=model,
                            messages=messages,
                            temperature=self.temperature
                        )
                        return resp.choices[0].message.content or ""
                    except Exception as e:
                        if model == self.model_name:
                            continue
                        raise e

            elif self.provider == "gemini":
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                resp = self.client.generate_content(full_prompt)
                return resp.text if resp.text else ""

            elif self.provider in ["openrouter", "openai"]:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                resp = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature
                )
                return resp.choices[0].message.content or ""

        except Exception as e:
            return f"❌ {self.provider.capitalize()} Error: {str(e)}"

    def stream(self, prompt: str, system_prompt: str = None) -> Generator[str, None, None]:
        """Streaming token generator."""
        if self.provider == "unconfigured":
            yield (
                "⚠️ **No valid API Key detected.**\n\n"
                "Please replace the placeholder in your `.env` file with your actual key:\n\n"
                "```env\n"
                "GROQ_API_KEY=gsk_your_actual_key_here\n"
                "```\n\n"
                "👉 Get your free key at **https://console.groq.com/keys**"
            )
            return

        try:
            if self.provider == "groq":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                try:
                    stream_resp = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        temperature=self.temperature,
                        stream=True
                    )
                    for chunk in stream_resp:
                        if chunk.choices and chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
                except Exception:
                    # Fallback to secondary model
                    fallback_resp = self.client.chat.completions.create(
                        model=self.fallback_model,
                        messages=messages,
                        temperature=self.temperature,
                        stream=True
                    )
                    for chunk in fallback_resp:
                        if chunk.choices and chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content

            elif self.provider == "gemini":
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                resp = self.client.generate_content(full_prompt, stream=True)
                for chunk in resp:
                    if chunk.text:
                        yield chunk.text

            elif self.provider in ["openrouter", "openai"]:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                resp = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    stream=True
                )
                for chunk in resp:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content

        except Exception as e:
            yield f"\n\n❌ {self.provider.capitalize()} Error: {str(e)}"