import io
import os
from pathlib import Path

from PIL import Image


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}


def load_image(source: str | Path | bytes | Image.Image) -> Image.Image:
    if isinstance(source, Image.Image):
        return source
    if isinstance(source, bytes):
        return Image.open(io.BytesIO(source))
    source = str(source)
    ext = os.path.splitext(source)[1].lower()
    if ext == ".pdf":
        return _convert_pdf_first_page(source)
    if ext in SUPPORTED_EXTENSIONS:
        return Image.open(source)
    raise ValueError(f"Unsupported file format: {ext}")


def _convert_pdf_first_page(pdf_path: str, dpi: int = 200) -> Image.Image:
    try:
        from pdf2image import convert_from_path
        images = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=1)
        if not images:
            raise ValueError("PDF has no pages")
        return images[0]
    except ImportError:
        raise ImportError(
            "pdf2image is required to process PDF files. "
            "Install with: pip install invoice-parser[pdf]"
        )


def enhance_image(image: Image.Image) -> Image.Image:
    if image.mode != "RGB":
        image = image.convert("RGB")
    return image


def image_to_bytes(image: Image.Image, fmt: str = "PNG") -> bytes:
    buf = io.BytesIO()
    image.save(buf, format=fmt)
    return buf.getvalue()
