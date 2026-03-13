from __future__ import annotations

import datetime
import time
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Iterable, List, Mapping

import gspread
import requests
from oauth2client import client as oauth_client
from oauth2client.service_account import ServiceAccountCredentials

from utils.schema_formatter import OUTPUT_FIELDS

_time_offset = 0.0
try:
    r = requests.get("https://www.googleapis.com", timeout=3)
    google_dt = parsedate_to_datetime(r.headers["Date"])
    google_time = google_dt.timestamp()
    local_time = time.time()
    if abs(google_time - local_time) > 300:
        _time_offset = google_time - local_time
        _orig_time = time.time

        def _patched_time():
            return _orig_time() + _time_offset

        time.time = _patched_time

        # oauth2client uses its own module-level UTC clock when minting JWTs.
        oauth_client._UTCNOW = lambda: datetime.datetime.utcnow() + datetime.timedelta(seconds=_time_offset)
except Exception:
    pass


def _get_client(credentials_path: Path) -> gspread.Client:
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(str(credentials_path), scopes)
    return gspread.authorize(creds)


def append_to_sheet(
    credentials_path: Path,
    sheet_name: str,
    worksheet_name: str,
    records: Iterable[Mapping[str, Any]],
) -> None:
    if not credentials_path.exists():
        raise FileNotFoundError(f"Google credentials not found at {credentials_path}")
    try:
        client = _get_client(credentials_path)
    except Exception as exc:
        raise ValueError(f"Invalid Google credentials: {exc}")
    try:
        sh = client.open(sheet_name)
    except gspread.SpreadsheetNotFound:
        raise ValueError(f"Could not find a Google Sheet named '{sheet_name}'. Please ensure you have created a blank Google Spreadsheet named EXACTLY '{sheet_name}' and shared it with the service account email.")
    except gspread.exceptions.APIError as e:
        raise ValueError(f"Google API Error: {e}. Ensure you enabled Google Sheets and Google Drive APIs.")
        
    try:
        ws = sh.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=worksheet_name, rows="1000", cols=str(len(OUTPUT_FIELDS)))

    rows: List[Mapping[str, Any]] = list(records)
    if not rows:
        return

    values: List[List[Any]] = []
    for row in rows:
        values.append([row.get(field, "") for field in OUTPUT_FIELDS])

    # Ensure header exists.
    existing = ws.get_all_values()
    if not existing:
        ws.append_row(OUTPUT_FIELDS)

    ws.append_rows(values)

