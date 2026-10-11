import torch
from config import IMAGE_MODEL
from gpu import device

_pipe = None
STYLE = ", clean modern flat illustration, soft gradients, cohesive color palette, no text, high quality"


def _load():
    from diffusers import AutoPipelineForText2Image
    if device() == "cuda":
        pipe = AutoPipelineForText2Image.from_pretrained(IMAGE_MODEL, torch_dtype=torch.float16, variant="fp16")
        pipe.enable_model_cpu_offload()   # بيحمّل كل جزء على الكارت وقت الحاجة بس (مناسب لـ 8 GB)
        pipe.enable_vae_tiling()          # بيمنع spike في الذاكرة وقت فك الصورة
    else:
        pipe = AutoPipelineForText2Image.from_pretrained(IMAGE_MODEL)  # CPU: بطيء جداً
    return pipe


def generate(prompt: str, size=(1024, 576)):
    global _pipe
    if _pipe is None:
        _pipe = _load()
    return _pipe(prompt + STYLE, width=size[0], height=size[1],
                 num_inference_steps=4, guidance_scale=0.0).images[0]