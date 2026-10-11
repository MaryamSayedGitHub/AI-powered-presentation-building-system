"""LLM موحّد: Groq / Gemini / xAI / Ollama (كلهم OpenAI-compatible) + Anthropic. الاختيار من LLM_PROVIDER في .env"""
import json, os, re
from dotenv import load_dotenv

load_dotenv()

# provider: (base_url, اسم متغير الـ key)
OPENAI_COMPAT = {
    "groq":   ("https://api.groq.com/openai/v1", "GROQ_API_KEY"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai/", "GOOGLE_API_KEY"),
    "xai":    ("https://api.x.ai/v1", "XAI_API_KEY"),
    "ollama": (None, None),
}


def _provider():
    return os.getenv("LLM_PROVIDER", "groq").lower()


def ask(system: str, user: str, max_tokens: int = 4000, json_mode: bool = False) -> str:
    p = _provider()
    model = os.getenv(f"{p.upper()}_MODEL")
    if not model:
        raise RuntimeError(f"{p.upper()}_MODEL فاضي في .env")
    temp = float(os.getenv("LLM_TEMPERATURE", "0"))

    if p == "anthropic":
        from anthropic import Anthropic
        r = Anthropic().messages.create(model=model, max_tokens=max_tokens, temperature=temp, system=system,
                                        messages=[{"role": "user", "content": user}])
        return r.content[0].text

    from openai import OpenAI
    base, key_env = OPENAI_COMPAT[p]
    if p == "ollama":
        base, key = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") + "/v1", "ollama"
    else:
        key = os.getenv(key_env)
        if not key:
            raise RuntimeError(f"{key_env} فاضي في .env")
    client = OpenAI(base_url=base, api_key=key)
    kw = dict(model=model, temperature=temp, max_tokens=max_tokens,
              messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
    if json_mode:
        try:
            return client.chat.completions.create(response_format={"type": "json_object"}, **kw).choices[0].message.content
        except Exception:
            pass  # بعض الموديلات مبتدعمش json mode، نكمّل من غيره
    return client.chat.completions.create(**kw).choices[0].message.content


def _extract_json(text: str):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        a, b = text.find("{"), text.rfind("}")      # الموديلات الأضعف أحياناً بتضيف كلام حوالين الـ JSON
        return json.loads(text[a:b + 1])


def ask_json(system: str, user: str, **kw):
    sys = system + "\nReturn ONLY one valid JSON object. No markdown fences, no commentary."
    for attempt in range(2):
        try:
            return _extract_json(ask(sys, user, json_mode=True, **kw))
        except json.JSONDecodeError:
            if attempt == 1:
                raise
