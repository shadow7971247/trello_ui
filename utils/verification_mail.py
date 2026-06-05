"""Получение кода верификации Atlassian из почты (IMAP)."""

from __future__ import annotations

import email
import imaplib
import os
import re
import time
from datetime import datetime, timezone
from email.header import decode_header
from email.utils import parsedate_to_datetime

import allure

_CODE_PATTERNS = (
    re.compile(r"verification code[:\s]+(\d{6})", re.I),
    re.compile(r"security code[:\s]+(\d{6})", re.I),
    re.compile(r"\b(\d{6})\b"),
)

_ATLASSIAN_HINTS = ("atlassian", "trello", "id.atlassian.com")


def imap_configured() -> bool:
    host = os.getenv("TRELLO_IMAP_HOST", "").strip()
    password = os.getenv("TRELLO_IMAP_PASSWORD", "").strip()
    return bool(host and password)


def _decode_mime(value: str) -> str:
    parts: list[str] = []
    for chunk, enc in decode_header(value):
        if isinstance(chunk, bytes):
            parts.append(chunk.decode(enc or "utf-8", errors="replace"))
        else:
            parts.append(chunk)
    return "".join(parts)


def _extract_code(text: str) -> str | None:
    for pattern in _CODE_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1)
    return None


def _message_text(msg: email.message.Message) -> str:
    chunks: list[str] = []
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() not in ("text/plain", "text/html"):
                continue
            payload = part.get_payload(decode=True)
            if payload:
                chunks.append(payload.decode(part.get_content_charset() or "utf-8", errors="replace"))
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            chunks.append(payload.decode(msg.get_content_charset() or "utf-8", errors="replace"))
    return "\n".join(chunks)


def _is_atlassian_message(msg: email.message.Message) -> bool:
    subject = _decode_mime(msg.get("Subject", ""))
    from_hdr = _decode_mime(msg.get("From", ""))
    blob = f"{subject} {from_hdr}".lower()
    return any(hint in blob for hint in _ATLASSIAN_HINTS)


def fetch_verification_code(
    *,
    not_before: datetime | None = None,
    timeout_sec: float | None = None,
    poll_sec: float = 5.0,
) -> str:
    """
    Ждёт письмо Atlassian с 6-значным кодом и возвращает его.
    Требует TRELLO_IMAP_HOST и TRELLO_IMAP_PASSWORD.
    """
    if not imap_configured():
        raise RuntimeError(
            "IMAP не настроен: задайте TRELLO_IMAP_HOST и TRELLO_IMAP_PASSWORD "
            "(для Proton нужен Bridge; для CI удобнее Gmail + app password)."
        )

    host = os.getenv("TRELLO_IMAP_HOST", "").strip()
    port = int(os.getenv("TRELLO_IMAP_PORT", "993"))
    user = os.getenv("TRELLO_IMAP_USER", os.getenv("TRELLO_EMAIL", "")).strip()
    password = os.getenv("TRELLO_IMAP_PASSWORD", "").strip()
    folder = os.getenv("TRELLO_IMAP_FOLDER", "INBOX").strip() or "INBOX"
    use_ssl = os.getenv("TRELLO_IMAP_SSL", "true").lower() == "true"
    wait = timeout_sec if timeout_sec is not None else float(
        os.getenv("TRELLO_VERIFICATION_WAIT_SEC", "120")
    )
    since = not_before or datetime.now(timezone.utc)

    deadline = time.monotonic() + wait
    last_error: Exception | None = None

    with allure.step(f"Получить код верификации из IMAP ({host})"):
        while time.monotonic() < deadline:
            try:
                mail = imaplib.IMAP4_SSL(host, port) if use_ssl else imaplib.IMAP4(host, port)
                mail.login(user, password)
                mail.select(folder)
                _, data = mail.search(None, "UNSEEN")
                ids = (data[0] or b"").split()
                # Сначала непрочитанные, потом последние письма.
                if not ids:
                    _, data = mail.search(None, "ALL")
                    ids = (data[0] or b"").split()[-10:]

                for msg_id in reversed(ids):
                    _, msg_data = mail.fetch(msg_id, "(RFC822)")
                    if not msg_data or not msg_data[0]:
                        continue
                    raw = msg_data[0][1]
                    msg = email.message_from_bytes(raw)
                    if not _is_atlassian_message(msg):
                        continue
                    msg_date = msg.get("Date")
                    if msg_date:
                        try:
                            dt = parsedate_to_datetime(msg_date)
                            if dt.tzinfo is None:
                                dt = dt.replace(tzinfo=timezone.utc)
                            if dt < since:
                                continue
                        except Exception:
                            pass
                    body = _message_text(msg)
                    subject = _decode_mime(msg.get("Subject", ""))
                    code = _extract_code(f"{subject}\n{body}")
                    if code:
                        allure.attach(
                            f"subject={subject}\ncode={code}",
                            name="verification-email",
                            attachment_type=allure.attachment_type.TEXT,
                        )
                        mail.logout()
                        return code
                mail.logout()
            except Exception as exc:
                last_error = exc
            time.sleep(poll_sec)

    detail = f" ({last_error})" if last_error else ""
    raise TimeoutError(
        f"Код верификации не пришёл за {int(wait)} с через IMAP{detail}"
    )
