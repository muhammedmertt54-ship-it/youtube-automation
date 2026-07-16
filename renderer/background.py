from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw, ImageFilter


NAVY_TOP = (5, 18, 55)
NAVY_BOTTOM = (13, 39, 96)
WHITE = (248, 250, 255)
RED = (239, 56, 74)
BLUE_GLOW = (55, 120, 255)


def create_gradient(width: int, height: int) -> Image.Image:
    image = Image.new("RGB", (width, height), NAVY_TOP)
    draw = ImageDraw.Draw(image)

    for y in range(height):
        ratio = (y / max(1, height - 1)) ** 1.15
        color = tuple(
            int(NAVY_TOP[i] * (1.0 - ratio) + NAVY_BOTTOM[i] * ratio)
            for i in range(3)
        )
        draw.line((0, y, width, y), fill=color)

    return image.convert("RGBA")


def draw_particles(
    draw: ImageDraw.ImageDraw,
    frame_number: int,
    scene_index: int,
    width: int,
    height: int,
) -> None:
    random.seed(scene_index * 1000)

    for particle_index in range(24):
        base_x = random.randint(0, width)
        base_y = random.randint(0, height)
        speed = random.uniform(0.15, 0.55)
        radius = random.choice([1, 1, 2, 2, 3])

        x = (
            base_x
            + math.sin(frame_number * 0.015 * speed + particle_index) * 18
        ) % width
        y = (base_y - frame_number * speed * 0.38) % height
        alpha = random.randint(18, 55)

        draw.ellipse(
            (int(x - radius), int(y - radius), int(x + radius), int(y + radius)),
            fill=(180, 210, 255, alpha),
        )


def draw_wave_lines(
    draw: ImageDraw.ImageDraw,
    frame_number: int,
    width: int,
    height: int,
) -> None:
    phase = frame_number * 0.035
    configs = [
        (86, 17, 118, (255, 255, 255, 205), 7, 0.0),
        (116, 22, 135, (239, 56, 74, 225), 10, 1.3),
        (height - 112, 22, 128, (239, 56, 74, 220), 10, 0.7),
        (height - 80, 15, 110, (255, 255, 255, 195), 7, 2.1),
    ]

    for base_y, amplitude, period, color, line_width, offset in configs:
        points = []
        for x in range(-20, width + 21, 8):
            y = base_y + math.sin(x / period + phase + offset) * amplitude
            points.append((x, int(y)))
        draw.line(points, fill=color, width=line_width, joint="curve")


def draw_glow_circle(
    layer: Image.Image,
    center_x: int,
    center_y: int,
    radius: int,
    color: tuple[int, int, int] = BLUE_GLOW,
    alpha: int = 70,
) -> None:
    glow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse(
        (
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
        ),
        fill=(*color, alpha),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(max(8, radius // 2)))
    layer.alpha_composite(glow)


def apply_vignette(image: Image.Image) -> None:
    width, height = image.size
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pixels = overlay.load()
    center_x = width / 2
    center_y = height / 2
    max_distance = math.sqrt(center_x**2 + center_y**2)

    for y in range(0, height, 4):
        for x in range(0, width, 4):
            distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            ratio = max(0.0, min(1.0, distance / max_distance))
            alpha = int(max(0, (ratio - 0.45) * 150))

            for yy in range(y, min(y + 4, height)):
                for xx in range(x, min(x + 4, width)):
                    pixels[xx, yy] = (0, 0, 0, alpha)

    image.alpha_composite(overlay)
