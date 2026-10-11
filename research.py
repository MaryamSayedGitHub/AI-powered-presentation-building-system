"""بحث اختياري على النت (Tavily) عشان الـ Planner يبني على معلومات حقيقية. من غير TAVILY_API_KEY بيرجّع نص فاضي."""
import os
from dotenv import load_dotenv

load_dotenv()


def research(topic: str, max_results: int = 5) -> str:
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        return ""
    from tavily import TavilyClient
    res = TavilyClient(api_key=key).search(topic, max_results=max_results, search_depth="basic")
    return "\n".join(f"- {r['title']}: {r['content'][:400]} ({r['url']})" for r in res.get("results", []))
