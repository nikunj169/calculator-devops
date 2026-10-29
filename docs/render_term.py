"""Render a captured text file as a terminal-window PNG: render_term.py <in.txt> <out.png> <title> [wrap]"""
import sys, textwrap
from PIL import Image, ImageDraw, ImageFont
src, out, title = sys.argv[1:4]
wrap = int(sys.argv[4]) if len(sys.argv) > 4 else 130
font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 22)
lines = []
for raw in open(src).read().rstrip("\n").split("\n"):
    lines += textwrap.wrap(raw.expandtabs(4), wrap, subsequent_indent="    ", drop_whitespace=False) or [""]
cw = font.getbbox("M")[2]; lh = 30; pad = 24; bar = 44
W = max(900, pad * 2 + cw * max(len(l) for l in lines)); H = bar + pad * 2 + lh * len(lines)
img = Image.new("RGB", (W, H), "#1e1e1e"); d = ImageDraw.Draw(img)
d.rectangle([0, 0, W, bar], fill="#323232")
for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    d.ellipse([18 + i * 26, 14, 34 + i * 26, 30], fill=c)
tf = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 18)
d.text(((W - d.textlength(title, font=tf)) / 2, 12), title, font=tf, fill="#cccccc")
y = bar + pad
for l in lines:
    color = "#e6e6e6"
    if l.startswith("$"): color = "#7ee787"
    elif "HTTP 400" in l or "FAIL" in l: color = "#ffa657"
    elif "Finished: SUCCESS" in l or "Healthy" in l or "healthy" in l or "Health check passed" in l: color = "#56d364"
    elif l.startswith("[Pipeline] {"): color = "#79c0ff"
    d.text((pad, y), l, font=font, fill=color); y += lh
img.save(out)
print(out, img.size)
