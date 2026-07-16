from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Transform:
    x_offset: float = 0.0
    y_offset: float = 0.0
    scale: float = 1.0
    opacity: int = 255


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def ease_in_out(t: float) -> float:
    t = clamp(t)
    return 0.5 - 0.5 * math.cos(math.pi * t)


def ease_out_back(t: float) -> float:
    t = clamp(t)
    c1 = 1.70158
    c3 = c1 + 1.0
    return 1.0 + c3 * (t - 1.0) ** 3 + c1 * (t - 1.0) ** 2


def transform_for(animation: str, progress: float, width: int, height: int) -> Transform:
    """Return the visual transform for a scene animation."""
    progress = clamp(progress)
    intro = clamp(progress / 0.20)

    if animation == "fade_in":
        return Transform(opacity=int(255 * ease_in_out(intro)))

    if animation == "pop":
        return Transform(scale=max(0.02, ease_out_back(intro)))

    if animation == "slide_left":
        return Transform(x_offset=(1.0 - ease_in_out(intro)) * width * 0.42)

    if animation == "slide_right":
        return Transform(x_offset=-(1.0 - ease_in_out(intro)) * width * 0.42)

    if animation == "slow_zoom":
        return Transform(scale=0.94 + progress * 0.12)

    if animation == "pulse":
        return Transform(scale=1.0 + math.sin(progress * math.pi * 6.0) * 0.055)

    if animation == "shake":
        return Transform(x_offset=math.sin(progress * math.pi * 22.0) * 9.0)

    if animation == "float":
        return Transform(y_offset=math.sin(progress * math.pi * 4.0) * 18.0)

    if animation == "bounce":
        return Transform(y_offset=-abs(math.sin(progress * math.pi * 5.0)) * 25.0)

    return Transform()
