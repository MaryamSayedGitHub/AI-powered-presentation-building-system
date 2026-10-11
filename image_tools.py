"""أدوات تعديل الصور. كل أداة: PIL.Image -> PIL.Image. بتتحمّل lazy عشان الـ VRAM."""
import numpy as np, torch
from PIL import Image, ImageFilter

_cache = {}


def remove_bg(img):
    from rembg import remove
    return remove(img)  # RGBA


def upscale(img, scale=4):
    """Real-ESRGAN: تحسين الجودة/الدقة العامة."""
    from realesrgan import RealESRGANer
    from basicsr.archs.rrdbnet_arch import RRDBNet
    if "esrgan" not in _cache:
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        _cache["esrgan"] = RealESRGANer(
            scale=4, model=model, tile=400, half=torch.cuda.is_available(),
            model_path="https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth")
    bgr = np.array(img.convert("RGB"))[:, :, ::-1]
    out, _ = _cache["esrgan"].enhance(bgr, outscale=scale)
    return Image.fromarray(out[:, :, ::-1])


def restore_face(img):
    """GFPGAN: ترميم الوشوش (GAN-based، أنسب من StyleGAN الخام للتحسين)."""
    from gfpgan import GFPGANer
    if "gfpgan" not in _cache:
        _cache["gfpgan"] = GFPGANer(
            model_path="https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth",
            upscale=2, arch="clean", channel_multiplier=2, bg_upsampler=None)
    bgr = np.array(img.convert("RGB"))[:, :, ::-1]
    _, _, out = _cache["gfpgan"].enhance(bgr, has_aligned=False, only_center_face=False, paste_back=True)
    return Image.fromarray(out[:, :, ::-1])


def segment(img, points=None, box=None):
    """SAM: بيرجع mask (L) للعنصر اللي المستخدم ضغط عليه (points) أو حدده (box)."""
    from ultralytics import SAM
    if "sam" not in _cache:
        _cache["sam"] = SAM("sam_b.pt")
    kw = {}
    if points:
        kw.update(points=points, labels=[1] * len(points))
    if box:
        kw.update(bboxes=box)
    res = _cache["sam"](np.array(img.convert("RGB")), **kw)[0]
    mask = res.masks.data.cpu().numpy().max(0)
    return Image.fromarray((mask * 255).astype("uint8"))


def remove_object(img, points=None, box=None):
    """SAM يطلّع الـ mask + LaMa يملا المكان (inpainting)."""
    from simple_lama_inpainting import SimpleLama
    if "lama" not in _cache:
        _cache["lama"] = SimpleLama()
    mask = segment(img, points, box).filter(ImageFilter.MaxFilter(15))  # نوسّع الـ mask شوية
    return _cache["lama"](img.convert("RGB"), mask)


def keep_object(img, points=None, box=None):
    """عكس السابق: اقطع العنصر المختار بس (خلفية شفافة)."""
    rgba = img.convert("RGBA")
    rgba.putalpha(segment(img, points, box))
    return rgba


def crop(img, box=None, aspect=None):
    if box:
        return img.crop(tuple(box))
    w, h = img.size
    aw, ah = map(int, aspect.split(":"))
    t = aw / ah
    if w / h > t:
        nw = int(h * t); l = (w - nw) // 2
        return img.crop((l, 0, l + nw, h))
    nh = int(w / t); top = (h - nh) // 2
    return img.crop((0, top, w, top + nh))


OPS = {"remove_bg": remove_bg, "upscale": upscale, "restore_face": restore_face,
       "remove_object": remove_object, "keep_object": keep_object, "crop": crop}


def apply_ops(img, ops):
    """ops = [{"op": "remove_bg"}, {"op": "crop", "aspect": "4:3"}, {"op": "remove_object", "points": [[x, y]]}]"""
    for o in ops or []:
        o = dict(o)
        img = OPS[o.pop("op")](img, **o)
    return img
