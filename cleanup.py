from db import delete_file_record, expired_records
from storage import delete_encrypted


def cleanup_expired_files() -> int:
    count = 0
    for row in expired_records():
        delete_encrypted(row["stored_filename"])
        delete_file_record(row["token"])
        count += 1
    return count
