from __future__ import annotations

import math

from PIL import Image, ImageDraw

from .animations import transform_for
from .background import draw_glow_circle


WHITE = (248, 250, 255)
RED = (239, 56, 74)
NAVY = (5, 18, 55)


def draw_heart(draw, cx, cy, size, broken=False):
    points = []
    for step in range(0, 361, 4):
        angle = math.radians(step)
        x = 16 * math.sin(angle) ** 3
        y = (
            13 * math.cos(angle)
            - 5 * math.cos(2 * angle)
            - 2 * math.cos(3 * angle)
            - math.cos(4 * angle)
        )
        points.append((int(cx + x * size / 34), int(cy - y * size / 34)))
    draw.polygon(points, fill=RED)

    if broken:
        top = cy - size // 2
        crack = [
            (cx - 6, top + size * 0.16),
            (cx + 18, top + size * 0.34),
            (cx - 13, top + size * 0.52),
            (cx + 11, top + size * 0.70),
            (cx - 7, top + size * 0.88),
        ]
        draw.line(crack, fill=NAVY, width=max(8, size // 24))


def draw_person(canvas, cx, cy, scale=1.0, pose="neutral"):
    draw = ImageDraw.Draw(canvas)
    stroke = max(10, int(18 * scale))
    head_radius = int(52 * scale)
    torso_length = int(170 * scale)
    limb_length = int(112 * scale)
    head_y = int(cy - torso_length * 0.67)

    draw.ellipse(
        (
            cx - head_radius - 8,
            head_y - head_radius + 11,
            cx + head_radius + 8,
            head_y + head_radius + 27,
        ),
        fill=(0, 0, 0, 62),
    )
    draw.ellipse(
        (
            cx - head_radius,
            head_y - head_radius,
            cx + head_radius,
            head_y + head_radius,
        ),
        fill=WHITE,
    )

    shoulder_y = int(cy - torso_length * 0.25)
    hip_y = int(cy + torso_length * 0.55)
    draw.line((cx, shoulder_y, cx, hip_y), fill=WHITE, width=stroke)

    if pose == "thinking":
        draw.line((cx, shoulder_y, cx - 70*scale, cy + 20*scale), fill=WHITE, width=stroke)
        draw.line((cx, shoulder_y, cx + 48*scale, head_y + 24*scale), fill=WHITE, width=stroke)
        draw.ellipse((cx + 34*scale, head_y + 7*scale, cx + 64*scale, head_y + 37*scale), fill=WHITE)
    elif pose == "happy":
        draw.line((cx, shoulder_y, cx - limb_length*.72, shoulder_y - limb_length*.55), fill=WHITE, width=stroke)
        draw.line((cx, shoulder_y, cx + limb_length*.72, shoulder_y - limb_length*.55), fill=WHITE, width=stroke)
    elif pose == "walking":
        draw.line((cx, shoulder_y, cx - 58*scale, cy + 28*scale), fill=WHITE, width=stroke)
        draw.line((cx, shoulder_y, cx + 62*scale, cy - 16*scale), fill=WHITE, width=stroke)
    elif pose == "confident":
        draw.line((cx, shoulder_y, cx - 78*scale, cy + 22*scale, cx - 44*scale, hip_y - 10*scale), fill=WHITE, width=stroke)
        draw.line((cx, shoulder_y, cx + 78*scale, cy + 22*scale, cx + 44*scale, hip_y - 10*scale), fill=WHITE, width=stroke)
    else:
        draw.line((cx, shoulder_y, cx - 72*scale, cy + 40*scale), fill=WHITE, width=stroke)
        draw.line((cx, shoulder_y, cx + 72*scale, cy + 40*scale), fill=WHITE, width=stroke)

    if pose == "walking":
        draw.line((cx, hip_y, cx - 70*scale, hip_y + 82*scale), fill=WHITE, width=stroke)
        draw.line((cx, hip_y, cx + 90*scale, hip_y + 42*scale), fill=WHITE, width=stroke)
    else:
        draw.line((cx, hip_y, cx - 58*scale, hip_y + 100*scale), fill=WHITE, width=stroke)
        draw.line((cx, hip_y, cx + 58*scale, hip_y + 100*scale), fill=WHITE, width=stroke)

    eye_y = int(head_y - 10*scale)
    draw.ellipse((cx - 26*scale, eye_y - 8*scale, cx - 12*scale, eye_y + 6*scale), fill=NAVY)
    draw.ellipse((cx + 12*scale, eye_y - 8*scale, cx + 26*scale, eye_y + 6*scale), fill=NAVY)


def draw_eye(draw, cx, cy, size):
    draw.ellipse((cx-size, cy-size*.55, cx+size, cy+size*.55), fill=WHITE)
    draw.ellipse((cx-size*.38, cy-size*.38, cx+size*.38, cy+size*.38), fill=RED)
    draw.ellipse((cx-size*.17, cy-size*.17, cx+size*.17, cy+size*.17), fill=NAVY)


def draw_brain(draw, cx, cy, size):
    radius = size // 5
    offsets = [
        (-2,-1),(-1,-2),(0,-2),(1,-2),(2,-1),
        (-2,0),(-1,0),(0,0),(1,0),(2,0),
        (-2,1),(-1,2),(0,2),(1,2),(2,1),
    ]
    for ox, oy in offsets:
        x = cx + ox * radius * .72
        y = cy + oy * radius * .61
        draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=WHITE)
    draw.line((cx, cy-size*.36, cx, cy+size*.36), fill=RED, width=max(8,size//22))


def draw_message(draw, cx, cy, size):
    draw.rounded_rectangle((cx-size, cy-size*.55, cx+size, cy+size*.55), radius=int(size*.25), fill=WHITE)
    draw.polygon([(cx-size*.45, cy+size*.45), (cx-size*.12, cy+size*.85), (cx-size*.05, cy+size*.45)], fill=WHITE)
    for idx in range(3):
        x = cx - size*.45 + idx*size*.45
        draw.ellipse((x-size*.08, cy-size*.08, x+size*.08, cy+size*.08), fill=RED)


def draw_two_people(layer, cx, cy, size, mode):
    distance = size * (.48 if mode == "close" else .82)
    draw_person(layer, int(cx-distance), cy, scale=size/420, pose="neutral")
    draw_person(layer, int(cx+distance), cy, scale=size/420, pose="neutral")
    draw = ImageDraw.Draw(layer)

    if mode == "close":
        draw_heart(draw, cx, int(cy-size*.55), int(size*.45))
    elif mode == "apart":
        draw.line((cx, cy-size*.75, cx, cy+size*.70), fill=RED, width=max(8,int(size*.035)))
    else:
        draw_message(draw, cx, int(cy-size*.56), size*.38)


def draw_visual(
    visual_key: str,
    animation: str,
    progress: float,
    width: int,
    height: int,
) -> Image.Image:
    layer = Image.new("RGBA", (width, height), (0,0,0,0))
    transform = transform_for(animation, progress, width, height)
    cx = int(width/2 + transform.x_offset)
    cy = int(height*.44 + transform.y_offset)
    scale = transform.scale

    draw_glow_circle(layer, cx, cy, 165, alpha=52)
    draw = ImageDraw.Draw(layer)

    person_poses = {
        "mindy_thinking": "thinking",
        "mindy_sad": "sad",
        "mindy_happy": "happy",
        "mindy_walking": "walking",
        "mindy_sitting": "neutral",
        "mindy_confident": "confident",
        "mindy_listening": "thinking",
        "mindy_talking": "neutral",
        "mindy_looking_away": "neutral",
    }

    if visual_key in person_poses:
        draw_person(layer, cx, cy+10, scale=1.04*scale, pose=person_poses[visual_key])
        if visual_key == "mindy_talking":
            draw_message(draw, cx+180, cy-205, 78)
    elif visual_key == "two_people_close":
        draw_two_people(layer, cx, cy+25, 300*scale, "close")
    elif visual_key == "two_people_apart":
        draw_two_people(layer, cx, cy+25, 285*scale, "apart")
    elif visual_key == "two_people_talking":
        draw_two_people(layer, cx, cy+25, 285*scale, "talking")
    elif visual_key == "heart_broken":
        draw_heart(draw, cx, cy, int(330*scale), broken=True)
    elif visual_key == "heart_full":
        draw_heart(draw, cx, cy, int(330*scale), broken=False)
    elif visual_key == "brain_thinking":
        draw_brain(draw, cx, cy, int(340*scale))
    elif visual_key == "eye_looking":
        draw_eye(draw, cx, cy, int(220*scale))
    elif visual_key == "message_bubble":
        draw_message(draw, cx, cy, int(230*scale))
    else:
        draw_person(layer, cx, cy+20, scale=1.06*scale, pose="thinking")

    if transform.opacity < 255:
        alpha = layer.getchannel("A")
        alpha = alpha.point(lambda value: int(value * transform.opacity / 255))
        layer.putalpha(alpha)

    return layer
