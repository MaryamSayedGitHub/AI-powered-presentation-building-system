"""PPTX -> صور -> فيديو (Ken-Burns zoom + fade) + صوت + avatar في الركن."""
import glob, os, subprocess
from pathlib import Path


def _sh(cmd):
    subprocess.run(cmd, check=True)


def _dur(audio):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", audio])
    return float(out.strip())


def pptx_to_pngs(pptx, out_dir):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    _sh(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(pptx)])
    pdf = out_dir / (Path(pptx).stem + ".pdf")
    _sh(["pdftoppm", "-png", "-r", "120", str(pdf), str(out_dir / "slide")])
    return sorted(glob.glob(str(out_dir / "slide-*.png")))


def render(pptx, slides, out_path, work_dir):
    work = Path(work_dir); pngs = pptx_to_pngs(pptx, work)
    clips = []
    for i, (png, s) in enumerate(zip(pngs, slides)):
        d = _dur(s["audio"]) + 0.8
        frames = int(d * 25); clip = str(work / f"clip_{i}.mp4")
        inputs = ["-i", png, "-i", s["audio"]]
        vf = (f"[0:v]scale=3840:-2,zoompan=z='1+0.10*on/{frames}':d={frames}:s=1920x1080:fps=25,"
              f"fade=t=in:st=0:d=0.5,fade=t=out:st={d-0.5:.2f}:d=0.5[bg]")
        if s.get("avatar"):
            inputs += ["-i", s["avatar"]]
            vf += ";[2:v]scale=360:-2[av];[bg][av]overlay=W-w-40:H-h-40[v]"
        else:
            vf += ";[bg]null[v]"
        _sh(["ffmpeg", "-y", *inputs, "-filter_complex", vf, "-map", "[v]", "-map", "1:a",
             "-t", f"{d:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", clip])
        clips.append(clip)
    lst = work / "list.txt"
    lst.write_text("".join(f"file '{os.path.abspath(c)}'\n" for c in clips))
    _sh(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out_path)])
    return str(out_path)
