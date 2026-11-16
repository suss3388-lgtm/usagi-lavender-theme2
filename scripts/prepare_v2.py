#!/usr/bin/env python3
"""Build revision 2 from the user's original artwork; no generative redraw."""
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "build-source/usagi-lavender-theme2"
DRAW = PROJECT / "app/src/main/theme/drawable-xxhdpi"
SOURCE = PROJECT / "design/source"

def input_file(name):
    aliases = {
        "200614.png": "file_00000000d50082099f20787de0b9824d.png",
        "1794869806252.png": "file_0000000024748206a5d943989cc05052.png",
    }
    names = [name, aliases.get(name, name)]
    for p in [base/n for base in [ROOT, ROOT/"assets"] for n in names]:
        if p.is_file():
            return p
    raise FileNotFoundError("Required original artwork missing: " + name)

# Use the replacement background exactly as supplied: no motif extraction,
# recoloring, opacity adjustment, shrinking, or pattern regeneration.
background = input_file("200614.png")
canvas = Image.open(background).convert("RGBA")
assert canvas.height > canvas.width, "Expected the supplied portrait background"
selected = Image.open(input_file("1794869806252.png")).convert("RGBA")
if selected.getextrema()[3][0] == 255:
    # If the download flattened transparency to a black matte, remove only
    # the near-black region connected to the outer border. The white sticker
    # border separates it from the original character's black line art.
    from collections import deque
    w,h=selected.size
    px=selected.load()
    q=deque([(x,0) for x in range(w)]+[(x,h-1) for x in range(w)]+
            [(0,y) for y in range(h)]+[(w-1,y) for y in range(h)])
    seen=set()
    while q:
        x,y=q.popleft()
        if (x,y) in seen or not (0<=x<w and 0<=y<h):
            continue
        seen.add((x,y))
        r,g,b,a=px[x,y]
        if max(r,g,b)>12:
            continue
        px[x,y]=(r,g,b,0)
        q.extend([(x-1,y),(x+1,y),(x,y-1),(x,y+1)])
assert selected.getextrema()[3][0] == 0, "Selected icon needs a transparent outer background"
shutil.copyfile(background, SOURCE/"background-v2.png")
for name in ["theme_background_image","theme_chatroom_background_image",
             "theme_passcode_background_image","theme_splash_image"]:
    shutil.copyfile(background, DRAW/(name+".png"))

# A transparent, aspect-preserving 64dp tile replaces only selected states.
selected=selected.crop(selected.getbbox())
selected.thumbnail((172,172),Image.Resampling.LANCZOS)
tile=Image.new("RGBA",(192,192))
tile.alpha_composite(selected,((192-selected.width)//2,(192-selected.height)//2))
for tab in ["friends","chats","now","shopping","more"]:
    tile.save(DRAW/f"theme_maintab_ico_{tab}_focused_image.png")

def ninepatch(image,name,sx,sy,px,py):
    w,h=image.size
    out=Image.new("RGBA",(w+2,h+2))
    out.alpha_composite(image,(1,1))
    d=ImageDraw.Draw(out)
    for line in [(sx[0]+1,0,sx[1]+1,0),(0,sy[0]+1,0,sy[1]+1),
                 (px[0]+1,h+1,px[1]+1,h+1),(w+1,py[0]+1,w+1,py[1]+1)]:
        d.line(line,fill=(0,0,0,255))
    out.save(DRAW/(name+".9.png"))

# KakaoTalk can force a bubble below its NinePatch intrinsic width.
# Padding therefore reserves at least ALL fixed columns, independently of text
# width. The character remains in those fixed columns on both receive/send.
W,H=228,240
SX=(174,209)
SY=(176,199)
FIXED_WIDTH=W-(SX[1]-SX[0]+1)
for side,fill,label in [("you","#FFFDF5","incoming"),("me","#FFECC1","outgoing")]:
    img=Image.new("RGBA",(W,H))
    ImageDraw.Draw(img).rounded_rectangle((2,102,W-3,H-3),radius=27,fill=fill)
    art=Image.open(SOURCE/f"bubble/{label}_decoration_192.png").convert("RGBA")
    art.thumbnail((126,126),Image.Resampling.LANCZOS)
    x=8 if side=="you" else W-8-art.width
    img.alpha_composite(art,(x,0))
    # Receive stretches to the right of the artwork; send stretches to its left.
    sx=SX if side=="you" else (18,53)
    px=(100,127)  # 200px horizontal padding > 192px of non-stretch columns.
    assert px[0]+(W-1-px[1]) >= FIXED_WIDTH
    ninepatch(img,f"theme_chatroom_bubble_{side}_01_image",sx,SY,px,(156,179))
    # Character pixels are identical across narrow and long simulated bubbles.
    def render(width):
        a,b=sx
        parts=[img.crop((0,0,a,H)),
               img.crop((a,0,b+1,H)).resize((width-FIXED_WIDTH,H),Image.Resampling.NEAREST),
               img.crop((b+1,0,W,H))]
        result=Image.new("RGBA",(width,H))
        offset=0
        for part in parts:
            result.alpha_composite(part,(offset,0))
            offset+=part.width
        return result
    for width in [201,228,700]:
        result=render(width)
        position=8 if side=="you" else width-8-art.width
        original=img.crop((x,0,x+art.width,102))
        actual=result.crop((position,0,position+art.width,102))
        assert original.tobytes()==actual.tobytes(), (side,width,"character changed")
    # Export representative widths as review evidence.
    preview=Image.new("RGBA",(760,800),"#F2E8FB")
    for y,width in [(20,201),(280,350),(540,700)]:
        preview.alpha_composite(render(width),(16,y))
    (ROOT/"v2-previews").mkdir(exist_ok=True)
    preview.save(ROOT/f"v2-previews/{side}-bubble-widths.png")

# Source launcher and nonlocalized theme labels keep the existing identity.
for p in (PROJECT/"app/src/main/theme").glob("values*/strings.xml"):
    tree=ET.parse(p)
    for node in tree.getroot():
        if node.attrib.get("name") in ["app_name","theme_title"]:
            node.text="우사기 라벤더"
    tree.write(p,encoding="utf-8",xml_declaration=True)
gradle=PROJECT/"app/build.gradle.kts"
text=gradle.read_text().replace('versionName = "1.0.0"','versionName = "1.1.0"')
gradle.write_text(text)
canvas.resize((720,1440)).save(ROOT/"v2-previews/background.png")
sheet=Image.new("RGBA",(960,192),"#F2E8FB")
for i,tab in enumerate(["friends","chats","now","shopping","more"]):
    sheet.alpha_composite(Image.open(DRAW/f"theme_maintab_ico_{tab}_focused_image.png"),(192*i,0))
sheet.save(ROOT/"v2-previews/selected-menu.png")
print("Revision 2 prepared: supplied 200614.png background unchanged, fixed-character padding, selected tab art.")
