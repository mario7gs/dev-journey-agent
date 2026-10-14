from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.pdf_exporter import PDFExportError, render_pdf


def test_render_pdf_invokes_headless_browser(monkeypatch, tmp_path):
    html_path = tmp_path / "report.html"
    pdf_path = tmp_path / "report.pdf"
    html_path.write_text("<html><body>report</body></html>", encoding="utf-8")
    seen: dict[str, object] = {}

    def fake_run(command, **kwargs):
        seen["command"] = command
        seen["kwargs"] = kwargs
        output = next(item for item in command if str(item).startswith("--print-to-pdf="))
        Path(str(output).split("=", 1)[1]).write_bytes(b"%PDF-1.7 test")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("tools.pdf_exporter.find_chrome", lambda _binary=None: "/usr/bin/chrome")
    monkeypatch.setattr("tools.pdf_exporter.subprocess.run", fake_run)

    result = render_pdf(html_path, pdf_path)

    assert result == pdf_path.resolve()
    command = seen["command"]
    assert isinstance(command, list)
    assert "--headless=new" in command
    assert "--no-pdf-header-footer" in command
    assert html_path.resolve().as_uri() in command
    assert pdf_path.resolve().exists()


def test_render_pdf_reports_missing_browser(monkeypatch, tmp_path):
    html_path = tmp_path / "report.html"
    html_path.write_text("<html></html>", encoding="utf-8")
    monkeypatch.setattr("tools.pdf_exporter.find_chrome", lambda _binary=None: None)

    with pytest.raises(PDFExportError, match="No Chromium-compatible browser"):
        render_pdf(html_path, tmp_path / "report.pdf")
