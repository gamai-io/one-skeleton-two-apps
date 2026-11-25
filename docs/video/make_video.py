#!/usr/bin/env python3
"""Render the real demo output into a short MP4 (terminal look, typed lines)."""
import subprocess, textwrap, os, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "video"
OUT.mkdir(parents=True, exist_ok=True)

def run(cmd):
    r = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True)
    return (r.stdout + r.stderr).rstrip().splitlines()

lines = []
lines += ["$ python3 run_demo.py"]
lines += run("python3 run_demo.py")
lines += ["", "$ python3 run_demo.py --tamper"]
lines += run("python3 run_demo.py --tamper")

W, H = 1280, 720
BG, FG, ACC = (13, 15, 18), (222, 226, 230), (110, 200, 140)
RED = (235, 110, 110)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 20)
bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 22)

def frame(visible_lines, title="kiroween · one skeleton, two apps"):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # title bar
    d.rectangle([0, 0, W, 44], fill=(24, 27, 32))
    d.ellipse([16, 14, 30, 28], fill=(237, 106, 94))
    d.ellipse([38, 14, 52, 28], fill=(245, 191, 79))
    d.ellipse([60, 14, 74, 28], fill=(98, 197, 84))
    d.text((92, 12), title, font=font, fill=(150, 156, 165))
    y = 70
    for ln in visible_lines[-26:]:
        col = FG
        if "REFUTED" in ln: col = RED
        elif "CONFIRMED" in ln: col = ACC
        elif ln.startswith("$"): col = (140, 170, 240)
        elif "body hash mismatch" in ln: col = RED
        for seg in textwrap.wrap(ln, 96) or [""]:
            d.text((28, y), seg, font=font, fill=col)
            y += 24
    return img

frames = []
HOLD = 5   # ~0.5 s per line at 10 fps
for i in range(1, len(lines) + 1):
    fr = frame(lines[:i])
    frames.extend([fr] * HOLD)
frames.extend([frames[-1]] * 20)   # final hold

for idx, fr in enumerate(frames):
    fr.save(OUT / f"f{idx:04d}.png")

subprocess.run(
    f'ffmpeg -y -loglevel error -framerate 10 -i "{OUT}/f%04d.png" '
    f'-vf "format=yuv420p" -c:v libx264 -preset medium -crf 20 "{OUT}/demo.mp4"',
    check=True, shell=True)
for f in OUT.glob("f*.png"): f.unlink()
print("video:", OUT / "demo.mp4", os.path.getsize(OUT / "demo.mp4"), "bytes",
      "| frames:", len(frames))
