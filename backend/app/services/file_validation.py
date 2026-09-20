import os
import re
from pathlib import Path
from typing import Tuple
from fastapi import HTTPException, status
from backend.app.config import get_settings

settings = get_settings()

# Magic byte signatures
PDF_MAGIC_BYTES = b"%PDF-"
ZIP_MAGIC_BYTES = b"PK\x03\x04"


def sanitize_filename(filename: str | None) -> str:
    """
    Sanitize an uploaded filename to prevent directory traversal and injection attacks.
    Removes path components and restricts characters to a safe set.
    """
    if not filename:
        return "unnamed_resume"

    # Strip any directory path components (e.g. ../../../etc/passwd -> passwd)
    clean_name = Path(filename).name

    # Remove non-printable or suspicious path characters
    clean_name = re.sub(r'[^\w\s\.-]', '_', clean_name)

    # Ensure filename doesn't start with sensitive patterns like .env
    if clean_name.startswith(".") or clean_name.lower().endswith((".env", ".key", ".pem")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File upload rejected: Invalid or restricted filename.",
        )

    return clean_name or "unnamed_resume"


def validate_file(filename: str, content: bytes, mime_type: str | None = None) -> Tuple[str, str]:
    """
    Validates an uploaded file's filename, size, extension, and binary content signature.

    Returns:
        Tuple[str, str]: (sanitized_filename, extension)

    Raises:
        HTTPException: 400 Bad Request or 413 Payload Too Large on validation failure.
    """
    # 1. Sanitize filename
    safe_filename = sanitize_filename(filename)
    extension = Path(safe_filename).suffix.lower()

    # 2. Check for empty files
    if not content or len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty (0 bytes). Please upload a valid document.",
        )

    # 3. Check file size against limit (5MB)
    if len(content) > settings.MAX_FILE_SIZE_BYTES:
        max_mb = settings.MAX_FILE_SIZE_BYTES / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"File size exceeds maximum allowed limit of {max_mb:.0f} MB.",
        )

    # 4. Check extension
    if extension not in settings.ALLOWED_EXTENSIONS:
        allowed_str = ", ".join(settings.ALLOWED_EXTENSIONS)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{extension}'. Allowed file types are: {allowed_str}.",
        )

    # 5. Magic Byte / Binary Content Header Inspection
    if extension == ".pdf":
        if not content.startswith(PDF_MAGIC_BYTES):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File claims to be a PDF but lacks a valid PDF header signature.",
            )
    elif extension == ".docx":
        if not content.startswith(ZIP_MAGIC_BYTES):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File claims to be a DOCX document but lacks a valid zip binary signature.",
            )

    return safe_filename, extension
