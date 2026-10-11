"""Lip-sync avatar عن طريق SadTalker (صورة + صوت -> فيديو). بديل: Wav2Lip / MuseTalk / HeyGen API."""
import glob, os, subprocess
from config import SADTALKER_DIR


def lipsync(image_path, audio_path, out_dir):
    out_dir = os.path.abspath(out_dir); os.makedirs(out_dir, exist_ok=True)
    wav = os.path.join(out_dir, "a.wav")
    subprocess.run(["ffmpeg", "-y", "-i", os.path.abspath(audio_path), "-ar", "16000", wav], check=True)
    subprocess.run(
        ["python", "inference.py", "--driven_audio", wav, "--source_image", os.path.abspath(image_path),
         "--result_dir", out_dir, "--still", "--preprocess", "full", "--enhancer", "gfpgan"],
        cwd=SADTALKER_DIR, check=True)
    return max(glob.glob(os.path.join(out_dir, "**", "*.mp4"), recursive=True), key=os.path.getmtime)
