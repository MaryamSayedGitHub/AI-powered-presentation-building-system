import argparse
from graph import draft_graph, produce_graph

ap = argparse.ArgumentParser()
ap.add_argument("--topic", required=True); ap.add_argument("--slides", type=int, default=6)
ap.add_argument("--lang", default="ar"); ap.add_argument("--video", action="store_true")
ap.add_argument("--avatar", help="صورة وش للـ avatar")
a = ap.parse_args()

state = draft_graph().invoke({"topic": a.topic, "n_slides": a.slides, "lang": a.lang})
state.update(make_video=a.video, avatar_image=a.avatar, user_images={}, image_ops={})
out = produce_graph().invoke(state)
print("PPTX:", out["pptx"], "| VIDEO:", out.get("video"))
