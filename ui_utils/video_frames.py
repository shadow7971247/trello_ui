"""Кадры для локального MP4 (UI_VIDEO_FRAMES_DIR)."""

from __future__ import annotations

import os
from pathlib import Path

_frame_counter = 0


def save_video_frame(png: bytes) -> None:
    global _frame_counter
    frames_dir = os.getenv("UI_VIDEO_FRAMES_DIR", "").strip()
    if not frames_dir or not png:
        return
    _frame_counter += 1
    path = Path(frames_dir) / f"frame_{_frame_counter:04d}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def reset_video_frames() -> None:
    global _frame_counter
    _frame_counter = 0
