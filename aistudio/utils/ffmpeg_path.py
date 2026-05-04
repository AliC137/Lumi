"""Ensure bundled ffmpeg under ``aimodels/`` is discoverable (PATH + pydub)."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _exe_name() -> str:
    return "ffmpeg.exe" if os.name == "nt" else "ffmpeg"


def _project_root() -> Path:
    # .../aistudio/utils/ffmpeg_path.py -> aiStudio/
    return Path(__file__).resolve().parents[2]


def _find_bundled_ffmpeg() -> Path | None:
    aimodels = _project_root() / "aimodels"
    if not aimodels.is_dir():
        return None

    name = _exe_name()
    for rel in (
        name,
        f"ffmpeg/{name}",
        f"ffmpeg/bin/{name}",
        f"bin/{name}",
    ):
        candidate = aimodels / rel
        if candidate.is_file():
            return candidate.resolve()

    # e.g. ``aimodels/ffmpeg-8.0-essentials_build/bin/ffmpeg.exe`` (official builds zip)
    if os.name == "nt":
        for exe in sorted(aimodels.glob("**/bin/ffmpeg.exe")):
            if exe.is_file():
                return exe.resolve()
    for exe in sorted(aimodels.glob("**/bin/ffmpeg")):
        if exe.is_file():
            return exe.resolve()

    for exe in sorted(aimodels.glob(f"**/{name}")):
        if exe.is_file():
            return exe.resolve()

    return None


def _configure_pydub(ffmpeg_exe: str) -> None:
    try:
        from pydub import AudioSegment

        exe_path = Path(ffmpeg_exe)
        probe_name = "ffprobe.exe" if os.name == "nt" else "ffprobe"
        probe = exe_path.parent / probe_name

        AudioSegment.converter = ffmpeg_exe
        if hasattr(AudioSegment, "ffmpeg"):
            AudioSegment.ffmpeg = ffmpeg_exe  # type: ignore[attr-defined]
        if probe.is_file() and hasattr(AudioSegment, "ffprobe"):
            AudioSegment.ffprobe = str(probe)  # type: ignore[attr-defined]
    except ImportError:
        pass


def ensure_local_ffmpeg_on_path() -> str | None:
    """
    Prepend the directory containing bundled ffmpeg to PATH, then point pydub at it.

    Returns absolute path to ffmpeg when found under ``aimodels/``, else None.
    """
    exe = _find_bundled_ffmpeg()
    if exe is None:
        return None

    bin_dir = str(exe.parent)
    os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
    _configure_pydub(str(exe))
    return str(exe)


# Allow ``python -m aistudio.utils.ffmpeg_path`` for quick checks
if __name__ == "__main__":
    p = ensure_local_ffmpeg_on_path()
    print("ffmpeg:", p or "(not found under aimodels/)")
    sys.exit(0 if p else 1)
