import gc
import torch


def device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


def free_vram():
    """نادِها بعد كل مرحلة تقيلة (توليد صور / تعديل صور / avatar) عشان الـ 8 GB متخلصش."""
    import image_gen, image_tools
    image_gen._pipe = None
    image_tools._cache.clear()
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()