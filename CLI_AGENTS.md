# CLI_AGENTS.md

## Purpose

This project includes CLI helper agents to manage the project during development, testing, and demo.

Run commands from the project root.

## Initialize Database

```bash
python cli.py init-db
```

Creates the SQLite database and required tables.

## List Stored File Records

```bash
python cli.py list-files
```

Shows token, filename, expiry time, download count, and metadata cleaning status.

## Delete Expired Files

```bash
python cli.py cleanup-expired
```

Removes expired database records and encrypted files.

## Smoke Test Crypto

```bash
python cli.py smoke-test
```

Checks:

- Password-derived encryption
- Correct decryption
- Wrong password rejection
- Token generation

## Project Tree

```bash
python cli.py tree
```

Prints the project structure.

## Why CLI Agents Help

They make the project easier to present:

- You can show database initialization.
- You can show encrypted file records.
- You can clean expired demo data.
- You can prove encryption works from the terminal.
