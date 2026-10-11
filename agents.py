"""الـ Agents: كل واحد ليه دور واحد واضح (Planner / Writer / Critic)."""
from llm import ask_json

TRANSITIONS = ["fade", "push", "wipe", "cover", "zoom"]
LANG_NAME = {"ar": "simple Modern Standard Arabic", "en": "English"}
NARRATION_STYLE = {
    "ar": ("natural Egyptian colloquial Arabic (عامية مصرية) for EVERY slide, never formal Arabic. "
           "Use words like: ده، دلوقتي، عشان، إزاي، كده، مش. Keep the same style on all slides. "
           "Put a space between every two words."),
    "en": "conversational English",
}
def planner(topic, n_slides, lang, audience="general", notes=""):
    sys = "You are a presentation architect. Design a clear narrative arc: hook, problem, solution, evidence, call to action."
    user = (f"Topic: {topic}\nAudience: {audience}\nSlides: {n_slides}\nLanguage: {LANG_NAME[lang]}\n"
            + (f"Research notes (put real facts from here into the slide goals):\n{notes}\n" if notes else "")
            + 'Return {"title": str, "slides": [{"idx": int, "goal": str}]}')
    return ask_json(sys, user)


def write_slide(deck_title, slide_plan, lang, prev_titles, feedback=None):
    sys = ("You write ONE slide plus its spoken narration. Rules: title <= 8 words; 3-5 bullets, each <= 12 words; "
           "narration 40-70 words, natural spoken style; image_prompt is ALWAYS English, describes a concrete "
           "illustration (no text in image), style: clean modern flat illustration, cohesive palette; "
           f"transition one of {TRANSITIONS}.")
    user = (f"Deck: {deck_title}\nPrevious slide titles: {prev_titles}\nThis slide goal: {slide_plan['goal']}\n"
            f"Language for title/bullets: {LANG_NAME[lang]}\nNarration style: {NARRATION_STYLE[lang]}\n"
            + (f"Fix this feedback: {feedback}\n" if feedback else "")
            + 'Return {"title": str, "bullets": [str], "narration": str, "image_prompt": str, "transition": str}')
    
    return ask_json(sys, user)


def critic(deck_title, slides):
    sys = ("You are a strict presentation reviewer. Check: flow between slides, redundancy, too much text, "
           "image_prompt quality, narration matching bullets.")
    user = (f"Deck: {deck_title}\nSlides: {slides}\n"
            'Return {"ok": bool, "issues": [{"idx": int, "feedback": str}]}  (idx = 0-based position)')
    return ask_json(sys, user)