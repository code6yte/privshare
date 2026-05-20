import shutil
import subprocess
import tempfile
import zipfile
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

    suffix = input_path.suffix.lower()

    if suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        return _clean_image_with_exiftool(input_path, output_path)

    if suffix == ".pdf":
        return _clean_pdf_with_exiftool(input_path, output_path)

    if suffix in {".docx", ".xlsx", ".pptx"}:
        return _clean_office_file(input_path, output_path)

    if suffix == ".zip":
        return _clean_zip_file(input_path, output_path)

    if suffix in {".txt", ".csv"}:
        shutil.copy2(input_path, output_path)
        return MetadataCleanResult(
            output_path=output_path,
            status="cleaned",
            cleaner_used="native",
            details=f"{suffix.upper()} files do not contain embedded metadata; file was copied safely.",
        )

    result = _clean_with_exiftool(input_path, output_path)
    if result:
        return result

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


def _clean_image_with_exiftool(input_path: Path, output_path: Path) -> MetadataCleanResult:
    result = _clean_with_exiftool(input_path, output_path)
    if result:
        return result

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


def _clean_pdf_with_exiftool(input_path: Path, output_path: Path) -> MetadataCleanResult:
    result = _clean_with_exiftool(input_path, output_path)
    if result:
        return result

    return _clean_pdf_with_pypdf(input_path, output_path)


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


def _clean_office_file(input_path: Path, output_path: Path) -> MetadataCleanResult:
    """Clean metadata from Office files (docx, xlsx, pptx) by stripping docProps XML files."""
    try:
        _strip_office_metadata(input_path, output_path)
        return MetadataCleanResult(
            output_path=output_path,
            status="cleaned",
            cleaner_used="office-cleaner",
            details="Removed docProps/core.xml and docProps/app.xml metadata from Office file.",
        )
    except Exception as exc:
        shutil.copy2(input_path, output_path)
        return MetadataCleanResult(
            output_path=output_path,
            status="copied",
            cleaner_used="office-cleaner-fallback",
            details=f"Office metadata cleaning failed, copied original before encryption: {exc}",
        )


def _strip_office_metadata(input_path: Path, output_path: Path) -> None:
    """Recreate a ZIP-based Office file without docProps metadata files."""
    metadata_files = {
        "docProps/core.xml",
        "docProps/app.xml",
        "docProps/custom.xml",
    }
    with zipfile.ZipFile(input_path, "r") as zin:
        with zipfile.ZipFile(output_path, "w", compression=zin.compression) as zout:
            for item in zin.infolist():
                if item.filename not in metadata_files:
                    data = zin.read(item.filename)
                    zout.writestr(item, data)


def _clean_zip_file(input_path: Path, output_path: Path) -> MetadataCleanResult:
    """Clean metadata from ZIP files by removing embedded ExifTool-readable metadata from contained files."""
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            extract_dir = Path(tmpdir) / "extracted"
            extract_dir.mkdir()

            with zipfile.ZipFile(input_path, "r") as zf:
                zf.extractall(extract_dir)

            cleaned_count = 0
            for file_path in extract_dir.rglob("*"):
                if file_path.is_file():
                    suffix = file_path.suffix.lower()
                    if suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
                        _clean_with_exiftool(file_path, file_path)
                        cleaned_count += 1
                    elif suffix == ".pdf":
                        _clean_pdf_with_pypdf(file_path, file_path)
                        cleaned_count += 1

            with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for file_path in extract_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(extract_dir)
                        zf.write(file_path, arcname)

            return MetadataCleanResult(
                output_path=output_path,
                status="cleaned",
                cleaner_used="zip-cleaner",
                details=f"Extracted ZIP, cleaned metadata from {cleaned_count} contained files, re-packed.",
            )
    except Exception as exc:
        shutil.copy2(input_path, output_path)
        return MetadataCleanResult(
            output_path=output_path,
            status="copied",
            cleaner_used="zip-cleaner-fallback",
            details=f"ZIP metadata cleaning failed, copied original before encryption: {exc}",
        )
