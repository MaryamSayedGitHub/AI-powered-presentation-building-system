"""اختبار كل أداة لوحدها. شغّله بالترتيب وشوف أنهي واحدة بتفشل.
uv run python test_vision.py gen | bg | upscale | face | sam | crop [path]"""
import sys, time
from PIL import Image
import image_gen, image_tools
from gpu import free_vram

cmd = sys.argv[1]
src = sys.argv[2] if len(sys.argv) > 2 else "output/test_gen.png"
t = time.time()

if cmd == "gen":
    image_gen.generate("a friendly robot teacher explaining charts in a classroom").save("output/test_gen.png")
else:
    img = Image.open(src).convert("RGB")
    if cmd == "bg":
        image_tools.remove_bg(img).save("output/test_bg.png")
    elif cmd == "upscale":
        image_tools.upscale(img, 2).save("output/test_up.png")
    elif cmd == "face":
        image_tools.restore_face(img).save("output/test_face.png")
    elif cmd == "sam":   # بيمسح العنصر اللي في نص الصورة
        w, h = img.size
        image_tools.remove_object(img, points=[[w // 2, h // 2]]).save("output/test_sam.png")
    elif cmd == "crop":
        image_tools.crop(img, aspect="1:1").save("output/test_crop.png")

import torch
if torch.cuda.is_available():
    print(f"peak VRAM: {torch.cuda.max_memory_allocated()/1e9:.1f} GB")
free_vram()
print(f"{cmd} done in {time.time()-t:.1f}s")