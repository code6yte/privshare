import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PIL import Image
from pypdf import PdfReader, PdfWriter


@dataclass
class MetadataCleanResult:
    output_path: Path
    status: str
    cleaner_used: str
    details: str


def clean_metadata(input_path: Path, output_dir: Path) -> MetadataCleanResult:
    """Create a metadata-cleaned copy of input_path inside output_dir.

    ExifTool is required. Raises RuntimeError if not available.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"cleaned_{input_path.name}"

    if not _exiftool_available():
        raise RuntimeError("ExifTool is required but not found on the system. Install it first.")

    result = _clean_with_exiftool(input_path, output_path)
    if result:
        return result

    suffix = input_path.suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        return _clean_image_with_pillow(input_path, output_path)

    if suffix == ".pdf":
        return _clean_pdf_with_pypdf(input_path, output_path)

    shutil.copy2(input_path, output_path)
    return MetadataCleanResult(
        output_path=output_path,
        status="copied",
        cleaner_used="copy-fallback",
        details="No specific metadata cleaner for this file type; file was copied before encryption.",
    )


def _exiftool_available() -> bool:
    return shutil.which("exiftool") is not None


def _clean_with_exiftool(input_path: Path, output_path: Path) -> Optional[MetadataCleanResult]:
    try:
        shutil.copy2(input_path, output_path)
        cmd = ["exiftool", "-overwrite_original", "-all=", str(output_path)]
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if completed.returncode == 0:
            return MetadataCleanResult(
                output_path=output_path,
                status="cleaned",
                cleaner_used="exiftool",
                details=(completed.stdout or "ExifTool metadata removal completed.").strip(),
            )
        return None
    except Exception:
        return None


def _clean_image_with_pillow(input_path: Path, output_path: Path) -> MetadataCleanResult:
    try:
        with Image.open(input_path) as img:
            data = list(img.getdata())
            cleaned = Image.new(img.mode, img.size)
            cleaned.putdata(data)
            save_kwargs = {}
            if input_path.suffix.lower() in {".jpg", ".jpeg"}:
                save_kwargs["quality"] = 95
            cleaned.save(output_path, **save_kwargs)
        return MetadataCleanResult(
            output_path=output_path,
            status="cleaned",
            cleaner_used="pillow",
            details="Image was re-saved without EXIF metadata.",
        )
    except Exception as exc:
        shutil.copy2(input_path, output_path)
        return MetadataCleanResult(
            output_path=output_path,
            status="copied",
            cleaner_used="pillow-fallback",
            details=f"Image cleaning failed, copied original before encryption: {exc}",
        )


def _clean_pdf_with_pypdf(input_path: Path, output_path: Path) -> MetadataCleanResult:
    try:
        reader = PdfReader(str(input_path))
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.add_metadata({})
        with output_path.open("wb") as f:
            writer.write(f)
        return MetadataCleanResult(
            output_path=output_path,
            status="cleaned",
            cleaner_used="pypdf",
            details="PDF pages were rewritten with empty document metadata.",
        )
    except Exception as exc:
        shutil.copy2(input_path, output_path)
        return MetadataCleanResult(
            output_path=output_path,
            status="copied",
            cleaner_used="pypdf-fallback",
            details=f"PDF cleaning failed, copied original before encryption: {exc}",
        )
