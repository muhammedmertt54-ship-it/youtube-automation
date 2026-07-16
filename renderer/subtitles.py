from __future__ import annotations

import math
import re
from pathlib import Path

from PIL import ImageDraw, ImageFont


WHITE = (248, 250, 255)
RED = (239, 56, 74)
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def load_fonts(width: int) -> dict[str, ImageFont.FreeTypeFont]:
    return {
        "body": ImageFont.truetype(FONT_BOLD, max(38, width // 16)),
        "body_small": ImageFont.truetype(FONT_BOLD, max(32, width // 18)),
        "brand": ImageFont.truetype(FONT_BOLD, max(22, width // 29)),
        "tiny": ImageFont.truetype(FONT_REGULAR, max(17, width // 38)),
    }


def wrap_words(draw, words, font, max_width):
    lines = []
    current = []

    for word in words:
        candidate = current + [word]
        candidate_text = " ".join(candidate)
        box = draw.textbbox((0, 0), candidate_text, font=font)

        if box[2] - box[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = [word]

    if current:
        lines.append(current)

    return lines


def draw_text_with_highlight(
    draw: ImageDraw.ImageDraw,
    text: str,
    highlight: str,
    scene_progress: float,
    width: int,
    height: int,
    fonts: dict,
) -> None:
    words = text.strip().split()
    font = fonts["body"] if len(text) <= 78 else fonts["body_small"]
    max_width = width - 100
    lines = wrap_words(draw, words, font, max_width)
    line_height = font.size + 18
    total_height = len(lines) * line_height
    start_y = int(height * 0.70 - total_height / 2)

    card_top = start_y - 34
    card_bottom = start_y + total_height + 27

    draw.rounded_rectangle(
        (34, card_top, width - 34, card_bottom),
        radius=34,
        fill=(2, 12, 39, 160),
        outline=(255, 255, 255, 30),
        width=2,
    )

    lowered_highlight = highlight.casefold().strip()

    for line_index, line_words in enumerate(lines):
        widths = [
            draw.textbbox((0, 0), word, font=font)[2]
            for word in line_words
        ]
        space_width = draw.textbbox((0, 0), " ", font=font)[2]
        line_width = sum(widths) + space_width * max(0, len(line_words) - 1)
        x = int((width - line_width) / 2)
        y = start_y + line_index * line_height

        for word_index, word in enumerate(line_words):
            clean_word = re.sub(r'^[^\wçğıöşüÇĞİÖŞÜ]+|[^\wçğıöşüÇĞİÖŞÜ]+$', '', word)
            is_highlight = clean_word.casefold() == lowered_highlight
            color = RED if is_highlight else WHITE

            draw.text((x + 3, y + 4), word, font=font, fill=(0, 0, 0, 130))
            draw.text((x, y), word, font=font, fill=color)

            if is_highlight:
                underline_y = y + font.size + 6
                pulse = 0.65 + 0.35 * (
                    0.5 + 0.5 * math.sin(scene_progress * math.pi * 4)
                )
                draw.rounded_rectangle(
                    (
                        x,
                        underline_y,
                        x + widths[word_index],
                        underline_y + 7,
                    ),
                    radius=3,
                    fill=(RED[0], RED[1], RED[2], int(255 * pulse)),
                )

            x += widths[word_index] + space_width


def draw_brand(
    draw: ImageDraw.ImageDraw,
    brand: str,
    scene_number: int,
    scene_count: int,
    width: int,
    fonts: dict,
) -> None:
    brand_box = draw.textbbox((0, 0), brand, font=fonts["brand"])
    brand_width = brand_box[2] - brand_box[0]
    x = width - brand_width - 34
    y = 31

    draw.rounded_rectangle(
        (x - 17, y - 8, x + brand_width + 17, y + 37),
        radius=18,
        fill=(255, 255, 255, 28),
        outline=(255, 255, 255, 50),
        width=1,
    )
    draw.text((x, y), brand, font=fonts["brand"], fill=WHITE)
    draw.text(
        (34, 35),
        f"{scene_number}/{scene_count}",
        font=fonts["tiny"],
        fill=(210, 220, 245, 210),
    )


def draw_progress(draw, progress: float, width: int, height: int) -> None:
    bar_x = 48
    bar_y = height - 50
    bar_width = width - 96
    bar_height = 7

    draw.rounded_rectangle(
        (bar_x, bar_y, bar_x + bar_width, bar_y + bar_height),
        radius=4,
        fill=(255, 255, 255, 45),
    )

    filled = int(bar_width * max(0.0, min(1.0, progress)))
    if filled > 0:
        draw.rounded_rectangle(
            (bar_x, bar_y, bar_x + filled, bar_y + bar_height),
            radius=4,
            fill=RED,
        )
