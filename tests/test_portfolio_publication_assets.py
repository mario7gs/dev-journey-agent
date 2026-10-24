from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_portfolio_publication_assets_follow_the_brand_contract() -> None:
    deck = (ROOT / "artifacts/portfolio/DEV_JOURNEY_PORTFOLIO_DECK.html").read_text(
        encoding="utf-8"
    )
    kit = (ROOT / "docs/PORTFOLIO_PUBLICATION_KIT.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "DEV JOURNEY" in deck
    assert "AGENT · FEATURE PLANNING COPILOT" in deck
    assert "A clearer way to start software work." in deck
    assert "Why it can be trusted" in deck
    assert "position:sticky" in deck
    assert "@media print" in deck
    assert 'href="#product"' in deck
    assert 'href="#evidence"' in deck
    assert "LinkedIn post — publish-ready" in kit
    assert "DEV_JOURNEY_AGENT_LINKEDIN_CAROUSEL.pdf" in kit
    assert "LinkedIn" in kit
    assert "GitHub" in kit
    assert "DEMO_SUMMARY.html" in kit
    assert "MCP" in kit
    assert "What this project does" in readme
    assert "PORTFOLIO_HANDOFF.md" in readme
    assert (ROOT / "artifacts/linkedin/DEV_JOURNEY_AGENT_LINKEDIN_CAROUSEL.pdf").is_file()
    assert (ROOT / "artifacts/linkedin/DEV_JOURNEY_AGENT_LINKEDIN_CAROUSEL.pptx").is_file()
    assert (ROOT / "CONTRIBUTING.md").is_file()
    assert (ROOT / "SECURITY.md").is_file()
