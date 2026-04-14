import os
from uuid import uuid4
from fastapi import UploadFile

RECEIPTS_DIR = os.path.join("media", "receipts")


def save_receipt(receipt: UploadFile) -> str:
    os.makedirs(RECEIPTS_DIR, exist_ok=True)

    ext = os.path.splitext(receipt.filename)[1].lower()
    filename = f"{uuid4().hex}{ext}"
    filepath = os.path.join(RECEIPTS_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(receipt.file.read())

    return filepath