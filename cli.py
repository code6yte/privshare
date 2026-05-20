import argparse
from pathlib import Path

from cleanup import cleanup_expired_files
from config import Config
from crypto_utils import InvalidPassword, decrypt_bytes, encrypt_bytes, generate_token
from db import init_db, list_file_records


def cmd_init_db(_args):
    Config.ensure_dirs()
    init_db()
    print(f"Database initialized at: {Config.DATABASE_PATH}")


def cmd_cleanup_expired(_args):
    removed = cleanup_expired_files()
    print(f"Removed expired files: {removed}")


def cmd_list_files(args):
    rows = list_file_records(limit=args.limit)
    if not rows:
        print("No file records found.")
        return
    for row in rows:
        print("-" * 72)
        print(f"Token:      {row['token']}")
        print(f"Filename:   {row['original_filename']}")
        print(f"Stored:     {row['stored_filename']}")
        print(f"Expires:    {row['expires_at']}")
        print(f"Downloads:  {row['download_count']}")
        print(f"Metadata:   {row['metadata_status']}")


def cmd_smoke_test(_args):
    password = "correct horse battery staple"
    wrong = "wrong password"
    data = b"Privacy preserving file sharing smoke test."

    encrypted = encrypt_bytes(data, password, iterations=Config.PBKDF2_ITERATIONS)
    decrypted = decrypt_bytes(encrypted.ciphertext, password, encrypted.salt, encrypted.nonce, iterations=Config.PBKDF2_ITERATIONS)
    assert decrypted == data

    try:
        decrypt_bytes(encrypted.ciphertext, wrong, encrypted.salt, encrypted.nonce, iterations=Config.PBKDF2_ITERATIONS)
        raise AssertionError("Wrong password should not decrypt")
    except InvalidPassword:
        pass

    token = generate_token(24)
    assert len(token) > 20

    print("Smoke test passed.")
    print("- Correct password decrypts")
    print("- Wrong password fails")
    print("- Secure token generated")


def cmd_tree(_args):
    root = Path.cwd()
    skip = {".git", ".venv", "__pycache__", ".pytest_cache"}
    for path in sorted(root.rglob("*")):
        parts = set(path.parts)
        if parts.intersection(skip):
            continue
        depth = len(path.relative_to(root).parts) - 1
        print("  " * depth + ("└── " if depth else "") + path.name)


def build_parser():
    parser = argparse.ArgumentParser(description="PrivShare CLI agents")
    sub = parser.add_subparsers(required=True)

    p = sub.add_parser("init-db", help="Initialize SQLite database")
    p.set_defaults(func=cmd_init_db)

    p = sub.add_parser("cleanup-expired", help="Delete expired encrypted files and records")
    p.set_defaults(func=cmd_cleanup_expired)

    p = sub.add_parser("list-files", help="List recent file records")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_list_files)

    p = sub.add_parser("smoke-test", help="Run basic crypto smoke test")
    p.set_defaults(func=cmd_smoke_test)

    p = sub.add_parser("tree", help="Print project tree")
    p.set_defaults(func=cmd_tree)

    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    args.func(args)
