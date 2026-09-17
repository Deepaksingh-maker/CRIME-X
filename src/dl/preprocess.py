"""Small, model-agnostic image preprocessing helpers."""

from __future__ import annotations

from io import BytesIO

from PIL import Image


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def validate_image_bytes(contents: bytes, filename: str, max_bytes: int = 10 * 1024 * 1024) -> Image.Image:
    """Validate an image for future inference without executing uploaded content."""

    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if f".{suffix}" not in SUPPORTED_EXTENSIONS:
        raise ValueError("Only JPG, JPEG, and PNG images are supported")
    if len(contents) > max_bytes:
        raise ValueError(f"Image exceeds the {max_bytes // (1024 * 1024)} MB size limit")
    image = Image.open(BytesIO(contents))
    image.load()
    return image.convert("RGB")