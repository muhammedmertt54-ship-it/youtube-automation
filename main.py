from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont


WIDTH = 1080
HEIGHT = 1920
FPS = 30

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Deep Worlds photo quote video renderer"
    )
    parser.add_argument("--manifest", default="videos/manifest.json")
    parser.add_argument("--output", default="final-video.mp4")
    return parser.parse_args()


def cover_image(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    source_ratio = image.width / image.height
    target_ratio = WIDTH / HEIGHT

    if source_ratio > target_ratio:
        new_height = HEIGHT
        new_width = round(HEIGHT * source_ratio)
    else:
        new_width = WIDTH
        new_height = round(WIDTH / source_ratio)

    image = image.resize(
        (new_width, new_height),
        Image.Resampling.LANCZOS,
    )

    left = (new_width - WIDTH) // 2
    top = (new_height - HEIGHT) // 2

    return image.crop((left, top, left + WIDTH, top + HEIGHT))


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = []

    for word in words:
        test = " ".join(current + [word])
        box = draw.textbbox((0, 0), test, font=font)

        if box[2] - box[0] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]

    if current:
        lines.append(" ".join(current))

    return lines


def create_frame(source, quote, brand, progress):
    zoom = 1.0 + progress * 0.08
    scaled_width = round(WIDTH * zoom)
    scaled_height = round(HEIGHT * zoom)

    frame = source.resize(
        (scaled_width, scaled_height),
        Image.Resampling.LANCZOS,
    )

    max_x = scaled_width - WIDTH
    max_y = scaled_height - HEIGHT

    x = round(max_x * (0.20 + progress * 0.60))
    y = round(max_y * (0.25 + progress * 0.30))

    x = max(0, min(max_x, x))
    y = max(0, min(max_y, y))

    frame = frame.crop((x, y, x + WIDTH, y + HEIGHT)).convert("RGBA")

    rgb = frame.convert("RGB")
    rgb = ImageEnhance.Contrast(rgb).enhance(1.08)
    rgb = ImageEnhance.Color(rgb).enhance(0.90)
    rgb = ImageEnhance.Brightness(rgb).enhance(0.92)
    frame = rgb.convert("RGBA")

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    for yy in range(HEIGHT):
        top_alpha = max(0, int(105 * (1 - yy / 550)))
        bottom_alpha = max(0, int(125 * ((yy - 1250) / 670)))
        alpha = max(top_alpha, bottom_alpha)

        if alpha > 0:
            overlay_draw.line(
                (0, yy, WIDTH, yy),
                fill=(0, 0, 0, min(150, alpha)),
            )

    frame.alpha_composite(overlay)

    draw = ImageDraw.Draw(frame)
    font_size = 66 if len(quote) <= 90 else 57
    font = ImageFont.truetype(FONT_BOLD, font_size)
    brand_font = ImageFont.truetype(FONT_BOLD, 30)

    lines = wrap_text(draw, quote, font, WIDTH - 150)
    line_height = font.size + 20
    total_height = len(lines) * line_height
    start_y = round(HEIGHT * 0.40 - total_height / 2)

    for index, line in enumerate(lines):
        box = draw.textbbox((0, 0), line, font=font)
        line_width = box[2] - box[0]

        text_x = (WIDTH - line_width) // 2
        text_y = start_y + index * line_height

        draw.text(
            (text_x + 4, text_y + 5),
            line,
            font=font,
            fill=(0, 0, 0, 220),
            stroke_width=5,
            stroke_fill=(0, 0, 0, 220),
        )

        draw.text(
            (text_x, text_y),
            line,
            font=font,
            fill=(255, 255, 255),
            stroke_width=3,
            stroke_fill=(0, 0, 0),
        )

    brand_box = draw.textbbox((0, 0), brand, font=brand_font)
    brand_width = brand_box[2] - brand_box[0]

    draw.text(
        (WIDTH - brand_width - 42, HEIGHT - 95),
        brand,
        font=brand_font,
        fill=(255, 255, 255, 220),
        stroke_width=2,
        stroke_fill=(0, 0, 0, 180),
    )

    return frame.convert("RGB")


def make_music_filter(music_key, duration):
    presets = {
        "sad_piano": (174.61, 220.00),
        "dark_ambient": (130.81, 164.81),
        "calm_piano": (196.00, 246.94),
        "motivational": (220.00, 277.18),
        "emotional": (174.61, 261.63),
        "night_mood": (146.83, 196.00),
        "cinematic": (110.00, 164.81),
    }

    first, second = presets.get(
        music_key,
        presets["night_mood"],
    )

    return (
        f"sine=frequency={first}:sample_rate=44100:duration={duration}"
    ), (
        f"sine=frequency={second}:sample_rate=44100:duration={duration}"
    )


def render(manifest_path, output_path):
    data = json.loads(
        Path(manifest_path).read_text(encoding="utf-8")
    )

    image_path = Path(data["image_path"])
    quote = str(data["quote"]).strip()
    brand = str(data.get("brand", "Deep Worlds")).strip()
    music_key = str(data.get("music_key", "night_mood")).strip()
    duration = float(data.get("duration", 9))

    source = cover_image(Image.open(image_path))
    total_frames = round(duration * FPS)

    with tempfile.TemporaryDirectory() as temp_dir:
        silent_video = Path(temp_dir) / "silent.mp4"
        music_file = Path(temp_dir) / "music.m4a"

        ffmpeg = subprocess.Popen(
            [
                "ffmpeg",
                "-y",
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
                "-s",
                f"{WIDTH}x{HEIGHT}",
                "-r",
                str(FPS),
                "-i",
                "-",
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "20",
                "-pix_fmt",
                "yuv420p",
                str(silent_video),
            ],
            stdin=subprocess.PIPE,
        )

        try:
            for frame_number in range(total_frames):
                progress = frame_number / max(1, total_frames - 1)
                frame = create_frame(source, quote, brand, progress)
                ffmpeg.stdin.write(frame.tobytes())
        finally:
            if ffmpeg.stdin:
                ffmpeg.stdin.close()

        if ffmpeg.wait() != 0:
            raise RuntimeError("Video render başarısız.")

        tone_1, tone_2 = make_music_filter(music_key, duration)

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                tone_1,
                "-f",
                "lavfi",
                "-i",
                tone_2,
                "-filter_complex",
                (
                    "[0:a]volume=0.014[a0];"
                    "[1:a]volume=0.009[a1];"
                    "[a0][a1]amix=inputs=2:normalize=0,"
                    "lowpass=f=900,"
                    "highpass=f=80,"
                    "afade=t=in:st=0:d=1,"
                    f"afade=t=out:st={max(0, duration-1.3)}:d=1.3[music]"
                ),
                "-map",
                "[music]",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                str(music_file),
            ],
            check=True,
        )

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(silent_video),
                "-i",
                str(music_file),
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-shortest",
                output_path,
            ],
            check=True,
        )

    print(f"Video oluşturuldu: {output_path}")


def main():
    args = parse_args()
    render(args.manifest, args.output)


if __name__ == "__main__":
    main()
