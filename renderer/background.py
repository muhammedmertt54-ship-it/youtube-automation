from __future__ import annotations

import math
import random
from PIL import Image, ImageDraw, ImageFilter

NAVY_TOP=(3,8,42)
NAVY_BOTTOM=(8,18,72)
WHITE=(248,250,255)
RED=(239,56,74)
BLUE_GLOW=(42,80,190)


def create_gradient(width,height):
    img=Image.new("RGB",(width,height),NAVY_TOP)
    d=ImageDraw.Draw(img)
    for y in range(height):
        r=(y/max(1,height-1))**1.2
        c=tuple(int(NAVY_TOP[i]*(1-r)+NAVY_BOTTOM[i]*r) for i in range(3))
        d.line((0,y,width,y),fill=c)
    return img.convert("RGBA")


def draw_particles(draw,frame_number,scene_index,width,height):
    random.seed(scene_index*777)
    for i in range(16):
        bx=random.randint(0,width); by=random.randint(0,height)
        speed=random.uniform(.12,.40)
        rad=random.choice([1,1,2])
        x=(bx+math.sin(frame_number*.012*speed+i)*12)%width
        y=(by-frame_number*speed*.25)%height
        a=random.randint(12,34)
        draw.ellipse((x-rad,y-rad,x+rad,y+rad),fill=(180,205,255,a))


def draw_wave_lines(draw,frame_number,width,height):
    phase=frame_number*.028
    configs=[
        (82,13,130,(255,255,255,150),5,0.0),
        (102,16,145,(239,56,74,170),7,1.2),
    ]
    for base,amp,period,color,lw,off in configs:
        pts=[]
        for x in range(-20,width+21,8):
            y=base+math.sin(x/period+phase+off)*amp
            pts.append((x,int(y)))
        draw.line(pts,fill=color,width=lw,joint="curve")


def draw_glow_circle(layer,cx,cy,radius,color=BLUE_GLOW,alpha=50):
    g=Image.new("RGBA",layer.size,(0,0,0,0))
    gd=ImageDraw.Draw(g)
    gd.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),fill=(*color,alpha))
    g=g.filter(ImageFilter.GaussianBlur(max(8,radius//2)))
    layer.alpha_composite(g)


def apply_vignette(image):
    w,h=image.size
    ov=Image.new("RGBA",image.size,(0,0,0,0))
    px=ov.load()
    cx=w/2; cy=h/2; md=math.sqrt(cx**2+cy**2)
    for y in range(0,h,4):
        for x in range(0,w,4):
            dist=math.sqrt((x-cx)**2+(y-cy)**2)
            ratio=max(0,min(1,dist/md))
            alpha=int(max(0,(ratio-.42)*170))
            for yy in range(y,min(y+4,h)):
                for xx in range(x,min(x+4,w)):
                    px[xx,yy]=(0,0,0,alpha)
    image.alpha_composite(ov)
