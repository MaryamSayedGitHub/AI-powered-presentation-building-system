from graph import draft_graph
s = draft_graph().invoke({"topic": "الذكاء الاصطناعي في التعليم", "n_slides": 3, "lang": "ar"})
with open("output/draft.md", "w", encoding="utf-8") as f:
    for x in s["slides"]:
        f.write(f"## {x['title']}\n\n" + "\n".join(f"- {b}" for b in x["bullets"]))
        f.write(f"\n\n🎙️ {x['narration']}\n\n")