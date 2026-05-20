from pathlib import Path

from config import Config


def encrypted_path(stored_filename: str) -> Path:
    Config.ensure_dirs()
    path = Config.STORAGE_DIR / stored_filename
    resolved_storage = Config.STORAGE_DIR.resolve()
    resolved_path = path.resolve()
    if resolved_storage not in resolved_path.parents and resolved_path != resolved_storage:
        raise ValueError("Unsafe storage path")
    return resolved_path


def save_encrypted(stored_filename: str, data: bytes) -> Path:
    path = encrypted_path(stored_filename)
    path.write_bytes(data)
    return path


def read_encrypted(stored_filename: str) -> bytes:
    return encrypted_path(stored_filename).read_bytes()


def delete_encrypted(stored_filename: str) -> None:
    path = encrypted_path(stored_filename)
    if path.exists():
        path.unlink()
