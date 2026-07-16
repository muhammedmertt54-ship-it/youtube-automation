from __future__ import annotations

import math
from PIL import Image, ImageDraw

from .animations import transform_for
from .background import draw_glow_circle

WHITE = (248, 250, 255)
LIGHT = (225, 232, 246)
RED = (239, 56, 74)
NAVY = (5, 18, 55)


def _head(draw, cx, cy, r, profile=False):
    if profile:
        draw.ellipse((cx-r, cy-r, cx+r*0.8, cy+r), fill=WHITE)
        draw.polygon([(cx+r*0.55, cy-r*0.15), (cx+r*1.0, cy), (cx+r*0.55, cy+r*0.12)], fill=WHITE)
    else:
        draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=WHITE)


def _torso(draw, cx, cy, w, h, female=False):
    if female:
        pts = [
            (cx-w*0.35, cy-h*0.45),
            (cx+w*0.35, cy-h*0.45),
            (cx+w*0.48, cy+h*0.10),
            (cx+w*0.62, cy+h*0.50),
            (cx-w*0.62, cy+h*0.50),
            (cx-w*0.48, cy+h*0.10),
        ]
        draw.polygon(pts, fill=WHITE)
    else:
        draw.rounded_rectangle(
            (cx-w*0.45, cy-h*0.45, cx+w*0.45, cy+h*0.50),
            radius=int(w*0.20),
            fill=WHITE,
        )


def draw_person(layer, cx, cy, scale=1.0, pose="neutral", female=False, profile=False):
    draw = ImageDraw.Draw(layer)
    head_r = 44*scale
    head_y = cy-145*scale
    _head(draw, cx, head_y, head_r, profile=profile)
    _torso(draw, cx, cy-20*scale, 120*scale, 180*scale, female=female)

    limb = max(12, int(18*scale))
    hip_y = cy+72*scale

    if pose == "thinking":
        draw.line((cx-28*scale, cy-40*scale, cx-88*scale, cy+28*scale), fill=WHITE, width=limb)
        draw.line((cx+25*scale, cy-40*scale, cx+72*scale, head_y+20*scale), fill=WHITE, width=limb)
        draw.ellipse((cx+60*scale, head_y+6*scale, cx+85*scale, head_y+31*scale), fill=WHITE)
    elif pose == "sad":
        draw.line((cx-25*scale, cy-40*scale, cx-70*scale, cy+55*scale), fill=WHITE, width=limb)
        draw.line((cx+25*scale, cy-40*scale, cx+70*scale, cy+55*scale), fill=WHITE, width=limb)
    elif pose == "happy":
        draw.line((cx-25*scale, cy-40*scale, cx-95*scale, cy-95*scale), fill=WHITE, width=limb)
        draw.line((cx+25*scale, cy-40*scale, cx+95*scale, cy-95*scale), fill=WHITE, width=limb)
    elif pose == "talking":
        draw.line((cx-25*scale, cy-40*scale, cx-85*scale, cy+20*scale), fill=WHITE, width=limb)
        draw.line((cx+25*scale, cy-40*scale, cx+105*scale, cy-18*scale), fill=WHITE, width=limb)
    else:
        draw.line((cx-25*scale, cy-40*scale, cx-78*scale, cy+25*scale), fill=WHITE, width=limb)
        draw.line((cx+25*scale, cy-40*scale, cx+78*scale, cy+25*scale), fill=WHITE, width=limb)

    if pose == "walking":
        draw.line((cx-22*scale, hip_y, cx-78*scale, hip_y+95*scale), fill=WHITE, width=limb)
        draw.line((cx+22*scale, hip_y, cx+90*scale, hip_y+50*scale), fill=WHITE, width=limb)
    else:
        draw.line((cx-22*scale, hip_y, cx-58*scale, hip_y+100*scale), fill=WHITE, width=limb)
        draw.line((cx+22*scale, hip_y, cx+58*scale, hip_y+100*scale), fill=WHITE, width=limb)

    if pose == "sad":
        draw.arc((cx-18*scale, head_y+8*scale, cx+18*scale, head_y+28*scale), 200, 340, fill=NAVY, width=max(3,int(4*scale)))
    else:
        draw.arc((cx-18*scale, head_y+2*scale, cx+18*scale, head_y+28*scale), 20, 160, fill=NAVY, width=max(3,int(4*scale)))


