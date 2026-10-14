"""Render local stakeholder HTML files to PDF with an installed Chromium browser."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


class PDFExportError(RuntimeError):
    """Raised when a local HTML document cannot be rendered to PDF."""


def find_chrome(binary: str | None = None) -> str | None:
    """Find a Chromium-compatible browser without downloading or using the network."""
    candidates = [binary, os.getenv("DJ_CHROME_BINARY"), "google-chrome", "chromium", "chromium-browser"]
    for candidate in candidates:
        if candidate:
            resolved = shutil.which(candidate)
            if resolved:
                return resolved
    return None


def render_pdf(
    html_path: str | Path,
    pdf_path: str | Path,
    *,
    chrome_binary: str | None = None,
    timeout_seconds: int = 60,
) -> Path:
    """Render a local HTML file to a PDF using headless Chrome."""
    source = Path(html_path).resolve()
    destination = Path(pdf_path).resolve()
    if not source.is_file():
        raise PDFExportError(f"HTML source not found: {source}")
    browser = find_chrome(chrome_binary)
    if browser is None:
        raise PDFExportError(
            "No Chromium-compatible browser found. Install Google Chrome or set DJ_CHROME_BINARY."
        )
    destination.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="dev-journey-chrome-") as profile_dir:
        command = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--no-pdf-header-footer",
            f"--user-data-dir={profile_dir}",
            f"--print-to-pdf={destination}",
            source.as_uri(),
        ]
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise PDFExportError(f"PDF renderer failed for {source.name}: {exc}") from exc
        if completed.returncode != 0:
            raise PDFExportError(
                f"PDF renderer exited with code {completed.returncode} for {source.name}."
            )

    if not destination.is_file() or destination.stat().st_size == 0:
        raise PDFExportError(f"PDF renderer produced no output: {destination}")
    return destination
