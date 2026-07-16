from __future__ import annotations

import argparse

from renderer.render import render_video


def parse_args():
    parser = argparse.ArgumentParser(
        description="Mindora psychology Shorts renderer"
    )
    parser.add_argument(
        "--manifest",
        default="videos/manifest.json",
        help="Manifest JSON yolu",
    )
    parser.add_argument(
        "--audio",
        default="voice.mp3",
        help="Ses dosyası yolu",
    )
    parser.add_argument(
        "--output",
        default="visuals_720x1280.mp4",
        help="Video çıktı yolu",
    )
    parser.add_argument(
        "--brand",
        default="MINDORA",
        help="Videonun sağ üstünde gösterilecek marka adı",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    render_video(
        manifest_path=args.manifest,
        audio_path=args.audio,
        output_path=args.output,
        brand=args.brand,
    )


if __name__ == "__main__":
    main()