def draw_heart(draw, cx, cy, size, broken=False):
    pts = []
    for deg in range(0, 361, 4):
        a = math.radians(deg)
        x = 16*math.sin(a)**3
        y = 13*math.cos(a)-5*math.cos(2*a)-2*math.cos(3*a)-math.cos(4*a)
        pts.append((int(cx+x*size/34), int(cy-y*size/34)))
    draw.polygon(pts, fill=RED)
    if broken:
        top = cy-size//2
        crack = [(cx-5, top+size*.15),(cx+15, top+size*.33),(cx-12, top+size*.52),(cx+12, top+size*.70),(cx-6, top+size*.88)]
        draw.line(crack, fill=NAVY, width=max(8,size//22))


def draw_eye(draw, cx, cy, size):
    draw.ellipse((cx-size, cy-size*.48, cx+size, cy+size*.48), fill=WHITE)
    draw.ellipse((cx-size*.34, cy-size*.34, cx+size*.34, cy+size*.34), fill=RED)
    draw.ellipse((cx-size*.13, cy-size*.13, cx+size*.13, cy+size*.13), fill=NAVY)


def draw_brain(draw, cx, cy, size):
    r = size//5
    for ox, oy in [(-2,-1),(-1,-2),(0,-2),(1,-2),(2,-1),(-2,0),(-1,0),(0,0),(1,0),(2,0),(-2,1),(-1,2),(0,2),(1,2),(2,1)]:
        x = cx+ox*r*.72
        y = cy+oy*r*.61
        draw.ellipse((x-r,y-r,x+r,y+r), fill=WHITE)
    draw.line((cx,cy-size*.36,cx,cy+size*.36), fill=RED, width=max(8,size//22))


def draw_message(draw, cx, cy, size):
    draw.rounded_rectangle((cx-size,cy-size*.5,cx+size,cy+size*.5), radius=int(size*.2), fill=WHITE)
    draw.polygon([(cx-size*.35,cy+size*.40),(cx-size*.10,cy+size*.78),(cx,cy+size*.40)], fill=WHITE)
    for i in range(3):
        x=cx-size*.42+i*size*.42
        draw.ellipse((x-size*.07,cy-size*.07,x+size*.07,cy+size*.07), fill=RED)


def draw_two_people(layer, cx, cy, size, mode):
    distance = size*(0.42 if mode=="close" else 0.62)
    draw_person(layer, int(cx-distance), cy, scale=size/360, female=False, profile=(mode!="apart"))
    draw_person(layer, int(cx+distance), cy, scale=size/360, female=True, profile=(mode!="apart"))
    draw = ImageDraw.Draw(layer)
    if mode=="close":
        draw_heart(draw, cx, int(cy-size*.52), int(size*.33))
    elif mode=="apart":
        draw.line((cx,cy-size*.70,cx,cy+size*.62), fill=RED, width=max(8,int(size*.03)))
    else:
        draw_message(draw, cx, int(cy-size*.50), size*.28)


def draw_visual(visual_key, animation, progress, width, height):
    layer = Image.new("RGBA",(width,height),(0,0,0,0))
    t = transform_for(animation, progress, width, height)
    cx = int(width/2+t.x_offset)
    cy = int(height*.50+t.y_offset)
    scale = t.scale

    draw_glow_circle(layer,cx,cy,150,alpha=42)
    draw = ImageDraw.Draw(layer)

    if visual_key == "mindy_thinking":
        draw_person(layer,cx,cy,scale=1.08*scale,pose="thinking")
    elif visual_key == "mindy_sad":
        draw_person(layer,cx,cy,scale=1.08*scale,pose="sad")
    elif visual_key == "mindy_happy":
        draw_person(layer,cx,cy,scale=1.08*scale,pose="happy")
    elif visual_key == "mindy_walking":
        draw_person(layer,cx,cy,scale=1.08*scale,pose="walking")
    elif visual_key == "mindy_talking":
        draw_person(layer,cx,cy,scale=1.08*scale,pose="talking")
        draw_message(draw,cx+165,cy-210,70)
    elif visual_key == "two_people_close":
        draw_two_people(layer,cx,cy,260*scale,"close")
    elif visual_key == "two_people_apart":
        draw_two_people(layer,cx,cy,250*scale,"apart")
    elif visual_key == "two_people_talking":
        draw_two_people(layer,cx,cy,250*scale,"talking")
    elif visual_key == "heart_broken":
        draw_heart(draw,cx,cy,int(300*scale),True)
    elif visual_key == "heart_full":
        draw_heart(draw,cx,cy,int(300*scale),False)
    elif visual_key == "brain_thinking":
        draw_brain(draw,cx,cy,int(320*scale))
    elif visual_key == "eye_looking":
        draw_eye(draw,cx,cy,int(205*scale))
    elif visual_key == "message_bubble":
        draw_message(draw,cx,cy,int(210*scale))
    else:
        draw_person(layer,cx,cy,scale=1.08*scale,pose="thinking")

    if t.opacity < 255:
        a = layer.getchannel("A")
        a = a.point(lambda v: int(v*t.opacity/255))
        layer.putalpha(a)
    return layer
