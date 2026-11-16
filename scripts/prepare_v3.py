#!/usr/bin/env python3
"""Build revision 3 from the user's original artwork; no generative redraw."""
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
        "1794869806252.png": "file_0000000024748206a5d943989cc05052.png",
    }
    names = [name, aliases.get(name, name)]
    for p in [base/n for base in [ROOT, ROOT/"assets"] for n in names]:
        if p.is_file():
            return p
    if name == "200624.png":
        known = {"file_00000000d50082099f20787de0b9824d.png",
                 "file_0000000024748206a5d943989cc05052.png"}
        candidates = [p for base in [ROOT, ROOT/"assets"] if base.is_dir()
                      for p in base.glob("file_*.png") if p.name not in known]
        if len(candidates) == 1:
            return candidates[0]
    raise FileNotFoundError("Required original artwork missing or ambiguous: " + name)

# Use the replacement background exactly as supplied: no motif extraction,
# recoloring, opacity adjustment, shrinking, or pattern regeneration.
background = input_file("200624.png")
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
shutil.copyfile(background, SOURCE/"background-v3.png")
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

# The first bubble is now two independent Android drawable layers.
# The body reuses the unmodified second-bubble NinePatch. The trimmed sticker
# is a fixed-size BitmapDrawable anchored to its corner; it never participates
# in the body's stretch tracks.
PREVIEW = ROOT/"v3-previews"
PREVIEW.mkdir(exist_ok=True)
XML = PROJECT/"app/src/main/theme/drawable"
XML.mkdir(exist_ok=True)
report = {}
for side,fill,label in [("you","#FFFDF5","incoming"),("me","#FFECC1","outgoing")]:
    full=Image.open(SOURCE/f"bubble/{label}_decoration_192.png").convert("RGBA")
    full.thumbnail((126,126),Image.Resampling.LANCZOS)
    bounds=full.getbbox()
    assert bounds, "Empty decoration"
    art=full.crop(bounds)
    # Removing transparent margins preserves every visible pixel and the
    # current character's scale, but no longer makes the text reserve a canvas.
    aw,ah=art.size
    inset=6
    body_top=max(0,ah-24)
    total_horizontal_padding=max(60,aw+2*inset)
    pad_left=total_horizontal_padding//2
    pad_right=total_horizontal_padding-pad_left
    text_top=body_top+24
    bottom=24
    png_name=f"usagi_bubble_decoration_{side}"
    art.save(DRAW/(png_name+".png"))
    for old in DRAW.glob(f"theme_chatroom_bubble_{side}_01_image.*"):
        old.unlink()
    gravity="left" if side=="you" else "right"
    def dp(px):
        return f"{px/3:.4f}dp"
    xml=f'''<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android"
    android:paddingMode="stack"
    android:paddingLeft="{dp(pad_left)}"
    android:paddingRight="{dp(pad_right)}"
    android:paddingTop="{dp(text_top)}"
    android:paddingBottom="{dp(bottom)}">
    <item android:top="{dp(body_top)}"
        android:drawable="@drawable/theme_chatroom_bubble_{side}_02_image" />
    <item android:{gravity}="{dp(inset)}" android:top="0dp"
        android:width="{dp(aw)}" android:height="{dp(ah)}"
        android:gravity="top|{gravity}">
        <bitmap android:src="@drawable/{png_name}"
            android:gravity="top|{gravity}" android:filter="true" />
    </item>
</layer-list>
'''
    (XML/f"theme_chatroom_bubble_{side}_01_image.xml").write_text(xml)
    # Text widths model a punctuation mark, one Korean glyph, and longer
    # messages at the same font size. Compare the actual complete sticker crop.
    sheet=Image.new("RGBA",(820,1150),"#F2E8FB")
    y=12
    cases=[]
    for text_width,text_height in [(9,54),(45,54),(90,54),(330,54),(330,114)]:
        width=text_width+pad_left+pad_right
        height=text_top+text_height+bottom
        assert width>=aw+2*inset
        assert height-body_top == text_height+48
        result=Image.new("RGBA",(width,height))
        ImageDraw.Draw(result).rounded_rectangle(
            (2,body_top+2,width-3,height-3),radius=32,fill=fill)
        x=inset if side=="you" else width-inset-aw
        result.alpha_composite(art,(x,0))
        assert result.crop((x,0,x+aw,body_top)).tobytes() == art.crop((0,0,aw,body_top)).tobytes()
        # Show the precise text box without generating or redrawing artwork.
        ImageDraw.Draw(result).rectangle(
            (pad_left,text_top,pad_left+text_width-1,text_top+text_height-1),
            outline="#76598D",width=1)
        sheet.alpha_composite(result,(12,y))
        y+=height+14
        cases.append({"text_width_px":text_width,"body_height_px":height-body_top,
                      "character_px":[aw,ah],"padding_x_px":[pad_left,pad_right]})
    sheet.save(PREVIEW/f"{side}-compact-bubble-layouts.png")
    report[side]=cases

# The first resources are XML now. Keep meaningful checks for the three source
# NinePatches (two continuation bodies and the tab background), and all XML refs.
validator=PROJECT/"scripts/validate_resources.py"
checks=validator.read_text().replace("len(patches) == 5","len(patches) == 3")
checks=checks.replace("expected four bubbles and one tab background",
                      "expected two continuation bubbles and one tab background")
validator.write_text(checks)
import json
(PREVIEW/"bubble-geometry.json").write_text(json.dumps(report,indent=2)+"\\n")

# Source launcher and nonlocalized theme labels keep the existing identity.
for p in (PROJECT/"app/src/main/theme").glob("values*/strings.xml"):
    tree=ET.parse(p)
    for node in tree.getroot():
        if node.attrib.get("name") in ["app_name","theme_title"]:
            node.text="우사기 라벤더"
    tree.write(p,encoding="utf-8",xml_declaration=True)
gradle=PROJECT/"app/build.gradle.kts"
text=gradle.read_text().replace('versionName = "1.0.0"','versionName = "1.2.0"')
# Pin AGP's debug signing input to the keystore restored by Actions. The
# SDK's own Android user directory can differ from the shell's ~/.android.
text=text.replace("android {", """android {
    signingConfigs.getByName("debug") {
        storeFile = file(System.getProperty("user.home") + "/.android/debug.keystore")
        storePassword = "android"
        keyAlias = "androiddebugkey"
        keyPassword = "android"
        enableV1Signing = true
        enableV2Signing = true
    }
""", 1)
gradle.write_text(text)
canvas.resize((720,1440)).save(ROOT/"v3-previews/background.png")
sheet=Image.new("RGBA",(960,192),"#F2E8FB")
for i,tab in enumerate(["friends","chats","now","shopping","more"]):
    sheet.alpha_composite(Image.open(DRAW/f"theme_maintab_ico_{tab}_focused_image.png"),(192*i,0))
sheet.save(ROOT/"v3-previews/selected-menu.png")
print("Revision 3 prepared: supplied 200624.png background unchanged, compact layered first bubbles, selected tab art.")
