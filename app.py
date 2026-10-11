"""streamlit run app.py"""
import streamlit as st
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates
from graph import draft_graph, produce_graph
from config import WORKDIR

st.set_page_config(page_title="AI Presentation Studio", layout="wide")
st.title("🎞️ AI Presentation Studio")

with st.sidebar:
    topic = st.text_area("موضوع البريزنتيشن")
    n = st.slider("عدد السلايدز", 3, 15, 6)
    lang = st.selectbox("اللغة", ["ar", "en"])
    make_video = st.checkbox("فيديو + صوت", True)
    av = st.file_uploader("صورة الـ Avatar (اختياري)", type=["png", "jpg"])
    if st.button("1) اعمل المسودة", type="primary") and topic:
        with st.spinner("Agents شغالين..."):
            st.session_state.state = draft_graph().invoke({"topic": topic, "n_slides": n, "lang": lang})

if "state" in st.session_state:
    s = st.session_state.state
    s.setdefault("user_images", {}); s.setdefault("image_ops", {})
    for i, sl in enumerate(s["slides"]):
        with st.expander(f"Slide {i+1}: {sl['title']}", expanded=(i == 0)):
            sl["title"] = st.text_input("العنوان", sl["title"], key=f"t{i}")
            sl["bullets"] = st.text_area("النقاط", "\n".join(sl["bullets"]), key=f"b{i}").split("\n")
            sl["narration"] = st.text_area("الشرح الصوتي", sl["narration"], key=f"n{i}")
            sl["image_prompt"] = st.text_input("Prompt الصورة", sl["image_prompt"], key=f"p{i}")
            up = st.file_uploader("أو ارفع صورتك", type=["png", "jpg", "jpeg"], key=f"u{i}")
            ops = []
            if up:
                path = WORKDIR / f"user_{i}.png"; img = Image.open(up).convert("RGB"); img.save(path)
                s["user_images"][i] = str(path)
                pt = streamlit_image_coordinates(img, key=f"c{i}", width=400)
                chosen = st.multiselect("تعديلات", ["remove_bg", "upscale", "restore_face", "crop 16:9"], key=f"o{i}")
                if pt and st.checkbox("امسح العنصر اللي ضغطت عليه", key=f"r{i}"):
                    k = img.width / pt["width"]
                    ops.append({"op": "remove_object", "points": [[pt["x"] * k, pt["y"] * k]]})
                for c in chosen:
                    ops.append({"op": "crop", "aspect": "16:9"} if c.startswith("crop") else {"op": c})
            s["image_ops"][i] = ops
    if st.button("2) اعمل البريزنتيشن النهائية"):
        s.update(make_video=make_video, user_images=s["user_images"], image_ops=s["image_ops"])
        if av:
            p = WORKDIR / "avatar.png"; Image.open(av).convert("RGB").save(p); s["avatar_image"] = str(p)
        with st.spinner("بنولّد الصور والصوت والملفات..."):
            out = produce_graph().invoke(s)
        st.download_button("⬇️ PPTX", open(out["pptx"], "rb"), "deck.pptx")
        if out.get("video"):
            st.video(out["video"])
