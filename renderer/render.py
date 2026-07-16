from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

from .background import (
    apply_vignette,
    create_gradient,
    draw_particles,
    draw_wave_lines,
)
from .subtitles import (
    draw_brand,
    draw_progress,
    draw_text_with_highlight,
    load_fonts,
)
from .visuals import draw_visual


def probe_duration(path: str) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def render_video(
    manifest_path: str = "videos/manifest.json",
    audio_path: str = "voice.mp3",
    output_path: str = "visuals_720x1280.mp4",
    brand: str = "MINDORA",
    width: int = 720,
    height: int = 1280,
    fps: int = 30,
) -> None:
    with open(manifest_path, "r", encoding="utf-8") as file:
        manifest = json.load(file)

    scenes = manifest.get("scenes", [])
    if not scenes:
        raise RuntimeError("Manifest içinde sahne bulunamadı.")

    audio_duration = probe_duration(audio_path)
    manifest_duration = sum(float(scene.get("duration", 5)) for scene in scenes)
    if manifest_duration <= 0:
        manifest_duration = len(scenes) * 5.0

    scale_factor = audio_duration / manifest_duration
    scene_durations = [
        max(2.8, float(scene.get("duration", 5)) * scale_factor)
        for scene in scenes
    ]
    scene_durations[-1] = max(
        2.8,
        scene_durations[-1] + audio_duration - sum(scene_durations),
    )

    total_frames = int(round(audio_duration * fps))
    scene_frame_counts = [max(1, int(round(d * fps))) for d in scene_durations]
    scene_frame_counts[-1] += total_frames - sum(scene_frame_counts)

    fonts = load_fonts(width)

    ffmpeg = subprocess.Popen(
        [
            "ffmpeg",
            "-y",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-s",
            f"{width}x{height}",
            "-r",
            str(fps),
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
            output_path,
        ],
        stdin=subprocess.PIPE,
    )

    frame_cursor = 0

    try:
        for scene_index, scene in enumerate(scenes):
            scene_frames = scene_frame_counts[scene_index]

            for local_frame in range(scene_frames):
                global_progress = frame_cursor / max(1, total_frames - 1)
                scene_progress = local_frame / max(1, scene_frames - 1)

                frame = create_gradient(width, height)
                draw = ImageDraw.Draw(frame, "RGBA")

                draw_particles(draw, frame_cursor, scene_index + 1, width, height)
                draw_wave_lines(draw, frame_cursor, width, height)
                draw_brand(
                    draw,
                    brand,
                    scene_index + 1,
                    len(scenes),
                    width,
                    fonts,
                )

                visual = draw_visual(
                    str(scene.get("visual_key", "mindy_thinking")),
                    str(scene.get("animation", "fade_in")),
                    scene_progress,
                    width,
                    height,
                )
                frame.alpha_composite(visual)

                draw = ImageDraw.Draw(frame, "RGBA")
                draw_text_with_highlight(
                    draw,
                    str(scene.get("text", "")),
                    str(scene.get("highlight", "")),
                    scene_progress,
                    width,
                    height,
                    fonts,
                )
                draw_progress(draw, global_progress, width, height)
                apply_vignette(frame)

                ffmpeg.stdin.write(frame.convert("RGB").tobytes())
                frame_cursor += 1

    finally:
        if ffmpeg.stdin:
            ffmpeg.stdin.close()

    return_code = ffmpeg.wait()
    if return_code != 0:
        raise RuntimeError(f"FFmpeg render hatası. Çıkış kodu: {return_code}")

    print(f"Render tamamlandı: {output_path}")
    print(f"Ses süresi: {audio_duration:.2f} saniye")
    print(f"Toplam frame: {frame_cursor}")
