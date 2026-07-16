from __future__ import annotations

import math
import re
from PIL import ImageDraw, ImageFont

WHITE = (248, 250, 255)
RED = (239, 56, 74)
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def load_fonts(width):
    return {
        "body": ImageFont.truetype(FONT_BOLD, max(36,width//18)),
        "body_small": ImageFont.truetype(FONT_BOLD, max(31,width//21)),
        "brand": ImageFont.truetype(FONT_BOLD, max(20,width//31)),
        "tiny": ImageFont.truetype(FONT_REGULAR, max(15,width//42)),
    }


def wrap_words(draw, words, font, max_width):
    lines=[]; current=[]
    for word in words:
        cand=current+[word]
        w=draw.textbbox((0,0)," ".join(cand),font=font)[2]
        if w<=max_width:
            current=cand
        else:
            if current: lines.append(current)
            current=[word]
    if current: lines.append(current)
    return lines


def draw_text_with_highlight(draw,text,highlight,scene_progress,width,height,fonts):
    font = fonts["body"] if len(text)<=75 else fonts["body_small"]
    lines = wrap_words(draw,text.split(),font,width-92)
    line_h = font.size+14
    total_h = len(lines)*line_h
    start_y = int(height*.25-total_h/2)
    key = highlight.casefold().strip()

    for li,line in enumerate(lines):
        widths=[draw.textbbox((0,0),w,font=font)[2] for w in line]
        space=draw.textbbox((0,0)," ",font=font)[2]
        line_w=sum(widths)+space*max(0,len(line)-1)
        x=(width-line_w)//2
        y=start_y+li*line_h

        for idx,word in enumerate(line):
            clean=re.sub(r'^[^\wçğıöşüÇĞİÖŞÜ]+|[^\wçğıöşüÇĞİÖŞÜ]+$','',word)
            is_key=clean.casefold()==key
            color=RED if is_key else WHITE
            draw.text((x+3,y+4),word,font=font,fill=(0,0,0,170))
            draw.text((x,y),word,font=font,fill=color)
            if is_key:
                pulse=.65+.35*(.5+.5*math.sin(scene_progress*math.pi*4))
                draw.rounded_rectangle((x,y+font.size+4,x+widths[idx],y+font.size+10),radius=3,fill=(RED[0],RED[1],RED[2],int(255*pulse)))
            x += widths[idx]+space


def draw_brand(draw,brand,scene_number,scene_count,width,fonts):
    draw.text((34,34),f"{scene_number}/{scene_count}",font=fonts["tiny"],fill=(210,220,245,210))
    box=draw.textbbox((0,0),brand,font=fonts["brand"])
    bw=box[2]-box[0]
    draw.text((width-bw-34,34),brand,font=fonts["brand"],fill=WHITE)


def draw_progress(draw,progress,width,height):
    y=height-55
    draw.line((0,y,width,y),fill=(255,255,255,180),width=3)
    draw.line((0,y,int(width*max(0,min(1,progress))),y),fill=RED,width=5)
    rights="ALL RIGHTS RESERVED"
    tiny=ImageFont.truetype(FONT_BOLD,max(14,width//45))
    draw.text((32,y+12),rights,font=tiny,fill=(240,240,245,220))
    brand="MINDORA"
    box=draw.textbbox((0,0),brand,font=tiny)
    draw.text((width-(box[2]-box[0])-32,y+12),brand,font=tiny,fill=(240,240,245,220))
