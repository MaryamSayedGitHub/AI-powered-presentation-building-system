"""الـ Orchestrator (LangGraph). graph للمسودة (research -> plan -> write -> critic loop) و graph للإنتاج."""
from typing import TypedDict
from PIL import Image
from langgraph.graph import StateGraph, END
import agents, image_gen, image_tools, tts, avatar, pptx_builder, video_render, research
from config import WORKDIR, MAX_REVISIONS
from gpu import free_vram


class S(TypedDict, total=False):
    topic: str; n_slides: int; lang: str; notes: str
    outline: dict; slides: list; review: dict; iters: int
    user_images: dict; image_ops: dict      # {slide_idx: path} , {slide_idx: [ops]}
    avatar_image: str; make_video: bool
    pptx: str; video: str


# ---------- draft graph ----------
def n_research(s):
    return {"notes": research.research(s["topic"])}


def n_plan(s):
    return {"outline": agents.planner(s["topic"], s["n_slides"], s["lang"], notes=s.get("notes", "")), "iters": 0}


def n_write(s):
    slides, titles = [], []
    for sp in s["outline"]["slides"]:
        sl = agents.write_slide(s["outline"]["title"], sp, s["lang"], titles)
        slides.append(sl); titles.append(sl["title"])
    return {"slides": slides}


def n_critic(s):
    return {"review": agents.critic(s["outline"]["title"], s["slides"]), "iters": s["iters"] + 1}


def n_fix(s):
    slides, titles = list(s["slides"]), [x["title"] for x in s["slides"]]
    for it in s["review"]["issues"]:
        i = it["idx"]
        if 0 <= i < len(slides):
            slides[i] = agents.write_slide(s["outline"]["title"], s["outline"]["slides"][i], s["lang"],
                                           titles[:i], feedback=it["feedback"])
    return {"slides": slides}


def route(s):
    return "fix" if (not s["review"]["ok"] and s["iters"] < MAX_REVISIONS) else END


def draft_graph():
    g = StateGraph(S)
    for name, fn in [("research", n_research), ("plan", n_plan), ("write", n_write),
                     ("critic", n_critic), ("fix", n_fix)]:
        g.add_node(name, fn)
    g.set_entry_point("research"); g.add_edge("research", "plan"); g.add_edge("plan", "write")
    g.add_edge("write", "critic")
    g.add_conditional_edges("critic", route, {"fix": "fix", END: END}); g.add_edge("fix", "critic")
    return g.compile()


# ---------- production graph ----------
def n_images(s):
    slides = [dict(x) for x in s["slides"]]
    for i, sl in enumerate(slides):
        if i in s.get("user_images", {}):
            img = Image.open(s["user_images"][i])
        elif sl.get("image_prompt"):
            img = image_gen.generate(sl["image_prompt"])
        else:
            continue
        img = image_tools.apply_ops(img, s.get("image_ops", {}).get(i))
        p = WORKDIR / f"img_{i}.png"; img.save(p); sl["image"] = str(p)
    free_vram()
    return {"slides": slides}


def n_audio(s):
    import tts
    slides = [dict(x) for x in s["slides"]]
    for i, sl in enumerate(slides):
        sl["audio"] = tts.synth(sl["narration"], WORKDIR / f"audio_{i}.mp3", s["lang"])
    return {"slides": slides}


def n_pptx(s):
    return {"pptx": pptx_builder.build({"slides": s["slides"]}, str(WORKDIR / "deck.pptx"), s["lang"])}


def n_video(s):
    slides = [dict(x) for x in s["slides"]]
    if s.get("avatar_image"):
        for i, sl in enumerate(slides):
            sl["avatar"] = avatar.lipsync(s["avatar_image"], sl["audio"], WORKDIR / f"avatar_{i}")
    free_vram()
    return {"video": video_render.render(s["pptx"], slides, WORKDIR / "final.mp4", WORKDIR / "frames")}


def go_video(s):
    return "video" if s.get("make_video") else END


def produce_graph():
    g = StateGraph(S)
    for name, fn in [("images", n_images), ("audio", n_audio), ("pptx", n_pptx), ("video", n_video)]:
        g.add_node(name, fn)
    g.set_entry_point("images"); g.add_edge("images", "audio"); g.add_edge("audio", "pptx")
    g.add_conditional_edges("pptx", go_video, {"video": "video", END: END}); g.add_edge("video", END)
    return g.compile()